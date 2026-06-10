import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_sensors.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_sensors-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_247():
    # All 247 CERN Sensors rows import; every LibSymbol/LibFootprint exists
    # upstream (no missing-asset carve-outs) and no row is a doc/graphical
    # denylist hit.
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_sensors").fetchone()[0] == 247


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_sensors"
    ).fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_sensors "
                    "WHERE mpn='ACS712ELCTR-05B-T'").fetchone()
    assert r["manufacturer"] == "ALLEGRO MICROSYSTEM"
    assert r["unique_id"] == "ALLEGRO MICROSYSTEM-ACS712ELCTR-05B-T"
    assert r["package"] == "SOIC8"
    assert r["pin_count"] == "8"
    assert r["kicad_symbol"] == "cern-sensors:ACS712"
    assert (r["kicad_footprint"]
            == "cern-ics-and-semiconductors-smd:SOIC127P600X175-8N")
    assert r["tags"] == "sensor"
    assert r["source"] == "cern_import"


def test_mpn_collision_kept_as_variants():
    # YAGEO 32208706 appears 4x in CERN (horizontal/vertical x De Morgan [alt]
    # footprint/symbol variants under one MPN); none has Part Number Nocolon ==
    # MPN, so the first sorted row wins <mfr>-<mpn> and the rest fall back to
    # <mfr>-<Part Number Nocolon> instead of being silently dropped.
    con = _con()
    rows = con.execute(
        "SELECT unique_id FROM cern_sensors WHERE mpn='32208706' "
        "ORDER BY unique_id").fetchall()
    assert [r[0] for r in rows] == [
        "YAGEO-32208706",
        "YAGEO-YAGEO_32208706_H [alt]",
        "YAGEO-YAGEO_32208706_V",
        "YAGEO-YAGEO_32208706_V [alt]",
    ]


def test_lifecycle_mapping():
    # CERN Status: 231 blank (-> Active), 14 'Not Recommended' (-> NRND), 2
    # 'Obsolete' (-> Obsolete). No Discontinued/Sourcing Difficulty in this table.
    con = _con()
    rows = dict(con.execute(
        "SELECT lifecycle_status, COUNT(*) FROM cern_sensors GROUP BY 1"))
    assert rows == {"Active": 231, "NRND": 14, "Obsolete": 2}


def test_no_type_tail_columns():
    # Sensors is a grab-bag; schema carries no type-specific tail. Guard that the
    # table is exactly core + pin_count + component_height (no sensor_type etc.).
    con = _con()
    cols = {r[1] for r in con.execute("PRAGMA table_info(cern_sensors)")}
    assert "pin_count" in cols and "component_height" in cols
    # nothing sensor-parametric snuck in
    for forbidden in ("sensor_type", "sense_type", "sensor_kind",
                      "voltage_rating", "current_rating", "channels"):
        assert forbidden not in cols


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_sensors WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_sensors WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_sensors WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_sensors WHERE kicad_symbol LIKE '%:%'"):
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
