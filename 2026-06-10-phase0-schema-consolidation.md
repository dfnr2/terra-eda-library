# Phase 0: Part-Type Schema Consolidation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every part type one canonical parametric column set, defined once and shared by both its CERN table (`cern_<type>`) and its terra-native table (`<type>`), so the datasheet/param harvest has a stable target schema.

**Architecture:** A part table's `_0_schema.sql` (the full `CREATE TABLE`) becomes **generated** by `tools/gen_schema.py` from two committed snippets: `db/schema/core.sql` (the 34 shared core columns) and `db/schema/types/<type>.sql` (the type-specific tail). One fragment, two includers (the CERN and native tables of that type), so their column sets are provably identical. A `make schema` target regenerates all of them; a sync test fails the build if a committed `_0_schema.sql` drifts from what the generator would emit.

**Tech Stack:** Python 3 (stdlib only), SQLite, GNU Make, pytest. Parent spec: `./2026-06-10-datasheet-param-resolver-design.md` (this is its blocking Phase 0).

**Why generation, not `.read` includes:** SQLite has no `INCLUDE`, and `.read` only runs *complete* statements — you cannot split one `CREATE TABLE` across files. So the schema files are generated from snippets instead.

**Background — the divergence this resolves (from the survey):** the native non-passive tables (`diodes`, `mosfet`, `ic_opamp`, `ic_logic`, `leds`, `switches`, `ic_analog`, `inductors`) currently carry a *legacy generic tail* migrated from the old flat `symbols` table (`class, component_type, component_value, reference, sim_type, sim_library, temp_*, tolerance`), not real parametrics — and they are near-empty scaffolds (e.g. `diodes` 9 rows, `ic_opamp` 1). Two native tables already have real schemas and are the quality bar: `bjt` (transistor parametrics) and `connectors` (38-column spec). The CERN tables carry minimal purpose-built tails and the real data volume. Canonical fragments are designed fresh from the CLAUDE.md component-type specs, using `bjt`/`connectors`/CERN tails as references, and the native legacy cruft is dropped.

---

## File Structure

- `db/schema/core.sql` — **Create.** The 34 core column definitions, verbatim from the current `cern_diodes` core block, as a reusable snippet (column lines only, no `CREATE TABLE` wrapper). Single source of truth for the core.
- `db/schema/types/<type>.sql` — **Create (one per type).** The canonical parametric tail for that type (column lines only). Types: `diodes`, `transistors`, `op_amps`, `logic`, `leds`, `switches`, `inductors`, `analog`, `connectors`.
- `db/schema/table_map.json` — **Create.** Maps each generated table → `{type, tier_default, dump_priority_default}`. Drives which tables share which fragment.
- `tools/gen_schema.py` — **Create.** Reads core + fragment + table_map, emits each table's `db/tables/<table>/<table>_0_schema.sql`.
- `tests/test_gen_schema.py` — **Create.** Unit tests for the generator.
- `tests/test_schema_consolidation.py` — **Create.** Invariant tests: cern/native column-set equality per type, and committed-schema-in-sync guard.
- `db/tables/<table>/<table>_0_schema.sql` — **Modify (regenerated)** for every consolidated table.
- `Makefile` — **Modify.** Add a `schema` target and make it a prerequisite of the table builds.

---

## Task 1: Extract the shared core snippet

**Files:**
- Create: `db/schema/core.sql`
- Test: `tests/test_schema_consolidation.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_schema_consolidation.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_core_snippet_has_34_columns():
    core = (ROOT / "db/schema/core.sql").read_text()
    # one column definition per non-comment, non-blank line
    lines = [l for l in core.splitlines() if l.strip() and not l.strip().startswith("--")]
    assert len(lines) == 34, f"expected 34 core columns, got {len(lines)}"
    # spot-check anchors
    assert any(l.strip().startswith("unique_id TEXT PRIMARY KEY") for l in lines)
    assert any(l.strip().startswith("tier INTEGER") for l in lines)
    assert any(l.strip().startswith("sim_params TEXT") for l in lines)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_schema_consolidation.py::test_core_snippet_has_34_columns -v`
Expected: FAIL (file does not exist).

- [ ] **Step 3: Create `db/schema/core.sql`**

Copy the 34 core column lines exactly from `db/tables/cern_diodes/cern_diodes_0_schema.sql` (the block from `unique_id TEXT PRIMARY KEY,` through `sim_params TEXT`). `tier` and `dump_priority` keep placeholder defaults that the generator overrides per table (see Task 2):

```sql
-- db/schema/core.sql
-- The 34 shared core columns for every part table. Column definitions only —
-- gen_schema.py wraps these in CREATE TABLE and appends the type fragment.
-- tier/dump_priority DEFAULTs here are placeholders; gen_schema.py rewrites them per table_map.json.
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
    sim_params TEXT
```

Note: no trailing comma after `sim_params TEXT` — the generator inserts the comma before the type fragment.

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_schema_consolidation.py::test_core_snippet_has_34_columns -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add db/schema/core.sql tests/test_schema_consolidation.py
git commit -m "extract shared 34-column core schema snippet"
```

---

## Task 2: The schema generator

**Files:**
- Create: `tools/gen_schema.py`, `db/schema/table_map.json`
- Test: `tests/test_gen_schema.py`

- [ ] **Step 1: Write `db/schema/table_map.json`** (start with the diodes pair; later tasks extend it)

```json
{
  "cern_diodes": { "type": "diodes", "tier_default": 5, "dump_priority_default": 0 },
  "diodes":      { "type": "diodes", "tier_default": 2, "dump_priority_default": 1 }
}
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_gen_schema.py
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run([sys.executable, str(ROOT/"tools/gen_schema.py"), *args],
                          capture_output=True, text=True, cwd=ROOT)

def test_emits_create_table_with_core_and_fragment(tmp_path):
    # diodes fragment must exist for this test (created in Task 3); here we assert the wrapper shape
    out = run("--print", "cern_diodes").stdout
    assert out.startswith("CREATE TABLE cern_diodes (")
    assert "unique_id TEXT PRIMARY KEY" in out
    assert "diode_type TEXT" in out          # from the type fragment
    assert "tier INTEGER DEFAULT 5" in out   # cern default from table_map
    assert out.rstrip().endswith(");")

def test_native_gets_same_columns_different_defaults():
    cern = run("--print", "cern_diodes").stdout
    native = run("--print", "diodes").stdout
    def cols(sql):
        body = sql[sql.index("(")+1: sql.rindex(")")]
        return [c.strip().split()[0] for c in body.split(",\n") if c.strip() and not c.strip().startswith("--")]
    assert cols(cern) == cols(native)        # identical column set + order
    assert "tier INTEGER DEFAULT 2" in native  # native default differs
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/test_gen_schema.py -v`
Expected: FAIL (generator + diodes fragment missing).

- [ ] **Step 4: Write `tools/gen_schema.py`**

```python
#!/usr/bin/env python3
"""Generate each part table's _0_schema.sql from the shared core + per-type fragment.

Reads db/schema/core.sql, db/schema/types/<type>.sql, and db/schema/table_map.json.
Emits CREATE TABLE <table> ( <core> , <type-fragment> ); to
db/tables/<table>/<table>_0_schema.sql (or stdout with --print).
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
    core = _lines(CORE.read_text())
    # apply per-table tier / dump_priority defaults
    out = []
    for l in core:
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
    targets = args or list(table_map)
    for table in targets:
        cfg = table_map[table]
        dest = ROOT / f"db/tables/{table}/{table}_0_schema.sql"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(table, cfg))
        print(f"  wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run the diodes-fragment dependency forward** — these tests need `db/schema/types/diodes.sql`, created next in Task 3. Mark Task 2 tests `xfail` is NOT allowed; instead, do Task 3 Step 1 (create the fragment) now, then run:

Run: `uv run pytest tests/test_gen_schema.py -v`
Expected: PASS (after the diodes fragment from Task 3 exists).

- [ ] **Step 6: Commit**

```bash
git add tools/gen_schema.py db/schema/table_map.json tests/test_gen_schema.py db/schema/types/diodes.sql
git commit -m "add gen_schema.py: generate _0_schema.sql from core + type fragment"
```

---

## Task 3: Diodes pilot — fragment, regenerate both tables, prove equivalence

**Files:**
- Create: `db/schema/types/diodes.sql`
- Modify (regenerate): `db/tables/cern_diodes/cern_diodes_0_schema.sql`, `db/tables/diodes/diodes_0_schema.sql`
- Test: `tests/test_schema_consolidation.py`

Canonical diodes tail (from CLAUDE.md "diodes - Type, Vf, If, Vr" + CERN-populated `diode_type/voltage_rating/power_rating`):

- [ ] **Step 1: Create `db/schema/types/diodes.sql`**

```sql
-- db/schema/types/diodes.sql
-- Canonical parametric tail for diodes (cern_diodes + diodes).
    diode_type TEXT,          -- rectifier | schottky | zener | tvs | small-signal | ...
    voltage_rating TEXT,      -- Vr (reverse standoff / working)
    forward_voltage TEXT,     -- Vf
    forward_current TEXT,     -- If
    power_rating TEXT,        -- Pd where applicable (TVS/zener)
    current_rating TEXT       -- Io (rectifiers)
```

- [ ] **Step 2: Write the equivalence test**

```python
# add to tests/test_schema_consolidation.py
import sqlite3, json, subprocess, sys

def _table_cols(schema_sql_path):
    con = sqlite3.connect(":memory:")
    con.executescript(schema_sql_path.read_text())
    name = schema_sql_path.parent.name
    return [r[1] for r in con.execute(f'PRAGMA table_info("{name}")')]

def test_diodes_cern_and_native_have_identical_columns():
    cern = _table_cols(ROOT/"db/tables/cern_diodes/cern_diodes_0_schema.sql")
    native = _table_cols(ROOT/"db/tables/diodes/diodes_0_schema.sql")
    assert cern == native, f"diodes schema mismatch:\n cern={cern}\n native={native}"
    assert "diode_type" in cern and "forward_voltage" in cern
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/test_schema_consolidation.py::test_diodes_cern_and_native_have_identical_columns -v`
Expected: FAIL (native `diodes` still has the legacy tail; schemas not yet regenerated).

- [ ] **Step 4: Regenerate both diodes schemas**

Run: `uv run python tools/gen_schema.py cern_diodes diodes`
Expected output: `wrote db/tables/cern_diodes/cern_diodes_0_schema.sql` and `... diodes ...`.

- [ ] **Step 5: Run the equivalence + generator tests**

Run: `uv run pytest tests/test_schema_consolidation.py tests/test_gen_schema.py -v`
Expected: PASS.

- [ ] **Step 6: Rebuild diodes DBs and confirm they load**

Run: `make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5 cern_diodes-build diodes-build`
Expected: both build with no SQL error. Then:
Run: `sqlite3 db/cern_diodes.db "SELECT diode_type, forward_voltage FROM cern_diodes LIMIT 1;"`
Expected: a row (columns exist; harvested values may be empty for now).

- [ ] **Step 7: Run the CERN diodes table test (catch regressions)**

Run: `make cern_diodes-test`
Expected: PASS. If it asserts on a dropped legacy column, update that test to the canonical column (note the change in the commit).

- [ ] **Step 8: Commit**

```bash
git add db/schema/types/diodes.sql db/tables/cern_diodes/cern_diodes_0_schema.sql \
        db/tables/diodes/diodes_0_schema.sql tests/test_schema_consolidation.py
git commit -m "consolidate diodes schema: one canonical tail for cern_diodes + diodes"
```

---

## Task 4: Build wiring + drift guard

Make schema generation a build step and fail the build if a committed `_0_schema.sql` is stale.

**Files:**
- Modify: `Makefile`
- Test: `tests/test_schema_consolidation.py`

- [ ] **Step 1: Write the drift-guard test**

```python
# add to tests/test_schema_consolidation.py
def test_committed_schemas_match_generator():
    table_map = json.loads((ROOT/"db/schema/table_map.json").read_text())
    for table in table_map:
        gen = subprocess.run([sys.executable, str(ROOT/"tools/gen_schema.py"),
                              "--print", table], capture_output=True, text=True, cwd=ROOT).stdout
        on_disk = (ROOT/f"db/tables/{table}/{table}_0_schema.sql").read_text()
        assert gen == on_disk, f"{table}_0_schema.sql is stale — run `make schema`"
```

- [ ] **Step 2: Run it**

Run: `uv run pytest tests/test_schema_consolidation.py::test_committed_schemas_match_generator -v`
Expected: PASS (diodes already regenerated; only diodes in table_map so far).

- [ ] **Step 3: Add the `schema` target to the Makefile**

Insert near the other `.PHONY` targets:

```makefile
.PHONY: schema
schema: $(VENV_MARKER)
	@echo "Regenerating part-table schemas from db/schema/ ..."
	@$(PYTHON) tools/gen_schema.py
```

- [ ] **Step 4: Verify the target runs and is idempotent**

Run: `make schema && git diff --stat db/tables/*/*_0_schema.sql`
Expected: no diff (already in sync).

- [ ] **Step 5: Commit**

```bash
git add Makefile tests/test_schema_consolidation.py
git commit -m "add make schema target + drift guard for generated table schemas"
```

---

## Tasks 5–12: Per-type fragments

Each task follows the **identical shape** as Task 3 (create fragment → add the table pair(s) to `table_map.json` → `gen_schema.py` → equivalence test → rebuild → table test → commit). The per-type column lists below are the concrete fragments; defaults in `table_map.json` are `tier_default: 5, dump_priority_default: 0` for `cern_*` rows and `tier_default: 2, dump_priority_default: 1` for native rows (matching diodes).

For each task, the steps are:
1. Create `db/schema/types/<type>.sql` with the columns shown.
2. Add the type's table rows to `db/schema/table_map.json`.
3. `uv run python tools/gen_schema.py <tables…>`.
4. `uv run pytest tests/test_schema_consolidation.py -v` (the parametrized equivalence + drift tests cover the new pair).
5. `make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5 <table>-build` for each table; then `make <cern_table>-test`.
6. Commit `git commit -m "consolidate <type> schema"`.

Add this parametrized equivalence test once (replaces the single diodes assertion as the type list grows):

```python
# tests/test_schema_consolidation.py
import pytest
PAIRS = {  # type -> (native tables, cern tables)
    "diodes": (["diodes"], ["cern_diodes"]),
    "transistors": (["bjt", "mosfet"], ["cern_transistors"]),
    "op_amps": (["ic_opamp"], ["cern_op_amps"]),
    "logic": (["ic_logic"], ["cern_logic", "cern_standard_logic"]),
    "leds": (["leds"], ["cern_leds_displays"]),
    "switches": (["switches"], ["cern_switches"]),
    "inductors": (["inductors"], []),
    "analog": (["ic_analog"], ["cern_analog_interface"]),
    "connectors": (["connectors"], ["cern_molex", "cern_samtec"]),  # all connector vendors share
}

@pytest.mark.parametrize("type_,pair", PAIRS.items())
def test_type_tables_share_columns(type_, pair):
    natives, cerns = pair
    tables = natives + cerns
    colsets = {t: _table_cols(ROOT/f"db/tables/{t}/{t}_0_schema.sql") for t in tables if (ROOT/f"db/tables/{t}/{t}_0_schema.sql").exists()}
    ref = None
    for t, cols in colsets.items():
        if ref is None: ref = cols
        assert cols == ref, f"{t} diverges for type {type_}"
```

### Task 5 — `transistors` (bjt, mosfet, cern_transistors)

Use `bjt`'s existing real schema as the bar; unify BJT + MOSFET into one transistor tail.

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
    transition_freq TEXT,
    temp_junction_max TEXT
```

Note in the commit: `bjt`'s richer columns (`vcb_max, veb_max, ib_max, hfe_min/max`) are intentionally dropped to the unified set; if you want to keep them, add to this fragment and regenerate — but keep cern/native identical.

### Task 6 — `op_amps` (ic_opamp, cern_op_amps)

```sql
-- db/schema/types/op_amps.sql
    amplifier_type TEXT,      -- voltage-fb | current-fb | instrumentation | ...
    channels INTEGER,
    gain_bandwidth TEXT,      -- GBW
    slew_rate TEXT,
    input_offset TEXT,
    supply_voltage TEXT,
    input_noise TEXT
```

### Task 7 — `logic` (ic_logic, cern_logic, cern_standard_logic)

```sql
-- db/schema/types/logic.sql
    logic_family TEXT,        -- 74HC | 74LVC | 4000 | ...
    gate_function TEXT,       -- and | or | nand | mux | ff | buffer | ...
    channels INTEGER,
    propagation_delay TEXT,
    supply_voltage TEXT
```

### Task 8 — `leds` (leds, cern_leds_displays)

Use the existing `cern_leds_displays` tail as the bar (it is already real), add `viewing_angle`:

```sql
-- db/schema/types/leds.sql
    color TEXT,
    wavelength_nm TEXT,
    forward_voltage_v TEXT,
    current_max_ma TEXT,
    luminous_intensity TEXT,
    viewing_angle TEXT
```

### Task 9 — `switches` (switches, cern_switches)

```sql
-- db/schema/types/switches.sql
    switch_type TEXT,         -- tactile | toggle | dip | rotary | slide | pushbutton | ...
    poles INTEGER,
    throws INTEGER,
    current_rating TEXT,
    voltage_rating TEXT,
    actuation_force TEXT
```

### Task 10 — `inductors` (inductors only; no CERN inductor table ported yet)

```sql
-- db/schema/types/inductors.sql
    inductance TEXT,
    tolerance TEXT,
    current_rating TEXT,      -- rated
    saturation_current TEXT,
    dcr TEXT,                 -- DC resistance
    srf TEXT                  -- self-resonant frequency
```

### Task 11 — `analog` (ic_analog, cern_analog_interface)

CERN analog-interface is a grab-bag; keep the tail minimal and function-oriented:

```sql
-- db/schema/types/analog.sql
    function_type TEXT,       -- adc | dac | comparator | mux | vref | interface | ...
    channels INTEGER,
    resolution_bits TEXT,
    interface TEXT,           -- spi | i2c | parallel | ...
    supply_voltage TEXT
```

### Task 12 — `connectors` (connectors + all `cern_<vendor>` tables)

The native `connectors` 38-column schema is already the canonical bar. The fragment is that exact column set (everything in `connectors` beyond the 34 core, **minus** `exclude_from_bom` which is core). Add **every** ported CERN connector vendor to `table_map.json` under `type: connectors`: `cern_molex, cern_samtec, cern_tyco, cern_3m, cern_amphenol, cern_erni, cern_fci, cern_harting, cern_harwin, cern_lemo, cern_mentor, cern_phoenix, cern_souriau, cern_stelvio_kontek_comatel, cern_weidmuller, cern_sockets`.

- [ ] **Step 1:** Extract the connector tail into `db/schema/types/connectors.sql` by copying the type-specific columns from `db/tables/connectors/connectors_0_schema.sql` (the 38 columns from `connector_category` through `mating_part_hint`).
- [ ] **Step 2–6:** Same shape as Task 3, but regenerate `connectors` + all 16 `cern_*` connector tables. After regeneration, the CERN vendor tables gain 38 (currently-empty) parametric columns — verify a sample still builds and its existing row count is unchanged.

```bash
make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5 cern_molex-build
sqlite3 db/cern_molex.db "SELECT COUNT(*) FROM cern_molex;"   # unchanged (503)
```

---

## Task 13: Passive-table safety (resistors_smt, capacitors_smt are heavily populated)

These native tables hold real data (resistors_smt 22,539; capacitors_smt 4,863) and are **not** part of the cern pairing above. Do NOT regenerate them through `gen_schema.py` unless a `resistors`/`capacitors` fragment is defined that is a **superset** of their current columns. This task only *verifies* they are untouched by Phase 0.

**Files:** Test only: `tests/test_schema_consolidation.py`

- [ ] **Step 1: Add a guard test**

```python
def test_passive_tables_not_in_table_map():
    table_map = json.loads((ROOT/"db/schema/table_map.json").read_text())
    for t in ("resistors_smt", "resistors_th", "capacitors_smt", "capacitors_th"):
        assert t not in table_map, f"{t} populated/curated — out of Phase 0 scope, do not regenerate"
```

- [ ] **Step 2: Run + commit**

Run: `uv run pytest tests/test_schema_consolidation.py::test_passive_tables_not_in_table_map -v` → PASS

```bash
git add tests/test_schema_consolidation.py
git commit -m "guard: keep populated passive tables out of Phase 0 schema regeneration"
```

---

## Task 14: Drop native legacy-cruft columns from regenerated tables

The regenerated native non-passive schemas (diodes, mosfet, ic_opamp, ic_logic, leds, switches, ic_analog, inductors) **no longer contain** the legacy columns (`class, component_type, component_value, reference, sim_type, sim_library, temp_*, tolerance`) because the canonical fragments omit them. Since these tables are near-empty scaffolds, confirm no real data is lost.

**Files:** Test only.

- [ ] **Step 1: Verify data loss is zero for dropped columns**

Run, for each native table, that every dropped column is empty across all rows before regeneration. Use the pre-Phase-0 per-table DB (rebuild from git stash if needed) OR assert row counts are trivially small and inspect:

```bash
for t in diodes mosfet ic_opamp ic_logic leds switches ic_analog inductors; do
  echo "== $t =="
  sqlite3 db/$t.db "SELECT COUNT(*) FROM $t;"
done
```

Expected: single-digit/low counts. For any table with >0 rows, confirm the dropped legacy columns held no unique information (their real data lives in core `value`/`description`/`package`). Document findings in the commit message.

- [ ] **Step 2: Commit (if any schema/data adjustments were needed)**

```bash
git commit -am "confirm no data loss dropping legacy generic columns from native part tables"
```

---

## Task 15: Full rebuild + suite + spec invariant note

- [ ] **Step 1: Full master build**

Run: `make clean && make EXCLUDE_TABLES="resistors_smt resistors_th" DEFAULT_TIER=5`
Expected: builds `db/terra.db` with no SQL error; `make schema` drift guard clean.

- [ ] **Step 2: Run the full suite**

Run: `uv run pytest tests/ -q`
Expected: all PASS (including the new `test_gen_schema.py` and `test_schema_consolidation.py`).

- [ ] **Step 3: Confirm the `_v` views still build** (every part table needs `unique_id` + `tier`, both in core)

Run: `sqlite3 db/terra.db "SELECT COUNT(*) FROM cern_diodes_v;"`
Expected: a count, no `no such column` error.

- [ ] **Step 4: Commit any remaining regenerated artifacts**

```bash
git add -A db/tables db/schema
git commit -m "rebuild all consolidated schemas; full suite green"
```

---

## Self-Review

- **Spec coverage:** This plan implements the spec's Phase 0 §"part-type schema consolidation": one shared fragment per type, included by both CERN and native tables, with the column set as the contract for the harvest allowlist. The generator + drift guard make "one fragment, two includers" enforceable, replacing the spec's hand-waved `cat`/`.read` note (which SQLite can't do for partial statements) with a concrete generation mechanism.
- **Downstream contract:** the harvest allowlist (`CORE_HARVEST_COLUMNS` + type-fragment columns) in the resolver spec now has concrete fragment files (`db/schema/types/*.sql`) to read its type-fragment column set from.
- **Out of scope (correct):** populated passive tables (resistors/capacitors) — guarded out in Task 13; a future plan defines their fragments as supersets. CERN-only types with no native counterpart (regulators, optocouplers, dc-dc, crystals, relays, fuses, sensors, transformers, power supplies, thermistors, batteries) keep their existing tails as canonical and can be folded into `table_map.json` later with `type` = themselves; not required for the harvest gate.
- **Open confirmations for the executor/user:** the per-type canonical column lists (Tasks 5–12) are designed from CLAUDE.md type specs + existing `bjt`/`connectors`/CERN tails; they are the one place a human should sanity-check before mass regeneration, since they define the library's parametric data model.
