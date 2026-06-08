# cern_erni — Human Audit

Source: CERN `ERNI` connectors (78 parts). Generated via `tools/cern_import.generate`.

## Automated
- [ ] `make cern_erni-build` green; covered by `tests/test_cern_connectors.py` (row count,
      no dup unique_id, symbols are the shared cern-connectors lib, all footprints AND
      symbols resolve, nicks registered).
- [ ] `uv run pytest -q` green.

## Sampling (≥ 20 parts)
- [ ] MPN matches the datasheet; `pin_count` and series consistent with the description.
- [ ] `kicad_symbol` (cern-connectors) and `kicad_footprint` (cern-cern_erni-*) render in KiCad.

## Notes
- [ ] Connector vendor; shares the "Connectors" symbol lib; no type tail.
- [ ] 3D: best-effort via resolve_connector (D-Sub, Molex KK-254/PicoBlade, generic pin headers/sockets from clean standard-pitch grids); proprietary/mezzanine -> human drop-folder.
- [ ] No terra reconciliation (new category).

## Sign-off
- Auditor: ______  Date: ______
