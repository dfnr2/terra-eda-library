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
All mapping rules live in `tools/model_map.py` (codified once, never re-derived). Add this
part type's packages there, then `uv run python tools/apply_3d_models.py --table cern_<name>`
(rewrites footprint `(model …)` refs; offsets left for human positioning). The resolver has
three strategies, tried in order — extend whichever fits the package:
- **Exact SMD** (`SMD_PACKAGE_MODEL`): one package string → one model file (SMD has one
  canonical model per package).
- **THT axial families** (`THT_AXIAL_FAMILY`): KiCad parameterizes axial models by lead
  pitch+orientation, so a package alone is not enough. `apply_3d_models` *measures* the
  footprint's pad pitch and the resolver picks the nearest horizontal model within
  `AXIAL_PITCH_TOL_MM` (1.5mm) — declining when no shipped geometry fits (e.g. DO-201AD at
  20.32mm), rather than mis-mapping.
- **THT TO families** (`TO_FAMILY`): orientation (-v/-h/FLIP) and lead count live in the
  *footprint name*, not the package; `apply_3d_models` parses them (`fp_orientation`,
  `fp_leads`) and the resolver builds `<family>-<leads>_<orientation>.step`, verifying it
  exists (KiCad ships only Vertical TO-247, so horizontal TO-247 declines).

- **Bridges + blank-package bodies** (`resolve_from_footprint`, `BRIDGE_BODY`,
  `SMD_BODY_DIRECT`): CERN often leaves `package` blank but encodes the body in the
  *footprint name* (`FAIRCHILD_GBU_V`, `SODFL3516X80N`, `DIOMELF1911N`, `DO-201`).
  `apply_3d_models` falls back to `resolve_from_footprint`, which maps bridge codes →
  `Diode_Bridge_*`, SMD body codes (SODFL→SOD-123F/128, DIOMELF→MELF family by size,
  PowerDI/PowerMite), then any known package key embedded in the name.

When one footprint's parts carry conflicting package labels (CERN data quirk), the label
backing the most parts wins. Record deliberate non-mappings in `SKIP_REASON` with the reason
so the gaps are documented, not mysterious. Lock new rules with a case in
`tests/test_model_map.py`. Don't build a per-MPN web downloader — KiCad ships models for
almost every body; extend the codified map instead. The genuine residual (power modules,
exotic SMD, orientations KiCad lacks) goes to a human drop-folder under `kicad_3dmodels/`.

## 6. Tests + audit
`db/tables/cern_<name>/test_cern_<name>.py`: row count; no duplicate `unique_id`; known-part
field mapping; **every symbol AND footprint resolves** to a real file; nicknames present in
the generated lib-tables. Run `make cern_<name>-test` and `uv run pytest tests/ -q`. Add an
`AUDIT.md` (sample N parts vs datasheets, sign-off).

## 7. KiCad registration (one-time, never per-table)
Register globally: the `terra` database lib + two `(type "Table")` includes (symbol +
footprint) pointing at the generated lib-tables; `make` keeps them current as libs are added,
so no KiCad edit per ported table. Do NOT hand-add individual libs via the GUI (nickname
typos / partial per-project entries → "footprint not found" / missing fields). The `terra`
database connection string is an absolute path to `db/terra.db` (vars aren't expanded there).
**Full procedure:** `docs/kicad-registration.md` (preconditions, exact lib lines, project
de-duplication, verify, rollback).

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
- `make` does NOT track `tools/cern_libmap.py` or `tools/model_map.py` as build deps. After
  editing them (new nickname, footprint fixup, package map), the affected table's
  `*_generated_*.sql` is considered up-to-date and won't regenerate. Force it: `rm` the
  table's `*_generated_*.sql` + `db/<table>.db`, then rebuild. `apply_3d_models` reads the
  *master* `db/terra.db`, so rebuild the master (full `make`) before re-running it.
- CERN `LibFootprint`/`LibSymbol` fields occasionally contain typos or spurious/dropped
  suffixes that don't match any real file (e.g. `SOT95P2d80X100-6N`, a `…521`/`…521R`
  mismatch, a `+THERMAL` suffix). The footprint-resolution test catches these; correct them
  in `cern_libmap.FOOTPRINT_ITEM_FIXUP` (deterministic bad-name → real-name map).
