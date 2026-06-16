# Stage 4 — Project Conversion Write Engine

**Status:** Design for implementation. Stages 1–3 (the read-only `tools/terra_convert.py`
analyzer) are done and committed; this is the *write* side. It mutates terra and the project,
so it is split by risk and gated on the human-approved decisions captured in
`plans/project-conversion.md`.

## Goal

Apply a board's approved conversion: **fill terra from the board's curated parts**, and
**rewrite the board to use terra parts** — safely, reproducibly, and reviewably. The engine
never invents substitutions; it consumes the analyzer's records plus the approved
substitution/harvest decisions.

## Two phases, by risk

- **4a — terra-side writes** are *additive* to the library: new parts, new tables, migrated
  footprints, CERN deletions. Verified by `make` + the test suite; reversible via git.
- **4b — schematic rewrite** *mutates the user's board*. It is pin-preserving by construction
  and verified against the netlist; anything it can't prove safe is left for manual handling.

4a lands first (committed, build-verified). 4b runs per board afterward.

---

## 4a — terra-side writes  (tool: `tools/terra_harvest.py`)

Input: the analyzer's `--json` records for one board + the approved manifest.

1. **Harvest curated parts into native tables — scripts always.** Every harvested part,
   *including singletons*, is emitted by a committed **generator script** under
   `db/tables/<table>/run_*.py`, with the curated fields (MPN, manufacturer, value,
   description, datasheet, RoHS link, footprint) baked into the script as data. `terra_harvest`
   reads the curated fields from the schematic and writes/extends that script; its output SQL
   is generated (gitignored, `dump_priority = 0`) like the passive generators. No hand-written
   SQL rows.
   - Mainboard targets: `diodes` (VESD05A1, SMF18A, SMF6.0A, SM712), `connectors` (6 Molex/
     Hirose/Kycon/Leader/RRC parts).

2. **Create the two new component types.** Each follows the canonical pattern: a
   `db/schema/types/<type>.sql` fragment, a `table_map.json` entry, a `db/tables/<type>/`
   directory, and a harvest generator.
   - `test_points` tail: `tp_style` (loop/pad/socket), `pad_dia_mm`, `mount` (SMT/THT), `color`.
   - `batteries` tail: `chemistry`, `nominal_voltage_v`, `capacity_ah`, `energy_wh`,
     `rechargeable`, `interface` (e.g. SMBus/smart).
   *(Tails are proposals — adjust on review.)*

3. **Migrate hand-curated footprints.** For each part whose footprint is a custom `nema:`
   library entry (the connectors, SM712, the test point), copy the `.kicad_mod` from the
   project's footprint library into a terra footprint library
   (`kicad_footprints/<lib>.pretty/`), and set the part's `kicad_footprint` to the terra
   reference. Source paths resolve via the project's `fp-lib-table`. 3D-model references inside
   the `.kicad_mod` are repointed to `${TERRA_EDA_LIB}` if present.

4. **Delete the superseded CERN entries.** A part ported native that had a CERN equivalent
   (e.g. `SM712`, and `U2` `PCA9306DCT` → native) is removed from its `cern_*` table and its
   MPN added to the `tools/cern_promoted.py` exclusion, mirroring the `led_drivers` promotion.

5. **Verify.** `make` + `make verify` + the test suite stay green, then re-run
   `terra_convert.py` on the board: the harvested gaps now resolve to **Tier A** native parts
   and the CERN entries no longer surface. This is the acceptance test for 4a.

---

## 4b — schematic rewrite  (tool: `tools/terra_rewrite.py`)

Rewrite each convertible placed symbol's `lib_id` to `terra:<unique_id>`. The hazard: terra
parts reference the **standard** KiCad symbols, which may differ in orientation/geometry from
the `nema` symbols (e.g. the legacy resistor is drawn horizontal; `Device:R_US` is vertical).
A bare `lib_id` swap would move the pins and break nets. The engine therefore applies a
**pin-preserving placement transform** and proves it.

### Per-symbol algorithm
1. Compute the **legacy** symbol's absolute pin coordinates and the net at each pin, from
   `nema.kicad_sym` plus the instance's `at` / rotation / mirror.
2. Compute the **terra** part's symbol pin geometry (from its `kicad_symbol`).
3. Search the finite transform set — rotation ∈ {0°, 90°, 180°, 270°} × mirror ∈ {none, X, Y}
   — for one under which the terra symbol's pins land on the **same absolute coordinates** as
   the legacy pins. Polarized parts (diodes, polarized caps, etc.) additionally require pin
   *identity* (e.g. anode↔anode) to match at each coordinate; non-polarized 2-pin parts accept
   either assignment.
4. **If a transform is found:** rewrite `lib_id` → `terra:<unique_id>` and set the instance's
   `at`/rotation/mirror to it; preserve reference, UUID, and connections. Pins do not move, so
   nets are preserved by construction. (For the mainboard resistors this resolves to **+90°**.)
5. **If none is found** (different pin span, unresolvable polarity): leave the symbol untouched
   and add it to the manual-review list with the reason.

### Safety invariants
- For every rewritten symbol, the set of (pin coordinate → net) pairs is **identical** before
  and after — asserted, not assumed.
- The engine never modifies a symbol it cannot prove safe.
- Idempotent: re-running is a no-op on already-`terra:` instances.

### Verification (the gold check)
Export the board's netlist before and after (`kicad-cli sch export netlist`); the diff must be
**empty**. A non-empty diff aborts/reverts the rewrite. ERC is run as a secondary check.

---

## Sequencing, inputs, reversibility

- **Order:** 4a (committed, build-verified) → 4b per board. CERN deletions happen only after
  the native port is confirmed in the build.
- **Inputs:** the analyzer's records + the approved substitution table and harvest manifest in
  `plans/project-conversion.md`. The engine applies decisions; it does not make them.
- **Reversibility:** every step is a reviewable `git diff`; CERN deletions are recoverable from
  history. Commit per logical step (harvest, new types, footprints, deletes, then each board's
  rewrite).

## Out of scope (for now)
- Auto re-routing wires when pins cannot be aligned — those parts go to manual.
- Hierarchical/multi-sheet schematics (the first board is flat) — note as a follow-up.
