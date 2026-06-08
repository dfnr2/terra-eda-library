import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_dc_dc_converters.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_dc_dc_converters-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_444():
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_dc_dc_converters").fetchone()[0] == 444


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_dc_dc_converters").fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_dc_dc_converters WHERE mpn='TEN 15-2411'").fetchone()
    assert r["manufacturer"] == "TRACO POWER"
    assert r["unique_id"] == "TRACO POWER-TEN 15-2411"
    assert r["pin_count"] == "5"
    assert r["kicad_symbol"] == "cern-dc-dc-converters:DCDC_TRACO_TEN15_Single Output"
    assert r["kicad_footprint"] == "cern-ics-and-semiconductors-thd:DCDC_TRACO_TEN15"


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_dc_dc_converters WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_dc_dc_converters WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_dc_dc_converters WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_dc_dc_converters WHERE kicad_symbol LIKE '%:%'"):
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
