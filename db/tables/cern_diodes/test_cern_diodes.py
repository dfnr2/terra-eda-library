import os
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_diodes.db"


def _con():
    env = {**os.environ, "CERN_SQLITE": "/users/dave/vsrc/cern-kicad-libs/CERN.sqlite"}
    subprocess.run(["make", "cern_diodes-build"], cwd=ROOT, check=True,
                   capture_output=True, env=env)
    return sqlite3.connect(DB)


def test_row_count_is_962():
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_diodes").fetchone()[0] == 962


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_diodes").fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute(
        "SELECT * FROM cern_diodes WHERE mpn='0402ESDA-MLP'").fetchone()
    assert r["manufacturer"] == "EATON"
    assert r["unique_id"] == "EATON-0402ESDA-MLP"
    assert r["package"] == "0402"
    assert r["voltage_rating"] == "8kV"
    assert r["pin_count"] == "2"
    assert r["component_height"] == "0.44mm"
    assert r["lifecycle_status"] == "Active"
    assert r["diode_type"] == "TVS Bi-Directional"
    assert r["kicad_symbol"] == "cern-diodes:Diode TVS Bi-Directional"
    assert r["kicad_footprint"] == "cern-ics-and-semiconductors-smd:EATON_0402ESDA-MLP"


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_diodes WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_diodes WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    """Every kicad_footprint must point at an actual .kicad_mod in kicad_footprints/.
    The nickname equals the copied lib's filename stem (<nick>.pretty)."""
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_diodes WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    """Every kicad_symbol must name an item that exists in kicad_symbols/<nick>.kicad_sym."""
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_diodes WHERE kicad_symbol LIKE '%:%'"):
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
