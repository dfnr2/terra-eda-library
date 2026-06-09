# Terra HTTP Library (v1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the slow ODBC `.kicad_dbl` with a local FastAPI server that implements KiCad's HTTP Library v1 API over the existing `db/terra.db`, plus a generated `terra.kicad_httplib`.

**Architecture:** A read-only FastAPI app loads `terra.kicad_dbl` as its field/library spec and serves four endpoints (`/v1/`, `/v1/categories.json`, `/v1/parts/category/{id}.json`, `/v1/parts/{id}.json`). Category listings are filtered by a default `tier <= 2` cutoff; the build is fixed first so curated/CERN parts are tier 0 (not the schema default 5). Part `id` is a stable `sha1(unique_id)[:16]`; the placed-symbol handle is `name = sanitize(display) + "_" + id`.

**Tech Stack:** Python 3.13, uv, FastAPI + uvicorn, SQLite (stdlib `sqlite3`), pytest + httpx (`TestClient`).

**Spec:** `docs/superpowers/specs/2026-06-08-terra-http-library-design.md` (read it before starting).

**Deviation from spec (justified):** the spec lists a `[project.scripts] terra-server` console script. `tools/` is not a declared package and the project has no build backend configured, so a console entry point would pull in packaging setup with no functional benefit — `make serve` runs `uv run python tools/terra_server.py`, which fully satisfies the requirement. The console script is omitted from v1.

---

## File Structure

- `pyproject.toml` — add `fastapi`, `uvicorn` runtime deps; `httpx` dev dep (Task 1).
- `tools/retier_static.py` — **new**: promotes non-parametric tables to `tier 0` (Task 2). One job: the re-tier transform.
- `Makefile` — wire re-tier into the `db/terra.db` recipe; add `serve` and `terra.kicad_httplib` targets (Tasks 3, 8, 9).
- `tools/terra_server.py` — **new**: the FastAPI app. Pure helpers (`part_id`, `sanitize`, `build_name`, `display_value`), spec loader (`load_spec`), id map + invariant (`build_id_map`), serializer (`serialize_part`), app factory (`create_app`), and `main()` (Tasks 4–8). One responsibility: serve the HTTP Library API.
- `tools/generate_kicad_httplib.py` — **new**: writes the static `terra.kicad_httplib` connection file (Task 9).
- `tests/test_retier_static.py` — **new** (Task 2).
- `tests/test_terra_server.py` — **new**: helper unit tests + `TestClient` endpoint tests, with a shared fixture DB (Tasks 4–7).
- `tests/test_generate_httplib.py` — **new** (Task 9).

Run all tests with: `uv run pytest tests/ -q`

---

### Task 1: Add dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add runtime + dev dependencies**

Edit `pyproject.toml` so the `dependencies` and `dev` lists read exactly:

```toml
dependencies = [
    "pyyaml>=6.0.3",
    "sexpdata>=1.0.2",
    "fastapi>=0.115",
    "uvicorn>=0.34",
]

[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "httpx>=0.28",
]
```

- [ ] **Step 2: Sync and verify the imports resolve**

Run: `uv sync && uv run python -c "import fastapi, uvicorn, httpx; print('ok')"`
Expected: prints `ok` (uv installs the new packages, no ImportError).

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "add fastapi/uvicorn/httpx deps for terra HTTP server"
```

---

### Task 2: Re-tier tool — promote static/curated tables to tier 0

Every CERN/static table is `tier=5` (schema default); only `resistors_smt`/`capacitors_smt` are intentionally tiered. This tool sets `tier=0` on every tiered table **except** the parametric set, so the `tier <= 2` cutoff keeps curated content.

**Files:**
- Create: `tools/retier_static.py`
- Test: `tests/test_retier_static.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_retier_static.py
import sqlite3
from tools.retier_static import retier_static, tables_with_tier


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE cern_x (unique_id TEXT PRIMARY KEY, tier INTEGER DEFAULT 5);
        INSERT INTO cern_x (unique_id) VALUES ('a'), ('b');           -- default 5
        CREATE TABLE resistors_smt (unique_id TEXT PRIMARY KEY, tier INTEGER);
        INSERT INTO resistors_smt VALUES ('r0', 0), ('r3', 3);
        CREATE TABLE tags (unique_id TEXT, tag TEXT);                 -- no tier column
        """
    )
    conn.commit()
    return conn


def test_tables_with_tier_excludes_non_tier_tables():
    conn = _make_db()
    assert set(tables_with_tier(conn)) == {"cern_x", "resistors_smt"}


def test_retier_promotes_static_but_not_parametric():
    conn = _make_db()
    promoted = retier_static(conn, parametric=["resistors_smt"])
    # cern_x: both rows were tier 5 -> 0
    assert [r[0] for r in conn.execute("SELECT tier FROM cern_x")] == [0, 0]
    assert promoted["cern_x"] == 2
    # resistors_smt untouched (parametric)
    assert sorted(r[0] for r in conn.execute("SELECT tier FROM resistors_smt")) == [0, 3]
    assert "resistors_smt" not in promoted
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_retier_static.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.retier_static'`.

- [ ] **Step 3: Write the implementation**

```python
# tools/retier_static.py
#!/usr/bin/env python3
"""Promote static/curated tables to tier 0.

Every non-parametric table defaults to tier 5 (the schema default for migrated/
CERN imports). The HTTP server's default `tier <= 2` cutoff would otherwise hide
all of them. This sets tier=0 on every tiered table except the parametric set
(resistors_smt, capacitors_smt), which carry deliberately-assigned tiers.
"""
import sqlite3
import sys
from typing import Iterable


def tables_with_tier(conn: sqlite3.Connection) -> list[str]:
    """Names of non-sqlite tables that have a `tier` column."""
    out = []
    for (name,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{name}")')]
        if "tier" in cols:
            out.append(name)
    return out


def retier_static(conn: sqlite3.Connection, parametric: Iterable[str]) -> dict[str, int]:
    """Set tier=0 on every tiered table not in `parametric`. Returns {table: rows_changed}."""
    parametric = set(parametric)
    promoted: dict[str, int] = {}
    for table in tables_with_tier(conn):
        if table in parametric:
            continue
        cur = conn.execute(f'UPDATE "{table}" SET tier = 0 WHERE tier IS NOT 0')
        if cur.rowcount:
            promoted[table] = cur.rowcount
    conn.commit()
    return promoted


def main() -> None:
    db_path = sys.argv[1]
    parametric = sys.argv[2:]
    conn = sqlite3.connect(db_path)
    promoted = retier_static(conn, parametric)
    for table, n in sorted(promoted.items()):
        print(f"  re-tiered {table}: {n} rows -> tier 0")
    conn.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_retier_static.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/retier_static.py tests/test_retier_static.py
git commit -m "add retier_static: promote non-parametric tables to tier 0"
```

---

### Task 3: Wire re-tier into the build and rebuild the DB

**Files:**
- Modify: `Makefile` (the `db/terra.db` recipe, after the table-loading loop ~line 213)

- [ ] **Step 1: Add the parametric-table variable**

Just below `DEFAULT_TIER := 2` (Makefile ~line 18), add:

```make
# Tables with deliberately-assigned tiers; everything else is re-tiered to 0.
PARAMETRIC_TIER_TABLES := resistors_smt capacitors_smt
```

- [ ] **Step 2: Call the re-tier tool in the db/terra.db recipe**

In the `db/terra.db:` recipe, immediately after the table-loading `@for table_dir ... done` block and **before** the `@echo "  Inserting default config..."` line, insert:

```make
	@echo "  Re-tiering static/curated tables to tier 0..."
	@$(PYTHON) tools/retier_static.py $@ $(PARAMETRIC_TIER_TABLES)
```

(`$(PYTHON)` is already defined in the Makefile and used by other recipes; `$@` is `db/terra.db`.)

- [ ] **Step 3: Rebuild and verify CERN is now tier 0 and visible at the cutoff**

```bash
rm -f db/terra.db && make db/terra.db
uv run python - <<'PY'
import sqlite3
c = sqlite3.connect("db/terra.db")
# every cern_* table must be entirely tier 0
bad = []
for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cern_%'"):
    mx = c.execute(f'SELECT MAX(tier) FROM "{t}"').fetchone()[0]
    if mx not in (0, None):
        bad.append((t, mx))
print("non-zero-tier CERN tables:", bad)
vis = sum(c.execute(f'SELECT COUNT(*) FROM "{t}" WHERE tier<=2').fetchone()[0]
          for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cern_%'"))
print("CERN parts visible at tier<=2:", vis)
assert not bad, bad
assert vis > 10000, vis
print("OK")
PY
```
Expected: `non-zero-tier CERN tables: []`, a CERN visible count in the ~13k range, then `OK`.

- [ ] **Step 4: Commit**

```bash
git add Makefile
git commit -m "re-tier static/curated tables to 0 in db/terra.db build"
```

---

### Task 4: Server pure helpers (id, sanitize, name)

**Files:**
- Create: `tools/terra_server.py`
- Test: `tests/test_terra_server.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_terra_server.py
from tools.terra_server import part_id, sanitize, build_name


def test_part_id_is_stable_16_hex():
    pid = part_id("KEMET-C0402C508D4GACTU")
    assert pid == part_id("KEMET-C0402C508D4GACTU")          # deterministic
    assert len(pid) == 16 and all(ch in "0123456789abcdef" for ch in pid)


def test_sanitize_maps_illegal_chars_to_underscore():
    # '/', ':', and space are illegal in KiCad LIB_ID symbol names
    assert sanitize("OKI-78SR-3.3/1.5 W:C") == "OKI-78SR-3.3_1.5_W_C"
    # already-legal chars are untouched
    assert sanitize("RC0603-10k_v2.0") == "RC0603-10k_v2.0"


def test_build_name_is_unique_and_falls_back_to_id():
    pid = part_id("MFR-PN1")
    assert build_name("MFR/PN 1", pid) == f"MFR_PN_1_{pid}"
    assert build_name("", pid) == pid
    assert build_name(None, pid) == pid
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.terra_server'`.

- [ ] **Step 3: Write the helpers**

```python
# tools/terra_server.py
#!/usr/bin/env python3
"""Local FastAPI server implementing KiCad's HTTP Library v1 API over db/terra.db.

Reads terra.kicad_dbl as the field/library spec. Part id is a stable hash of
unique_id; the placed-symbol name embeds that id so it is globally unique and
stable across rebuilds. See docs/superpowers/specs/2026-06-08-terra-http-library-design.md.
"""
import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

# Allow-list is a strict subset of KiCad's legal LIB_ID symbol-name characters
# (KiCad rejects '/', ':', and whitespace). Anything else -> '_'.
_ILLEGAL = re.compile(r"[^A-Za-z0-9._-]")


def part_id(unique_id: str) -> str:
    """Stable, URL-safe part id: first 16 hex chars of sha1(unique_id)."""
    return hashlib.sha1(unique_id.encode("utf-8")).hexdigest()[:16]


def sanitize(s: str) -> str:
    """Replace every non-allow-list character with '_' (KiCad-normalization-safe)."""
    return _ILLEGAL.sub("_", s)


def build_name(display: str | None, pid: str) -> str:
    """Globally-unique, stable symbol name: sanitized display + id, or just id."""
    if display:
        return f"{sanitize(display)}_{pid}"
    return pid
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/terra_server.py tests/test_terra_server.py
git commit -m "add terra_server id/sanitize/name helpers"
```

---

### Task 5: Spec loader + id map + global-uniqueness invariant

**Files:**
- Modify: `tools/terra_server.py`
- Test: `tests/test_terra_server.py`

- [ ] **Step 1: Add a shared fixture and the failing tests**

Add to the **top** of `tests/test_terra_server.py` (after the existing imports):

```python
import json
import sqlite3
import pytest
from tools.terra_server import load_spec, build_id_map, display_value

# A tiny DB + dbl mirroring terra's shape: base table `bjt` (dbl points at `bjt_v`),
# unique_id PK, mpn/value display fields, kicad_symbol/footprint, tier 0..3.
DBL = {
    "libraries": [
        {
            "name": "BJT Transistors",
            "table": "bjt_v",
            "key": "unique_id",
            "symbols": "kicad_symbol",
            "footprints": "kicad_footprint",
            "fields": [
                {"column": "mpn", "name": "Manufacturer PN",
                 "visible_in_chooser": True, "visible_on_add": False},
                {"column": "value", "name": "Value",
                 "visible_in_chooser": True, "visible_on_add": True},
                {"column": "kicad_symbol", "name": "Symbol",
                 "visible_in_chooser": False, "visible_on_add": False},
                {"column": "kicad_footprint", "name": "Footprint",
                 "visible_in_chooser": True, "visible_on_add": False},
            ],
        }
    ]
}


@pytest.fixture
def fixture_db(tmp_path):
    db = tmp_path / "t.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE bjt (
            unique_id TEXT PRIMARY KEY, mpn TEXT, value TEXT,
            kicad_symbol TEXT, kicad_footprint TEXT, tier INTEGER
        );
        INSERT INTO bjt VALUES
            ('NXP-BC847',  'BC847',  'NPN', 'Transistors:BJT', 'SOT:SOT-23', 0),
            ('NXP-BC857',  'BC857',  'PNP', 'Transistors:BJT', 'SOT:SOT-23', 1),
            ('OBS-XYZ/1',  'XYZ/1',  'NPN', 'Transistors:BJT', 'SOT:SOT-23', 3);
        """
    )
    conn.commit()
    conn.close()
    dbl = tmp_path / "terra.kicad_dbl"
    dbl.write_text(json.dumps(DBL))
    return db, dbl


def test_load_spec_resolves_base_table_and_display_col(fixture_db):
    _, dbl = fixture_db
    specs = load_spec(dbl)
    assert len(specs) == 1
    s = specs[0]
    assert s["category_id"] == "bjt" and s["base_table"] == "bjt"   # _v stripped
    assert s["key"] == "unique_id"
    assert s["display_col"] == "mpn"                                # first non-reserved field
    assert s["symbols"] == "kicad_symbol" and s["footprints"] == "kicad_footprint"


def test_build_id_map_covers_all_rows_ignoring_tier(fixture_db):
    db, dbl = fixture_db
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    id_map = build_id_map(conn, load_spec(dbl))
    assert len(id_map) == 3                                         # tier-3 row included
    from tools.terra_server import part_id
    assert id_map[part_id("OBS-XYZ/1")] == ("bjt", "OBS-XYZ/1")


def test_build_id_map_rejects_duplicate_unique_id(tmp_path):
    db = tmp_path / "dup.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE a (unique_id TEXT, kicad_symbol TEXT, kicad_footprint TEXT, mpn TEXT, tier INTEGER);
        CREATE TABLE b (unique_id TEXT, kicad_symbol TEXT, kicad_footprint TEXT, mpn TEXT, tier INTEGER);
        INSERT INTO a VALUES ('SAME','s','f','m',0);
        INSERT INTO b VALUES ('SAME','s','f','m',0);
        """
    )
    conn.commit()
    dbl = tmp_path / "d.kicad_dbl"
    dbl.write_text(json.dumps({"libraries": [
        {"name": "A", "table": "a", "key": "unique_id", "symbols": "kicad_symbol",
         "footprints": "kicad_footprint", "fields": [{"column": "mpn", "name": "Manufacturer PN",
         "visible_in_chooser": True, "visible_on_add": False}]},
        {"name": "B", "table": "b", "key": "unique_id", "symbols": "kicad_symbol",
         "footprints": "kicad_footprint", "fields": [{"column": "mpn", "name": "Manufacturer PN",
         "visible_in_chooser": True, "visible_on_add": False}]},
    ]}))
    conn2 = sqlite3.connect(db)
    with pytest.raises(ValueError, match="duplicate unique_id"):
        build_id_map(conn2, load_spec(dbl))
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: FAIL — `ImportError: cannot import name 'load_spec'`.

- [ ] **Step 3: Implement the loader, id map, and display helper**

Append to `tools/terra_server.py`:

```python
def load_spec(dbl_path: str | Path) -> list[dict]:
    """Load terra.kicad_dbl; return one spec per library with the base table resolved."""
    data = json.loads(Path(dbl_path).read_text())
    specs = []
    for lib in data["libraries"]:
        table = lib["table"]
        base = table[:-2] if table.endswith("_v") else table
        sym, fp = lib.get("symbols"), lib.get("footprints")
        display_col = None
        for field in lib["fields"]:
            if field["column"] in (sym, fp):
                continue
            display_col = field["column"]
            break
        specs.append({
            "category_id": base,
            "name": lib["name"],
            "base_table": base,
            "key": lib["key"],
            "symbols": sym,
            "footprints": fp,
            "display_col": display_col,
            "fields": lib["fields"],
        })
    return specs


def display_value(row: Any, spec: dict) -> str | None:
    """The human-readable string used for the name prefix: display col, else key."""
    d = row[spec["display_col"]] if spec["display_col"] else None
    return d if d else row[spec["key"]]


def build_id_map(conn: sqlite3.Connection, specs: list[dict]) -> dict[str, tuple[str, str]]:
    """Map part_id -> (base_table, unique_id) over ALL rows (tier-agnostic).

    Enforces the build invariant: unique_id non-null and globally unique. Raises
    ValueError on a null key, a cross-table duplicate, or a hash collision.
    """
    id_map: dict[str, tuple[str, str]] = {}
    seen: set[str] = set()
    for spec in specs:
        table, key = spec["base_table"], spec["key"]
        for (uid,) in conn.execute(f'SELECT "{key}" FROM "{table}"'):
            if uid is None:
                raise ValueError(f"null {key} in {table}")
            if uid in seen:
                raise ValueError(f"duplicate unique_id across tables: {uid}")
            seen.add(uid)
            pid = part_id(uid)
            if pid in id_map:
                raise ValueError(f"hash collision for unique_id {uid}")
            id_map[pid] = (table, uid)
    return id_map
```

- [ ] **Step 4: Run to verify the tests pass**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: PASS (all tests in the file pass).

- [ ] **Step 5: Commit**

```bash
git add tools/terra_server.py tests/test_terra_server.py
git commit -m "add terra_server spec loader, id map, and uniqueness invariant"
```

---

### Task 6: Part serializer

**Files:**
- Modify: `tools/terra_server.py`
- Test: `tests/test_terra_server.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_terra_server.py`:

```python
from tools.terra_server import serialize_part, part_id, load_spec


def test_serialize_part_shape_and_footprint(fixture_db):
    _, dbl = fixture_db
    spec = load_spec(dbl)[0]
    row = {"unique_id": "OBS-XYZ/1", "mpn": "XYZ/1", "value": "NPN",
           "kicad_symbol": "Transistors:BJT", "kicad_footprint": "SOT:SOT-23", "tier": 3}
    pid = part_id("OBS-XYZ/1")
    out = serialize_part(row, spec, pid)

    assert out["id"] == pid
    assert out["name"] == f"XYZ_1_{pid}"                       # '/' sanitized
    assert out["symbolIdStr"] == "Transistors:BJT"
    # booleans are STRINGS
    for k in ("exclude_from_bom", "exclude_from_board", "exclude_from_sim"):
        assert out[k] == "false"
    # footprint is the canonical fields.footprint, not a top-level key
    assert out["fields"]["footprint"] == {"value": "SOT:SOT-23", "visible": "true"}
    # the kicad_symbol / kicad_footprint columns are NOT re-emitted as Symbol/Footprint
    assert "Symbol" not in out["fields"]
    assert "Footprint" not in out["fields"]
    # a normal field carries its visibility as a string
    assert out["fields"]["Value"] == {"value": "NPN", "visible": "true"}


def test_serialize_part_skips_null_fields(fixture_db):
    _, dbl = fixture_db
    spec = load_spec(dbl)[0]
    row = {"unique_id": "X", "mpn": None, "value": "", "kicad_symbol": "L:S",
           "kicad_footprint": None, "tier": 0}
    out = serialize_part(row, spec, part_id("X"))
    assert "Manufacturer PN" not in out["fields"]              # None skipped
    assert "Value" not in out["fields"]                        # "" skipped
    assert "footprint" not in out["fields"]                    # null footprint omitted
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: FAIL — `ImportError: cannot import name 'serialize_part'`.

- [ ] **Step 3: Implement the serializer**

Append to `tools/terra_server.py`:

```python
def serialize_part(row: Any, spec: dict, pid: str) -> dict:
    """Build the KiCad HTTP part object for one DB row."""
    sym, fp = spec["symbols"], spec["footprints"]
    name = build_name(display_value(row, spec), pid)

    fields: dict[str, dict] = {}
    fp_val = row[fp] if fp else None
    if fp_val:
        fields["footprint"] = {"value": str(fp_val), "visible": "true"}

    for field in spec["fields"]:
        col = field["column"]
        if col in (sym, fp):                 # skip Symbol/Footprint -> no clobber
            continue
        val = row[col]
        if val is None or val == "":
            continue
        fields[field["name"]] = {
            "value": str(val),
            "visible": "true" if field.get("visible_in_chooser") else "false",
        }

    return {
        "id": pid,
        "name": name,
        "symbolIdStr": str(row[sym] or ""),
        "exclude_from_bom": "false",
        "exclude_from_board": "false",
        "exclude_from_sim": "false",
        "fields": fields,
    }
```

> `row[col]` works for both `sqlite3.Row` and `dict`. For `dict` rows missing a column, the serializer is only called on full `SELECT *` rows, so every spec column is present.

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/terra_server.py tests/test_terra_server.py
git commit -m "add terra_server part serializer (string bools, canonical footprint)"
```

---

### Task 7: FastAPI app factory + the four endpoints

**Files:**
- Modify: `tools/terra_server.py`
- Test: `tests/test_terra_server.py`

- [ ] **Step 1: Write the failing endpoint tests**

Add to `tests/test_terra_server.py`:

```python
from fastapi.testclient import TestClient
from tools.terra_server import create_app, part_id


def _client(fixture_db, tier=2):
    db, dbl = fixture_db
    return TestClient(create_app(str(db), str(dbl), tier=tier))


def test_root_has_nonempty_categories_and_parts(fixture_db):
    r = _client(fixture_db).get("/v1/")
    assert r.status_code == 200
    body = r.json()
    assert body["categories"] and body["parts"]                # non-empty strings


def test_categories_listing(fixture_db):
    body = _client(fixture_db).get("/v1/categories.json").json()
    assert body == [{"id": "bjt", "name": "BJT Transistors", "description": ""}]


def test_category_parts_apply_tier_cutoff(fixture_db):
    # default tier<=2 excludes the tier-3 row 'OBS-XYZ/1'
    body = _client(fixture_db).get("/v1/parts/category/bjt.json").json()
    ids = {p["id"] for p in body}
    assert part_id("NXP-BC847") in ids and part_id("NXP-BC857") in ids
    assert part_id("OBS-XYZ/1") not in ids
    # --tier 3 includes it
    body3 = _client(fixture_db, tier=3).get("/v1/parts/category/bjt.json").json()
    assert part_id("OBS-XYZ/1") in {p["id"] for p in body3}


def test_category_part_name_matches_detail_name(fixture_db):
    c = _client(fixture_db)
    listed = {p["id"]: p["name"] for p in c.get("/v1/parts/category/bjt.json").json()}
    pid = part_id("NXP-BC847")
    detail = c.get(f"/v1/parts/{pid}.json").json()
    assert detail["name"] == listed[pid]                       # byte-match


def test_part_detail_resolves_hidden_tier3_directly(fixture_db):
    # parts/{id} is tier-agnostic even though the listing hid it
    pid = part_id("OBS-XYZ/1")
    detail = _client(fixture_db).get(f"/v1/parts/{pid}.json").json()
    assert detail["symbolIdStr"] == "Transistors:BJT"


def test_unknown_category_and_part_404(fixture_db):
    c = _client(fixture_db)
    assert c.get("/v1/parts/category/nope.json").status_code == 404
    assert c.get("/v1/parts/deadbeefdeadbeef.json").status_code == 404
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: FAIL — `ImportError: cannot import name 'create_app'`.

- [ ] **Step 3: Implement the app factory**

Append to `tools/terra_server.py`:

```python
def create_app(db_path: str, dbl_path: str, tier: int = 2):
    """Build the FastAPI app. Read-only DB connection; spec + id map built at startup."""
    from fastapi import FastAPI, HTTPException

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    specs = load_spec(dbl_path)
    specs_by_cat = {s["category_id"]: s for s in specs}
    id_map = build_id_map(conn, specs)

    app = FastAPI()

    @app.get("/v1/")
    def root():
        return {"categories": "v1/categories.json", "parts": "v1/parts"}

    @app.get("/v1/categories.json")
    def categories():
        return [{"id": s["category_id"], "name": s["name"], "description": ""} for s in specs]

    @app.get("/v1/parts/category/{category}.json")
    def parts_in_category(category: str):
        spec = specs_by_cat.get(category)
        if spec is None:
            raise HTTPException(status_code=404, detail="unknown category")
        rows = conn.execute(f'SELECT * FROM "{spec["base_table"]}" WHERE tier <= ?', (tier,))
        out = []
        for row in rows:
            pid = part_id(row[spec["key"]])
            out.append({"id": pid, "name": build_name(display_value(row, spec), pid)})
        return out

    @app.get("/v1/parts/{pid}.json")
    def part(pid: str):
        loc = id_map.get(pid)
        if loc is None:
            raise HTTPException(status_code=404, detail="unknown part")
        table, uid = loc
        spec = specs_by_cat[table]
        row = conn.execute(
            f'SELECT * FROM "{table}" WHERE "{spec["key"]}" = ?', (uid,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="unknown part")
        return serialize_part(row, spec, pid)

    return app
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_terra_server.py -q`
Expected: PASS (all helper + endpoint tests green).

- [ ] **Step 5: Commit**

```bash
git add tools/terra_server.py tests/test_terra_server.py
git commit -m "add terra_server FastAPI app with four v1 endpoints and tier cutoff"
```

---

### Task 8: CLI entry point + `make serve`

**Files:**
- Modify: `tools/terra_server.py`, `Makefile`

- [ ] **Step 1: Add the CLI `main()`**

Append to `tools/terra_server.py`:

```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Terra KiCad HTTP Library server")
    parser.add_argument("--db", default="db/terra.db")
    parser.add_argument("--dbl", default="terra.kicad_dbl")
    parser.add_argument("--tier", type=int, default=2)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8361)
    args = parser.parse_args()

    import uvicorn
    app = create_app(args.db, args.dbl, tier=args.tier)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Add the `serve` target to the Makefile**

Add near the other `.PHONY` targets:

```make
.PHONY: serve
serve: db/terra.db terra.kicad_dbl
	$(PYTHON) tools/terra_server.py --db db/terra.db --dbl terra.kicad_dbl --tier 2
```

- [ ] **Step 3: Smoke-test the server end to end**

```bash
make serve &
SERVER_PID=$!
sleep 3
curl -s http://127.0.0.1:8361/v1/ ; echo
curl -s http://127.0.0.1:8361/v1/categories.json | head -c 200 ; echo
# pick the first CERN category and fetch one part
CAT=$(curl -s http://127.0.0.1:8361/v1/categories.json | uv run python -c "import sys,json;print(json.load(sys.stdin)[0]['id'])")
PID=$(curl -s "http://127.0.0.1:8361/v1/parts/category/$CAT.json" | uv run python -c "import sys,json;print(json.load(sys.stdin)[0]['id'])")
curl -s "http://127.0.0.1:8361/v1/parts/$PID.json"; echo
kill $SERVER_PID
```
Expected: root returns `{"categories":...,"parts":...}`; categories is a non-empty JSON array; the part object has `id`, `name`, `symbolIdStr`, string `exclude_*`, and a `fields` object.

- [ ] **Step 4: Commit**

```bash
git add tools/terra_server.py Makefile
git commit -m "add terra_server CLI main and make serve target"
```

---

### Task 9: Generate `terra.kicad_httplib`

**Files:**
- Create: `tools/generate_kicad_httplib.py`
- Modify: `Makefile`
- Test: `tests/test_generate_httplib.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_generate_httplib.py
from tools.generate_kicad_httplib import build_httplib


def test_httplib_config_shape():
    cfg = build_httplib()
    src = cfg["source"]
    assert src["type"] == "REST_API"
    assert src["api_version"] == "v1"
    assert src["root_url"].startswith("http://127.0.0.1:8361")
    assert src["token"] == ""
    # timeout keys must be the part/categories pair, NOT timeout_seconds
    assert "timeout_parts_seconds" in src and "timeout_categories_seconds" in src
    assert "timeout_seconds" not in src
```

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest tests/test_generate_httplib.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.generate_kicad_httplib'`.

- [ ] **Step 3: Implement the generator**

```python
# tools/generate_kicad_httplib.py
#!/usr/bin/env python3
"""Write the terra.kicad_httplib connection file (KiCad HTTP Library v1)."""
import json
import sys
from pathlib import Path


def build_httplib(root_url: str = "http://127.0.0.1:8361/") -> dict:
    return {
        "meta": {"version": 1.0},
        "name": "Terra EDA Library",
        "source": {
            "type": "REST_API",
            "api_version": "v1",
            "root_url": root_url,
            "token": "",
            "timeout_parts_seconds": 3600,
            "timeout_categories_seconds": 86400,
        },
    }


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("terra.kicad_httplib")
    out.write_text(json.dumps(build_httplib(), indent=2) + "\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify it passes**

Run: `uv run pytest tests/test_generate_httplib.py -q`
Expected: PASS.

- [ ] **Step 5: Add a Makefile target and generate the file**

Add to the Makefile:

```make
.PHONY: httplib
httplib terra.kicad_httplib:
	$(PYTHON) tools/generate_kicad_httplib.py terra.kicad_httplib
```

Run: `make httplib && uv run python -c "import json;print(json.load(open('terra.kicad_httplib'))['source']['api_version'])"`
Expected: prints `v1`.

- [ ] **Step 6: Commit**

```bash
git add tools/generate_kicad_httplib.py tests/test_generate_httplib.py Makefile terra.kicad_httplib
git commit -m "generate terra.kicad_httplib connection file"
```

---

### Task 10: Real-KiCad validation (manual)

No automated test can cover KiCad's own behavior; do this by hand and record results in the commit message.

**Files:** none (manual checklist)

- [ ] **Step 1: Register the HTTP library in KiCad**

Ensure `sym-lib-table` / `fp-lib-table` still resolve the underlying `.kicad_sym` / `.kicad_mod` libraries (unchanged from the dbl setup). Add `terra.kicad_httplib` as a library in KiCad's Symbol Library Table. Start the server: `make serve`.

- [ ] **Step 2: Verify browse + place**

Open the Symbol Chooser. Confirm: categories load; expanding a CERN category (now tier 0) lists parts; expanding `resistors_smt` lists ~4.8k (tier ≤ 2) and feels acceptable; place a part and confirm its symbol + footprint resolve.

- [ ] **Step 3: Verify Update-from-Library across a rebuild**

Place a part, then `rm -f db/terra.db && make db/terra.db && make serve`, restart KiCad's library cache, and run *Tools → Update Symbols from Library*. Confirm the placed part still re-resolves (its `name`/id is stable across the rebuild).

- [ ] **Step 4: Characterize the hidden-part case**

Place a `tier ≤ 2` part. Restart the server with `--tier 0` (so that part is now hidden from listings). Expire KiCad's cache / restart, and run *Update from Library*. Record whether KiCad orphans the part (expected per the spec's listing→name→id path) so the orphan-on-tighten rule is documented behavior.

- [ ] **Step 5: Benchmark the stress category**

Time expanding `resistors_smt` (~4.8k) in the Symbol Chooser. If it is unacceptably slow, that is the signal to build the subcategory splitter (out of scope here) — note the measurement in `fastload.org`.

- [ ] **Step 6: Record results**

```bash
git commit --allow-empty -m "validate terra HTTP library in KiCad

- browse/place/update-from-library across a rebuild: <result>
- hidden-part orphan behavior under --tier tightening: <result>
- resistors_smt (~4.8k) expand timing: <result>"
```

---

## Self-Review

**Spec coverage:** four endpoints (Task 7) ✓; root non-empty (Task 7 test) ✓; `hash(unique_id)` id + uniqueness invariant (Tasks 4–5) ✓; `name = sanitize+id`, normalization-safe, byte-match (Tasks 4, 6, 7) ✓; `fields.footprint` canonical + skip symbol/footprint columns (Task 6) ✓; string booleans (Task 6) ✓; tier ≤ 2 cutoff via `--tier`, listing-only, part-detail tier-agnostic (Task 7) ✓; **static→0 re-tier + build verification** (Tasks 2–3) ✓; packaging deps (Task 1) ✓; `.kicad_httplib` with correct timeout keys (Task 9) ✓; `make serve` (Task 8) ✓; real-KiCad update + hidden-part characterization (Task 10) ✓.

**Deviations flagged:** console-script entry omitted (see header) — `make serve` covers it.

**Open spec items deferred to execution judgment:** exact display/lead column per library (Task 5 picks first non-reserved field — adjust if a table's first field is poor); resolving the 5 cross-table dups (the Task 5 invariant *fails the build* until they're resolved — resolve them when Task 3's rebuild first trips the duplicate check). Note: Task 3 rebuild may surface the 5 duplicate `unique_id`s when `build_id_map` runs in Task 7's first real-DB serve; resolve by assigning each to one canonical category in the source `db/tables/.../*.sql`.

**Type consistency:** `part_id`, `sanitize`, `build_name`, `display_value`, `load_spec` (spec dict keys: `category_id/name/base_table/key/symbols/footprints/display_col/fields`), `build_id_map` (→ `{pid: (table, uid)}`), `serialize_part(row, spec, pid)`, `create_app(db, dbl, tier)` — names and signatures match across all tasks and tests.
