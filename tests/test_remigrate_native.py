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


# ---------------------------------------------------------------------------
# Semantic map unit tests (transform functions)
# ---------------------------------------------------------------------------

def _import_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("remigrate_native", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_diode_type_schottky():
    """'Schottky Diode' → 'schottky'."""
    mod = _import_module()
    result = mod._diode_type_transform("Schottky Diode")
    assert result == "schottky", f"expected 'schottky', got {result!r}"


def test_diode_type_bare_dropped():
    """Bare 'Diode' is a generic category; should map to None (dropped)."""
    mod = _import_module()
    result = mod._diode_type_transform("Diode")
    assert result is None, f"expected None (drop), got {result!r}"


def test_diode_type_schottky_no_suffix():
    """'Schottky' without 'Diode' suffix is preserved as 'schottky'."""
    mod = _import_module()
    result = mod._diode_type_transform("Schottky")
    assert result == "schottky", f"expected 'schottky', got {result!r}"


def test_mosfet_power_rating_split_space():
    """'28V 5A' → v_ce_ds_max='28V', i_c_d_max='5A'."""
    mod = _import_module()
    v, i = mod._parse_voltage_token("28V 5A"), mod._parse_current_token("28V 5A")
    assert v == "28V", f"expected '28V', got {v!r}"
    assert i == "5A", f"expected '5A', got {i!r}"


def test_mosfet_power_rating_split_comma():
    """'30V, 3.8A' → v_ce_ds_max='30V', i_c_d_max='3.8A'."""
    mod = _import_module()
    v, i = mod._parse_voltage_token("30V, 3.8A"), mod._parse_current_token("30V, 3.8A")
    assert v == "30V", f"expected '30V', got {v!r}"
    assert i == "3.8A", f"expected '3.8A', got {i!r}"


def test_mosfet_power_rating_split_comma2():
    """'20V, 4.2A' → v_ce_ds_max='20V', i_c_d_max='4.2A'."""
    mod = _import_module()
    v, i = mod._parse_voltage_token("20V, 4.2A"), mod._parse_current_token("20V, 4.2A")
    assert v == "20V", f"expected '20V', got {v!r}"
    assert i == "4.2A", f"expected '4.2A', got {i!r}"


# ---------------------------------------------------------------------------
# Semantic map integration tests — verify mapped values land in the DB
# ---------------------------------------------------------------------------

SCHEMAS = {t: ROOT / "db" / "tables" / t / f"{t}_0_schema.sql"
           for t in ("diodes", "mosfet", "ic_analog", "ic_memory", "ic_logic", "ic_drivers")}
DATA = {t: ROOT / "db" / "tables" / t / f"{t}_1_migrated.sql"
        for t in ("diodes", "mosfet", "ic_analog", "ic_memory", "ic_logic", "ic_drivers")}


def _load_db(table):
    """Load schema + data into in-memory sqlite; return connection."""
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMAS[table].read_text())
    con.executescript(DATA[table].read_text())
    return con


def test_diodes_schottky_diode_type():
    """Schottky diodes must have diode_type='schottky'; bare 'Diode' rows have NULL.

    The legacy data has 4 rows with component_type='Schottky Diode' (3 Vishay + 1 OnSemi),
    so 4 schottky rows are expected.
    """
    con = _load_db("diodes")
    schottky_count = con.execute(
        "SELECT COUNT(*) FROM diodes WHERE diode_type = 'schottky'"
    ).fetchone()[0]
    assert schottky_count == 4, f"expected 4 schottky rows, got {schottky_count}"
    total = con.execute("SELECT COUNT(*) FROM diodes").fetchone()[0]
    assert total == 9, f"expected 9 diode rows, got {total}"
    con.close()


def test_mosfet_v_and_i_populated():
    """All 3 mosfet rows should have v_ce_ds_max and i_c_d_max set."""
    con = _load_db("mosfet")
    rows = con.execute(
        "SELECT mpn, v_ce_ds_max, i_c_d_max FROM mosfet ORDER BY mpn"
    ).fetchall()
    assert len(rows) == 3, f"expected 3 mosfet rows, got {len(rows)}"
    for mpn, v, i in rows:
        assert v is not None, f"v_ce_ds_max is NULL for {mpn}"
        assert i is not None, f"i_c_d_max is NULL for {mpn}"
    # Check the specific values
    by_mpn = {mpn: (v, i) for mpn, v, i in rows}
    assert by_mpn.get("BTS5030-1EJA") == ("28V", "5A"), \
        f"BTS5030-1EJA mismatch: {by_mpn.get('BTS5030-1EJA')!r}"
    assert by_mpn.get("DMP3099L") == ("30V", "3.8A"), \
        f"DMP3099L mismatch: {by_mpn.get('DMP3099L')!r}"
    assert by_mpn.get("IRLM2502TRPBF") == ("20V", "4.2A"), \
        f"IRLM2502TRPBF mismatch: {by_mpn.get('IRLM2502TRPBF')!r}"
    con.close()


def test_ic_analog_function_type():
    """INA180A2 must have function_type='current sense amplifier'."""
    con = _load_db("ic_analog")
    row = con.execute(
        "SELECT function_type FROM ic_analog WHERE mpn = 'INA180A2'"
    ).fetchone()
    assert row is not None, "INA180A2 not found"
    assert row[0] == "current sense amplifier", \
        f"expected 'current sense amplifier', got {row[0]!r}"
    con.close()


def test_ic_memory_memory_type():
    """24LC32AT-I/OT must have memory_type='EEPROM'."""
    con = _load_db("ic_memory")
    row = con.execute(
        "SELECT memory_type FROM ic_memory WHERE mpn LIKE '%24LC32A%'"
    ).fetchone()
    assert row is not None, "24LC32A row not found"
    assert row[0] == "EEPROM", f"expected 'EEPROM', got {row[0]!r}"
    con.close()


def test_ic_logic_gate_function_level_shifter():
    """SN74LVC1G139 (Level Shifter) row must have gate_function='level shifter'."""
    con = _load_db("ic_logic")
    count = con.execute(
        "SELECT COUNT(*) FROM ic_logic WHERE gate_function = 'level shifter'"
    ).fetchone()[0]
    assert count >= 1, "no level shifter gate_function found"
    total = con.execute("SELECT COUNT(*) FROM ic_logic").fetchone()[0]
    assert total == 4, f"expected 4 ic_logic rows, got {total}"
    con.close()


def test_ic_drivers_row_count_and_mappings():
    """14 rows total; SZNUD3124DMT1G must have i_max_device='150 mA'; level shifters mapped."""
    con = _load_db("ic_drivers")
    total = con.execute("SELECT COUNT(*) FROM ic_drivers").fetchone()[0]
    assert total == 14, f"expected 14 ic_drivers rows, got {total}"

    row = con.execute(
        "SELECT i_max_device FROM ic_drivers WHERE mpn LIKE '%SZNUD3124%'"
    ).fetchone()
    assert row is not None, "SZNUD3124DMT1G row not found"
    assert row[0] == "150 mA", f"expected i_max_device='150 mA', got {row[0]!r}"

    # Level Shifters should have driver_type populated
    ls_count = con.execute(
        "SELECT COUNT(*) FROM ic_drivers WHERE driver_type = 'level shifter'"
    ).fetchone()[0]
    assert ls_count >= 1, "no 'level shifter' driver_type rows found"
    con.close()
