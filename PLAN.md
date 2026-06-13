# Terra EDA Library — Philosophy and Plan

## Why Terra exists

Terra is built around one workflow conviction: **a schematic should carry
fully-qualified, orderable parts — never generic symbols whose values are filled
in later.**

The common EDA workflow places a generic part (a bare resistor symbol) and
annotates value, tolerance, and package downstream. The usual justification is
"you don't know every value while laying out the circuit." That doesn't hold up:

- Deferring part identity is inefficient, error-prone, and a standing source of
  BOM inconsistency — the deferred work reappears as manual fixes all the way
  down the chain.
- A **rich library makes substitution easier than ad-hoc value entry.** When the
  library already holds real parts, swapping one for another is a single
  reselection, not a cascade of manual edits.

So Terra's product is the library that makes the fully-qualified workflow
practical: place a real MPN, and the BOM is correct by construction.

## What Terra is

**Terra is the "3D" (richly-specified, BOM-able) version of KiCad's "2D"
(symbol + footprint) shipped libraries.** KiCad already ships curated symbols and
footprints, and most interesting parts ship with a datasheet field. Terra turns
those into complete, orderable parts.

### Source of truth: scripts, not a database

The canonical library is the **version-controlled scripts and assets** under
`db/tables/`. The SQL and the database (`db/terra.db`) are both generated
artifacts, rebuilt deterministically by `make`. **Every part has a script — even
bespoke one-offs.** A part that exists only as data can't follow a schema change
or a convention switch (US vs. EU symbol styles); a scripted part is regenerated
under the new configuration. A few legacy parts still live as tracked SQL and are
slated for migration to scripts. This is deliberate, and it is what separates
Terra from inventory systems:

- Every part change is a **diff** you can review in a pull request.
- The build is **deterministic** and round-trip verified (`make verify`).
- "What changed and why" lives in **git history**, not an application's audit
  log.

This is why off-the-shelf stores like InvenTree or Part-DB don't fit. Those are
*stores* — they hold whatever you put in, with the live database as the source of
truth. Terra is a *generator* — its value is the pipeline that manufactures
fully-qualified parts from KiCad's libraries, datasheets, and parametric sources.
That pipeline sits upstream of any database and cannot be bought.

## Substitutability

A mature library must express alternates. Terra does this **denormalized**:

- Every row is a real, orderable MPN
  (`unique_id = <manufacturer>-<mpn>[-<variant>]`).
- `part_locator` is the **equivalence key** (the "part inventory number"): rows
  that share a `part_locator` are interchangeable.
- Listing alternates is therefore one query (`WHERE part_locator = ?`), run on
  the **cold path** — a BOM/procurement tool — not during BOM generation.

There are deliberately **no normalized PIN tables and no `alternates` table**.
BOM generation is the hot, high-stakes path and must stay trivial: the placed MPN
is already orderable. Listing alternates is rare and low-stakes, so that is where
the extra step belongs. A pure-PIN scheme would tax the hot path and reintroduce
resolve-later — the same deferral we reject for schematic capture, just moved into
procurement. A ranked, approved AML (approved-manufacturer-list) table is a future
addition *only if* procurement demands it.

This rests on `part_locator` being **robust = a computed canonical key**:

- **One shared canonicalization function**, used by every part-creation path
  (generators, the KiCad-seed pipeline, CERN fold-ins) — never per-generator
  string formatting, or equivalence silently breaks at the seams between sources,
  which is exactly where alternates matter most.
- A pure deterministic function of normalized specs: canonical value magnitude
  (so `100nF` ≡ `0.1µF`), canonical tolerance and ratings, and **package
  included** (a 10k 0603 and a 10k 0805 must not collide).
- A **per-component-type substitution-field set** — dielectric is load-bearing
  for capacitors, temperature coefficient for precision resistors, and
  second-source compatibility is a harder question for ICs.

## The go-forward plan

### Seed from KiCad's shipped libraries

Iterate KiCad's symbol/footprint libraries and turn each part we want into a
complete Terra part. The pipeline branches on symbol type:

- **Specific-part symbols** (e.g. `MCU_ST_STM32:…`, op-amps, regulators) carry a
  usable datasheet field and often a designated footprint → harvest one rich row
  each: validate-and-harvest the datasheet *link* (download only if needed) →
  pull parameters from Nexar or the datasheet → upsert the SQL row → next symbol.
- **Generic symbols** (`Device:*`, no MPN, footprint by filter) → hand to the
  datasheet-driven **value-space generators**. The existing resistor and
  capacitor generators are the model: parametrics generated from the MPN,
  datasheets that dedup massively across a series, footprints already
  KiCad-curated.

Parameter harvest leans on the Nexar free Evaluation tier (Altium credentials,
~1000 matched parts/month, window closing ~Nov 2026), so the sweep runs
datasheet-first (cheap, ungated) and Nexar-params-second (gated), prioritized
against that window.

### Wind down CERN

The CERN import was a breadth bet whose only durable asset was bespoke
footprints — and that value is diminished by missing 3D models and thin tables.
KiCad's shipped libraries supersede it as the seed, so CERN becomes a **donor
being wound down**, in this exact order:

1. **Fold in where helpful** — promote only the CERN parts/footprints that fill a
   gap KiCad's libraries don't already cover, using the `led_drivers` promotion
   pattern (`tools/cern_promoted.py`).
2. **Exclude `cern_*` tables from the build** — reversible; confirm `make clean &&
   make` and the test suite stay green and that nothing native references them.
3. **Delete the `cern_*` part-data tables.** Retain bespoke footprint/symbol
   assets still referenced by promoted native parts.

The concrete steps behind each item live in [PROCESSES.md](PROCESSES.md).
