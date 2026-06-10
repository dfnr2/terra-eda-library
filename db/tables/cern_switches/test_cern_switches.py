import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_switches.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_switches-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_226():
    # All 226 CERN Switches rows import; nothing is excluded (no denylist hits,
    # no GENERIC/Undefined manufacturers, solder jumpers kept as real parts).
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_switches").fetchone()[0] == 226


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_switches"
    ).fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_switches "
                    "WHERE mpn='B3F-1000'").fetchone()
    assert r["manufacturer"] == "OMRON"
    assert r["unique_id"] == "OMRON-B3F-1000"
    assert r["part_locator"] == "PB_OMRON_B3F-1000"
    assert r["switch_type"] == "push-button"
    assert r["pin_count"] == "4"
    assert r["kicad_symbol"] == "cern-switches:PB SPST 12NO-34NO"
    assert r["kicad_footprint"] == "cern-switches:PB_OMRON_B3F-1000"


def test_switch_type_from_symbol_prefix():
    # Every row classifies from the CERN symbol-name prefix; the set is fixed and
    # no row is left blank (the Family column is a grab-bag, so the symbol prefix
    # is the type dimension).
    con = _con()
    rows = dict(con.execute(
        "SELECT switch_type, COUNT(*) FROM cern_switches GROUP BY 1"))
    assert rows == {
        "switch": 84, "push-button": 67, "dip": 41,
        "rotary": 24, "knob": 6, "tilt": 2, "jumper": 2}
    assert con.execute(
        "SELECT COUNT(*) FROM cern_switches WHERE switch_type=''").fetchone()[0] == 0


def test_mpn_collision_kept_as_variants():
    # CTS 204-124ST appears twice in CERN (base + _a symbol variant sharing one
    # footprint). Both must survive: the PNN==MPN row keeps <mfr>-<mpn>, the
    # variant falls back to <mfr>-<Part Number Nocolon> rather than being dropped.
    con = _con()
    rows = con.execute(
        "SELECT unique_id FROM cern_switches WHERE mpn='204-124ST' "
        "ORDER BY unique_id").fetchall()
    assert [r[0] for r in rows] == ["CTS-204-124ST", "CTS-SW_CTS_204-124ST_a"]
    # The two solder jumpers share manufacturer/MPN 'None'; both kept distinct.
    jumpers = con.execute(
        "SELECT unique_id FROM cern_switches WHERE manufacturer='None' "
        "ORDER BY unique_id").fetchall()
    assert [r[0] for r in jumpers] == ["None-JUMPSMD0805_G50", "None-None"]


def test_lifecycle_mapping():
    # CERN Switches Status: None (->Active), Obsolete (->Obsolete), Not
    # Recommended (->NRND).
    con = _con()
    rows = dict(con.execute(
        "SELECT lifecycle_status, COUNT(*) FROM cern_switches GROUP BY 1"))
    assert rows == {"Active": 219, "NRND": 1, "Obsolete": 6}


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_switches WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_switches WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_switches WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_switches WHERE kicad_symbol LIKE '%:%'"):
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
