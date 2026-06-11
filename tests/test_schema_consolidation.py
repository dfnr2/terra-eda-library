# tests/test_schema_consolidation.py
import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def _cols(text):
    return [l for l in text.splitlines() if l.strip() and not l.strip().startswith("--")]

def test_core_snippet_has_41_columns():
    core = (ROOT / "db/schema/core.sql").read_text()
    lines = _cols(core)
    assert len(lines) == 41, f"expected 41 core columns, got {len(lines)}"
    assert lines[0].strip().startswith("unique_id TEXT PRIMARY KEY")
    names = [l.strip().split()[0] for l in lines]
    for required in ("variant", "exclude_from_bom", "pin_count", "component_height",
                     "temp_operating_min", "temp_soldering", "sim_params"):
        assert required in names, f"core missing {required}"


def _table_cols(schema_sql_path):
    con = sqlite3.connect(":memory:")
    con.executescript(schema_sql_path.read_text())
    name = schema_sql_path.parent.name
    return [r[1] for r in con.execute(f'PRAGMA table_info("{name}")')]

def test_diodes_cern_and_native_identical_columns():
    cern = _table_cols(ROOT/"db/tables/cern_diodes/cern_diodes_0_schema.sql")
    native = _table_cols(ROOT/"db/tables/diodes/diodes_0_schema.sql")
    assert cern == native, f"diodes mismatch:\n cern={cern}\n native={native}"
    assert "diode_type" in cern and "forward_voltage" in cern
    assert "pin_count" in cern and "temp_operating_min" in cern   # core present
    assert "tolerance" not in cern and "component_type" not in cern  # legacy dropped
