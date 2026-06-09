import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_leds_displays.db"


def _con():
    # CERN.sqlite resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_leds_displays-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_514():
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_leds_displays").fetchone()[0] == 514


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_leds_displays").fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute(
        "SELECT * FROM cern_leds_displays WHERE mpn='597-3301-507F'").fetchone()
    assert r["manufacturer"] == "DIALIGHT"
    assert r["unique_id"] == "DIALIGHT-597-3301-507F"
    assert r["color"] == "Green"
    assert r["kicad_symbol"] == "cern-leds-displays:LED Green 1C 2A"
    assert r["kicad_footprint"] == "cern-ics-and-semiconductors-smd:LED_DIALIGHT_597-3301-507F"


def test_color_values_sane():
    """color is a colour word from the symbol (or blank); never a pinout token."""
    con = _con()
    assert con.execute(
        "SELECT COUNT(*) FROM cern_leds_displays WHERE color='Green'").fetchone()[0] > 0
    bad = con.execute(
        "SELECT COUNT(*) FROM cern_leds_displays WHERE color GLOB '*[0-9]*'").fetchone()[0]
    assert bad == 0


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_leds_displays WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_leds_displays WHERE kicad_symbol LIKE '%:%'"):
        nick, name = val.split(":", 1)
        f = ROOT / "kicad_symbols" / f"{nick}.kicad_sym"
        if nick not in cache:
            cache[nick] = f.read_text() if f.is_file() else ""
        if f'(symbol "{name}"' not in cache[nick]:
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved symbols, e.g. {missing[:5]}"


def test_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_leds_displays WHERE kicad_symbol != ''"):
        assert f'(name "{val.split(":", 1)[0]}")' in sym
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_leds_displays WHERE kicad_footprint LIKE '%:%'"):
        assert f'(name "{val.split(":", 1)[0]}")' in fp
