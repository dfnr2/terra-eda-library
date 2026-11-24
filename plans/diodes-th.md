# diodes_th: through-hole diodes

Started 2026-11-24. Terra had no common through-hole diodes: the `diodes` table holds
8 harvested parts, mostly SMD. `diodes_th` follows `resistors_th`, `capacitors_th` and
`crystals_th`:
- It reuses the `diodes` type columns, so it is listed in `PAIRS` in
  `tests/test_schema_consolidation.py` next to `diodes`.
- KiCad shows it as its own category.

## Families

| Generator | Parts | Package | Rows |
|---|---|---|---|
| `run_300_onsemi_axial.py` | 1N914, 1N4148, 1N4448 small-signal switching | DO-35 | 3 |
| | 1N4001G-1N4007G, 1 A rectifiers | DO-41 | 7 |
| | 1N5817G/18G/19G, 1 A Schottky | DO-41 | 3 |
| | 1N5400G/01G/02G/04G/06G/07G/08G, 3 A rectifiers | DO-201AD | 7 |
| `run_310_small_schottky.py` | Vishay BAT85S-TAP, Vishay BAT43-TAP, Microchip 1N5711 | DO-35 | 3 |

**Why onsemi:** it is the one maker with current data sheets for all four families, and
each part was in stock at Mouser on 2026-11-24.
- **Ordering codes:** the bulk, bag or box codes.
- **1N400x:** the old leaded codes are marked DISCONTINUED in onsemi's own table, so
  the Pb-free `G` codes are used.
- **1N540x:** onsemi makes no 1N5403 or 1N5405.

**Data sheets** (`datasheets/onsemi/`):
- `1n914-d.pdf` (Rev 6, 2024)
- `1n4001-d.pdf` (Rev 18, 2024)
- `1n5817-d.pdf` (Rev 11, 2021)
- `1n5400-d.pdf` (Rev 12, 2021)

**Columns:**
- `value` is the JEDEC number.
- `voltage_rating` is VRRM.
- `current_rating` is IO, and `forward_current` is the DC IF: 300 mA for the
  small-signal parts, otherwise the same as IO.
- `forward_voltage` is the data sheet's maximum VF at its test current.
- IFSM, trr and CT go in the description.

**Symbols and footprints:** stock `Diode:<JEDEC>`, with the footprint each symbol names:
DO-35 at 7.62 mm, DO-41 at 10.16 mm and DO-201AD at 15.24 mm, all horizontal.

**Small-signal Schottky diodes:** onsemi makes none of these, so each comes from its
current maker. All three were in stock at Mouser on 2026-11-24.
- **BAT85S:** Vishay's current DO-35 version of the BAT85; Nexperia's original isn't
  stocked. Data sheet `datasheets/vishay/bat85s.pdf` (doc 85513). It uses the stock
  `Diode:BAT85` symbol.
- **BAT43:** Vishay, data sheet `datasheets/vishay/bat42-bat43.pdf` (doc 85660). ST's
  BAT43 is obsolete.
- **1N5711:** Microchip (formerly Microsemi), data sheet
  `datasheets/microchip/1n5711-1n5712-schottky-lds-0040.pdf` (LDS-0040). Vishay's and
  ST's are obsolete.
  - The stocked code is the tin-lead commercial part, so `rohs = 'No'`. The e3 RoHS
    version isn't stocked.
  - `voltage_rating` is the 50 V VRWM; the 70 V breakdown is in the description.
  - Microchip's site refuses plain fetches, so the PDF is Mouser's copy, downloaded
    through Chrome.
  - There is no Microchip product page, so `manufacturer_link` is blank.

## Results (2026-11-24)

- 23 rows, 23 parts.
