import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "db/tables/cern_diodes/cern_diodes_0_schema.sql"

EXPECTED = {
    # 41 canonical core columns
    "unique_id", "part_locator", "mpn", "manufacturer", "variant", "package",
    "value", "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status",
    "rohs", "rohs_document_link", "allow_substitution", "tracking",
    "standards_version", "bom_comment", "created_at", "updated_at", "created_by",
    "source", "dump_priority", "tier", "tags", "sim_model_type", "sim_device",
    "sim_pins", "sim_model_file", "sim_params",
    "pin_count", "component_height",
    "exclude_from_bom",
    "temp_operating_min", "temp_operating_max",
    "temp_storage_min", "temp_storage_max", "temp_soldering",
    # 6 diode-specific tail columns
    "diode_type", "voltage_rating", "forward_voltage", "forward_current",
    "current_rating", "power_rating",
}


def test_schema_columns():
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA.read_text())
    cols = {r[1] for r in con.execute("PRAGMA table_info(cern_diodes)")}
    assert cols == EXPECTED
