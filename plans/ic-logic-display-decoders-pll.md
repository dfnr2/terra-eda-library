# ic_logic: 7-segment display decoders and HC/HCT PLLs (`run_350_display_decoders_pll.py`)

**Date:** 2026-11-25
**Status:** Done; 9 devices, 21 rows (see Results)

## Scope

ic_logic had the TTL BCD decoders (74LS46-49, 74LS246-249), the CMOS CD4543B, CD4056B
and CD4033B, the CD4046B PLL and the 74LS629 VCO. All of those come from
`run_320`/`run_330`, which build rows from KiCad's stock 74xx and 4xxx symbol
libraries. Neither library has a 4511, 4026, 74HC4046A, 7046A, 9368 or 14495 symbol,
so those parts were missing. This generator writes their rows by hand:

| Kind | Part | Maker |
|---|---|---|
| BCD 7-segment | CD4511B latch/decoder/driver | TI |
| BCD 7-segment | CD4026B decade counter with 7-segment outputs | TI |
| BCD 7-segment | CD74HC4511 | TI |
| Hex (0-F) 7-segment | DM9368 latch/decoder/driver, constant-current outputs | Fairchild |
| Hex (0-F) 7-segment | MC14495-1 latch/decoder LED driver | Motorola |
| PLL | CD74HC4046A, CD74HCT4046A | TI |
| PLL with lock detector | CD74HC7046A, CD74HCT7046A | TI |

## Sources

Every data sheet is parked locally. Rows point at it through
`${TERRA_EDA_LIB}/datasheets/...`, never at a web URL.

| Data sheet | File |
|---|---|
| CD4511B (SCHS072B, Harris scan) | `datasheets/ti/cd4511b.pdf` |
| CD4026B/CD4033B (SCHS031B, Harris scan) | `datasheets/ti/cd4026b.pdf` |
| CD54/74HC4511, CD74HCT4511 (SCHS279E) | `datasheets/ti/cd74hc4511.pdf` |
| CD54/74HC(T)4046A (SCHS204J) | `datasheets/ti/cd74hc4046a.pdf` |
| CD74HC(T)7046A (SCHS218C) | `datasheets/ti/cd74hc7046a.pdf` |
| Fairchild DM9368 (DS009796, Dec 2001) | `datasheets/fairchild/dm9368-7-segment-decoder-driver-latch.pdf` |
| Motorola MC14495-1 | `datasheets/motorola/mc14495-1-hex-7-segment-latch-decoder-driver.pdf` |

- The TI sheets came from `ti.com/lit/ds/symlink/`. Each one ends with TI's
  package-option addendum, printed 18-Sep-2026.
- The DM9368 sheet is Fairchild's own PDF. It came from the Wayback Machine's copy of
  `fairchildsemi.com/ds/DM/DM9368.pdf`, captured in 2003.
- The MC14495-1 sheet is the Motorola CMOS data book page. It came from the futurlec
  mirror that KiCad's `Driver_LED:MC14495P` symbol links to.
- The two Harris-era CD4xxx sheets are image scans, so their parametrics were read
  from the page images. pdftotext gets nothing from them.

## Lifecycle

Digi-Key and Mouser refuse scripted fetches (403 and an Access Denied captcha). So the
TI parts take their status from the addenda above. Each status matches the TI product
page.

| Part | Rows | Status |
|---|---|---|
| CD4511B | E, NSR | Active. There is no SOIC (D) package, so the 5.3 mm SOP (NS) is the SMD row. |
| CD4026B | E, NSR | Active. Same packages as the CD4511B. |
| CD74HC4511 | E, M96 | Active. The CD74HC4511M tube is Obsolete, so the M96 reel code is used. |
| CD74HCT4511 | (none) | CD74HCT4511E is **NRND**, and it is the only HCT code, so it is not generated. |
| CD74HC(T)4046A, CD74HC(T)7046A | E, M | Active |
| CD74HC9046A | (none) | TI has no data sheet or product page for it (symlink returns 404), so it is not generated. |
| DM9368N | N | **Obsolete.** Digi-Key lists the onsemi DM9368N as obsolete. |
| MC14495P1, MC14495DW1 | P1, DW1 | **Obsolete.** A Digi-Key search finds no listing (2026-11-25), and onsemi does not carry it. |

The two hex decoders are kept as Obsolete rows for restorations, which buy NOS or
surplus stock. `run_315_ttl_standard.py` set that precedent.

## Decisions

- **Packages.** Each part gets one PDIP row and one 1.27 mm SMD row, as in run_315 and
  run_330. TSSOP, CDIP and the small T&R codes are left out.
- **Footprints.**
  - NS SOP: `Package_SO:SOIC-16W_5.3x10.2mm_P1.27mm`, whose stock tags are
    `Texas_NS0016A`.
  - Motorola case 751G (DW): `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm`.
- **`value`.** The value is what a schematic shows: `CD4511B`, `CD4026B`, `74HC4511`,
  `74HC4046A`, `74HCT4046A`, `74HC7046A`, `74HCT7046A`, `DM9368`, `MC14495-1`.
- **`logic_family`.**
  - The DM9368 is Fairchild 9300-series TTL, so its family is `9300`.
  - The MC14495-1 is `4000B`, Motorola CMOS MSI. Its supply range is 4.5-18 V, not
    3-18 V.
- **`function_category`.**
  - The PLLs use a new value, `pll`. CD4046B is still `other`, from the run_330 harvest.
  - The CD4026B is a `counter`.
  - The rest are `decoder`.
- **HC PLL supply range.** `supply_voltage_min` is 3.0 V. The VCO section needs
  3-6 V, although the digital section runs from 2 V; the description says so.
- **Output drive is written as the data sheet states it.**
  - CD4511B: NPN emitter-follower source outputs, 25 mA. `voh_min` is the sheet's
    4.1 V, not the 4000B 4.95 V.
  - DM9368: 16-22 mA constant-current source outputs.
  - MC14495-1: 290 Ω internal series resistors, and pin 11 (j) is open-drain.
- **`allow_substitution`.** It is `Yes` for the TI parts, which have second sources
  (MC14511, HEF4511, NXP 74HC4046A). It is `No` for the single-source hex decoders.

## Symbols

KiCad has no stock symbol with a correct pinout for any of these parts. So they are
drawn in `kicad_symbols/terra_symbols_ic_logic.kicad_sym`, from each data sheet's pin
diagram. Each symbol has VDD/VCC and VSS/GND power pins. Every pin number and pin type
was checked against the data sheet.

- **`4511`** serves the CD4511B and the CD74HC4511, whose pinouts are identical (the
  HC sheet's D0-D3 are A-D). Both parts also get a variant `IEEE` row on the stock
  `4xxx_IEEE:4511`, which matches pin for pin.
- **`4026`:**
  - 1 CLK, 2 INH, 3 DEI, 4 DEO, 5 CO, 14 ungated c, 15 RESET.
  - Segments on 6, 7 and 9-13.
- **`74HC4046`** serves the HC and HCT 4046A. Pin numbering matches the CD4046B, but
  pin 15 is PC3OUT where the CD4046B has its zener. `4xxx:4046` labels that pin ZOUT,
  so it is not reused.
- **`74HC7046`:** pin 1 is LD (lock detect out), pin 15 is CLD (lock-detect capacitor),
  and there is no PCP or PC3.
- **`9368`:** pin 4 is the bidirectional ~BI/~RBO, pin 5 is ~RBI, and pin 3 is ~LE.
- **`MC14495-1`:** the stock `Driver_LED:MC14495P` matches the pin numbers. It is not
  used because it calls pin 11 `~{VCR}` and makes it an input. On the MC14495-1, pin 11
  is the open-drain j output, so an LED on that pin would fail ERC. The stock
  description also says "BCD" for a hex decoder.

## Results (2026-11-25)

- `run_350_display_decoders_pll.py` writes 9 devices and 21 rows:
  - CD4511B: 4 rows (2 plus 2 IEEE).
  - CD4026B: 2 rows.
  - 74HC4511: 4 rows (2 plus 2 IEEE).
  - DM9368: 1 row.
  - MC14495-1: 2 rows.
  - 74HC4046A, 74HCT4046A, 74HC7046A and 74HCT7046A: 2 rows each.
- No unique_id collides with an existing row. The generator fails loudly on a
  duplicate, on a missing data sheet, or on a missing terra symbol.
- `make ic_logic-generate && make ic_logic-build`: `db/ic_logic.db` now has 896 rows.
- `pytest tests/`: 218 passed, 1 failed. The failure is
  `test_terra_owned_libs_are_in_generated_lib_tables`, for
  `terra_symbols_voltage_regulator`, a library another table's work added. It is not
  caused by this change, and a top-level `make` regenerates the lib tables.
- All six new symbols parse and plot with `kicad-cli sym export svg`.

## Follow-ups

- Existing rows that this work showed to be wrong, which run_330 and run_320 own:
  - **CD4033BE:** the run_330 row says Active, but the CD4026B/CD4033B addendum shows
    it is **NRND**.
  - **CD4046B:** its `function_category` is `other` and could be `pll`.
  - **74LS46-49:** their rows still point at web data sheet URLs and say Active.
- CD74HCT4511E, if Dave wants NRND rows for repairs.
- Other hex decoders, if a board needs them: TIL311 (display with built-in decoder),
  MC14558, 74LS48 variants.
