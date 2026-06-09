"""Spec-driven tests for tools.terra_server (KiCad HTTP Library v1).

These tests are written against the spec
(docs/superpowers/specs/2026-06-08-terra-http-library-design.md) and the pinned
API contract. They build their own fixture SQLite database + .kicad_dbl spec and
exercise the pure helpers and the FastAPI endpoints via TestClient.

The implementation (tools/terra_server.py) is written independently; this module
imports from it but does not stub it.
"""

import hashlib
import json
import re
import sqlite3

import pytest

from tools.terra_server import (
    build_id_map,
    build_name,
    create_app,
    display_value,
    load_spec,
    part_id,
    sanitize,
    serialize_part,
)

# fastapi.testclient is the documented way to drive create_app(...).
from fastapi.testclient import TestClient


ALLOWED_CHARS = re.compile(r"^[A-Za-z0-9._-]*$")

# An MPN containing '/', space and ':' to exercise sanitize end to end.
SLASHED_MPN = "MURATA POWER SOLUTIONS-OKI-78SR-3.3/1.5:W36H"


def _expected_pid(unique_id):
    """Reference implementation of the id hash, per the contract."""
    return hashlib.sha1(unique_id.encode()).hexdigest()[:16]


def _kicad_fix_illegal_chars(s):
    """Mimic KiCad's LIB_ID sanitization: replace '/', ':', whitespace and any
    non-allow-list char with '_'."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

# Rows for the primary `bjt` base table. Columns:
# unique_id, mpn, value, kicad_symbol, kicad_footprint, tier
BJT_ROWS = [
    # tier 0 (curated) — visible at default cutoff
    ("CERN-BJT-0001", "BC847", "NPN 45V", "Transistor_BJT:BC847", "Package_TO_SOT_SMD:SOT-23", 0),
    # tier 1 — visible at default cutoff; MPN with '/', space, ':' for sanitize
    ("CERN-BJT-0002", SLASHED_MPN, "Module", "Transistor_BJT:Generic", "Package:Custom", 1),
    # tier 3 — hidden at default cutoff (tier<=2), visible at --tier 3
    ("CERN-BJT-0003", "MMBT3904", "NPN 40V", "Transistor_BJT:MMBT3904", "", 3),
    # a row whose footprint AND value are NULL/empty to exercise omission rules
    ("CERN-BJT-0004", "BC857", None, "Transistor_BJT:BC857", None, 0),
]


def _make_db(path, rows):
    conn = sqlite3.connect(str(path))
    conn.execute(
        """
        CREATE TABLE bjt (
            unique_id      TEXT,
            mpn            TEXT,
            value          TEXT,
            kicad_symbol   TEXT,
            kicad_footprint TEXT,
            tier           INTEGER
        )
        """
    )
    conn.executemany(
        "INSERT INTO bjt (unique_id, mpn, value, kicad_symbol, kicad_footprint, tier)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()
    return path


def _dbl_spec():
    """A .kicad_dbl JSON whose single library points at the `bjt_v` view.

    fields list (order matters: display_col = first non-symbol/footprint column):
      - mpn   -> "Manufacturer PN"
      - value -> "Value"
      - kicad_symbol    -> "Symbol"   (visible_in_chooser false; the symbols col)
      - kicad_footprint -> "Footprint"(visible_in_chooser true;  the footprints col)
    """
    return {
        "meta": {"version": 0},
        "name": "Terra",
        "libraries": [
            {
                "name": "Bipolar Transistors",
                "table": "bjt_v",
                "key": "unique_id",
                "symbols": "kicad_symbol",
                "footprints": "kicad_footprint",
                "fields": [
                    {"column": "mpn", "name": "Manufacturer PN", "visible_in_chooser": True},
                    {"column": "value", "name": "Value", "visible_in_chooser": True},
                    {"column": "kicad_symbol", "name": "Symbol", "visible_in_chooser": False},
                    {"column": "kicad_footprint", "name": "Footprint", "visible_in_chooser": True},
                ],
            }
        ],
    }


@pytest.fixture
def db_path(tmp_path):
    """Fixture SQLite DB with rows at tier 0, 1 and 3."""
    return _make_db(tmp_path / "terra.db", BJT_ROWS)


@pytest.fixture
def dbl_path(tmp_path):
    """Matching .kicad_dbl spec file on disk."""
    p = tmp_path / "terra.kicad_dbl"
    p.write_text(json.dumps(_dbl_spec()))
    return p


@pytest.fixture
def specs(dbl_path):
    return load_spec(str(dbl_path))


@pytest.fixture
def spec(specs):
    """The single library spec dict."""
    return specs[0]


@pytest.fixture
def client(db_path, dbl_path):
    """TestClient at the default tier cutoff (2)."""
    return TestClient(create_app(str(db_path), str(dbl_path)))


@pytest.fixture
def client_tier3(db_path, dbl_path):
    """TestClient with the cutoff raised to 3 so tier-3 rows appear in listings."""
    return TestClient(create_app(str(db_path), str(dbl_path), tier=3))


# --------------------------------------------------------------------------- #
# part_id
# --------------------------------------------------------------------------- #

def test_part_id_deterministic_16_lower_hex():
    pid = part_id("CERN-BJT-0001")
    # deterministic
    assert pid == part_id("CERN-BJT-0001")
    # first 16 hex chars of sha1(unique_id)
    assert pid == _expected_pid("CERN-BJT-0001")
    # exactly 16 lowercase hex chars
    assert len(pid) == 16
    assert re.fullmatch(r"[0-9a-f]{16}", pid)


def test_part_id_distinct_for_distinct_input():
    assert part_id("CERN-BJT-0001") != part_id("CERN-BJT-0002")


# --------------------------------------------------------------------------- #
# sanitize
# --------------------------------------------------------------------------- #

def test_sanitize_replaces_slash_colon_space():
    assert sanitize("a/b") == "a_b"
    assert sanitize("a:b") == "a_b"
    assert sanitize("a b") == "a_b"
    assert sanitize("MURATA POWER/OKI:78SR") == "MURATA_POWER_OKI_78SR"


def test_sanitize_leaves_legal_strings_unchanged():
    legal = "Abc_123.def-XYZ"
    assert sanitize(legal) == legal


def test_sanitize_output_is_allow_list_only():
    out = sanitize(SLASHED_MPN)
    assert ALLOWED_CHARS.fullmatch(out)


# --------------------------------------------------------------------------- #
# build_name
# --------------------------------------------------------------------------- #

def test_build_name_combines_sanitized_display_and_pid():
    pid = part_id("CERN-BJT-0001")
    assert build_name("BC847", pid) == f"BC847_{pid}"


def test_build_name_falls_back_to_pid_when_display_empty():
    pid = part_id("CERN-BJT-0001")
    assert build_name(None, pid) == pid
    assert build_name("", pid) == pid


def test_build_name_sanitizes_slash_in_display():
    pid = part_id("CERN-BJT-0002")
    name = build_name(SLASHED_MPN, pid)
    assert name == f"{sanitize(SLASHED_MPN)}_{pid}"
    assert "/" not in name and ":" not in name and " " not in name


def test_build_name_is_allow_list_and_fix_illegal_is_noop():
    # name must contain only allow-list chars, and KiCad's FixIllegalChars is a no-op.
    pid = part_id("CERN-BJT-0002")
    name = build_name(SLASHED_MPN, pid)
    assert ALLOWED_CHARS.fullmatch(name)
    assert _kicad_fix_illegal_chars(name) == name


def test_build_name_unique_for_same_display_different_pid():
    # Two rows with the same MPN still get distinct names via the pid suffix.
    n1 = build_name("BC847", part_id("CERN-BJT-0001"))
    n2 = build_name("BC847", part_id("CERN-BJT-9999"))
    assert n1 != n2


# --------------------------------------------------------------------------- #
# load_spec
# --------------------------------------------------------------------------- #

def test_load_spec_strips_v_suffix_to_base_table(spec):
    assert spec["base_table"] == "bjt"


def test_load_spec_carries_key_symbols_footprints(spec):
    assert spec["key"] == "unique_id"
    assert spec["symbols"] == "kicad_symbol"
    assert spec["footprints"] == "kicad_footprint"


def test_load_spec_display_col_is_first_non_symbol_footprint_field(spec):
    # First field column not equal to the symbols/footprints column -> "mpn".
    assert spec["display_col"] == "mpn"


def test_load_spec_name_and_fields_present(spec):
    assert spec["name"] == "Bipolar Transistors"
    # carries the field definitions
    field_cols = {f["column"] for f in spec["fields"]}
    assert {"mpn", "value", "kicad_symbol", "kicad_footprint"} <= field_cols


# --------------------------------------------------------------------------- #
# display_value
# --------------------------------------------------------------------------- #

def test_display_value_uses_display_col_when_truthy(spec):
    row = {"unique_id": "CERN-BJT-0001", "mpn": "BC847"}
    assert display_value(row, spec) == "BC847"


def test_display_value_falls_back_to_key_when_display_empty(spec):
    row = {"unique_id": "CERN-BJT-0004", "mpn": None}
    assert display_value(row, spec) == "CERN-BJT-0004"
    row2 = {"unique_id": "CERN-BJT-0004", "mpn": ""}
    assert display_value(row2, spec) == "CERN-BJT-0004"


# --------------------------------------------------------------------------- #
# build_id_map
# --------------------------------------------------------------------------- #

def test_build_id_map_covers_all_rows_including_high_tier(db_path, specs):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    id_map = build_id_map(conn, specs)
    conn.close()
    # every fixture row, regardless of tier, is present
    for unique_id in ("CERN-BJT-0001", "CERN-BJT-0002", "CERN-BJT-0003", "CERN-BJT-0004"):
        pid = part_id(unique_id)
        assert pid in id_map
        base_table, mapped_uid = id_map[pid]
        assert base_table == "bjt"
        assert mapped_uid == unique_id
    assert len(id_map) == len(BJT_ROWS)


def test_build_id_map_raises_on_cross_table_duplicate_unique_id(tmp_path):
    # Second tiny DB/dbl with two tables sharing a unique_id.
    db = tmp_path / "dup.db"
    conn = sqlite3.connect(str(db))
    for tbl in ("alpha", "beta"):
        conn.execute(
            f"CREATE TABLE {tbl} (unique_id TEXT, mpn TEXT, value TEXT,"
            " kicad_symbol TEXT, kicad_footprint TEXT, tier INTEGER)"
        )
    conn.execute(
        "INSERT INTO alpha VALUES ('SHARED-UID', 'A', 'v', 'Lib:Sa', 'Lib:Fa', 0)"
    )
    conn.execute(
        "INSERT INTO beta VALUES ('SHARED-UID', 'B', 'v', 'Lib:Sb', 'Lib:Fb', 0)"
    )
    conn.commit()

    dbl = tmp_path / "dup.kicad_dbl"
    dbl.write_text(
        json.dumps(
            {
                "meta": {"version": 0},
                "name": "Dup",
                "libraries": [
                    {
                        "name": "Alpha",
                        "table": "alpha_v",
                        "key": "unique_id",
                        "symbols": "kicad_symbol",
                        "footprints": "kicad_footprint",
                        "fields": [
                            {"column": "mpn", "name": "Manufacturer PN", "visible_in_chooser": True},
                            {"column": "kicad_symbol", "name": "Symbol", "visible_in_chooser": False},
                            {"column": "kicad_footprint", "name": "Footprint", "visible_in_chooser": True},
                        ],
                    },
                    {
                        "name": "Beta",
                        "table": "beta_v",
                        "key": "unique_id",
                        "symbols": "kicad_symbol",
                        "footprints": "kicad_footprint",
                        "fields": [
                            {"column": "mpn", "name": "Manufacturer PN", "visible_in_chooser": True},
                            {"column": "kicad_symbol", "name": "Symbol", "visible_in_chooser": False},
                            {"column": "kicad_footprint", "name": "Footprint", "visible_in_chooser": True},
                        ],
                    },
                ],
            }
        )
    )
    dup_specs = load_spec(str(dbl))
    conn.row_factory = sqlite3.Row
    with pytest.raises(ValueError):
        build_id_map(conn, dup_specs)
    conn.close()


def test_build_id_map_raises_on_null_key(tmp_path):
    db = tmp_path / "nullkey.db"
    conn = sqlite3.connect(str(db))
    conn.execute(
        "CREATE TABLE bjt (unique_id TEXT, mpn TEXT, value TEXT,"
        " kicad_symbol TEXT, kicad_footprint TEXT, tier INTEGER)"
    )
    conn.execute("INSERT INTO bjt VALUES (NULL, 'X', 'v', 'Lib:S', 'Lib:F', 0)")
    conn.commit()

    dbl = tmp_path / "nullkey.kicad_dbl"
    dbl.write_text(json.dumps(_dbl_spec()))
    nk_specs = load_spec(str(dbl))
    conn.row_factory = sqlite3.Row
    with pytest.raises(ValueError):
        build_id_map(conn, nk_specs)
    conn.close()


# --------------------------------------------------------------------------- #
# serialize_part
# --------------------------------------------------------------------------- #

def _row(unique_id):
    for r in BJT_ROWS:
        if r[0] == unique_id:
            return {
                "unique_id": r[0],
                "mpn": r[1],
                "value": r[2],
                "kicad_symbol": r[3],
                "kicad_footprint": r[4],
                "tier": r[5],
            }
    raise KeyError(unique_id)


def test_serialize_part_basic_shape_and_string_booleans(spec):
    row = _row("CERN-BJT-0001")
    pid = part_id("CERN-BJT-0001")
    part = serialize_part(row, spec, pid)

    assert part["id"] == pid
    assert part["name"] == build_name("BC847", pid)
    assert part["symbolIdStr"] == "Transistor_BJT:BC847"

    # All booleans are STRINGS, never JSON booleans.
    for key in ("exclude_from_bom", "exclude_from_board", "exclude_from_sim"):
        assert part[key] in ("true", "false")
        assert isinstance(part[key], str)
    assert part["exclude_from_bom"] == "false"
    assert part["exclude_from_board"] == "false"
    assert part["exclude_from_sim"] == "false"


def test_serialize_part_footprint_is_in_fields_not_top_level(spec):
    row = _row("CERN-BJT-0001")
    pid = part_id("CERN-BJT-0001")
    part = serialize_part(row, spec, pid)

    assert "footprint" not in part  # not a top-level key
    fp = part["fields"]["footprint"]
    assert fp == {"value": "Package_TO_SOT_SMD:SOT-23", "visible": "true"}


def test_serialize_part_no_symbol_field_and_no_duplicate_footprint_field(spec):
    row = _row("CERN-BJT-0001")
    pid = part_id("CERN-BJT-0001")
    part = serialize_part(row, spec, pid)
    fields = part["fields"]

    # The symbols/footprints columns (surfaced as "Symbol"/"Footprint" in the dbl)
    # MUST NOT appear as generic fields.
    assert "Symbol" not in fields
    # The only "footprint"-ish key is the canonical lowercase one.
    assert "Footprint" not in fields
    assert "footprint" in fields
    # canonical footprint not clobbered by a generic field
    assert fields["footprint"]["value"] == "Package_TO_SOT_SMD:SOT-23"


def test_serialize_part_generic_fields_visibility_and_values(spec):
    row = _row("CERN-BJT-0001")
    pid = part_id("CERN-BJT-0001")
    part = serialize_part(row, spec, pid)
    fields = part["fields"]

    # mpn -> "Manufacturer PN", visible_in_chooser True -> "true"
    assert fields["Manufacturer PN"] == {"value": "BC847", "visible": "true"}
    # value -> "Value", visible True
    assert fields["Value"] == {"value": "NPN 45V", "visible": "true"}


def test_serialize_part_visible_false_field_serializes_string_false(spec):
    # Use a spec variant where the Value field is visible_in_chooser False.
    custom = _dbl_spec()
    custom["libraries"][0]["fields"][1]["visible_in_chooser"] = False
    import tempfile, os
    fd, p = tempfile.mkstemp(suffix=".kicad_dbl")
    os.write(fd, json.dumps(custom).encode())
    os.close(fd)
    try:
        s = load_spec(p)[0]
    finally:
        os.unlink(p)

    row = _row("CERN-BJT-0001")
    pid = part_id("CERN-BJT-0001")
    part = serialize_part(row, s, pid)
    assert part["fields"]["Value"]["visible"] == "false"


def test_serialize_part_omits_null_and_empty_fields(spec):
    # CERN-BJT-0004 has value=None and footprint=None.
    row = _row("CERN-BJT-0004")
    pid = part_id("CERN-BJT-0004")
    part = serialize_part(row, spec, pid)
    fields = part["fields"]

    # null value field omitted (never emit "None")
    assert "Value" not in fields
    # null footprint omitted entirely
    assert "footprint" not in fields
    # present field still emitted
    assert fields["Manufacturer PN"]["value"] == "BC857"


def test_serialize_part_empty_footprint_string_omitted(spec):
    # CERN-BJT-0003 has kicad_footprint = "" (empty string).
    row = _row("CERN-BJT-0003")
    pid = part_id("CERN-BJT-0003")
    part = serialize_part(row, spec, pid)
    assert "footprint" not in part["fields"]


def test_serialize_part_no_json_boolean_anywhere(spec):
    # Round-trip through JSON and assert no Python/JSON booleans survive.
    row = _row("CERN-BJT-0001")
    pid = part_id("CERN-BJT-0001")
    part = serialize_part(row, spec, pid)

    def assert_no_bools(obj):
        if isinstance(obj, bool):
            raise AssertionError("found a JSON boolean")
        if isinstance(obj, dict):
            for v in obj.values():
                assert_no_bools(v)
        elif isinstance(obj, list):
            for v in obj:
                assert_no_bools(v)

    assert_no_bools(part)


# --------------------------------------------------------------------------- #
# Endpoint: /v1/ (root)
# --------------------------------------------------------------------------- #

def test_root_returns_categories_and_parts_nonempty_strings(client):
    resp = client.get("/v1/")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body.keys()) >= {"categories", "parts"}
    for key in ("categories", "parts"):
        assert isinstance(body[key], str)
        assert body[key] != ""  # KiCad checks !.empty()


# --------------------------------------------------------------------------- #
# Endpoint: categories.json
# --------------------------------------------------------------------------- #

def test_categories_json_shape_and_contents(client):
    resp = client.get("/v1/categories.json")
    assert resp.status_code == 200
    cats = resp.json()
    assert isinstance(cats, list)
    assert len(cats) == 1
    cat = cats[0]
    assert set(cat.keys()) == {"id", "name", "description"}
    assert cat["id"] == "bjt"  # base table name
    assert cat["name"] == "Bipolar Transistors"
    assert cat["description"] == ""


# --------------------------------------------------------------------------- #
# Endpoint: parts/category/{id}.json  (tier cutoff)
# --------------------------------------------------------------------------- #

def test_parts_category_default_tier_excludes_tier3(client):
    resp = client.get("/v1/parts/category/bjt.json")
    assert resp.status_code == 200
    parts = resp.json()
    ids = {p["id"] for p in parts}
    # tier 0/1/0 rows present
    assert part_id("CERN-BJT-0001") in ids
    assert part_id("CERN-BJT-0002") in ids
    assert part_id("CERN-BJT-0004") in ids
    # tier 3 row excluded
    assert part_id("CERN-BJT-0003") not in ids
    # each entry carries id and name
    for p in parts:
        assert "id" in p and "name" in p
        assert p["name"]


def test_parts_category_tier3_app_includes_tier3(client_tier3):
    resp = client_tier3.get("/v1/parts/category/bjt.json")
    assert resp.status_code == 200
    ids = {p["id"] for p in resp.json()}
    assert part_id("CERN-BJT-0003") in ids


def test_parts_category_id_matches_hash_of_unique_id(client):
    resp = client.get("/v1/parts/category/bjt.json")
    parts = {p["id"]: p for p in resp.json()}
    assert part_id("CERN-BJT-0001") in parts
    # id is the hash of the row's unique_id
    assert _expected_pid("CERN-BJT-0001") in parts


def test_parts_category_unknown_category_404(client):
    resp = client.get("/v1/parts/category/does_not_exist.json")
    assert resp.status_code == 404


# --------------------------------------------------------------------------- #
# Endpoint: parts/{id}.json
# --------------------------------------------------------------------------- #

def test_parts_id_returns_full_part_object(client):
    pid = part_id("CERN-BJT-0001")
    resp = client.get(f"/v1/parts/{pid}.json")
    assert resp.status_code == 200
    part = resp.json()
    assert part["id"] == pid
    assert part["symbolIdStr"] == "Transistor_BJT:BC847"
    assert part["fields"]["footprint"]["value"] == "Package_TO_SOT_SMD:SOT-23"
    # string booleans over the wire
    assert part["exclude_from_bom"] == "false"
    assert "Symbol" not in part["fields"]
    assert "Footprint" not in part["fields"]
    assert "footprint" not in part  # not top-level


def test_parts_id_name_byte_matches_category_listing_name(client):
    pid = part_id("CERN-BJT-0001")
    listing = client.get("/v1/parts/category/bjt.json").json()
    listed = next(p for p in listing if p["id"] == pid)
    direct = client.get(f"/v1/parts/{pid}.json").json()
    assert listed["name"] == direct["name"]  # byte-for-byte match


def test_parts_id_resolves_tier3_part_even_though_hidden_from_listing(client):
    # parts/{id} is tier-AGNOSTIC: resolves the tier-3 part the listing hid.
    pid = part_id("CERN-BJT-0003")
    # confirm it is hidden from the default listing
    listing_ids = {p["id"] for p in client.get("/v1/parts/category/bjt.json").json()}
    assert pid not in listing_ids
    # ...yet directly resolvable
    resp = client.get(f"/v1/parts/{pid}.json")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid


def test_parts_id_unknown_id_404(client):
    resp = client.get("/v1/parts/deadbeefdeadbeef.json")
    assert resp.status_code == 404


def test_parts_id_no_json_booleans_over_wire(client):
    pid = part_id("CERN-BJT-0001")
    # Read raw text and assert no bare JSON booleans appear as values.
    raw = client.get(f"/v1/parts/{pid}.json").text
    parsed = json.loads(raw)

    def assert_no_bools(obj):
        assert not isinstance(obj, bool)
        if isinstance(obj, dict):
            for v in obj.values():
                assert_no_bools(v)
        elif isinstance(obj, list):
            for v in obj:
                assert_no_bools(v)

    assert_no_bools(parsed)
