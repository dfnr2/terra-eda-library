---
name: port-cern-library
description: >-
  Repeatable procedure for porting a CERN KiCad library/table into the terra-eda-library
  (this repo). Use this whenever importing a CERN component table into terra — creating a
  new cern_<table> table, writing its schema + import generator, copying CERN symbols/
  footprints into terra's hierarchy, mapping 3D models, and wiring up tests. Trigger on
  requests like "import the CERN <X> table", "port cern_samtec / cern_diodes / connectors",
  "add the CERN op-amps to terra", "scale out the CERN import", or any work under
  db/tables/cern_* . Use it even if the user just names a CERN table without saying "port".
---

# Porting a CERN library/table into terra

Import one CERN table (e.g. `Diodes`, `SAMTEC`, `Operational Amplifiers`) into terra as a
`cern_<name>` table. Distilled from the `cern_diodes` pilot. Background designs:
`docs/superpowers/specs/2026-06-06-cern-diodes-importer-design.md`,
`…/2026-06-07-symbol-footprint-hierarchy-design.md`, `…/2026-06-07-3d-models-design.md`.

**Everything is regenerable** — edit schema/scripts and re-run; no live-DB migration. Set
`CERN_SQLITE=/users/dave/vsrc/cern-kicad-libs/CERN.sqlite` for any build that regenerates a
`cern_*` table. Source DB: `CERN.sqlite`. Existing scaffolding to reuse:
`tools/cern_source.py` (read CERN.sqlite), `tools/cern_libmap.py` (nickname map),
`tools/cern_reconcile.py`, `tools/generate_lib_tables.py`, `tools/model_map.py`,
`tools/apply_3d_models.py`, and `db/tables/cern_diodes/` as the worked example.

## 0. Inspect the CERN table
- List columns + fill rates; identify the **type-specific tail** (columns beyond CERN's
  28-col core) — e.g. `Pin Count`, `Voltage`, `Power`, `TC`, `Tolerance`, `Color`, `Family`.
- **Exclude rule** — drop only true non-parts: (a) `Manufacturer ∈ (GENERIC,Undefined,'')`
  **only for passive tables** (resistors/caps); (b) a doc/graphical **denylist** everywhere
  (`%Read Me%`, `%Drill-Drawing%`, `CERN_OHL%`, `Empty`, copyright). Keep real
  mechanical/generic parts (bonding pads, epoxy, PCB modules).
- Note: `Manufacturer Part Number` is **NOT unique** — footprint/mounting/reel variants
  share one MPN. `Part Number Nocolon` is unique (1:1 with rows).

## 1. Table dir + schema
`db/tables/cern_<name>/cern_<name>_0_schema.sql` = the **canonical core** (as in
`resistors_smt_0_schema.sql`, with `tier INTEGER DEFAULT 5`) + the adopted `pin_count` and
`component_height` + the **type-specific tail** for this part type. Every part table must
have `unique_id` and `tier` — the build's `_v` filtered views require both.

## 2. Generator `run_100_cern_import.py`
Copy the diode generator as a template. Field mapping:
- `mpn`=`Manufacturer Part Number`; `manufacturer`=`Manufacturer`; `package`=`Case`;
  `value`/`description`=`Part Description`; `datasheet`=filename hint; `pin_count`,
  `component_height`; `lifecycle_status` from `Status`
  (`Obsolete`→Obsolete, `Not Recommended`/`Sourcing Difficulty`→NRND, else Active); plus
  the type tail.
- **`unique_id` = `"<manufacturer>-<mpn>"`**; on intra-CERN MPN collision, fall back to
  `"<manufacturer>-<Part Number Nocolon>"` (a safety gate must raise on any residual dup so
  variants are never silently dropped). `part_locator` = `Part Number Nocolon`. Iterate rows
  sorted by Part Number Nocolon for deterministic output.
- **Reconciliation:** none for a new category. For passive tables overlapping existing terra
  parts, use `tools/cern_reconcile.py` (exact match on type/value/package/composition/
  tolerance — never fuzzy).
- Escape single quotes in SQL. Emit one `tags` insert per part. `source='cern_import'`,
  `dump_priority=0`.

## 3. Symbols & footprints (terra-owned hierarchy)
terra owns its libs under `kicad_symbols/` (`.kicad_sym`) and `kicad_footprints/`
(`.pretty`); parts reference terra nicknames, never KiCad's built-in `Device:`/`Diode_SMD:`.
- Find the CERN SchLib + PcbLibs the parts reference (`LibSymbol`/`LibFootprint`).
- **Copy** each into terra with a normalized name (lowercase, non-alphanumerics→`-`,
  `cern-` prefix; nickname = filename stem): `SchLib/Foo.kicad_sym` →
  `kicad_symbols/cern-foo.kicad_sym`; `PcbLib/BAR.pretty` → `kicad_footprints/cern-bar.pretty`.
- Add the CERN→terra nickname entries to `tools/cern_libmap.py`; the generator rewrites each
  part's `kicad_symbol`/`kicad_footprint` to the terra nicknames.

## 4. Build
`CERN_SQLITE=… make EXCLUDE_TABLES="resistors_smt resistors_th" [DEFAULT_TIER=5]` builds
`db/cern_<name>.db`, master `db/terra.db`, `terra.kicad_dbl` (absolute DB path — KiCad does
NOT expand path vars in the dbl connection string), and the generated
`kicad_symbols/sym-lib-table` + `kicad_footprints/fp-lib-table`. (`DEFAULT_TIER=5` so tier-5
catalog parts are visible.)

## 5. 3D models
Extend `tools/model_map.py` with this part type's packages → KiCad bundled models, then
`uv run python tools/apply_3d_models.py --table cern_<name>` (rewrites footprint `(model …)`
refs; offsets left for human positioning). Unmapped/blank packages → download tail + human.

## 6. Tests + audit
`db/tables/cern_<name>/test_cern_<name>.py`: row count; no duplicate `unique_id`; known-part
field mapping; **every symbol AND footprint resolves** to a real file; nicknames present in
the generated lib-tables. Run `make cern_<name>-test` and `uv run pytest tests/ -q`. Add an
`AUDIT.md` (sample N parts vs datasheets, sign-off).

## 7. KiCad registration (one-time, never per-table)
Two `(type "Table")` includes — one symbol, one footprint — pointing at the generated
lib-tables; `make` keeps them current as libs are added. Do NOT hand-add libs via the KiCad
GUI (nickname typos → "footprint not found"). The `terra` database library's connection
string is an absolute path to `db/terra.db`, emitted by `tools/generate_kicad_dbl_files.py`.

## Gotchas (hard-won)
- `Manufacturer Part Number` is not unique → disambiguate `unique_id` by Part Number Nocolon.
- KiCad expands path vars in lib-table URIs but NOT in the `.kicad_dbl` connection string →
  use an absolute DB path. To debug "[SQLite]connect failed", test the exact string with
  `isql -k "DRIVER=…;Database=<abs>;"` — if isql connects but KiCad doesn't, a var is unexpanded.
- KiCad caches libraries at load and is single-instance → fully quit + relaunch to re-read
  config; a second launch while one runs just hands off (no log output).
- Every part table needs `unique_id` and `tier`, or its `_v` view fails
  (`no such column: p.tier` / `p.unique_id`).
- Pass `EXCLUDE_TABLES`/`DEFAULT_TIER`/`CERN_SQLITE` on EVERY `make` (incl. `project-db`) —
  make rebuilds prerequisites, so omitting them silently re-includes resistors / wrong tier.
