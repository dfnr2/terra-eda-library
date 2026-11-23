# capacitors_electrolytic_th: general-purpose radial and axial electrolytics

Part of `plans/vintage-computer-parts.md` phase 9. The table so far held only the
Chemi-Con KYC, a low-ESR radial. Vintage boards want plain general-purpose radials and,
on restorations, axials. Both families go into the existing table: radial vs axial is
core `package`, so the schema doesn't change.

## Families

| Generator | Family | Package | Rows |
|---|---|---|---|
| `run_510_panasonic_eca.py` | Panasonic M-A (ECA-xxM), 85 °C 2000 h | Radial | 130 |
| `run_520_vishay_021asm.py` | Vishay BCcomponents 021 ASM, 85 °C | Axial | 102 |

**Why these two:**
- **M-A:** the long-running Panasonic general-purpose radial, 6.3-450 V.
- **021 ASM:** the former Philips 2222 021 series, so 1970s-80s parts lists often name
  it by its old 12NC. Vishay points its retired ELM/EBM axials at it.

Both set `low_esr = 'no'` explicitly, because the column defaults to `'yes'`.

## Sources (2026-11-23)

**Panasonic M-A**
- **Data sheet:** `datasheets/panasonic/panasonic-m-a-series-radial-aluminum-electrolytic.pdf`.
  It holds the cover and the five M-A pages (catalog pages 81-85, dated 01-Sep-25) of
  Panasonic's 2025.9 aluminum electrolytic catalog.
- **Status in the catalog:** the series is flagged "Some part numbers are discontinued".
  Seven 160-400 V rows are marked EOL and are left out: ECA2CM331, 2CM471, 2DM221,
  2DM331, 2EM221, 2VM101 and 2GM101.
- **Part numbers:** the catalog prints them without a hyphen (ECA1HM101). Panasonic's
  product pages and distributors use ECA-1HM101, which is the stored MPN. Both forms
  go in keywords.
- **Ratings stored:** ripple current at 120 Hz / 85 °C. tan δ (120 Hz) goes in the
  description. The catalog gives no ESR, so `esr_ohm` stays blank.

**Vishay 021 ASM**
- **Data sheet:** `datasheets/vishay/vishay-021asm-axial-aluminum-electrolytic.pdf`,
  Vishay document 28325, revision 16-Sep-16, from vishay.com. Vishay's product page is
  current.
- **Rows:** one per Table 3 entry, with ripple current (100 Hz / 85 °C), ESR (100 Hz),
  and tan δ and 10 kHz impedance in the description.
- **Endurance:** from the life code. L1 is 1000 h, L2 2000 h and L3 5000 h, all at 85 °C.
- **Which ordering code:** form AA (loose axial leads) where Table 3 has one, which is
  case 10×30 and up. Otherwise form BA, taped in an ammo box with straight leads.

## Validation in the generators

- **ECA:** the part number's value code (`221`, `2R2`) must match the catalog
  capacitance. The voltage code must be one the catalog defines.
- **021 ASM:** the ordering code's form digit, voltage digit and value code must match
  the row. In the value code, 8 means ×0.1 and 9 means ×1. The 905xx codes are a
  separate numbering and are not decoded.
- **Both:** duplicate part numbers fail the build.

## Symbols and footprints

- **Symbol:** stock `Device:CP` for both families.
- **ECA footprints:** stock `Capacitor_THT:CP_Radial_D<D>mm_P<F>mm`, using the
  catalog's lead space for each diameter:

  | Diameter (mm) | 5 | 6.3 | 8 | 10 | 12.5 | 16 | 18 |
  |---|---|---|---|---|---|---|---|
  | Lead space (mm) | 2.0 | 2.5 | 3.5 | 5.0 | 5.0 | 7.5 | 7.5 |

- **021 ASM footprints:** stock `Capacitor_THT:CP_Axial_L<L>mm_D<D>mm_P<F>mm_Horizontal`.
  KiCad has one for each of the 13 case sizes, at the data sheet's minimum bend pitch
  (Table 1, F min). The 3D models come with the footprints.

## Lifecycle (Mouser, 2026-11-23)

**ECA:** all 130 catalog part numbers are listed at Mouser.
- Most are in stock.
- Several 160-400 V parts are non-stocked with a 37-week lead time. They are still
  orderable, so they stay Active.

**Not added:** Mouser also lists some ECA values that the 2025 catalog no longer shows,
such as ECA-1CM331 and ECA-1EM100. These look like remaining stock and are not added.

**021 ASM:** all 102 ordering codes are listed at Mouser. Most are in stock. A few are
non-stocked with an 8-10 week lead time, so they also stay Active.

## Results (2026-11-23)

- 130 ECA rows and 102 021 ASM rows. The table now has 350 rows.
- All 20 footprints resolve in KiCad 10's stock libraries.
- `make verify` is clean: 219 tests pass.
