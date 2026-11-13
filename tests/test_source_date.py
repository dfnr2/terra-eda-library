# tests/test_source_date.py
"""'Changed On' is stable across rebuilds: it comes from git, not the build clock."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import source_date  # noqa: E402
from generate_kicad_dbl_files import create_field_config  # noqa: E402


def test_generated_sql_maps_to_generator_and_helpers():
    sql = ROOT / "db/tables/capacitors_th/capacitors_th_generated_300_tdk_fg.sql"
    names = {p.name for p in source_date.sources_for(sql)}
    assert "run_300_tdk_fg.py" in names
    assert "_keywords.py" in names and "fg_catalog.json" in names


def test_static_sql_maps_to_itself():
    sql = ROOT / "db/tables/diodes/diodes_0_schema.sql"
    assert source_date.sources_for(sql) == [sql.resolve()]


def test_updated_on_is_an_iso_date_and_repeatable():
    sql = ROOT / "db/tables/mosfet/mosfet_generated_310_nexperia_bss.sql"
    first = source_date.updated_on(sql)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", first)
    assert source_date.updated_on(sql) == first


def test_symbol_fields_have_changed_on_and_no_built_on():
    assert create_field_config("created_at", "resistors_th") is None
    assert create_field_config("updated_at", "resistors_th")["name"] == "Changed On"
