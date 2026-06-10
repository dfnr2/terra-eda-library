import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_crystals_oscillators.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_crystals_oscillators-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_332():
    con = _con()
    assert con.execute(
        "SELECT COUNT(*) FROM cern_crystals_oscillators").fetchone()[0] == 332


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_crystals_oscillators"
    ).fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_crystals_oscillators "
                    "WHERE mpn='ABM3B-12.000MHZ-B2-T'").fetchone()
    assert r["manufacturer"] == "ABRACON"
    assert r["unique_id"] == "ABRACON-ABM3B-12.000MHZ-B2-T"
    assert r["xtal_type"] == "Quartz Crystal"
    assert r["frequency"] == "12MHZ"
    assert r["value"] == "12MHZ"
    assert r["pin_count"] == "2"
    assert r["kicad_footprint"] == "cern-ics-and-semiconductors-smd:XTAL_ABRACON_ABM3B"
    assert r["kicad_symbol"] == ("cern-crystals-oscillators:"
                                 "Quartz Crystal 1X 2GND 3X 4GND")


def test_mpn_collision_kept_as_variants():
    # FOX FXO-HC735R-125 appears twice in CERN; the variant row must keep its
    # Part Number Nocolon-based unique_id instead of being silently dropped.
    con = _con()
    rows = con.execute(
        "SELECT unique_id FROM cern_crystals_oscillators WHERE mpn='FXO-HC735R-125' "
        "ORDER BY unique_id").fetchall()
    assert [r[0] for r in rows] == [
        "FOX-FXO-HC735R-125", "FOX-OSC_125MHZ_VECTRON_VX-501-0253"]


def test_xtal_type_values():
    con = _con()
    rows = dict(con.execute(
        "SELECT xtal_type, COUNT(*) FROM cern_crystals_oscillators GROUP BY 1"))
    assert set(rows) == {"", "Quartz Crystal", "Oscillator"}
    assert rows["Quartz Crystal"] > 50
    assert rows["Oscillator"] > 200
    # blanks are only the device-named silicon oscillator symbols (LTC/MC/AD/ROS)
    assert rows[""] < 15


def test_frequency_fill_rate():
    con = _con()
    n = con.execute("SELECT COUNT(*) FROM cern_crystals_oscillators "
                    "WHERE frequency != ''").fetchone()[0]
    assert n >= 320  # 321/332 rows carry a CERN Value frequency


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_crystals_oscillators WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_crystals_oscillators WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_crystals_oscillators WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_crystals_oscillators WHERE kicad_symbol LIKE '%:%'"):
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
