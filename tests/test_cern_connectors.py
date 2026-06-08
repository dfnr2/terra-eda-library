"""Parameterized checks for the CERN connector vendor tables.

Connector vendors are uniform (shared "Connectors" symbol lib, per-vendor
footprint libs, no type tail), so one parameterized module covers them all
instead of a near-duplicate test file per vendor. cern_molex keeps its own
known-part test.
"""
import sqlite3
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# table -> expected row count
TABLES = {
    "cern_samtec": 1363,
    "cern_tyco": 467,
    "cern_3m": 359,
    "cern_phoenix": 347,
    "cern_harting": 323,
    "cern_amphenol": 194,
    "cern_harwin": 145,
    "cern_souriau": 97,
    "cern_lemo": 90,
    "cern_fci": 83,
    "cern_erni": 78,
    "cern_weidmuller": 62,
    "cern_stelvio_kontek_comatel": 106,
    "cern_mentor": 10,
}

_sym_cache = {}


def _con(table):
    # CERN.sqlite resolved by tools.cern_source (vendored clone or $CERN_SQLITE).
    subprocess.run(["make", f"{table}-build"], cwd=ROOT, check=True, capture_output=True)
    return sqlite3.connect(ROOT / f"db/{table}.db")


@pytest.mark.parametrize("table,expected", TABLES.items())
def test_row_count(table, expected):
    assert _con(table).execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == expected


@pytest.mark.parametrize("table", TABLES)
def test_no_duplicate_unique_ids(table):
    n, d = _con(table).execute(
        f"SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM {table}").fetchone()
    assert n == d


@pytest.mark.parametrize("table", TABLES)
def test_symbols_are_shared_connectors_lib(table):
    con = _con(table)
    for (val,) in con.execute(
            f"SELECT DISTINCT kicad_symbol FROM {table} WHERE kicad_symbol LIKE '%:%'"):
        assert val.startswith("cern-connectors:"), f"{table}: unexpected symbol lib {val}"


@pytest.mark.parametrize("table", TABLES)
def test_nicks_registered(table):
    con = _con(table)
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for (val,) in con.execute(
            f"SELECT DISTINCT kicad_symbol FROM {table} WHERE kicad_symbol != ''"):
        assert f'(name "{val.split(":", 1)[0]}")' in sym
    for (val,) in con.execute(
            f"SELECT DISTINCT kicad_footprint FROM {table} WHERE kicad_footprint LIKE '%:%'"):
        assert f'(name "{val.split(":", 1)[0]}")' in fp


@pytest.mark.parametrize("table", TABLES)
def test_footprints_resolve(table):
    con = _con(table)
    missing = []
    for (val,) in con.execute(
            f"SELECT DISTINCT kicad_footprint FROM {table} WHERE kicad_footprint LIKE '%:%'"):
        nick, name = val.split(":", 1)
        if not (ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod").is_file():
            missing.append(val)
    assert not missing, f"{table}: {len(missing)} unresolved footprints, e.g. {missing[:5]}"


@pytest.mark.parametrize("table", TABLES)
def test_symbols_resolve(table):
    con = _con(table)
    missing = []
    for (val,) in con.execute(
            f"SELECT DISTINCT kicad_symbol FROM {table} WHERE kicad_symbol LIKE '%:%'"):
        nick, name = val.split(":", 1)
        f = ROOT / "kicad_symbols" / f"{nick}.kicad_sym"
        if nick not in _sym_cache:
            _sym_cache[nick] = f.read_text() if f.is_file() else ""
        if f'(symbol "{name}"' not in _sym_cache[nick]:
            missing.append(val)
    assert not missing, f"{table}: {len(missing)} unresolved symbols, e.g. {missing[:5]}"
