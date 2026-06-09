# cern_leds_displays — Human Audit

Source: CERN `LEDs & Displays` (514 parts). Generated via `tools/cern_import.generate`.

## Automated
- [ ] `make cern_leds_displays-test` green (count 514, no dup unique_id, known-part
      597-3301-507F, color sane, all footprints AND symbols resolve, nicks registered).
- [ ] `uv run pytest -q` green.

## Sampling (≥ 20 parts spanning colors / types)
- [ ] MPN matches the datasheet; `color` matches; `package`/`pin_count` match.
- [ ] `kicad_symbol` and `kicad_footprint` render in KiCad.

## tail derivation (color, wavelength_nm, + datasheet params)
- [ ] `color` comes from CERN's dedicated `Color` column (Green/Red/Blue/Yellow/Red-Green/
      Red/Green/Blue/'3x Red/Green'/…), falling back to the symbol name where the column is
      blank — 442/514 coloured.
- [ ] `wavelength_nm` parsed from the description where stated ("590nm"→590) — 16 parts.
- [ ] `luminous_intensity`, `forward_voltage_v`, `current_max_ma`: **not in the CERN
      database** (datasheet parameters). Columns added; blank now, to be filled by the
      datasheet sweep. Confirm the column names/units.

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
