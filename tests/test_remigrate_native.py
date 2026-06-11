# tests/test_remigrate_native.py
"""Tests for tools/remigrate_native.py — re-migration of legacy terra-native INSERT rows
onto the canonical Phase-0 schema columns."""

import sqlite3
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "remigrate_native.py"
DIODES_SCHEMA = ROOT / "db" / "tables" / "diodes" / "diodes_0_schema.sql"
DIODES_MIGRATED = ROOT / "db" / "tables" / "diodes" / "diodes_1_migrated.sql"

# ---------------------------------------------------------------------------
# Import parse_temp_range for unit testing
# ---------------------------------------------------------------------------

def _import_parse_temp_range():
    import importlib.util
    spec = importlib.util.spec_from_file_location("remigrate_native", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.parse_temp_range


# ---------------------------------------------------------------------------
# parse_temp_range unit tests
# ---------------------------------------------------------------------------

def test_parse_temp_range_slash_C():
    ptr = _import_parse_temp_range()
    assert ptr("-65C/150C") == (-65.0, 150.0)

def test_parse_temp_range_plus_sign():
    ptr = _import_parse_temp_range()
    assert ptr("-40C/+85C") == (-40.0, 85.0)

def test_parse_temp_range_to_keyword():
    ptr = _import_parse_temp_range()
    assert ptr("-55 to 125") == (-55.0, 125.0)

def test_parse_temp_range_tilde_degrees():
    ptr = _import_parse_temp_range()
    assert ptr("-55°C ~ 125°C") == (-55.0, 125.0)

def test_parse_temp_range_junk():
    ptr = _import_parse_temp_range()
    assert ptr("If applicable") == (None, None)

def test_parse_temp_range_single_number():
    """A single number like '150C' can't produce min/max — expect (None, None)."""
    ptr = _import_parse_temp_range()
    assert ptr("150C") == (None, None)

def test_parse_temp_range_empty():
    ptr = _import_parse_temp_range()
    assert ptr("") == (None, None)


# ---------------------------------------------------------------------------
# Integration test: run rewriter on real diodes file, check output
# ---------------------------------------------------------------------------

DROPPED_COLS = {
    "class", "component_type", "component_value", "composition",
    "number_of_pins", "reference", "sim_library", "sim_type",
    "temp_coeff", "tolerance",
}

# bare temp_operating/temp_storage column names should not appear in INSERT column lists
BARE_LEGACY_TEMP = {"temp_operating", "temp_storage"}

PLACEHOLDER_VALUES = {"if applicable", "na", "n/a", "tbd", "none"}


def _rewritten_sql():
    """Return the current contents of diodes_1_migrated.sql — the rewriter
    must have already been applied before this test module is imported at
    test time, OR we call the rewriter inline here.  We call it inline so
    the test is self-contained."""
    result = subprocess.run(
        [sys.executable, str(TOOL), "diodes"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, f"remigrate_native failed:\n{result.stderr}"
    return DIODES_MIGRATED.read_text()


def test_no_dropped_columns_in_rewritten_file():
    sql = _rewritten_sql()
    for col in DROPPED_COLS:
        # Look for the column name in INSERT column lists (surrounded by " or space/comma)
        assert f'"{col}"' not in sql, f"dropped column '{col}' still present in rewritten file"

def test_no_bare_legacy_temp_columns():
    sql = DIODES_MIGRATED.read_text()
    for col in BARE_LEGACY_TEMP:
        assert f'"{col}"' not in sql, f"bare legacy temp column '{col}' still present in rewritten file"

def test_canonical_columns_present():
    sql = DIODES_MIGRATED.read_text()
    assert '"pin_count"' in sql, "pin_count column missing from rewritten file"
    assert '"temp_operating_min"' in sql, "temp_operating_min missing from rewritten file"
    assert '"temp_operating_max"' in sql, "temp_operating_max missing from rewritten file"

def test_no_placeholder_values_survive():
    sql = DIODES_MIGRATED.read_text()
    lower = sql.lower()
    for placeholder in PLACEHOLDER_VALUES:
        # A placeholder as a SQL string value would appear as '...'
        assert f"'{placeholder}'" not in lower, \
            f"placeholder value '{placeholder}' survived in rewritten file"

def test_rewritten_file_executes_cleanly_against_schema():
    """Load schema + rewritten data into in-memory sqlite; verify 9 rows."""
    con = sqlite3.connect(":memory:")
    schema_sql = DIODES_SCHEMA.read_text()
    data_sql = DIODES_MIGRATED.read_text()
    # Strip the CREATE TABLE from the data file (schema provides it)
    # The rewritten file should NOT have a CREATE TABLE; schema file does.
    con.executescript(schema_sql)
    con.executescript(data_sql)
    count = con.execute("SELECT COUNT(*) FROM diodes").fetchone()[0]
    assert count == 9, f"expected 9 diode rows after load, got {count}"
    con.close()

def test_mmbd914_fields_preserved():
    """MMBD914 row must have pin_count=3, temp_operating_min=-65, temp_operating_max=150."""
    con = sqlite3.connect(":memory:")
    con.executescript(DIODES_SCHEMA.read_text())
    con.executescript(DIODES_MIGRATED.read_text())
    row = con.execute(
        "SELECT pin_count, temp_operating_min, temp_operating_max FROM diodes WHERE mpn LIKE 'MMBD914%'"
    ).fetchone()
    assert row is not None, "MMBD914 row not found"
    pin_count, tmin, tmax = row
    assert str(pin_count) == "3", f"expected pin_count=3, got {pin_count!r}"
    assert float(tmin) == -65.0, f"expected temp_operating_min=-65, got {tmin!r}"
    assert float(tmax) == 150.0, f"expected temp_operating_max=150, got {tmax!r}"
    con.close()

def test_identity_fields_preserved():
    """unique_id, mpn, manufacturer, source, dump_priority must survive for all 9 rows."""
    con = sqlite3.connect(":memory:")
    con.executescript(DIODES_SCHEMA.read_text())
    con.executescript(DIODES_MIGRATED.read_text())
    rows = con.execute(
        "SELECT unique_id, mpn, manufacturer, source, dump_priority FROM diodes"
    ).fetchall()
    assert len(rows) == 9
    for uid, mpn, mfr, source, dp in rows:
        # The UNKNOWN row has NULL manufacturer but non-null unique_id
        assert uid is not None
        assert source == "terra_sym", f"source not preserved for {uid}: {source!r}"
        assert dp == 100, f"dump_priority not preserved for {uid}: {dp!r}"
    con.close()
