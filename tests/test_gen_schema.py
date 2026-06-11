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
    out = run("--print", "cern_diodes").stdout
    assert out.startswith("CREATE TABLE cern_diodes (")
    assert "unique_id TEXT PRIMARY KEY" in out
    assert "diode_type TEXT" in out             # from fragment
    assert "tier INTEGER DEFAULT 5" in out      # cern default from table_map
    assert out.rstrip().endswith(");")

def test_native_same_columns_different_defaults():
    cern = run("--print", "cern_diodes").stdout
    native = run("--print", "diodes").stdout
    assert _cols(cern) == _cols(native)         # identical column set + order
    assert "tier INTEGER DEFAULT 2" in native   # native default differs
    assert len(_cols(cern)) == 41 + 6           # 41 core + 6 diode tail
