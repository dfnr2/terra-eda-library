import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_relays.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_relays-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_300():
    # 302 CERN rows minus the 2 whose symbol+footprint were never created
    # upstream (REL_FINDER_56.32.9.012.0040, RELS_FINDER_96.12).
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_relays").fetchone()[0] == 300


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_relays"
    ).fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_relays "
                    "WHERE mpn='G6K-2F-Y-DC5'").fetchone()
    assert r["manufacturer"] == "OMRON ELECTRONIC"
    assert r["unique_id"] == "OMRON ELECTRONIC-G6K-2F-Y-DC5"
    assert r["part_locator"] == "REL_OMRON_G6K-2F-Y-5VDC"
    assert r["relay_kind"] == "Relay"
    assert r["coil_voltage"] == "5VDC"
    assert r["value"] == "5VDC"
    assert r["pin_count"] == "8"
    assert r["kicad_symbol"] == "cern-relays:REL_OMRON_G6K-2"
    assert r["kicad_footprint"] == "cern-relays:REL_OMRON_G6K-2F-Y"


def test_mpn_collision_kept_as_variants():
    # PANASONIC SFS3-DC24V appears three times in CERN (base + _a + _a [alt]
    # symbol variants); the variant rows must keep their Part Number
    # Nocolon-based unique_ids instead of being silently dropped.
    con = _con()
    rows = con.execute(
        "SELECT unique_id FROM cern_relays WHERE mpn='SFS3-DC24V' "
        "ORDER BY unique_id").fetchall()
    assert [r[0] for r in rows] == [
        "PANASONIC-REL_PANASONIC_SFS3-DC24V_a",
        "PANASONIC-REL_PANASONIC_SFS3-DC24V_a [alt]",
        "PANASONIC-SFS3-DC24V"]


def test_relay_kind_values():
    con = _con()
    rows = dict(con.execute(
        "SELECT relay_kind, COUNT(*) FROM cern_relays GROUP BY 1"))
    # Every row classifies: REL_* symbols -> Relay, RELS_*/SOCKET* -> Socket.
    assert set(rows) == {"Relay", "Socket"}
    assert rows["Relay"] == 277
    assert rows["Socket"] == 23


def test_coil_voltage_fill_rate():
    con = _con()
    n = con.execute("SELECT COUNT(*) FROM cern_relays "
                    "WHERE coil_voltage != ''").fetchone()[0]
    assert n == 274  # all relays except sockets/accessories carry a CERN Value
    blank_kinds = {k for (k,) in con.execute(
        "SELECT DISTINCT relay_kind FROM cern_relays WHERE coil_voltage = ''")}
    assert "Socket" in blank_kinds


def test_lifecycle_mapping():
    # Relays adds CERN statuses Discontinued (->Obsolete), Recommended and
    # None (->Active) on top of the usual map.
    con = _con()
    rows = dict(con.execute(
        "SELECT lifecycle_status, COUNT(*) FROM cern_relays GROUP BY 1"))
    assert rows == {"Active": 177, "NRND": 115, "Obsolete": 8}


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_relays WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_relays WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_relays WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_relays WHERE kicad_symbol LIKE '%:%'"):
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
