import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_fuses.db"


def _con():
    # CERN.sqlite is resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", "cern_fuses-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_315():
    # All 315 CERN Fuses rows import; every LibSymbol/LibFootprint exists upstream
    # (no missing-asset carve-outs) and no row is a doc/graphical denylist hit.
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_fuses").fetchone()[0] == 315


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_fuses"
    ).fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute("SELECT * FROM cern_fuses "
                    "WHERE mpn='SF-0603F050-2'").fetchone()
    assert r["manufacturer"] == "BOURNS"
    assert r["unique_id"] == "BOURNS-SF-0603F050-2"
    assert r["fuse_kind"] == "Fuse"
    assert r["current_rating"] == "500mA-50V"
    assert r["value"] == "500mA-50V"
    assert r["kicad_symbol"] == "cern-fuses:Fuse"
    assert r["kicad_footprint"] == "cern-fuses:FUSC_BOURNS_SF-0603F"


def test_mpn_collision_kept_as_variants():
    # BOURNS MF-R050 appears twice in CERN (vertical + _h horizontal footprint
    # variants under one MPN); the variant row must keep its Part Number
    # Nocolon-based unique_id instead of being silently dropped.
    con = _con()
    rows = con.execute(
        "SELECT unique_id FROM cern_fuses WHERE mpn='MF-R050' "
        "ORDER BY unique_id").fetchall()
    assert [r[0] for r in rows] == [
        "BOURNS-FUSR_BOURNS_MF-R050_h",
        "BOURNS-MF-R050"]


def test_fuse_kind_values():
    # fuse_kind is the CERN 'Family' column (deterministic, filled 315/315), with
    # the one plural normalized: 'Fuses Resettable' -> 'Fuse Resettable'.
    con = _con()
    rows = dict(con.execute(
        "SELECT fuse_kind, COUNT(*) FROM cern_fuses GROUP BY 1"))
    assert rows == {
        "Fuse": 169,
        "Fuse Resettable": 87,
        "Fuse Holder": 22,
        "Fuse & Holder": 16,
        "Surge Arrester": 14,
        "Fuse Holder Cover": 3,
        "Fuse Clip": 3,
        "Fuse SCP": 1,
    }
    assert con.execute(
        "SELECT COUNT(*) FROM cern_fuses WHERE fuse_kind=''").fetchone()[0] == 0


def test_current_rating_fill_rate():
    con = _con()
    n = con.execute("SELECT COUNT(*) FROM cern_fuses "
                    "WHERE current_rating != ''").fetchone()[0]
    assert n == 287  # blanks are the 28 holders/clips/covers (no rating)
    blank_kinds = {k for (k,) in con.execute(
        "SELECT DISTINCT fuse_kind FROM cern_fuses WHERE current_rating = ''")}
    assert {"Fuse Holder", "Fuse Clip", "Fuse Holder Cover"} <= blank_kinds


def test_lifecycle_mapping():
    con = _con()
    rows = dict(con.execute(
        "SELECT lifecycle_status, COUNT(*) FROM cern_fuses GROUP BY 1"))
    assert rows == {"Active": 303, "Obsolete": 12}


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_fuses WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_fuses WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"


def test_all_footprint_files_resolve():
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_fuses WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{len(missing)} unresolved footprints, e.g. {missing[:5]}"


def test_all_symbol_items_resolve():
    cache = {}
    con = _con()
    missing = []
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_fuses WHERE kicad_symbol LIKE '%:%'"):
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
