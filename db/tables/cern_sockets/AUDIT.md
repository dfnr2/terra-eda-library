# cern_sockets — Human Audit

Source: CERN `Sockets` (167 IC sockets). Generated via `tools/cern_import.generate`.

## Automated
- [ ] `make cern_sockets-test` green (count 167, no dup unique_id, known-part 1-822473-1,
      all footprints AND symbols resolve, nicks registered).
- [ ] `uv run pytest -q` green.

## Sampling (≥ 20 parts)
- [ ] MPN matches; `pin_count` and socket type consistent with the description.
- [ ] `kicad_symbol` and `kicad_footprint` render in KiCad.

## Notes
- [ ] IC sockets (PLCC / QFN test / DIP / DIMM / TSOP). Own "Sockets" symbol lib
      (cern-sockets); one part uses the shared "Connectors" lib. No type tail.
- [ ] 3D: 31/167 (18%) — true uniform pin grids map to PinHeader/PinSocket; DIP-spaced and
      bespoke sockets (PLCC/QFN/DIMM) decline (the row-spacing guard prevents wrong
      2.54mm-row models) → human drop-folder.
- [ ] No terra reconciliation (new category).

## Sign-off
- Auditor: ______  Date: ______
