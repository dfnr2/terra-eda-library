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

**Everything is regenerable** — edit schema/scripts and re-run; no live-DB migration.

**Source layout:** the CERN repo is vendored in-tree at `vendor/cern-kicad-libs/` (a
gitignored shallow clone — set it up once with
`git clone --depth 1 <cern-kicad-libs> vendor/cern-kicad-libs`). `tools/cern_source.py`
finds `CERN.sqlite` there automatically, so builds need **no** `CERN_SQLITE` env var (set it
only to point elsewhere). The CERN symbol/footprint libraries to copy live under
`vendor/cern-kicad-libs/SchLib/` and `vendor/cern-kicad-libs/PcbLib/`.

Existing scaffolding to reuse: `tools/cern_source.py` (read CERN.sqlite),
`tools/cern_libmap.py` (nickname map + `ITEM_FIXUP`), `tools/cern_reconcile.py`,
`tools/generate_lib_tables.py`, `tools/model_map.py`, `tools/apply_3d_models.py`,
`tools/fix_footprint_attrs.py`, and `db/tables/cern_diodes/` as the worked example.

## 0. Inspect the CERN table
- List columns + fill rates; identify the **type-specific tail**. Reality check: CERN's
  `Component Type`/`Component Kind` columns are almost always uniformly `Standard` (useless),
  and parametric columns (voltage/power/etc.) are usually absent — so the tail is typically
  **derived from the `LibSymbol` name** (see §2). Grab-bag categories with device-named
  symbols and no single type dimension (e.g. Analog & Interface, Logic, Standard Logic,
  DC-DC) get **no tail at all** — that's a legitimate, common outcome.
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
- **Type tail from the symbol name** (the usual source — CERN has no parametric columns):
  take the `LibSymbol` item name, cut the trailing pinout / `Type N` / `xN` / `[alt]` / `_a`
  descriptors to get the base type, and keep it only if it matches a type keyword for this
  part type (`NPN|PNP|MOSFET|JFET|IGBT…`, `Optocoupler|PhotoMOS|Relay…`, `REG|VREF|REF…`);
  otherwise leave blank (a bare device-named symbol like `IXGR32N170H1` → blank). Pull a
  `channels` column from the `xN` token when present. Worked examples: the diodes /
  transistors / regulators / op_amps / optocouplers generators.
- Escape single quotes in SQL. Emit one `tags` insert per part. `source='cern_import'`,
  `dump_priority=0`.

## 3. Symbols & footprints (terra-owned hierarchy)
terra owns its libs under `kicad_symbols/` (`.kicad_sym`) and `kicad_footprints/`
(`.pretty`); parts reference terra nicknames, never KiCad's built-in `Device:`/`Diode_SMD:`.
- Find the CERN SchLib + PcbLibs the parts reference (`LibSymbol`/`LibFootprint`).
- **Copy** each from `vendor/cern-kicad-libs/` into terra with a normalized name (lowercase,
  non-alphanumerics→`-`, `cern-` prefix; nickname = filename stem):
  `vendor/cern-kicad-libs/SchLib/Foo.kicad_sym` → `kicad_symbols/cern-foo.kicad_sym`;
  `vendor/cern-kicad-libs/PcbLib/BAR.pretty` → `kicad_footprints/cern-bar.pretty`.
- Add the CERN→terra nickname entries to `tools/cern_libmap.py`; the generator rewrites each
  part's `kicad_symbol`/`kicad_footprint` to the terra nicknames.
- CERN symbol libs contain literal `[alt]` (De Morgan) variants as **distinct symbols** — keep
  the `LibSymbol` ref as-is (don't strip `[alt]`); it resolves to the real symbol. The
  symbol-resolution test catches any that don't.
- **Footprint normalization** is the `make normalize-footprints` target (after the build): it
  runs `fix_footprint_attrs` (sets `smd`/`through_hole` type from the pads — the CERN
  conversion leaves none, so KiCad shows them "Other/Virtual"; reports any footprint filed in
  the wrong lib) then `apply_3d_models` per `cern_*` table (§5). Idempotent; it re-resolves
  shared footprints as the part population grows, so re-run it after each new table.

## 4. Build
`make EXCLUDE_TABLES="resistors_smt resistors_th" [DEFAULT_TIER=5]` builds `db/cern_<name>.db`,
master `db/terra.db`, `terra.kicad_dbl` (absolute DB path — KiCad does NOT expand path vars in
the dbl connection string), and the generated `kicad_symbols/sym-lib-table` +
`kicad_footprints/fp-lib-table`. (`DEFAULT_TIER=5` so tier-5 catalog parts are visible.)
CERN.sqlite is found in `vendor/` automatically — no `CERN_SQLITE` needed.

## 5. 3D models
All mapping rules live in `tools/model_map.py` (codified once, never re-derived). Add this
part type's packages there, then run `make normalize-footprints` (or, for one table while
iterating, `uv run python tools/apply_3d_models.py --table cern_<name>`) to rewrite footprint
`(model …)` refs and set alignment offsets. The resolver has these strategies, tried in
order — extend whichever fits the package:
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

- **Bridges + blank-package bodies + dimensioned IC packages** (`resolve_from_footprint`):
  CERN often leaves `package` blank/coarse but encodes the body in the *footprint name*.
  `apply_3d_models` falls back to `resolve_from_footprint`, which handles: dimensioned
  **QFN/DFN/QFP** via `_resolve_quad` (parses IPC names like `QFN50P700X700X90-49N` /
  `QFP50P900X900X160-48N` → matches KiCad parametric model by family+pitch+leads(N or N-1)
  +nearest body; QFP name is the lead-span so body = span−2mm); dimensioned **BGA** via
  `_resolve_bga` (`BGA<balls>C<pitch>P<RxC>_<body>` → exact ball count + pitch, which
  disambiguates same-ball-count bodies, + nearest body; declines ball counts/pitches KiCad
  doesn't ship); bridge codes → `Diode_Bridge_*`; SMD body codes (SODFL→SOD-123F/128,
  DIOMELF→MELF by size, PowerDI/PowerMite); then any known package key embedded in the name.
  These dimension resolvers lift every IC table at once — extend them rather than hand-listing
  dimensioned variants.

**3D coverage varies by category, and low is often correct, not a failure.** IC tables land
~60–90%; **vendor power modules (DC-DC) are ~0%** (bespoke footprints, no KiCad models) and
niche packages (optocoupler SOIC-4/5/6, exotic FPGA BGA ball counts) stay low. Note the
expectation in `AUDIT.md` so a low number isn't read as a regression.

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
- Pass `EXCLUDE_TABLES`/`DEFAULT_TIER` on EVERY `make` (incl. `project-db`) — make rebuilds
  prerequisites, so omitting them silently re-includes resistors / wrong tier. (`CERN_SQLITE`
  is no longer needed — `cern_source` finds the vendored clone.)
- `make` does NOT track `tools/cern_libmap.py` or `tools/model_map.py` as build deps. After
  editing them (new nickname, footprint fixup, package map), the affected table's
  `*_generated_*.sql` is considered up-to-date and won't regenerate. Force it: `rm` the
  table's `*_generated_*.sql` + `db/<table>.db`, then rebuild. `apply_3d_models` reads the
  *master* `db/terra.db`, so rebuild the master (full `make`) before re-running it.
- CERN `LibFootprint`/`LibSymbol` fields occasionally name an item that matches no real file/
  symbol — typos (`SOT95P2d80X100-6N`, `…-32AN`, `INFININEON…`), dropped/spurious suffixes
  (`…521` vs `…521R`, a `+THERMAL` suffix), an Altium export artifact (`TEXAS_DYY0016A` whose
  file is `TEXAS_DYY0016A - duplicate.kicad_mod`), or a variant symbol that was never created
  (`TXS0108ERGY` → use `TXS0108E_a`). The footprint/symbol resolution tests catch these;
  correct them in `cern_libmap.ITEM_FIXUP` (one deterministic bad-name → real-name map applied
  to both symbol and footprint refs).
