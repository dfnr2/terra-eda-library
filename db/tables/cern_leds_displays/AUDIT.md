# cern_leds_displays — Human Audit

Source: CERN `LEDs & Displays` (514 parts). Generated via `tools/cern_import.generate`.

## Automated
- [ ] `make cern_leds_displays-test` green (count 514, no dup unique_id, known-part
      597-3301-507F, color sane, all footprints AND symbols resolve, nicks registered).
- [ ] `uv run pytest -q` green.

## Sampling (≥ 20 parts spanning colors / types)
- [ ] MPN matches the datasheet; `color` matches; `package`/`pin_count` match.
- [ ] `kicad_symbol` and `kicad_footprint` render in KiCad.

## tail derivation (color)
- [ ] `color` is a colour word parsed from the symbol name (Green 107, Red 87, Yellow 49,
      Blue 48, Red-Green 25, …); blank (176) for light pipes, bargraphs, 7-segment without a
      colour word, and device-named symbols. Confirm acceptable.

## 3D model coverage
- [ ] 222/514 (43%). Chip LEDs at 0402/0603 map to KiCad diode chip models (D_0402/0603 —
      same body); blank-package vendor THT LEDs, PLCC, and odd chip codes (0805/1206/1208/
      1210) decline → human drop-folder. Note: proper LED_<size> models would need
      table-aware package dispatch (package "0805" is ambiguous across part types) — future.
- [ ] LEDs use the shared ICs-And-Semiconductors SMD/THD footprint libs (no new footprint lib).

## Known carve-outs
- [ ] Intra-CERN MPN-collision variants kept distinct via `Part Number Nocolon`.
- [ ] No terra reconciliation (new category; legacy `leds` table is separate).

## Sign-off
- Auditor: ______  Date: ______
