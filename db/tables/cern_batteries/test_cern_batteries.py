import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_batteries.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_batteries-build",
                    'EXCLUDE_TABLES=resistors_smt resistors_th', "DEFAULT_TIER=5"],
                   cwd=ROOT, check=True, capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_29():
    # All 29 CERN 'Batteries' rows import; every LibSymbol (8) and LibFootprint
    # (26) exists upstream (no missing-asset carve-outs) and no row is a
    # doc/graphical denylist hit.
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_batteries").fetchone()[0] == 29


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_batteries"
    ).fetchone()
    assert n == d


def test_known_coin_cell_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_batteries "
                    "WHERE part_locator='BAT_VARTA_CR2032'").fetchone()
    assert r["manufacturer"] == "VARTA"
    assert r["mpn"] == "6032101501"
    assert r["unique_id"] == "VARTA-6032101501"
    assert r["battery_kind"] == "cell"
    assert r["voltage"] == "3V"
    assert r["kicad_symbol"] == "cern-batteries:Battery No Pin"
    assert r["kicad_footprint"] == "cern-batteries:BAT_VARTA_CR2032"


def test_known_holder_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_batteries "
                    "WHERE part_locator='BATH_KEYSTONE_103'").fetchone()
    assert r["manufacturer"] == "KEYSTONE"
    assert r["mpn"] == "103"
    assert r["battery_kind"] == "holder"
    assert r["voltage"] == ""   # holders carry no cell voltage
    assert r["kicad_symbol"] == "cern-batteries:Battery Holder 2 Pin"
    assert r["kicad_footprint"] == "cern-batteries:BATH_KEYSTONE_103"


def test_mpn_collision_falls_back_to_nocolon():
    # MPN '54' and '1048P'/'1049'/'BK-18650-PC8' are shared by a base + [alt]/
    # variant footprint. The base (PNN == MPN-ish) keeps the bare mfr-mpn
    # unique_id; the variant falls back to mfr-<Part Number Nocolon>.
    con = _con()
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT part_locator, unique_id FROM cern_batteries "
        "WHERE mpn='54' ORDER BY part_locator").fetchall()
    uids = {r["part_locator"]: r["unique_id"] for r in rows}
    assert uids["BATH_KEYSTONE_54"] == "KEYSTONE-54"
    assert uids["BATH_KEYSTONE_54_a"] == "KEYSTONE-BATH_KEYSTONE_54_a"


def test_battery_kind_values():
    # battery_kind is derived from the CERN 'LibSymbol' name (deterministic,
    # filled 29/29): cell (the actual battery) vs holder (holder/clip).
    con = _con()
    rows = dict(con.execute(
        "SELECT battery_kind, COUNT(*) FROM cern_batteries GROUP BY 1"))
    assert rows == {"cell": 7, "holder": 22}
    assert con.execute(
        "SELECT COUNT(*) FROM cern_batteries WHERE battery_kind=''").fetchone()[0] == 0


def test_voltage_fill_rate():
    # CERN 'Value' carries the cell nominal voltage for the 7 bare cells; blank
    # for the holders. Copied verbatim; 7/29 filled.
    con = _con()
    n = con.execute("SELECT COUNT(*) FROM cern_batteries "
                    "WHERE voltage != ''").fetchone()[0]
    assert n == 7


def test_lifecycle_all_active():
    # CERN 'Status' is blank for all 29 rows -> Active.
    con = _con()
    rows = dict(con.execute(
        "SELECT lifecycle_status, COUNT(*) FROM cern_batteries GROUP BY 1"))
    assert rows == {"Active": 29}


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_batteries "
            "WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_batteries "
            "WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_batteries "
            "WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_batteries "
            "WHERE kicad_symbol LIKE '%:%'"):
        nick, name = val.split(":", 1)
        f = ROOT / "kicad_symbols" / f"{nick}.kicad_sym"
        if not f.is_file():
            missing.append(f"{val} (no lib {nick}.kicad_sym)")
            continue
        if nick not in cache:
            cache[nick] = f.read_text()
        if f'(symbol "{name}"' not in cache[nick]:
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved symbols, e.g. {missing[:5]}"
