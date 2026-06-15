import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import register_kicad as rk  # noqa: E402

TABLE = '(sym_lib_table\n  (version 7)\n  (lib (name "Device")(type "KiCad")(uri "x")(options "")(descr ""))\n)\n'
LINE = '(lib (name "terra")(type "HTTP")(uri "${TERRA_EDA_LIB}/terra.kicad_httplib")(options "")(descr ""))'


def test_insert_when_missing():
    new, changed = rk.ensure_lib_entry(TABLE, "terra", LINE)
    assert changed is True
    assert '(name "terra")' in new
    assert new.count("(lib (name") == 2          # original + inserted
    assert new.rstrip().endswith(")")             # still closed


def test_noop_when_present():
    once, _ = rk.ensure_lib_entry(TABLE, "terra", LINE)
    twice, changed = rk.ensure_lib_entry(once, "terra", LINE)
    assert changed is False
    assert twice == once


def test_kicad_config_dir_picks_highest_version(tmp_path):
    base = tmp_path / "kicad"
    for v in ("8.0", "9.0", "10.0"):
        (base / v).mkdir(parents=True)
    assert rk.kicad_config_dir(base).name == "10.0"


def test_register_inserts_into_both_tables(tmp_path):
    cfg = tmp_path / "kicad" / "10.0"
    cfg.mkdir(parents=True)
    (cfg / "sym-lib-table").write_text('(sym_lib_table\n  (version 7)\n)\n')
    (cfg / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n)\n')
    changed = rk.register(cfg)
    assert changed
    sym = (cfg / "sym-lib-table").read_text()
    assert '(name "terra")' in sym and '(name "terra-symbols")' in sym
    assert (cfg / "fp-lib-table").read_text().count('(name "terra-footprints")') == 1
    assert (cfg / "sym-lib-table.terra.bak").exists()
    # idempotent: second run makes no changes
    assert rk.register(cfg) == []
