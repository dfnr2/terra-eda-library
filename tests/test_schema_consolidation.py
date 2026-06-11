# tests/test_schema_consolidation.py
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
