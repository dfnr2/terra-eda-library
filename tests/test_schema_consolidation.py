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

def test_diodes_cern_and_native_identical_columns():
    cern = _table_cols(ROOT/"db/tables/cern_diodes/cern_diodes_0_schema.sql")
    native = _table_cols(ROOT/"db/tables/diodes/diodes_0_schema.sql")
    assert cern == native, f"diodes mismatch:\n cern={cern}\n native={native}"
    assert "diode_type" in cern and "forward_voltage" in cern
    assert "pin_count" in cern and "temp_operating_min" in cern   # core present
    assert "tolerance" not in cern and "component_type" not in cern  # legacy dropped


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
    "diodes": ["cern_diodes", "diodes"],
    "transistors": ["bjt", "mosfet", "cern_transistors"],
    "op_amps": ["ic_opamp", "cern_op_amps"],
    "logic": ["ic_logic", "cern_logic", "cern_standard_logic"],
    "analog": ["ic_analog", "cern_analog_interface"],
    "leds": ["leds", "cern_leds_displays"],
    "switches": ["switches", "cern_switches"],
    "inductors": ["inductors"],
    "ferrites": ["ferrites"],
    "ic_drivers": ["ic_drivers"],
    "ic_memory": ["ic_memory"],
    "ic_microcontrollers": ["ic_microcontrollers"],
    "connectors": ["connectors", "cern_3m", "cern_amphenol", "cern_erni", "cern_fci",
                   "cern_harting", "cern_harwin", "cern_lemo", "cern_mentor",
                   "cern_molex", "cern_phoenix", "cern_samtec", "cern_sockets",
                   "cern_souriau", "cern_stelvio_kontek_comatel", "cern_tyco",
                   "cern_weidmuller"],
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


def test_passive_tables_not_in_table_map():
    table_map = json.loads((ROOT/"db/schema/table_map.json").read_text())
    for t in ("resistors_smt", "resistors_th", "capacitors_smt", "capacitors_th"):
        assert t not in table_map, f"{t} curated — out of Phase 0 scope"

def test_deferred_cern_only_types_not_in_table_map():
    table_map = json.loads((ROOT/"db/schema/table_map.json").read_text())
    for t in ("cern_batteries", "cern_crystals_oscillators", "cern_dc_dc_converters",
              "cern_fuses", "cern_optocouplers", "cern_power_supplies", "cern_regulators",
              "cern_relays", "cern_sensors", "cern_thermistors_varistors", "cern_transformers"):
        assert t not in table_map, f"{t} deferred this round"
