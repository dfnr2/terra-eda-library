# tests/test_gen_schema.py
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run([sys.executable, str(ROOT/"tools/gen_schema.py"), *args],
                          capture_output=True, text=True, cwd=ROOT)

def _cols(sql):
    body = sql[sql.index("(")+1: sql.rindex(")")]
    return [c.strip().split()[0] for c in body.split(",\n")
            if c.strip() and not c.strip().startswith("--")]

def test_emits_create_table_with_core_and_fragment():
    out = run("--print", "diodes").stdout
    assert out.startswith("CREATE TABLE diodes (")
    assert "unique_id TEXT PRIMARY KEY" in out
    assert "diode_type TEXT" in out             # from fragment
    assert "tier INTEGER DEFAULT 2" in out      # default from table_map
    assert "sim_device TEXT DEFAULT 'D'" in out # sim default from table_map
    assert out.rstrip().endswith(");")

def test_shared_type_same_columns_different_defaults():
    bjt = run("--print", "bjt").stdout
    mosfet = run("--print", "mosfet").stdout
    diodes = run("--print", "diodes").stdout
    assert _cols(bjt) == _cols(mosfet)          # one type fragment -> identical columns
    assert len(_cols(diodes)) == 41 + 6         # 41 core + 6 diode tail
    assert "sim_device TEXT DEFAULT" not in bjt # sim default only where configured
