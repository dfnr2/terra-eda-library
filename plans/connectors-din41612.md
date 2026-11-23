# connectors: DIN 41612 Eurocard connectors (`run_400_din41612.py`)

Part of `plans/vintage-computer-parts.md` phase 8. Follows
`plans/connectors-conventions.md`: each part has a `-pins` per-pin row and a 3D model.

## Parts

All six are Harting DIN-Signal parts at performance level 2 (IEC 60603-2), with solder
pins. Each layout comes as an angled male for the plug-in card and a straight female
for the backplane.

| Layout | Male, angled (card) | Female, straight (backplane) |
|---|---|---|
| Type C, 96 contacts, rows a+b+c | 09 03 196 6921 (C096MS) | 09 03 296 6825 (C096FS) |
| Type B, 64 contacts, rows a+b | 09 02 164 6921 (B064MS) | 09 02 264 6825 (B064FS) |
| Type C, 64 contacts, rows a+c | 09 03 164 6921 (C064MS) | 09 03 264 6825 (C064FS) |

**Why Harting:** KiCad drew its stock Connector_DIN footprints from Harting's DIN 41612
catalogue. Part numbers are stored without spaces (`09031966921`), as distributors list
them. Each part gets its own row plus a `-pins` twin: 12 rows.

## Sources (2026-11-23)

- **Data sheets:** downloaded from harting.com, after accepting Harting's Download Terms
  of Use at Dave's request. They are in `datasheets/harting/harting-<pn>-din41612-<id>-datasheet.pdf`.
  The 09031966921 copy came from Mouser and is the same Harting PDF.
- **Drawings:** `datasheets/harting/harting-din41612-catalogue-chapter01.pdf`, Harting's
  DIN 41612 catalogue, chapter 01.

**Ratings, the same in all six data sheets:**
- 2 A rated current at 20 °C; the data sheets include a derating curve.
- −55 to +125 °C limiting temperature.
- 1 kV r.m.s. test voltage.
- Contact resistance ≤ 20 mΩ; insulation resistance > 10¹² Ω.
- At least 400 mating cycles.
- Insert: RAL 7032 pebble grey, UL94 V-0.
- Coding with loss of contacts (coding pin 09 02 000 9901).

No rated working voltage is given, so `voltage_rating` stays blank.

## Symbols, footprints and models

**Whole-connector symbols:**
- Stock `Connector:DIN41612_02x32_AB` and `_AC` for the two 64-contact layouts.
- KiCad has only a split 96-contact symbol, so the 96 uses a terra symbol,
  `DIN41612_03x32_ABC`: rows a and b down the left, row c on the right beside a.

**Per-pin symbols:** `Conn_PerPin_DIN41612_{AB,AC,ABC}_{2,3}x32`, numbered a1.., b1..,
c1.. as the footprints are.

**Footprints:** stock `Connector_DIN:DIN41612_{B,C}_{2,3}x32_{Male_Horizontal,Female_Vertical}_THT`.

**Models:**
- Type C uses KiCad's own 3D models.
- KiCad ships no type B models, although its type B footprints reference them. Both
  type B footprints are copied unchanged into `terra_footprints_connectors`, with the
  model path pointed at a block model that `run_400` generates.
- The block models come from catalogue chapter 01: the male drawing on page 3 and the
  female drawing on page 5.
  - Male: 85.2 mm body, 8.6 mm high, 3 mm tails.
  - Female: 85 mm body, 8.1 mm deep, 11.6 mm high, 7.9 mm flanges, 4.5 mm tails.
- A KiCad render shows them sitting like the stock type C models.

## Follow-ups

- **Lifecycle:** all six have current product pages on harting.com, and Mouser's search
  listed them on 2026-11-22 with data sheets attached. Stock levels were not checked.
- **Other variants not generated:** press-fit, performance levels 1 and 3, the 32-contact
  builds, and straight male or angled female ("inverse") parts.

## Results (2026-11-23)

- 12 rows.
- New symbols: 1 whole-connector and 3 per-pin.
- 2 copied type B footprints, each with a generated model.
- `make verify` is clean: 219 tests pass.
