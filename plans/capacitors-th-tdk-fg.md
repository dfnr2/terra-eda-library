# capacitors_th — TDK FG-series leaded MLCC generator

**Date:** 2026-06-28
**Status:** Done — 333 parts (196 C0G + 137 X7R); see Results
**Scope:** stand up the new `capacitors_th` table and populate it from the TDK FG
series (dipped radial-lead MLCC). Source datasheet:
`db/tables/capacitors_th/tdk-mlcc-through-hole-caps.pdf` (FG series, Nov 2024).

## Motivation

We have SMD MLCC (`capacitors_smt`) and radial-leaded electrolytics
(`capacitors_electrolytic_th`) but no **through-hole ceramic** table. The TDK FG
series (halogen-free, commercial grade, dipped radial lead, 10 V–630 V, 1 pF–47 µF)
is the seed.

## Decisions

- **Curated-but-toggleable coverage** (not the full matrix):
  - Dielectrics **C0G + X7R** on by default; X5R / X7S / X7T off (toggle).
  - **Exclude parts marked "not recommended for new designs"** (the gray cells in
    the range charts).
  - All FG types / both lead pitches and the full voltage range that the enabled
    dielectrics cover.
- **Tolerances (default):** C0G → `J` (±5%) for ≥10 pF, plus `C` (±0.25 pF) / `D`
  (±0.5 pF) for <10 pF; X7R → `K` (±10%). Toggleable per dielectric.
- **Packaging:** default `0` (bulk); `6` (taping) is a toggle.
- **Value display:** `value` = capacitance only (MLCC → no on-schematic voltage,
  per the existing visibility heuristic). SPICE notation (`100p`, `10n`, `1u`).
- **Datasheet** moved to the central local store `datasheets/tdk/` and referenced
  by `${TERRA_EDA_LIB}` (per the datasheet-storage convention), not a web URL.

## FG part-number encoding (authoritative reference)

```
FG  <pitch> <size> <diel> <volt> <cap> <tol> <internal> <pkg>
pitch: 1=2.5mm  2=5.0mm
size (LxW, mm): 8=4.0x5.5  4=4.5x5.5  6=5.5x6.0  0=5.5x7.0  2=7.5x8.5  3=8.5x11.0
  (type = pitch+size, e.g. FG28 = 5.0mm/4.0x5.5; FG18 = 2.5mm/4.0x5.5)
diel: C0G  X5R  X7R  X7S  X7T
volt: 1A=10 1C=16 1E=25 1H=50 2A=100 2E=250 2W=450 2J=630
cap : 3-digit EIA (010=1pF, 101=100pF, 102=1nF, 104=100nF, 106=10uF)
tol : C=±0.25pF  D=±0.5pF  J=±5%  K=±10%  M=±20%
pkg : 0=bulk  6=taping
```

Types present: pitch 5.0 → FG28/FG24/FG26/FG20/FG22/FG23; pitch 2.5 →
FG18/FG14/FG16/FG11.

## Architecture

### 1. Table registration
Add to `db/schema/table_map.json`:
```json
"capacitors_th": { "type": "capacitors", "tier_default": 2,
                   "dump_priority_default": 1, "sim_device": "C", "sim_pins": "1=+ 2=-" }
```
`make schema` generates `capacitors_th_0_schema.sql` (core + `capacitors` fragment,
identical tail to `capacitors_smt`). The library auto-registers (nickname =
`capacitors_th`).

### 2. Generator
`db/tables/capacitors_th/run_300_tdk_fg.py`, patterned on
`run_300_kemet_c0g_mlcc.py` (config block, encoding tables, value/MPN helpers) and
the `electrolytic_th` footprint table. Sets `source=NULL`, `dump_priority=0`
(generated, gitignored output).

### 3. Validity matrix
The valid (type × dielectric × voltage × cap-code) combinations — and each combo's
body type — are extracted from the datasheet range charts (pp.5-12) and catalog
tables (pp.16-42) into a data structure in the generator. MPNs are then built from
the encoding above. **No invented combinations** — only what the sheet lists, minus
the gray "not recommended" cells.

### 4. Footprints
Each FG type → a `Capacitor_THT:C_Rect_L*W*_P{2.50|5.00}mm` footprint, chosen by
body L×W and lead pitch. Use **stock KiCad THT footprints** where one matches the
TDK body dimensions; create a curated `terra_footprints_capacitors_th` footprint
(with a true-height 3D model later) only where none fits. Exact body dimensions and
the final type→footprint map are pinned from the datasheet dimension table during
implementation.

### 5. Field population (`capacitors` fragment + core)
- `value` (capacitance, SPICE notation), `voltage_rating_v`, `tolerance`
  (e.g. "±10%"), `cap_type`="MLCC", `dielectric_class` (C0G/X7R), `polarized`="No",
  `height_max_mm` = body T, temp −55/+125 (C0G/X7R; X5R −55/+85 if enabled later).
- `kicad_symbol`="Device:C"; `kicad_footprint` per §4.
- `unique_id`=`TDK-{mpn}`; `part_locator`=`cap-mlcc-{diel}-{val}-{tol}-{volt}-th-p{pitch}`
  (lowercase, not unique); `description`=`"MLCC TDK FG {diel} {val} {tol} {volt} radial {pitch}mm"`.
- `manufacturer`="TDK", `mpn`=full FG part number, `datasheet`=`${TERRA_EDA_LIB}/datasheets/tdk/fg-series-leaded-mlcc.pdf`,
  `manufacturer_link`=TDK product page.

## Out of scope
- X5R / X7S / X7T dielectrics (toggles, off by default).
- "Not recommended for new designs" parts.
- Tape-and-reel variants (toggle, off by default).
- Other TDK leaded series / other vendors.

## Build & verify
1. `make schema` (registers + generates `capacitors_th_0_schema.sql`).
2. `make capacitors_th-generate && make capacitors_th-build`.
3. Sanity: row count, a few spot-checks (MPN ↔ value/voltage/dielectric/footprint),
   confirm no gray "not recommended" parts emitted, confirm `value` is
   capacitance-only.
4. `make` then `make verify` (round-trip + tests clean).

## Results

Catalog extracted from the datasheet's catalog tables (pp.16-42) into
`fg_catalog.json`: **539 parts found, 206 "not recommended" excluded → 333
recommended** (C0G 196 + X7R 137) across all 10 FG types; **0 MPN-validation
mismatches** (every MPN's encoded type/dielectric/voltage matches its row).
`run_300_tdk_fg.py` reads the catalog and emits 333 rows. `make verify` clean
(261 tests); updated `test_passive_tables_folded_onto_canonical_core` to expect
`capacitors_th` (it had asserted "no source yet").

**Footprints (follow-up).** Each FG type maps to the nearest stock
`Capacitor_THT:C_Disc` at the correct lead pitch — holes and 2.5/5.0 mm pitch are
exact, body silhouette is approximate. **FG16 and FG11** (5.5 mm wide at 2.5 mm
pitch) have no stock disc that wide, so their `D5.0mm` footprint is undersized.
Exact custom `terra_footprints_capacitors_th` footprints (+true-height 3D) are a
recommended follow-up for fully-qualified geometry; the `TYPE_GEOM` map in the
generator is the single place to swap them in.

**Interim datasheet handling** matches the ic_logic round: the PDF lives in the
local store (`datasheets/tdk/`, LFS) and `datasheet` points at it via
`${TERRA_EDA_LIB}` — no web URL.
