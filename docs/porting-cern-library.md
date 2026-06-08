# Porting a CERN library/table into terra — runbook

Repeatable procedure for importing one CERN table (e.g. `Diodes`, `SAMTEC`,
`Operational Amplifiers`) into terra as a `cern_<name>` table. Distilled from the
`cern_diodes` pilot. Source designs:
`docs/superpowers/specs/2026-06-06-cern-diodes-importer-design.md`,
`…/2026-06-07-symbol-footprint-hierarchy-design.md`, `…/2026-06-07-3d-models-design.md`.

Prereqs: `CERN_SQLITE=/users/dave/vsrc/cern-kicad-libs/CERN.sqlite` for any build that
regenerates a `cern_*` table. Everything is regenerable — edit schema/scripts and re-run;
no live-DB migration.

## 0. Inspect the CERN table
- Columns + fill rates; identify the **type-specific tail** (cols beyond the 28-col CERN
  core) — e.g. `Pin Count`, `Voltage`, `Power`, `TC`, `Tolerance`, `Color`, `Family`.
- **Exclude rule:** drop only true non-parts — (a) `Manufacturer ∈ (GENERIC,Undefined,'')`
  **only for passive tables** (resistors/caps); (b) a doc/graphical **denylist** everywhere
  (`%Read Me%`, `%Drill-Drawing%`, `CERN_OHL%`, `Empty`, copyright). Keep real
  mechanical/generic parts (bonding pads, epoxy, modules).
- `Manufacturer Part Number` is **NOT unique** (footprint/mounting/reel variants share an
  MPN). `Part Number Nocolon` is unique. (See [[cern-mpn-not-unique-uniqueid-strategy]].)

## 1. Table dir + schema
- `db/tables/cern_<name>/cern_<name>_0_schema.sql` = **canonical core** (as in
  `resistors_smt_0_schema.sql`, `tier INTEGER DEFAULT 5`) + adopted `pin_count`,
  `component_height` + the **type-specific tail** for this part type.
- Every table needs `unique_id` + `tier` (the `_v` views require both).

## 2. Generator `run_100_cern_import.py`
Copy the diode one as a template. Field mapping:
- `mpn`=`Manufacturer Part Number`; `manufacturer`=`Manufacturer`; `package`=`Case`;
  `value`/`description`=`Part Description`; `datasheet`=filename hint; `pin_count`,
  `component_height`; `lifecycle_status` from `Status` (`Obsolete`→Obsolete,
  `Not Recommended`/`Sourcing Difficulty`→NRND, else Active); type tail as needed.
- **`unique_id` = `"<manufacturer>-<mpn>"`**; on intra-CERN collision fall back to
  `"<manufacturer>-<Part Number Nocolon>"` (safety gate raises on residual dup).
  `part_locator` = `Part Number Nocolon`. Iterate rows sorted by Part Number Nocolon for
  deterministic output.
- **Reconciliation:** none for a new category. For passive tables overlapping existing
  terra parts, use `tools/cern_reconcile.py` (exact match on type/value/package/
  composition/tolerance).
- SQL-escape single quotes. Emit one `tags` insert per part. `source='cern_import'`,
  `dump_priority=0`.

## 3. Symbols & footprints (terra-owned hierarchy)
- Find the CERN SchLib + PcbLibs the parts reference (`LibSymbol`/`LibFootprint`).
- **Copy** each into terra with normalized names (lowercase, non-alphanumerics→`-`,
  `cern-` prefix): `SchLib/Foo.kicad_sym`→`kicad_symbols/cern-foo.kicad_sym`;
  `PcbLib/BAR.pretty`→`kicad_footprints/cern-bar.pretty`. Nickname = filename stem.
- Add the CERN→terra nickname entries to `tools/cern_libmap.py` (or generalize it); the
  generator rewrites each part's `kicad_symbol`/`kicad_footprint` to the terra nicknames.
- Do **not** translate to KiCad built-in libs. (See [[terra-symbol-footprint-hierarchy]].)

## 4. Build
`CERN_SQLITE=… make EXCLUDE_TABLES="resistors_smt resistors_th" [DEFAULT_TIER=5]`
builds `db/cern_<name>.db`, master `db/terra.db`, `terra.kicad_dbl` (absolute DB path —
KiCad won't expand vars in the dbl connection string, see
[[kicad-dbl-connection-string-needs-absolute-path]]), and the generated
`kicad_symbols/sym-lib-table` + `kicad_footprints/fp-lib-table`.

## 5. 3D models (phase 2)
- Extend `tools/model_map.py` with this part type's packages → KiCad bundled models;
  run `uv run python tools/apply_3d_models.py --table cern_<name>` (rewrites footprint
  `(model …)` refs; offsets left for human positioning). Tail (unmapped/blank) → download.

## 6. Tests + audit
- `db/tables/cern_<name>/test_cern_<name>.py`: row count, no duplicate `unique_id`,
  known-part field mapping, **all symbols AND footprints resolve** to real files, nicks in
  the generated lib-tables. Run `make cern_<name>-test` + `uv run pytest tests/ -q`.
- `AUDIT.md`: sample N parts against datasheets; record sign-off.

## 7. KiCad registration (one-time, never per-table)
Two `(type "Table")` includes (symbol + footprint) pointing at the generated lib-tables;
`make` keeps them current as libs are added. Don't hand-add libs via the GUI (nickname
typos → "footprint not found"). The `terra` database library connection string is an
absolute path to `db/terra.db`, emitted by `tools/generate_kicad_dbl_files.py`.

## Gotchas (hard-won)
- MPN not unique → disambiguate by Part Number Nocolon.
- KiCad expands path vars in lib-table URIs but **not** in the `.kicad_dbl` connection
  string → absolute DB path.
- KiCad caches libs at load + is single-instance → fully restart to re-read config.
- Every part table must have `unique_id` and `tier` or its `_v` view fails.
