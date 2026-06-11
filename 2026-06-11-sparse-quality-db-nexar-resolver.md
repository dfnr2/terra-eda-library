# Sparse-but-High-Quality Terra DB + Nexar Parameter Resolver — Design

**Date:** 2026-06-11
**Status:** Design — pending Dave's review
**Supersedes/updates:** `2026-06-10-phase0-schema-consolidation.md` (the schema
mechanism still holds; the **fragment column lists here override** that plan's
Tasks 5–12) and `2026-06-10-datasheet-param-resolver-design.md` (the pipeline still
holds; the **data-source decision and allowlist here override** its Nexar/Octopart
assumptions). Authoritative column marks live in `schema-review.org`.

---

## 1. Strategy (the pivot this design records)

The CERN library import (35 `cern_*` tables, ~15.4k parts) gives us good
footprints and symbols but **weak database population** — not up to standard.
Rather than adopt CERN's data wholesale or keep syncing from it, we:

1. **Build a sparse but high-quality database.** Populate only the parts we can
   *match and properly populate*, leaving everything else honestly blank.
2. **Populate in place, in the `cern_*` buckets.** The matched parts stay in their
   CERN tables for now — no migration this round.
3. **Fold the DB-population + datasheet/HTTP tooling into `main`.**
4. **Proceed as before** to the terra-native passive generators (the real
   high-ROI work — see `terra-library-direction` memory).
5. **Later, one-time fold** the CERN parts into the native terra tables as a single
   operation, then **never sync from CERN again**. Phase 0's shared schema (one tail
   per type, used by both `cern_<type>` and native `<type>`) is what makes that fold
   trivial.
6. **Keep CERN footprints/symbols** as a harvest cache — pulled in when they help
   add new parts through the normal go-forward workflow.

"Sparse but high quality" is the governing principle: **fill-blanks-only, never
guess, record no-match/low-confidence rather than fabricate.**

---

## 2. Locked decisions

### Data source — Nexar/Octopart API, free Evaluation tier (CONFIRMED)

A live test query (`supSearchMpn`, 2026-06-11) confirmed the **free Evaluation tier**
returns **both** the datasheet URL (`bestDatasheet.url`) **and** the full parametric
`specs` (60+ attributes, e.g. min/max operating temp, min/max supply voltage, RoHS
status, flash/ram/eeprom sizes, pin/interface counts). The marketing compare-plans
table wrongly implies these are Enterprise-only; the API returns them on free.

- **Access:** Dave's Altium subscription (valid **through ~Nov 2026**). The Altium
  Live login authenticates the Nexar portal; the API itself needs an OAuth
  application (`client_id`/`client_secret`) created at nexar.com.
- **Hard constraint:** **1000 matched parts/month** quota. The harvest is therefore
  **paced** — ≤1000/month, **matchable/high-value parts first**, checkpointed and
  resumable across the ~5-month window (~5k parts max, which fits "sparse").
- **PDF param extraction is rejected** (too error-prone vs. Nexar's normalized
  structured data). The ~1,556 already-banked PDFs are reused only as **mirror
  inputs** (durable archival), not parsed.
- **Altium-tool export** (Manufacturer Part Search → BOM/CSV) is a **manual fallback
  only**, for parts Nexar can't match — not built this round.

### Temperature → promoted into core

Operating/storage/soldering temperature apply to every component, so they live in
**`core.sql`**, not a type fragment. Per Dave: operating required, storage +
soldering preferred. Modeled as **min/max numeric** (matches Nexar's separate
`min/maxoperatingtemperature` attributes and the `supply_voltage_min/max` choice):

- `temp_operating_min`, `temp_operating_max` — NUMBER (°C)
- `temp_storage_min`, `temp_storage_max` — NUMBER (°C)
- `temp_soldering` — NUMBER (°C peak)

Nexar reliably supplies **operating** temp; **storage/soldering** are usually absent
from structured data → they stay blank under fill-blanks-only (honest, by design).

### RoHS → EU baseline, harvested

Core already has `rohs` (status) + `rohs_document_link` (proof). We add **`rohs`** to
the harvest allowlist (it had only `rohs_document_link`). EU RoHS (Directive
2011/65/EU) is the baseline; Nexar's `rohs` attribute carries the status
("Compliant"). The proof-*document* link is usually absent from structured data → it
stays blank under fill-blanks-only.

### Schema confirmations (Dave approved 2026-06-11)

- **DROP-ALL = 9 columns** dropped everywhere: `class, component_type,
  component_value, composition, number_of_pins, reference, sim_library, sim_type,
  temp_coeff`. (The 3 temp columns are promoted to core instead, hence 9 not 12.
  `number_of_pins` text is dropped in favor of the canonical core `pin_count`,
  harvested from Nexar's clean `numberofpins`.)
- **connectors ADOPT = yes** — reuse the native 38-col connectors schema verbatim
  for all 17 connector tables.
- **dedupe `uart_count`** — `ic_microcontrollers` listed it twice; keep one.
- **temp_coeff stays out of core** — passive-specific (ppm/°C), reappears later in
  the resistor/capacitor fragments.

---

## Part A — Phase 0: schema consolidation

Mechanism is unchanged from `2026-06-10-phase0-schema-consolidation.md`:
`tools/gen_schema.py` generates each table's `_0_schema.sql` from `db/schema/core.sql`
+ `db/schema/types/<type>.sql`, driven by `db/schema/table_map.json`; a `make schema`
target + drift test keep committed schemas in sync; cern/native column-set equivalence
is asserted per type. **What changes is the column content**, below.

### Core — 41 columns (reconciled to the deployed schemas)

The spec originally assumed a clean 34-col core; the live schemas (survey 2026-06-11)
show the cores have **diverged in membership**, so the canonical core is pinned here
from what is actually deployed and populated:

- **33 base columns** `unique_id … sim_params` (incl. `variant`), copied from
  `cern_diodes_0_schema.sql`.
- **`exclude_from_bom`** — re-added (CLAUDE.md lists it core; default 0; currently
  present in only `connectors`).
- **`pin_count`, `component_height`** — already present and **populated** in 35 tables
  (the CERN import added them to core); kept as core, not dropped.
- **the 5 temperature columns** (`temp_operating_min/max`, `temp_storage_min/max`,
  `temp_soldering`).

Total = **41 columns**. Suggested placement: temp + `component_height` in a
physical/ratings block after `package`/`value`, `pin_count` near them; `tier`/
`dump_priority` defaults stay per-table via `table_map.json`. Because `pin_count` is
core, it is **removed from the `ic_microcontrollers` fragment** (below).

### Type fragments (final — from `schema-review.org` marks)

Each fragment is the type-specific tail appended after the 39 core columns.

```
diodes (cern_diodes, diodes):
  diode_type, voltage_rating, forward_voltage, forward_current,
  current_rating, power_rating

transistors (bjt, mosfet, cern_transistors):
  transistor_type, channels, v_ce_ds_max, i_c_d_max, power_dissipation,
  hfe_typ, rds_on, vgs_th, transition_freq, temp_junction_max

op_amps (ic_opamp, cern_op_amps):
  amplifier_type, channels, gain_bandwidth, slew_rate, input_offset,
  input_noise, supply_voltage_min, supply_voltage_max, power_rating

logic (ic_logic, cern_logic, cern_standard_logic):
  logic_family, gate_function, channels, propagation_delay,
  supply_voltage_min, supply_voltage_max

analog (ic_analog, cern_analog_interface):
  function_type, channels, resolution_bits, interface,
  supply_voltage_min, supply_voltage_max

leds (leds, cern_leds_displays):
  color, wavelength_nm, forward_voltage_v, current_max_ma,
  luminous_intensity, viewing_angle

switches (switches, cern_switches):
  switch_type, poles, throws, current_rating, voltage_rating, actuation_force

inductors (inductors):
  inductance, tolerance, current_rating, saturation_current,
  dc_resistance, self_res_freq

ferrites (ferrites):
  impedance_at_freq, dc_resistance, current_rating, power_rating, tolerance

ic_drivers (ic_drivers):
  driver_type, channels, supply_voltage_min, supply_voltage_max,
  i_max_device, i_max_channel, logic_polarity, output_type, power_rating

ic_memory (ic_memory):
  memory_type, capacity, word_size, speed, interface,
  persistence_cycles, persistence_years

ic_microcontrollers (ic_microcontrollers):
  family, core, supply_voltage_min, supply_voltage_max,
  flash_size, eeprom_size, ram_size, gpio_count, uart_count,
  i2c_count, timer_count, special_features
  (pin_count is CORE, not in this fragment)

connectors (connectors + all 16 cern_<vendor> tables):
  ADOPT the existing native connector TAIL verbatim
  (connector_category … mating_part_hint). The CORE portion is regenerated
  to the canonical 41-col core — see the column-order note below.
```

### Column-order normalization (all regenerated tables, connectors notably)

Generating every table through the one canonical core **normalizes core column
membership and order** across the library. The live cores have diverged: e.g.
`cern_diodes` has `variant` + `pin_count` + `component_height` but **not**
`exclude_from_bom`, while `connectors` has `exclude_from_bom` but **not** `variant`
(jumps `manufacturer → package`) and predates the temp columns. Regeneration replaces
each table's core with the canonical 41-col core — adding whatever it lacks
(`variant`, `exclude_from_bom`, `pin_count`, `component_height`, the 5 temp columns)
in canonical positions and grouping the core consistently. This is desirable, not a
special case.

**Invariant (data-safety guard):** a core reorder breaks **positional**
`INSERT … VALUES (…)`. All data INSERTs must be **column-qualified**
(`INSERT INTO <t> (col, …) VALUES (…)`) — the CERN import and `db_to_tables.py`
dumper should already emit this; Phase 0 adds a one-time assertion so no
regeneration silently misloads. Native `connectors` itself is an empty scaffold
(schema only, no data file), so its own reorder is risk-free; the populated
`cern_<vendor>` tables are the ones the invariant protects.

Numeric columns (`supply_voltage_*`, `channels`, `poles`, `throws`, `gpio_count`,
`uart_count`, `i2c_count`, `timer_count`, `pin_count`) use INTEGER/NUMBER as marked;
the rest are TEXT (values carry units, e.g. "72 MHz").

### Out of scope this round

- **CERN-only types** (regulators, optocouplers, dc_dc_converters,
  crystals_oscillators, relays, fuses, sensors, transformers, power_supplies,
  thermistors_varistors, batteries): keep existing tails, **deferred** ("defer the
  CERN work on these for now").
- **Passives** (resistors_smt/th, capacitors_smt/th): populated/curated; guarded out
  of `table_map.json`; fragments defined later as supersets.

---

## Part B — Nexar parameter/datasheet resolver

Pipeline unchanged from `2026-06-10-datasheet-param-resolver-design.md`; the deltas
are the data source (Nexar free Evaluation, confirmed), the allowlist additions, and
the pacing.

### Harvest (`harvest.py`, online, maintainer)

For each part across the target `cern_*` tables (matchable/high-value first), query
Nexar `supSearchMpn(q=<mpn>, limit=1)` (filter by manufacturer). On a high-confidence
match, write to the per-table sidecar `<table>_harvest.json` (keyed by `unique_id`):
the resolved `datasheet_source_url` (= `bestDatasheet.url`), `original_datasheet`, and
the **allowlisted** params. Rate-limited, **checkpointed**, incremental (skip
already-resolved), **capped at ≤1000 matched parts/month**, records
`no-match`/`low-confidence` (never guesses).

### Writable-column allowlist

- **`CORE_HARVEST_COLUMNS`**: `manufacturer_link`, `rohs_document_link`, **`rohs`**,
  `package`, **`temp_operating_min`**, **`temp_operating_max`**,
  **`temp_storage_min`**, **`temp_storage_max`**, **`temp_soldering`**, plus the
  `datasheet` reference.
- **The part type's Phase-0 fragment columns.**
- Everything else from Nexar is dropped. Curated columns (`description`, `value`,
  `mpn`, …) are never harvest targets.

### Field map (Nexar `shortname` → Terra column, per type)

A per-type YAML map (concept already in `tools/field_mappings.yaml`). Examples
validated against the live STM32 result:

```
minoperatingtemperature -> temp_operating_min     maxoperatingtemperature -> temp_operating_max
minsupplyvoltage        -> supply_voltage_min      maxsupplyvoltage        -> supply_voltage_max
rohs                    -> rohs                     case_package            -> package
flashmemorysize         -> flash_size              ramsize                 -> ram_size
eeprommemorysize        -> eeprom_size             corearchitecture        -> core
numberofpins            -> pin_count               numberofi2cchannels     -> i2c_count
numberofusartchannels   -> uart_count              numberoftimers_counters -> timer_count
```

Unmapped attributes are dropped. Value normalization (units, e.g. "85 °C" → 85) is a
harvest-side concern for the numeric columns.

### Mirror + apply (unchanged mechanism)

- **`mirror.py`** (online, `gh`): download each datasheet, content-address
  `<sha256>.pdf`, upload to a fixed GitHub **Release** tag (`--clobber`), record
  `download_url`+`sha256` in `assets/datasheets/manifest.json`. **Prefer an
  already-banked PDF** (from `assets/datasheets/by-name/`) as the mirror input when
  the MPN already has one; else fetch `bestDatasheet.url`. `prune.py` GCs unreferenced
  assets.
- **`apply_harvest.py`** (deterministic, in the `db/terra.db` recipe, keyed by
  `unique_id`): **fill-blanks-only** for allowlist params (curated wins; conflicts →
  `build/harvest_conflicts.tsv`, gitignored, rewritten each build); **always repoint
  `datasheet`** to the durable Release `download_url` when one exists, else leave it
  untouched (never blank/dangle).
- Optional per-user offline layer (`make datasheets` local cache + `localize` →
  `db/terra_local.db`) unchanged; never a prerequisite of `make all`.

### Determinism

`make` never hits the network. `db/terra.db` builds identically for everyone from the
committed manifest + sidecars; Nexar lookups and `gh` uploads happen only in
maintainer-run phases.

---

## 3. Sequencing — what folds into `main`

1. **Phase 0 schema consolidation** (Part A) — lands first; it's the blocking gate
   and the contract for what the harvest may write.
2. **Resolver plumbing + httplib tooling** (Part B) — `harvest`/`mirror`/`prune`/
   `apply_harvest`, sidecars, manifest, field maps, plus the existing
   `tools/datasheets/*`.
3. **Run the harvest** — paced ≤1000/month, matchable-first, **before ~Nov 2026**.
4. **Merge `feat/tier-tag-system` → `main`.**

---

## 4. Testing

- **Phase 0:** core = 41 columns; each `<type>.sql` included by both cern + native
  schemas with identical resulting column sets; committed `_0_schema.sql` matches the
  generator (drift guard); passives absent from `table_map.json`; `_v` views still
  build (need `unique_id` + `tier`, both core).
- **harvest:** fixture Nexar responses → field-map output respects the allowlist
  (drops the rest); low-confidence/no-match recorded; sidecar carries
  `datasheet_source_url` + `original_datasheet`; monthly cap honored.
- **apply_harvest (deterministic):** blanks filled, non-blanks preserved, conflicts
  logged, `datasheet` set to resolved `download_url` by `unique_id`; identical DB with
  empty vs populated local cache.
- **mirror/prune:** content-addressed upload, clobber, prune removes exactly the
  unreferenced hashes; banked-PDF-as-mirror-input path covered.
- **conflicts report** rewritten (not appended) — two builds yield identical output.

---

## 5. Open items / fallback

- **Nexar OAuth app** must be created at nexar.com (5-min one-time setup) before the
  sweep runs.
- **Altium-tool export** importer is the documented fallback for parts Nexar can't
  match; not built this round.
- **Storage/soldering temp** and **RoHS proof-document** columns will be largely
  blank from Nexar — acceptable per the sparse-high-quality principle; could be
  backfilled later from the Altium fallback or datasheet parsing if ever wanted.

---

## Self-Review

- **Scope:** focused on one round — schema consolidation + a paced Nexar harvest into
  the `cern_*` buckets. The future CERN→native fold and passive generators are
  explicitly out, with Phase 0 set up to make the former trivial.
- **Consistency:** the harvest allowlist = `CORE_HARVEST_COLUMNS` (incl. the new temp
  + rohs) ∪ the Phase-0 fragment columns; nothing writes outside the consolidated
  schema. Temp lives in core (type-agnostic); temp_coeff stays out (passive-specific).
- **Honesty:** fill-blanks-only + recorded no-match/low-confidence; known-blank
  columns (storage/soldering temp, RoHS doc) called out rather than fabricated.
