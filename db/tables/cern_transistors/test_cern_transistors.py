import os
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_transistors.db"


def _con():
    env = {**os.environ, "CERN_SQLITE": "/users/dave/vsrc/cern-kicad-libs/CERN.sqlite"}
    subprocess.run(["make", "cern_transistors-build"], cwd=ROOT, check=True,
                   capture_output=True, env=env)
    return sqlite3.connect(DB)


def test_row_count_is_685():
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_transistors").fetchone()[0] == 685


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_transistors").fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute(
        "SELECT * FROM cern_transistors WHERE mpn='TIP41C'").fetchone()
    assert r["manufacturer"] == "ST MICROELECTRONICS"
    assert r["unique_id"] == "ST MICROELECTRONICS-TIP41C"
    assert r["package"] == "TO-220"
    assert r["transistor_type"] == "NPN"
    assert r["pin_count"] == "3"
    assert r["lifecycle_status"] == "Active"
    assert r["kicad_symbol"] == "cern-transistors:NPN B1 C2 E3"
    assert r["kicad_footprint"] == "cern-ics-and-semiconductors-thd:TO-220-H"


def test_transistor_type_blank_for_device_named_symbols():
    """transistor_type is set only when the symbol names a type; device-named
    symbols (a bare MPN) leave it blank rather than echoing the part number."""
    con = _con()
    typed, blank = con.execute(
        "SELECT SUM(transistor_type != ''), SUM(transistor_type = '') "
        "FROM cern_transistors").fetchone()
    assert typed > 400 and blank > 0
    # No transistor_type should look like a bare MPN (no type keyword).
    bad = con.execute(
        "SELECT COUNT(*) FROM cern_transistors WHERE transistor_type != '' AND "
        "transistor_type NOT GLOB '*[A-Z]*' ").fetchone()[0]
    assert bad == 0


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_transistors WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_transistors WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_transistors WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_transistors WHERE kicad_symbol LIKE '%:%'"):
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
