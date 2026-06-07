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
    assert r["kicad_symbol"] == "cern_Diodes:Diode TVS Bi-Directional"
    assert r["kicad_footprint"] == "cern_ICs_SMD:EATON_0402ESDA-MLP"


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_config_templates/sym-lib-table").read_text()
    fp = (ROOT / "kicad_config_templates/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_diodes WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_diodes WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    """Every kicad_footprint must point at an actual .kicad_mod in the copied libs."""
    import sys
    sys.path.insert(0, str(ROOT))
    from tools import cern_libmap as lm
    nick_to_dir = {v: f"{k}.pretty" for k, v in lm.FOOTPRINT_LIB_NICK.items()}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_diodes WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        d = nick_to_dir.get(nick)
        if d is None:
            missing.append(f"{val} (unknown nick)")
            continue
        if not (ROOT / "assets/footprints/cern" / d / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    """Every kicad_symbol must name an item that exists in the copied symbol lib."""
    import sys
    sys.path.insert(0, str(ROOT))
    from tools import cern_libmap as lm
    nick_to_file = {v: f"{k}.kicad_sym" for k, v in lm.SYMBOL_LIB_NICK.items()}
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_diodes WHERE kicad_symbol LIKE '%:%'"):
        nick, name = val.split(":", 1)
        fn = nick_to_file.get(nick)
        if fn is None:
            missing.append(f"{val} (unknown nick)")
            continue
        if fn not in cache:
            cache[fn] = (ROOT / "assets/symbols/cern" / fn).read_text()
        if f'(symbol "{name}"' not in cache[fn]:
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved symbols, e.g. {missing[:5]}"
