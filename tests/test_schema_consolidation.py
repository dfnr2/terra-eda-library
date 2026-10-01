# tests/test_schema_consolidation.py
import glob
import json
import re
import sqlite3
import subprocess
import sys
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

def test_diodes_schema_has_tail_and_core():
    cols = _table_cols(ROOT/"db/tables/diodes/diodes_0_schema.sql")
    assert "diode_type" in cols and "forward_voltage" in cols
    assert "pin_count" in cols and "temp_operating_min" in cols   # core present
    assert "tolerance" not in cols and "component_type" not in cols  # legacy dropped


def test_committed_schemas_match_generator():
    table_map = json.loads((ROOT/"db/schema/table_map.json").read_text())
    for table in table_map:
        gen = subprocess.run([sys.executable, str(ROOT/"tools/gen_schema.py"),
                              "--print", table], capture_output=True, text=True,
                             cwd=ROOT).stdout
        on_disk = (ROOT/f"db/tables/{table}/{table}_0_schema.sql").read_text()
        assert gen == on_disk, f"{table}_0_schema.sql is stale — run `make schema`"


def test_data_inserts_are_column_qualified():
    bad = []
    bare = re.compile(r"INSERT\s+INTO\s+[\"']?(\w+)[\"']?\s+VALUES", re.IGNORECASE)
    for f in glob.glob(str(ROOT/"db/tables/*/*.sql")):
        if f.endswith("_0_schema.sql"):
            continue
        for m in bare.finditer(Path(f).read_text()):
            bad.append(f"{Path(f).name}: bare INSERT INTO {m.group(1)} VALUES")
    assert not bad, "positional INSERTs break under core reorder:\n" + "\n".join(bad[:20])


import pytest

PAIRS = {  # type -> list of all tables that must share columns
    "diodes": ["diodes"],
    "transistors": ["bjt", "mosfet"],
    "op_amps": ["ic_opamp"],
    "logic": ["ic_logic"],
    "analog": ["ic_analog"],
    "leds": ["optoelectronics_led"],
    "led_drivers": ["led_drivers"],
    "switches": ["switches"],
    "inductors": ["inductors"],
    "ferrites": ["ferrites_smt"],
    "ic_drivers": ["ic_drivers"],
    "ic_memory": ["ic_memory"],
    "ic_microcontrollers": ["ic_microcontrollers"],
    "test_points": ["test_points"],
    "batteries": ["batteries"],
    "capacitors_electrolytic": ["capacitors_electrolytic_th"],
    "optoelectronics_sensor": ["optoelectronics_sensor"],
    "connectors": ["connectors"],
    "relays_ssr": ["relays_ssr"],
}

@pytest.mark.parametrize("type_,tables", PAIRS.items())
def test_type_tables_share_columns(type_, tables):
    present = {t: _table_cols(ROOT/f"db/tables/{t}/{t}_0_schema.sql")
               for t in tables if (ROOT/f"db/tables/{t}/{t}_0_schema.sql").exists()}
    ref = None
    for t, cols in present.items():
        if ref is None:
            ref = cols
        assert cols == ref, f"{t} diverges for type {type_}"


def test_passive_tables_folded_onto_canonical_core():
    # The native passives were deferred during Phase 0, then folded onto the
    # canonical core afterward (numeric temp_*_min/max, type tails). They are now
    # managed by gen_schema like every other native table.
    table_map = json.loads((ROOT/"db/schema/table_map.json").read_text())
    expected = {
        "resistors_smt": "resistors",
        "capacitors_smt": "capacitors",
        "resistors_th": "resistors_th",   # axial metal-film (Yageo MFR), re-added
        "capacitors_th": "capacitors",    # TDK FG dipped radial-lead MLCC, added
    }
    for t, type_ in expected.items():
        assert t in table_map, f"{t} should be folded into table_map"
        assert table_map[t]["type"] == type_, f"{t} should use type {type_}"
