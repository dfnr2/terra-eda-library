# Library provenance gate — design

**Status:** approved design, pre-implementation
**Pilot:** `led_drivers` (complete — validated the whole approach end-to-end)

## Problem

Every `kicad_symbols/*.kicad_sym` and `kicad_footprints/*.pretty` directory is
currently globbed into the lib-tables KiCad sees, so all **21 CERN symbol libs +
36 CERN footprint libs** are registered alongside terra's own. CERN parts (and
parts already promoted into native tables) reference those `cern-*` assets
directly. CERN's symbols and parametric data are weak; its value is mostly the
**footprints**. We want imported assets to enter the terra libraries only after a
human has looked at them — and we want that to be an enforced invariant, not a
guideline.

## Goal

A served terra part may reference a symbol/footprint **only** if it is:

1. **KiCad-native** (a stock KiCad library), or
2. **terra-owned** (lives in a `terra*` library = it has been human-approved).

Anything else — `cern-*` today, any future imported source tomorrow — is
**quarantined**: it stays on disk as a mining reservoir but is neither registered
in KiCad's chooser nor allowed as a served part's reference.

## Decisions (settled during brainstorming)

- **Usage-driven, per-asset approval.** A CERN asset becomes a candidate only when
  a terra part actually needs it. Unused CERN assets stay quarantined untouched.
- **Hard build gate**, scoped to **served** rows (tier ≤ the serve cutoff, = 2).
  `cern_*` tables (tier 5, never served) are exempt — they are the reservoir. A
  `cern_*` row promoted to tier ≤ 2 *is* caught (correct).
- **Provenance is the library nickname.** No separate allowlist needed.
- **Per-category terra destination libs** (`terra-diodes`, `terra-led-drivers`, …),
  matching the existing `terra-*` structure.
- **Quarantine logically**, not physically: stop *registering* `cern-*`; the
  `cern-*` / `cern_*` prefix is a sufficient marker. CERN tables/libs are deleted
  wholesale later, not reorganized now.

## Classification rule

A reference `Nick:Item` (or a 3D model `${KICAD*_3DMODEL_DIR}/...`) classifies as:

| Class | Test | Verdict |
|-------|------|---------|
| **terra-owned** | a `terra*` file exists in `kicad_symbols/`/`kicad_footprints/` | allow |
| **quarantined** | a library present in terra's dirs that is **not** terra-owned (every `cern-*` today) | **block** |
| **native** | nickname backed by no terra file → a stock KiCad lib (`Device`, `Package_SO`, `Diode_SMD`, `Driver_LED`, `${KICAD*_3DMODEL_DIR}`) | allow |

By-nickname classification needs no KiCad install (CI-robust). When KiCad's
libraries *are* present, a secondary pass verifies that native references actually
resolve (catches typos / dangling refs); skipped gracefully when absent.

## Components

1. **`tools/provenance.py`** — single source of truth for the classification above
   (`classify(ref) -> {"terra"|"quarantined"|"native"}`, plus the optional
   native-resolution check). Mirrors how `tools/model_map.py` centralizes 3D mapping.

2. **`tests/test_provenance_gate.py`** — the hard gate. Enumerates every served row
   (tier ≤ 2) across **all** tables, classifies both `kicad_symbol` and
   `kicad_footprint`, and **fails** on any quarantined ref. Runs in `make verify`.
   `cern_*` tables are exempt by the tier filter.

3. **`tools/generate_lib_tables.py`** (change) — register only `terra*` libraries
   into `sym-lib-table` / `fp-lib-table`. `cern-*` files stay on disk but disappear
   from KiCad's chooser.

4. **`tools/approve_asset.py`** — the graduation tool. `approve_asset.py <ref>`:
   copies a `cern-*` symbol (from its `.kicad_sym`) or footprint (`.kicad_mod`, 3D
   model already resolved) into the matching per-category `terra-*` library, and
   rewrites the DB-source references `cern-…:Item → terra-…:Item`. Idempotent.
   **Copying is mechanical; refinement is human** — see the pilot: text restyle and
   graphic edits (the CRD circle) are done afterward in KiCad's Symbol Editor.

5. **A/B review surface (pattern, not code).** A temporary DB table (e.g.
   `ab_test`) whose rows pair each candidate symbol/footprint against its proposed
   native or terra replacement. Because the HTTP lib hot-reloads on DB change, the
   reviewer browses the candidates live in KiCad. The table is temporary and must
   be dropped (or tier-excluded) before the gate is enabled, since its rows
   intentionally reference `cern-*`.

## Worked example — `led_drivers` (done)

10 parts, demonstrating every path the policy produces:

- **Footprints:** 2 already native; 5 clean CERN→native swaps (exact pad-count
  match); 2 QFNs verified (pins/pads 1–25, EP = 25) then swapped to native
  `QFN-24-1EP`; 1 left on a terra-owned footprint. → **0 CERN footprints.**
- **Symbols:** `TLC5971RGE` → exact native `Driver_LED:TLC5971RGE`; the `CRD`
  (NSI450xx) → approved into `terra-diodes:Diode_CRD` (CERN body + added
  constant-current circle + text normalized); 4 ICs with no native equivalent
  (`MAX3967A`, `STCS05`, `TLC5920`, `TLC5925`) → approved into a new
  `terra-led-drivers` lib with text restyled to KiCad conventions
  (`Reference IC→U`, `Value ${DEVICE}→part name`, font `1.524→1.27mm`). → **0 CERN
  symbols.**

Lessons folded into the design: native **footprint** equivalents usually exist
(IPC-named CERN packages map to stock KiCad land patterns); native **symbol**
equivalents rarely do (only exact KiCad parts, e.g. `Driver_LED`), so most symbol
approvals are copy-to-terra plus human cleanup.

## Transition (enabling the gate)

The gate cannot flip on red. Each served (tier ≤ 2) table must first be made
green — `led_drivers` is the template. Order:

1. Land `tools/provenance.py` + `tools/approve_asset.py` (no enforcement yet).
2. Make each served table green (native swaps where possible, approve→terra
   otherwise). `led_drivers` already is.
3. Switch `generate_lib_tables.py` to terra-only registration.
4. Drop / tier-exclude the temporary `ab_test` table.
5. Enable `tests/test_provenance_gate.py` in `make verify`.

## Out of scope

- De-CERNing the **non-served** CERN library at scale (≈4,350 in-use CERN
  footprints still carry dangling `${CERN_3DMODEL_DIR}` 3D models; CERN 3D models
  were never vendored). Tracked separately; CERN is being wound down.
- Eventual deletion of the `cern_*` tables and `cern-*` libraries.
