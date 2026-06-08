import os
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_op_amps.db"


def _con():
    env = {**os.environ, "CERN_SQLITE": "/users/dave/vsrc/cern-kicad-libs/CERN.sqlite"}
    subprocess.run(["make", "cern_op_amps-build"], cwd=ROOT, check=True,
                   capture_output=True, env=env)
    return sqlite3.connect(DB)


def test_row_count_is_1569():
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_op_amps").fetchone()[0] == 1569


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_op_amps").fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_op_amps WHERE mpn='LM358AD'").fetchone()
    assert r["manufacturer"] == "TEXAS INSTRUMENTS"
    assert r["unique_id"] == "TEXAS INSTRUMENTS-LM358AD"
    assert r["package"] == "SOIC8"
    assert r["amplifier_type"] == "Operational Amplifier"
    assert r["channels"] == "2"
    assert r["pin_count"] == "8"
    assert r["kicad_symbol"] == "cern-operational-amplifiers:Operational Amplifier x2 Type1"
    assert r["kicad_footprint"] == "cern-ics-and-semiconductors-smd:SOIC127P600X175-8N"


def test_amplifier_type_normalized():
    """amplifier_type is the base class (no Type/xN/[alt] suffix), blank for
    device-named symbols; every non-blank value contains 'Amplifier'."""
    con = _con()
    bad = con.execute(
        "SELECT COUNT(*) FROM cern_op_amps WHERE amplifier_type != '' "
        "AND amplifier_type NOT LIKE '%Amplifier%'").fetchone()[0]
    assert bad == 0
    assert con.execute(
        "SELECT COUNT(*) FROM cern_op_amps WHERE amplifier_type LIKE '%Type%' "
        "OR amplifier_type LIKE '%[[]alt]%'").fetchone()[0] == 0


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_op_amps WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_op_amps WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_op_amps WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_op_amps WHERE kicad_symbol LIKE '%:%'"):
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
