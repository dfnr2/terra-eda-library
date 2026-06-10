import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_thermistors_varistors.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_thermistors_varistors-build",
                    'EXCLUDE_TABLES=resistors_smt resistors_th', "DEFAULT_TIER=5"],
                   cwd=ROOT, check=True, capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_53():
    # All 53 CERN 'Thermistors And Varistors' rows import; every LibSymbol (5) and
    # LibFootprint (42) exists upstream (no missing-asset carve-outs) and no row is
    # a doc/graphical denylist hit.
    con = _con()
    assert con.execute(
        "SELECT COUNT(*) FROM cern_thermistors_varistors").fetchone()[0] == 53


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_thermistors_varistors"
    ).fetchone()
    assert n == d


def test_known_ntc_chip_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_thermistors_varistors "
                    "WHERE mpn='NTCS0603E3104FXT'").fetchone()
    assert r["manufacturer"] == "VISHAY"
    assert r["unique_id"] == "VISHAY-NTCS0603E3104FXT"
    assert r["device_type"] == "NTC"
    assert r["package"] == "0603"
    assert r["value"] == "100k"
    assert r["kicad_symbol"] == "cern-resistors:Thermistor NTC"
    assert r["kicad_footprint"] == "cern-thermistors-and-varistors:THERMC1608X95N"


def test_known_varistor_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_thermistors_varistors "
                    "WHERE mpn='820412711'").fetchone()
    assert r["manufacturer"] == "WURTH"
    assert r["device_type"] == "Varistor"
    assert r["voltage"] == "275VAC"
    assert r["kicad_symbol"] == "cern-resistors:Varistor"
    assert r["kicad_footprint"] == "cern-thermistors-and-varistors:VAR_WURTH_820412711"


def test_device_type_values():
    # device_type is derived from the CERN 'LibSymbol' name (deterministic, filled
    # 53/53): the table cleanly splits NTC / PTC / Varistor, plus one TCO.
    con = _con()
    rows = dict(con.execute(
        "SELECT device_type, COUNT(*) FROM cern_thermistors_varistors GROUP BY 1"))
    assert rows == {"NTC": 24, "PTC": 13, "Varistor": 15, "TCO": 1}
    assert con.execute(
        "SELECT COUNT(*) FROM cern_thermistors_varistors "
        "WHERE device_type=''").fetchone()[0] == 0


def test_voltage_fill_rate():
    # CERN 'Voltage' is mostly filled for varistors (clamp voltage), sparse for
    # thermistors. Copied verbatim; 37/53 filled.
    con = _con()
    n = con.execute("SELECT COUNT(*) FROM cern_thermistors_varistors "
                    "WHERE voltage != ''").fetchone()[0]
    assert n == 37


def test_lifecycle_mapping():
    con = _con()
    rows = dict(con.execute(
        "SELECT lifecycle_status, COUNT(*) FROM cern_thermistors_varistors GROUP BY 1"))
    assert rows == {"Active": 50, "Obsolete": 3}


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_thermistors_varistors "
            "WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_thermistors_varistors "
            "WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_thermistors_varistors "
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
            "SELECT DISTINCT kicad_symbol FROM cern_thermistors_varistors "
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
