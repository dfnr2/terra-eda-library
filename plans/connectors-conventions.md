# connectors: per-pin symbol rows and generated 3D models

Conventions for every terra connector (Dave, 2026-11-22), backfilled the same day to
the vintage connector generators: `run_340` (EDAC 307), `run_370` (Molex KK 396
friction lock), `run_372` (Molex KK 396 round pin), `run_390` (TE MTA-156) and `run_395`
(Molex KK 156 41815). The card-edge (`run_380`) and DIN 41612 (`run_400`) generators
follow them from the start.

## What every connector gets

- **A symbol, a footprint and a 3D model.** Stock KiCad footprints bring KiCad's own
  models. Footprints terra writes reference a model named after the footprint in
  `assets/3dmodels/terra-connectors.3dshapes/`.
- **Two rows per part, with the same MPN and parameters.**
  - The whole-connector row: a one-body symbol, usually stock `Connector_Generic`.
  - The per-pin row: `variant = 'pins'`, `unique_id = '<Mfr>-<MPN>-pins'`, with a
    symbol that has one unit per pin, so each contact can sit next to its signal.

  `unique_id` is the primary key, so the two rows can't literally share one; the
  `-pins` suffix copies the 74xx `-IEEE` rows. KiCad's database library keys on
  `unique_id`, so both rows appear in the chooser.
- **Retro-documented parts.** A connector documented for use in a retro computer or
  game may be added even without a manufacturer drawing. This relaxes the "only series
  with a parked drawing" rule from `plans/connectors-edac-307-card-edge.md`.

## Per-pin symbols

These are generic, one per pin-numbering scheme. They're written into
`terra_symbols_connectors` by `db/tables/connectors/_connkit.py`, which the generators
call, so the symbols are rebuilt with the rows:

- `Conn_PerPin_NN`: pins 1-NN (2-18 exist so far).
- `Conn_PerPin_EdgeLetter_2xNN`: card edge numbered 1-NN on one side and A, B, ...
  (no G/I/O/Q) on the other.

Each unit copies the stock `Conn_01x01` style: a small box with one passive pin, the
pin name hidden and the number shown. A unit is named `-<pin>`. KiCad 10 shows a named
unit as reference + name, so placed units read `J1-12` and `J1-A` (checked with
`kicad-cli sch export svg`).

## Generated 3D models

- **Where the geometry lives.** A generator that writes footprints also defines
  `model_specs()`: `{footprint: [primitive, ...]}`, using boxes and round or square
  pins in footprint coordinates (z up from the board), taken from the drawing. The
  primitives are listed in `_connkit.py`.
- **Building.** `make connector-models` runs `tools/make_connector_models.py` under
  headless FreeCAD (`QT_QPA_PLATFORM=offscreen`, which keeps colours in the STEP). It
  builds only new or changed specs, using the hash manifest `generated.json`. The
  generators themselves never need FreeCAD.
- **Drift check.** `tests/test_connector_models.py` fails when a spec has no current
  model, or when a footprint references a missing model.
- **Accuracy.** The models are block approximations from the drawings' dimensions:
  housing outline and height, and pin size, height and tail. They're good for
  clearance and enclosure checks, not for photorealism. Use a vendor STEP instead when
  one downloads cleanly.
- **Size.** The 94 models so far average about 74 KB.

## Results (2026-11-22)

- 228 vintage connector parts, each with a `-pins` twin: 456 rows.
- 94 generated models. The 3192 long-pin builds got their own footprints
  (`_Pin16.18mm`, `_Pin32.51mm`) so their models show the real pin length.
- The `3192_1x17` plain footprint was dropped; only the 16.18 mm build exists in that
  size.
- `make verify` is clean: 219 tests pass.
