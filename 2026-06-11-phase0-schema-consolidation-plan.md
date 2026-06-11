# Phase 0 Schema Consolidation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every non-passive part type one canonical parametric column tail, defined once and shared by both its CERN table (`cern_<type>`) and its terra-native table (`<type>`), on top of a single canonical 41-column core — so the later Nexar harvest has a stable, deduplicated target schema and the future one-time CERN→native fold is trivial.

**Architecture:** Each part table's `_0_schema.sql` (the full `CREATE TABLE`) becomes **generated** by `tools/gen_schema.py` from two committed snippets: `db/schema/core.sql` (the 41 shared core columns) and `db/schema/types/<type>.sql` (the type-specific tail). `db/schema/table_map.json` maps each table → its type + per-table `tier`/`dump_priority` defaults. A `make schema` target regenerates all of them; a drift test fails the build if a committed `_0_schema.sql` differs from what the generator emits; equivalence tests assert cern and native tables of a type expose identical column sets. SQLite has no `INCLUDE` and `.read` cannot split one `CREATE TABLE`, so generation (not concatenation) is the mechanism.

**Tech Stack:** Python 3 (stdlib only), SQLite, GNU Make, pytest (`uv run pytest`). Authoritative spec: `./2026-06-11-sparse-quality-db-nexar-resolver.md` (Part A). Column marks: `./schema-review.org`.

**Background — the divergence this resolves (verified 2026-06-11):** the live core blocks have diverged in **membership**, not just order. `cern_diodes` carries `variant` + `pin_count` + `component_height` but not `exclude_from_bom`; `connectors` carries `exclude_from_bom` but not `variant`. `pin_count`/`component_height` are present and populated in 35 of 41 tables (CERN import added them). The native non-passive tables also carry a legacy generic tail from the old flat `symbols` table (`class, component_type, component_value, composition, number_of_pins, reference, sim_library, sim_type, temp_coeff`, plus per-type `tolerance`/`power_rating` cruft) — dropped here. The canonical core is pinned to what is deployed + populated, plus the 5 new temperature columns Dave requires.

---

## Canonical definitions (used throughout)

**Canonical core — 41 columns**, in this exact order (base 33 from `cern_diodes` + `pin_count`, `component_height`, `exclude_from_bom`, 5 temp). `tier`/`dump_priority` defaults are placeholders the generator rewrites per `table_map.json`:

```
unique_id, part_locator, mpn, manufacturer, variant, package, value, description,
datasheet, manufacturer_link, kicad_symbol, kicad_footprint, altium_symbol,
altium_footprint, lifecycle_status, rohs, rohs_document_link, allow_substitution,
tracking, standards_version, bom_comment, created_at, updated_at, created_by, source,
dump_priority, tier, tags, sim_model_type, sim_device, sim_pins, sim_model_file,
sim_params, pin_count, component_height, exclude_from_bom, temp_operating_min,
temp_operating_max, temp_storage_min, temp_storage_max, temp_soldering
```

**DROP-ALL (9 legacy columns)** removed from every regenerated table by virtue of the canonical core/fragments omitting them: `class, component_type, component_value, composition, number_of_pins, reference, sim_library, sim_type, temp_coeff`.

**table_map type → tables** (this round). `cern_*` rows default `tier_default: 5, dump_priority_default: 0`; native rows `tier_default: 2, dump_priority_default: 1`:

```
diodes              : cern_diodes(cern), diodes(native)
transistors         : bjt(native), mosfet(native), cern_transistors(cern)
op_amps             : ic_opamp(native), cern_op_amps(cern)
logic               : ic_logic(native), cern_logic(cern), cern_standard_logic(cern)
analog              : ic_analog(native), cern_analog_interface(cern)
leds                : leds(native), cern_leds_displays(cern)
switches            : switches(native), cern_switches(cern)
inductors           : inductors(native)
ferrites            : ferrites(native)
ic_drivers          : ic_drivers(native)
ic_memory           : ic_memory(native)
ic_microcontrollers : ic_microcontrollers(native)
connectors          : connectors(native) + cern_3m, cern_amphenol, cern_erni,
                      cern_fci, cern_harting, cern_harwin, cern_lemo, cern_mentor,
                      cern_molex, cern_phoenix, cern_samtec, cern_sockets,
                      cern_souriau, cern_stelvio_kontek_comatel, cern_tyco,
                      cern_weidmuller   (all type: connectors)
```

**Out of scope (do NOT add to table_map):** CERN-only types (`cern_batteries, cern_crystals_oscillators, cern_dc_dc_converters, cern_fuses, cern_optocouplers, cern_power_supplies, cern_regulators, cern_relays, cern_sensors, cern_thermistors_varistors, cern_transformers`) and passives (`resistors_smt, resistors_th, capacitors_smt, capacitors_th`). `_global` is not a part table.

---

## File Structure

- `db/schema/core.sql` — **Create.** 41 core column lines (no `CREATE TABLE` wrapper).
- `db/schema/types/<type>.sql` — **Create (13 files).** Per-type tail (column lines only): `diodes, transistors, op_amps, logic, analog, leds, switches, inductors, ferrites, ic_drivers, ic_memory, ic_microcontrollers, connectors`.
- `db/schema/table_map.json` — **Create.** Table → `{type, tier_default, dump_priority_default}`.
- `tools/gen_schema.py` — **Create.** Emits each table's `_0_schema.sql` from core + fragment.
- `tests/test_gen_schema.py` — **Create.** Generator unit tests.
- `tests/test_schema_consolidation.py` — **Create.** Core-count, equivalence, drift, INSERT-safety, passive-guard tests.
- `db/tables/<table>/<table>_0_schema.sql` — **Modify (regenerated)** for all 30 consolidated tables.
- `Makefile` — **Modify.** Add `schema` target as a prerequisite of table builds.

---

## Task 1: Canonical core snippet

**Files:** Create `db/schema/core.sql`; Test `tests/test_schema_consolidation.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run it, verify failure**

Run: `uv run pytest tests/test_schema_consolidation.py::test_core_snippet_has_41_columns -v`
Expected: FAIL (file does not exist).

- [ ] **Step 3: Create `db/schema/core.sql`**

```sql
-- db/schema/core.sql
-- The 41 shared core columns for every part table. Column definitions only —
-- gen_schema.py wraps these in CREATE TABLE and appends the type fragment.
-- tier/dump_priority DEFAULTs here are placeholders; gen_schema.py rewrites them per table_map.json.
-- No trailing comma after the last column — gen_schema.py inserts commas between columns.
    unique_id TEXT PRIMARY KEY,
    part_locator TEXT,
    mpn TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    variant TEXT,
    package TEXT,
    value TEXT,
    description TEXT,
    datasheet TEXT,
    manufacturer_link TEXT,
    kicad_symbol TEXT,
    kicad_footprint TEXT,
    altium_symbol TEXT,
    altium_footprint TEXT,
    lifecycle_status TEXT DEFAULT 'Active',
    rohs TEXT DEFAULT 'no',
    rohs_document_link TEXT,
    allow_substitution TEXT DEFAULT 'no',
    tracking TEXT DEFAULT 'no',
    standards_version TEXT DEFAULT 'v1.0',
    bom_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    source TEXT DEFAULT 'static',
    dump_priority INTEGER DEFAULT 1,
    tier INTEGER DEFAULT 5,
    tags TEXT DEFAULT '',
    sim_model_type TEXT,
    sim_device TEXT,
    sim_pins TEXT,
    sim_model_file TEXT,
    sim_params TEXT,
    pin_count TEXT,
    component_height TEXT,
    exclude_from_bom BOOLEAN NOT NULL DEFAULT 0,
    temp_operating_min REAL,
    temp_operating_max REAL,
    temp_storage_min REAL,
    temp_storage_max REAL,
    temp_soldering REAL
```

- [ ] **Step 4: Run it, verify pass**

Run: `uv run pytest tests/test_schema_consolidation.py::test_core_snippet_has_41_columns -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add db/schema/core.sql tests/test_schema_consolidation.py
git commit -m "add canonical 41-column core schema snippet"
```

---

## Task 2: Schema generator + table_map (diodes pilot)

**Files:** Create `tools/gen_schema.py`, `db/schema/table_map.json`; Test `tests/test_gen_schema.py`

- [ ] **Step 1: Write `db/schema/table_map.json`** (diodes pair only; later tasks extend it)

```json
{
  "cern_diodes": { "type": "diodes", "tier_default": 5, "dump_priority_default": 0 },
  "diodes":      { "type": "diodes", "tier_default": 2, "dump_priority_default": 1 }
}
```

- [ ] **Step 2: Write the failing generator tests**

```python
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
```

- [ ] **Step 3: Run, verify failure**

Run: `uv run pytest tests/test_gen_schema.py -v`
Expected: FAIL (generator + diodes fragment missing).

- [ ] **Step 4: Write `tools/gen_schema.py`**

```python
#!/usr/bin/env python3
"""Generate each part table's _0_schema.sql from the shared core + per-type fragment.

Reads db/schema/core.sql, db/schema/types/<type>.sql, db/schema/table_map.json.
Emits `CREATE TABLE <table> ( <core>, <type-fragment> );` to
db/tables/<table>/<table>_0_schema.sql (or stdout with --print <table>).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "db/schema/core.sql"
TYPES = ROOT / "db/schema/types"
MAP = ROOT / "db/schema/table_map.json"


def _lines(text: str) -> list[str]:
    return [l.rstrip() for l in text.splitlines()
            if l.strip() and not l.strip().startswith("--")]


def render(table: str, cfg: dict) -> str:
    out = []
    for l in _lines(CORE.read_text()):
        s = l.strip().rstrip(",")
        if s.startswith("tier INTEGER"):
            l = f"    tier INTEGER DEFAULT {cfg['tier_default']}"
        elif s.startswith("dump_priority INTEGER"):
            l = f"    dump_priority INTEGER DEFAULT {cfg['dump_priority_default']}"
        out.append(l.rstrip(","))
    frag = _lines((TYPES / f"{cfg['type']}.sql").read_text())
    cols = [c.rstrip(",") for c in out + frag]
    body = ",\n".join(cols)
    header = (f"-- db/tables/{table}/{table}_0_schema.sql\n"
              f"-- GENERATED by tools/gen_schema.py from db/schema/core.sql + "
              f"db/schema/types/{cfg['type']}.sql — DO NOT EDIT BY HAND.\n")
    return f"{header}\nCREATE TABLE {table} (\n{body}\n);\n"


def main() -> None:
    table_map = json.loads(MAP.read_text())
    args = sys.argv[1:]
    if args and args[0] == "--print":
        sys.stdout.write(render(args[1], table_map[args[1]]))
        return
    for table in (args or list(table_map)):
        cfg = table_map[table]
        dest = ROOT / f"db/tables/{table}/{table}_0_schema.sql"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(table, cfg))
        print(f"  wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Create the diodes fragment now** (the Task 2 tests depend on it; Task 3 covers regeneration)

```sql
-- db/schema/types/diodes.sql
-- Canonical parametric tail for diodes (cern_diodes + diodes).
    diode_type TEXT,        -- rectifier | schottky | zener | tvs | small-signal | ...
    voltage_rating TEXT,    -- Vr (reverse standoff / working)
    forward_voltage TEXT,   -- Vf
    forward_current TEXT,   -- If
    current_rating TEXT,    -- Io (rectifiers)
    power_rating TEXT        -- Pd where applicable (TVS/zener)
```

- [ ] **Step 6: Run, verify pass**

Run: `uv run pytest tests/test_gen_schema.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add tools/gen_schema.py db/schema/table_map.json db/schema/types/diodes.sql tests/test_gen_schema.py
git commit -m "add gen_schema.py + table_map: generate _0_schema.sql from core + type fragment"
```

---

## Task 3: Diodes pilot — regenerate both tables, prove equivalence

**Files:** Modify (regenerate) `db/tables/cern_diodes/cern_diodes_0_schema.sql`, `db/tables/diodes/diodes_0_schema.sql`; Test `tests/test_schema_consolidation.py`

- [ ] **Step 1: Add the column-extraction helper + equivalence test**

```python
# add to tests/test_schema_consolidation.py
import sqlite3

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
```

- [ ] **Step 2: Run, verify failure**

Run: `uv run pytest tests/test_schema_consolidation.py::test_diodes_cern_and_native_identical_columns -v`
Expected: FAIL (native `diodes` still has the legacy tail).

- [ ] **Step 3: Regenerate both diodes schemas**

Run: `uv run python tools/gen_schema.py cern_diodes diodes`
Expected: prints `wrote db/tables/cern_diodes/...` and `... diodes ...`.

- [ ] **Step 4: Run equivalence + generator tests**

Run: `uv run pytest tests/test_schema_consolidation.py tests/test_gen_schema.py -v`
Expected: PASS.

- [ ] **Step 5: Rebuild diodes DBs, confirm they load (column-qualified data still loads after reorder)**

Run: `make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5 cern_diodes-build diodes-build`
Expected: both build with no SQL error.
Run: `sqlite3 db/cern_diodes.db "SELECT COUNT(*) FROM cern_diodes;"`
Expected: the pre-existing row count, unchanged.
Run: `sqlite3 db/cern_diodes.db "SELECT diode_type, forward_voltage, temp_operating_min FROM cern_diodes LIMIT 1;"`
Expected: a row (new columns exist; harvested values may be empty).

- [ ] **Step 6: Run the CERN diodes table test**

Run: `make cern_diodes-test`
Expected: PASS. If it asserts on a dropped legacy column, update it to the canonical column and note the change in the commit.

- [ ] **Step 7: Commit**

```bash
git add db/schema/types/diodes.sql db/tables/cern_diodes/cern_diodes_0_schema.sql \
        db/tables/diodes/diodes_0_schema.sql tests/test_schema_consolidation.py
git commit -m "consolidate diodes schema: one canonical core + tail for cern_diodes + diodes"
```

---

## Task 4: `make schema` target + drift guard

**Files:** Modify `Makefile`; Test `tests/test_schema_consolidation.py`

- [ ] **Step 1: Write the drift-guard test**

```python
# add to tests/test_schema_consolidation.py
import json, subprocess, sys

def test_committed_schemas_match_generator():
    table_map = json.loads((ROOT/"db/schema/table_map.json").read_text())
    for table in table_map:
        gen = subprocess.run([sys.executable, str(ROOT/"tools/gen_schema.py"),
                              "--print", table], capture_output=True, text=True,
                             cwd=ROOT).stdout
        on_disk = (ROOT/f"db/tables/{table}/{table}_0_schema.sql").read_text()
        assert gen == on_disk, f"{table}_0_schema.sql is stale — run `make schema`"
```

- [ ] **Step 2: Run it**

Run: `uv run pytest tests/test_schema_consolidation.py::test_committed_schemas_match_generator -v`
Expected: PASS (only diodes in table_map so far, already regenerated).

- [ ] **Step 3: Add the `schema` target to the Makefile** (near the other `.PHONY` targets; make it a prerequisite of the per-table builds if not already)

```makefile
.PHONY: schema
schema: $(VENV_MARKER)
	@echo "Regenerating part-table schemas from db/schema/ ..."
	@$(PYTHON) tools/gen_schema.py
```

- [ ] **Step 4: Verify idempotent**

Run: `make schema && git diff --stat db/tables/*/*_0_schema.sql`
Expected: no diff.

- [ ] **Step 5: Commit**

```bash
git add Makefile tests/test_schema_consolidation.py
git commit -m "add make schema target + drift guard for generated table schemas"
```

---

## Task 5: Column-qualified-INSERT invariant guard

A core reorder is data-safe **only** if data INSERTs are column-qualified. Assert it once so no regeneration silently misloads the populated `cern_*` tables.

**Files:** Test `tests/test_schema_consolidation.py`

- [ ] **Step 1: Write the invariant test**

```python
# add to tests/test_schema_consolidation.py
import re, glob

def test_data_inserts_are_column_qualified():
    # Every INSERT in a table's data SQL must name its columns: INSERT INTO t (cols) VALUES
    bad = []
    bare = re.compile(r"INSERT\s+INTO\s+[\"']?(\w+)[\"']?\s+VALUES", re.IGNORECASE)
    for f in glob.glob(str(ROOT/"db/tables/*/*.sql")):
        if f.endswith("_0_schema.sql"):
            continue
        for m in bare.finditer(Path(f).read_text()):
            bad.append(f"{Path(f).name}: bare INSERT INTO {m.group(1)} VALUES")
    assert not bad, "positional INSERTs break under core reorder:\n" + "\n".join(bad[:20])
```

- [ ] **Step 2: Run it**

Run: `uv run pytest tests/test_schema_consolidation.py::test_data_inserts_are_column_qualified -v`
Expected: PASS. **If it FAILS**, the offending generator/import emits positional INSERTs — fix the emitter (CERN import `run_*_cern_import.py` and/or `tools/db_to_tables.py`) to write `INSERT INTO <t> (col, …) VALUES (…)`, regenerate those data files, and re-run until green. Document any emitter fix in the commit.

- [ ] **Step 3: Commit**

```bash
git add tests/test_schema_consolidation.py
git commit -m "guard: require column-qualified data INSERTs so core reorder is data-safe"
```

---

## Tasks 6–17: Per-type fragments

**Shared procedure for each type below** (identical shape to Task 3):

1. Create `db/schema/types/<type>.sql` with the columns shown.
2. Add the type's table rows to `db/schema/table_map.json` (cern rows `tier_default:5, dump_priority_default:0`; native rows `tier_default:2, dump_priority_default:1`).
3. Regenerate: `uv run python tools/gen_schema.py <tables…>`.
4. Test: `uv run pytest tests/test_schema_consolidation.py tests/test_gen_schema.py -v` (the parametrized equivalence + drift + invariant tests cover the new tables).
5. Rebuild each table: `make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5 <table>-build`; for each `cern_*` table also run `make <cern_table>-test` if a test file exists, and confirm `SELECT COUNT(*)` is unchanged.
6. Commit: `git commit -m "consolidate <type> schema"`.

**First, add the parametrized equivalence test** (replaces the single diodes assertion; covers every type as table_map grows):

- [ ] **Step 0 (once): add the parametrized equivalence test**

```python
# add to tests/test_schema_consolidation.py
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
```

(Types not yet generated are skipped via the `.exists()` filter; they activate as each task runs.)

### Task 6 — transistors (bjt, mosfet, cern_transistors)

```sql
-- db/schema/types/transistors.sql
    transistor_type TEXT,     -- npn | pnp | nmos | pmos | igbt | jfet | ...
    channels INTEGER,
    v_ce_ds_max TEXT,         -- Vce (BJT) / Vds (FET)
    i_c_d_max TEXT,           -- Ic / Id
    power_dissipation TEXT,
    hfe_typ TEXT,             -- BJT gain (null for FET)
    rds_on TEXT,              -- FET on-resistance (null for BJT)
    vgs_th TEXT,              -- FET threshold (null for BJT)
    transition_freq TEXT,     -- ft
    temp_junction_max TEXT    -- Tj max
```

### Task 7 — op_amps (ic_opamp, cern_op_amps)

```sql
-- db/schema/types/op_amps.sql
    amplifier_type TEXT,      -- voltage-fb | current-fb | instrumentation | ...
    channels INTEGER,
    gain_bandwidth TEXT,      -- GBW
    slew_rate TEXT,
    input_offset TEXT,
    input_noise TEXT,
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    power_rating TEXT         -- if specified; else n/a
```

### Task 8 — logic (ic_logic, cern_logic, cern_standard_logic)

```sql
-- db/schema/types/logic.sql
    logic_family TEXT,        -- 74HC | 74LVC | 4000 | ...
    gate_function TEXT,       -- and | or | nand | mux | ff | buffer | ...
    channels INTEGER,         -- gates/bits per package
    propagation_delay TEXT,   -- tpd
    supply_voltage_min REAL,
    supply_voltage_max REAL
```

### Task 9 — analog (ic_analog, cern_analog_interface)

```sql
-- db/schema/types/analog.sql
    function_type TEXT,       -- adc | dac | comparator | mux | vref | interface | ...
    channels INTEGER,
    resolution_bits TEXT,
    interface TEXT,           -- spi | i2c | parallel | ...
    supply_voltage_min REAL,
    supply_voltage_max REAL
```

### Task 10 — leds (leds, cern_leds_displays)

```sql
-- db/schema/types/leds.sql
    color TEXT,
    wavelength_nm TEXT,
    forward_voltage_v TEXT,
    current_max_ma TEXT,
    luminous_intensity TEXT,
    viewing_angle TEXT
```

### Task 11 — switches (switches, cern_switches)

```sql
-- db/schema/types/switches.sql
    switch_type TEXT,         -- tactile | toggle | dip | rotary | slide | ...
    poles INTEGER,
    throws INTEGER,
    current_rating TEXT,      -- contact current
    voltage_rating TEXT,      -- contact voltage
    actuation_force TEXT
```

### Task 12 — inductors (inductors)

```sql
-- db/schema/types/inductors.sql
    inductance TEXT,
    tolerance TEXT,
    current_rating TEXT,      -- rated
    saturation_current TEXT,  -- Isat
    dc_resistance TEXT,       -- DCR
    self_res_freq TEXT        -- SRF
```

### Task 13 — ferrites (ferrites)

```sql
-- db/schema/types/ferrites.sql
    impedance_at_freq TEXT,   -- impedance @ freq
    dc_resistance TEXT,       -- DCR
    current_rating TEXT,      -- rated
    power_rating TEXT,
    tolerance TEXT
```

### Task 14 — ic_drivers (ic_drivers)

```sql
-- db/schema/types/ic_drivers.sql
    driver_type TEXT,         -- gate | motor | led | line driver | ...
    channels INTEGER,
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    i_max_device TEXT,        -- max device current
    i_max_channel TEXT,       -- max current per channel
    logic_polarity TEXT,      -- inverting | noninverting | both
    output_type TEXT,         -- active | totem | open-collector | current-loop
    power_rating TEXT
```

### Task 15 — ic_memory (ic_memory)

```sql
-- db/schema/types/ic_memory.sql
    memory_type TEXT,         -- sram | dram | flash | eeprom | ...
    capacity TEXT,
    word_size TEXT,
    speed TEXT,
    interface TEXT,           -- spi | i2c | parallel | ...
    persistence_cycles TEXT,  -- write cycles before degradation
    persistence_years TEXT    -- retention years
```

### Task 16 — ic_microcontrollers (ic_microcontrollers)

`pin_count` is **core**, so it is NOT in this fragment.

```sql
-- db/schema/types/ic_microcontrollers.sql
    family TEXT,
    core TEXT,                -- CPU core
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    flash_size TEXT,
    eeprom_size TEXT,
    ram_size TEXT,
    gpio_count INTEGER,
    uart_count INTEGER,
    i2c_count INTEGER,
    timer_count INTEGER,
    special_features TEXT     -- brief URL-safe list
```

### Task 17 — connectors (connectors + 16 cern_<vendor> tables)

The native `connectors` tail is the canonical bar. Build the fragment by **copying the type-specific tail verbatim** from the current `db/tables/connectors/connectors_0_schema.sql` — every column **after** the core block (`connector_category` through `mating_part_hint`), **excluding** any core columns that appear interleaved there (`exclude_from_bom`, and `pin_count`/`component_height` if present — they are core now). Expected tail column names (verify against the file; do not invent):

```
connector_category, connector_family, connector_series, connector_type,
positions, rows, pitch_mm, row_pitch_mm, orientation, termination_type,
gender, polarized, keying_detail, locking_mechanism, shielding,
panel_mount_style, color, current_rating_a, voltage_rating_v,
contact_resistance_mohm, insulation_resistance_mohm, dielectric_withstand_vrms,
signal_type, wire_gauge_min_awg, wire_gauge_max_awg, insulation_dia_min_mm,
insulation_dia_max_mm, cable_type, flammability_rating, ip_rating,
creepage_clearance_note, mating_family, mating_part_hint
```

Write these (with their exact types from the file) to `db/schema/types/connectors.sql`, add all 17 tables to `table_map.json` under `type: connectors`, regenerate, and run the shared procedure. Extra verification — the populated CERN vendor tables must keep their row counts after gaining the (currently-empty) parametric + temp columns:

```bash
make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5 cern_molex-build
sqlite3 db/cern_molex.db "SELECT COUNT(*) FROM cern_molex;"   # unchanged (≈503)
```

- [ ] After all of Tasks 6–17: `uv run pytest tests/test_schema_consolidation.py -v` → every `test_type_tables_share_columns[...]` PASS, drift guard PASS.

---

## Task 18: Confirm no data loss from dropped legacy columns

The regenerated native non-passive tables no longer contain the 9 DROP-ALL legacy columns. Confirm the affected native tables held no unique data there.

**Files:** none (verification + commit message)

- [ ] **Step 1: Inspect row counts of regenerated native scaffolds**

```bash
for t in diodes mosfet bjt ic_opamp ic_logic ic_analog leds switches inductors ferrites ic_drivers ic_memory ic_microcontrollers; do
  echo -n "$t: "; sqlite3 db/$t.db "SELECT COUNT(*) FROM $t;" 2>/dev/null || echo "(no db)"
done
```

Expected: single-digit/low counts (near-empty scaffolds). For any table with >0 rows, confirm the dropped legacy columns (`class, component_type, component_value, composition, number_of_pins, reference, sim_library, sim_type, temp_coeff`, plus per-type `tolerance`/`power_rating` cruft) held no unique info — their real data lives in core `value`/`description`/`package` (or, for `number_of_pins`, the core `pin_count`).

- [ ] **Step 2: Commit findings**

```bash
git commit --allow-empty -am "confirm no data loss dropping legacy generic columns from native tables"
```

---

## Task 19: Passive-table guard

`resistors_smt` (22,539 rows), `resistors_th`, `capacitors_smt` (4,863), `capacitors_th` are populated/curated and **out of Phase 0**. Guard against accidentally regenerating them.

**Files:** Test `tests/test_schema_consolidation.py`

- [ ] **Step 1: Add the guard test**

```python
# add to tests/test_schema_consolidation.py
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
```

- [ ] **Step 2: Run + commit**

Run: `uv run pytest tests/test_schema_consolidation.py -v` → PASS

```bash
git add tests/test_schema_consolidation.py
git commit -m "guard: keep curated passives and deferred CERN-only types out of Phase 0 regeneration"
```

---

## Task 20: Full rebuild + suite

- [ ] **Step 1: Full master build**

Run: `make clean && make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5`
Expected: builds `db/terra.db` with no SQL error; `make schema` drift-clean.

- [ ] **Step 2: Run the full suite**

Run: `uv run pytest tests/ -q`
Expected: all PASS (incl. `test_gen_schema.py` + `test_schema_consolidation.py`).

- [ ] **Step 3: Confirm `_v` views still build** (every part table needs `unique_id` + `tier`, both core)

Run: `sqlite3 db/terra.db "SELECT COUNT(*) FROM cern_diodes_v;"`
Expected: a count, no `no such column` error.

- [ ] **Step 4: Commit any remaining regenerated artifacts**

```bash
git add -A db/tables db/schema Makefile
git commit -m "rebuild all consolidated schemas; full suite green"
```

---

## Self-Review

- **Spec coverage (Part A):** 41-col core incl. temp + `pin_count`/`component_height`/`exclude_from_bom` (Task 1); DROP-ALL=9 via omission (Tasks 3,18); all 13 type fragments from the marks, `pin_count` removed from MCU (Tasks 3,6–17); connectors ADOPT canonical core + native tail (Task 17); cern/native equivalence + drift guard (Tasks 3,4,6–17); column-qualified-INSERT invariant for the reorder (Task 5); CERN-only + passives deferred and guarded (Task 19). Part B (Nexar resolver) is intentionally a separate, follow-on plan.
- **Placeholders:** none — every fragment's SQL and every command is concrete; the only "copy from file" step (connectors tail) names the exact source file, the exact boundary columns, and the expected column list to verify against.
- **Type consistency:** `gen_schema.py` `render()`/`main()`, `_table_cols`, `_cols`, `PAIRS`, and the `table_map.json` shape (`type/tier_default/dump_priority_default`) are used identically across tasks. Numeric columns (`channels/poles/throws/*_count` INTEGER; `supply_voltage_min/max`, `temp_*` REAL) are consistent with the marks.
