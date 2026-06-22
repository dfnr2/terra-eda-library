# Footprint & 3D-model "waiting" tier

`terra_sym.pretty` (footprints) and `assets/3dmodels/legacy.3dshapes` (3D models)
hold assets carried in from the legacy libraries and the project harvests. Most
are not yet referenced by any terra database part or project board — they are
**waiting**, not orphaned: retained because they are expected to be adopted as
the catalog grows, not parked for deletion.

## Tiers

- **Active** — footprints referenced by a terra part (or an external board):
  ~14 in `terra_sym.pretty`, plus the curated per-category libs
  (`terra-diodes` / `terra-connectors` / `terra-optoelectronics` /
  `terra-test-points`). Generic package land patterns are referenced directly
  from KiCad's shipped libraries.
- **Waiting** — the remaining ~63 `terra_sym.pretty` footprints and their 3D
  models in `legacy.3dshapes`. `terra_sym` is registered in `fp-lib-table`, so
  they remain available; they simply have no consumer yet.

## Policy

- **Do not prune** waiting assets — they will be used eventually.
- The only removals are **true duplicates** of an asset already in use. A
  content-hash sweep (2026-06-22) found **no duplicate footprints** and **three
  duplicate 3D models** (byte-identical to the curated copies:
  `SM712-02HTG`, `560020-0320`, `Keystone-5017`); those legacy copies were
  removed and the referencing footprints repointed to the surviving curated ones.
- **Promotion:** when a part adopts a waiting footprint, move it into the
  appropriate curated `terra-<category>` lib (or switch to a KiCad-standard
  footprint), applying the `<Mfr>_<name>` convention for manufacturer-specific
  parts.

## The waiting set is derived, not hand-maintained

It is every `terra_sym.pretty` footprint not referenced by any row in
`db/terra.db` and not used by a board in the project trees (`nema-addon`,
`hotwire`, `target-led-kicad`, `abc4-spiro-cart-hw`, `abc4-spiro-hw`). Recompute
it rather than trusting a checked-in list, which would drift as parts are
promoted.
