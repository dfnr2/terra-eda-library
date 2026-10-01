---
name: add-terra-table
description: >-
  How to add parts to the terra library: either a new part family to an existing
  table, or a whole new component table (new type fragment, table_map entry,
  generator). Use for requests like "add the <series> to terra", "add a table for
  <component type>", "generate <manufacturer> <family> parts", "we need a
  capacitors_th / diodes_tvs style table for X", or when promoting parts from
  plans/cern-harvest-worklist.csv or a terra_convert gap report into native tables.
---

# Adding parts and tables to terra

Terra holds **fully-qualified, orderable parts**: a real MPN, its datasheet, the
right symbol and footprint, and a parametric tail filled from the datasheet. Every
row comes from a generator script. Nothing is hand-edited into SQL or into
`terra.db`, which is read-only after the build.

Most work adds a **family** to an existing table. A **new table** is only needed
when no existing type's columns fit the part.

Reference implementations, newest first. Read the one closest to your job:

| Table | Shows |
|---|---|
| `capacitors_th` (`run_300_tdk_fg.py`, `fg_catalog.json`, `plans/capacitors-th-tdk-fg.md`) | new table on an existing type; catalog transcribed to JSON; MPN-encoding validation; footprint mapping by body size |
| `voltage_reference` (`run_300_adi_references.py`) | BASE specs × package VARIANTS; parts with no usable symbol flagged REVIEW |
| `diodes_tvs` (`_tvs.py`, `run_300_littelfuse_smf.py`, `db/schema/types/tvs.sql`) | new type fragment; shared `insert`/`write` helper across several generators |
| `diodes_zener` (`_zener_family.py`, `run_32x_*.py`) | one helper, one small script per family |
| `resistors_th` (`run_200_yageo_mfr_metal_film.py`) | series-matrix generator with a config block |

## 1. Scope it

Settle these with Dave before writing code, and record them in a short
`plans/<table>-<family>.md` (see `plans/capacitors-th-tdk-fg.md`):

- **Which parts.** Take only what the datasheet lists; never invent combinations.
  Skip parts marked "not recommended for new designs". Put option axes (dielectrics,
  packaging, grades) behind a config toggle with sensible defaults.
- **Which table.** Look for an existing table first (`db/schema/table_map.json`).
- **The datasheet.** Park the PDF in `datasheets/<mfr>/<slug>.pdf` (Git LFS) before
  anything else. Rows reference it as `${TERRA_EDA_LIB}/datasheets/<mfr>/<slug>.pdf`,
  never as a web URL.

## 2. Columns (new type only)

A table's schema is the 41 shared columns in `db/schema/core.sql` plus one type
fragment in `db/schema/types/<type>.sql`. Never hand-edit a `_0_schema.sql`: it is
generated, and a drift test enforces that.

Before writing a fragment, **review the proposed columns with Dave**. List each
column with its SQL type and a one-line reason, next to what similar fragments
already use. Reuse existing names and units wherever the meaning matches
(`voltage_rating`, `channels`, `pin_count`, …). Fold anything every part has into
core rather than the tail. Keep the tail to what a designer filters or compares on;
the datasheet covers the rest.

Then register the table in `db/schema/table_map.json`:

```json
"capacitors_th": { "type": "capacitors", "tier_default": 2,
                   "dump_priority_default": 1, "sim_device": "C", "sim_pins": "1=+ 2=-" }
```

Native tables use tier 2. Set `sim_device`/`sim_pins` only for parts the built-in
SPICE models cover (R, C, L, D). Run `make schema` to write
`db/tables/<table>/<table>_0_schema.sql`.

A new table also needs:

- An entry in `PAIRS` in `tests/test_schema_consolidation.py`; if it's a passive,
  in `test_passive_tables_folded_onto_canonical_core` too.
- Optionally, a chooser label in `CATEGORY_DISPLAY_NAMES` in
  `tools/generate_kicad_dbl_files.py` if the table name reads poorly.

## 3. The generator

One `db/tables/<table>/run_NNN_<family>.py` per family. The number sets the
build order and leaves gaps for later families. It writes
`<table>_generated_NNN_<family>.sql`, which is gitignored.

- **Data first.** Transcribe the datasheet's tables into the script (a list of
  tuples) or, for large catalogs, a JSON file beside it. Keep a clear config block at
  the top.
- **Generated rows** set `source = NULL`, `dump_priority = 0`, `tier = 2`.
- **INSERTs name their columns** (`INSERT INTO t (cols…) VALUES …`). Positional
  INSERTs fail a test.
- **Identity:** `unique_id = "<Manufacturer>-<MPN>"`, made unique; fail loudly on a
  duplicate rather than dropping rows. `part_locator` is a lowercase functional
  descriptor (`tvs-5.0v-uni-sod123f`) and need not be unique.
- **`value`** is what belongs on the schematic. For capacitors it is capacitance
  only; voltage shows only for electrolytic/tantalum.
- **`keywords`**: comma-separated search terms; they become KiCad's Keywords.
- **Validate as you generate.** Where the MPN encodes parameters, decode it and
  check it against the row (capacitors_th found 0 mismatches this way).
- **When a family's generators share code**, put it in a `_<name>.py` helper in the
  table directory, as `_tvs.py` does.

## 4. Symbols and footprints

- **Prefer stock KiCad** (`Device:C`, `Diode_SMD:D_SOD-123F`, `Package_SO:…`) when
  the pinout and land pattern really match.
- **Custom symbols** go in `kicad_symbols/terra_symbols_<table>.kicad_sym`, and custom
  footprints in `kicad_footprints/terra_footprints_<table>.pretty`. Rows reference
  them as `terra_symbols_<table>:<Name>`. Both are registered automatically (nickname
  = file stem). Never use the catch-all `terra_sym`.
- **No symbol you trust?** Leave `kicad_symbol` NULL, put `REVIEW: …` in the
  description, and have the generator print those rows. Never borrow a symbol with a
  different pinout.
- **Approximate footprint?** Say so in the generator and plan, and keep the mapping
  in one table (`TYPE_GEOM`) so exact footprints can drop in later.
- KiCad 10 stacked-pin syntax `(number "[1,3,7,8]")` is valid; don't "fix" it.

## 5. Build and check

```
make schema                   # new type/table only
make <table>-generate && make <table>-build
make && make verify           # full rebuild + round-trip + tests
```

Spot-check a handful of rows against the datasheet: MPN, value, the key tail fields
and the footprint. Then record counts and any follow-ups in the plan's Results
section.

**Gotcha:** generated SQL rebuilds when a table's `run_*.py` or `*.json` changes, but
**not** when a `_helper.py` module changes. After editing a helper, run
`make <table>-clean` first.

## 6. Commit

Commit the datasheet, catalog, generator, helper, fragment, `table_map.json`,
regenerated `_0_schema.sql`, symbols/footprints, tests and plan together as one
change, described by what it adds (e.g. "add capacitors_th table with the TDK FG
leaded-MLCC series").
