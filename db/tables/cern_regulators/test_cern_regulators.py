import os
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_regulators.db"


def _con():
    env = {**os.environ, "CERN_SQLITE": "/users/dave/vsrc/cern-kicad-libs/CERN.sqlite"}
    subprocess.run(["make", "cern_regulators-build"], cwd=ROOT, check=True,
                   capture_output=True, env=env)
    return sqlite3.connect(DB)


def test_row_count_is_1056():
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_regulators").fetchone()[0] == 1056


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_regulators").fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute(
        "SELECT * FROM cern_regulators WHERE mpn='LM1117IMPX-ADJ'").fetchone()
    assert r["manufacturer"] == "TEXAS INSTRUMENTS"
    assert r["unique_id"] == "TEXAS INSTRUMENTS-LM1117IMPX-ADJ"
    assert r["package"] == "SOT223"
    assert r["regulator_type"] == "Regulator"
    assert r["pin_count"] == "4"
    assert r["kicad_symbol"] == "cern-regulators:REG3+1 1ADJ-2OUT-3IN+4OUT"
    assert r["kicad_footprint"] == "cern-ics-and-semiconductors-smd:SOT230P700X180-4N"


def test_regulator_type_values():
    """regulator_type is a coarse deterministic class from the symbol prefix:
    only '', 'Regulator', or 'Voltage Reference'."""
    con = _con()
    vals = {v for (v,) in con.execute(
        "SELECT DISTINCT regulator_type FROM cern_regulators")}
    assert vals <= {"", "Regulator", "Voltage Reference"}
    assert con.execute(
        "SELECT COUNT(*) FROM cern_regulators WHERE regulator_type='Regulator'"
    ).fetchone()[0] > 0


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_regulators WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_regulators WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_regulators WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_regulators WHERE kicad_symbol LIKE '%:%'"):
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
