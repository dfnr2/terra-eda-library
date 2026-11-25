# ic_analog: 555-family timers and PLL tone decoders

**Date:** 2026-11-25
**Status:** Done: 27 rows (24 timers, 3 tone decoder / PLL). See Results.
**Scope:** add the classic 555/556 timers (bipolar and CMOS), the LM567 tone decoder and
the NE565 PLL to the existing `ic_analog` table. Generators:
`db/tables/ic_analog/run_310_timers_555.py` and `run_320_tone_decoders.py`.

## Decisions

- **Table:** `ic_analog`, no new columns. The `analog` tail fits: `function_type`,
  `channels` (1 for 555, 2 for 556) and `supply_voltage_min/max`. Maximum frequency,
  supply current, output drive and bipolar vs CMOS go into `description` and
  `keywords`. `resolution_bits` and `interface` stay NULL.
- **`function_type`:** `timer` for the 555/556 parts, `tone-decoder` for the LM567C and
  `pll` for the NE565, which is a general-purpose PLL rather than a tone decoder.
- **Packages:** PDIP is the primary row. The SOIC twin is added when the same data sheet
  lists it as orderable (the ic_logic N/D convention). Where TI has obsoleted the SOIC
  tube, the reel code is used instead (NE555DR, SA555DR, SE555DR, NE556DR, TLC555CDR,
  TLC555IDR, LMC555CMX/NOPB), as ic_logic did for SN7404DR. The description marks these
  rows "reel".
- **Grades:** both the commercial (C) and industrial (I) grades of the TLC555 and TLC556,
  since both are orderable in PDIP and SOIC. SA556N is included next to SA555; it is
  the SA556's only orderable code.
- **`value`** is the device name (`NE555`, `TLC555`, `LM567C`, `NE565`), shared by grades.
- **`unique_id`:** `Texas_Instruments-<MPN>` to match the table's existing TI row;
  `Renesas-<MPN>`, `Signetics-<MPN>`. TI's `/NOPB` stays in the MPN.
- **Supply:** taken from the recommended operating conditions where the sheet gives them.
  Exceptions are noted in the generator docstrings:
  - LM555: the electrical table gives 4.5-16 V; the ROC table lists only an 18 V maximum.
    16 V is used.
  - LMC555: specified from 1.5 V. No recommended maximum is given, so the 15 V absolute
    maximum is used, and the description says so.
  - LM567C: the electrical table's 4.75-9 V is used; the ROC table prints 3.5-8.5 V.
  - NE565: ±6 V to ±12 V split supply, stored as the 12-24 V total span. The column has
    no split-supply form.
- **Operating temperature** per grade, from each sheet's ROC table or TI's orderable
  data: NE 0/70, SA -40/85, SE -55/125, TLC555/556 C 0/70 and I -40/85, LMC555C -40/85,
  ICM755x I -25/85, LM567C 0/70, NE565 0/70.

## Sources (`datasheets/`)

| File | Document |
|---|---|
| `ti/ne555.pdf` | NA555/NE555/SA555/SE555, SLFS022K (Mar 2026) |
| `ti/ne556.pdf` | NA556/NE556/SA556/SE556, SLFS023I (Mar 2025) |
| `ti/tlc555.pdf` | TLC555, SLFS043K (Jan 2026) |
| `ti/tlc556.pdf` | TLC556/TLC556M, SLFS047D (Mar 2026) |
| `ti/lmc555.pdf` | LMC555, SNAS558O (Nov 2026) |
| `ti/lm555.pdf` | LM555, SNAS548D (Jan 2015; TI's current revision) |
| `ti/lm567c.pdf` | LM567/LM567C, SNOSBQ4F (Jan 2022) |
| `renesas/icm7555-icm7556.pdf` | ICM7555/ICM7556, FN2867 Rev 10.01 (Mar 2020) |
| `signetics/ne565-phase-locked-loop.pdf` | NE/SE565 product specification (Jul 1988), a scanned copy mirrored at elektronikjk.pl |

The NE565 scan's text layer is poor OCR. Its figures were read from the page images.

## Lifecycle (2026-11-25)

Mouser and Digi-Key refuse scripted fetches, so lifecycle comes from the manufacturers:

- **TI:** per-ordering-code `marketingStatusDescription` in the ti.com product pages'
  orderable data, which matches the package addenda at the back of the 2025-26 sheets.
  Every code used is ACTIVE. Obsolete tubes that were skipped: NE555D, SA555D, NE556D,
  TLC555CD, TLC555ID, LMC555CM/NOPB.
- **Renesas:** part-detail pages show ICM7555IPAZ and ICM7555IBAZ Active and
  **ICM7556IPDZ Obsolete**; the ICM7556 product page is marked Obsolete too. Digi-Key and
  Octopart also list ICM7556IPDZ as obsolete (search snippets). No Renesas PDN naming it
  was found. It is kept, flagged Obsolete, because existing designs use it.
- **NE565N:** Obsolete. Signetics and Philips/NXP no longer make it. Kept for
  restorations.

## Symbols and footprints

- All stock KiCad `Timer:` symbols, one per device and package (`NE555P`/`NE555D`,
  `SA555P/D`, `SE555P/D`, `LM555xN/xM`, `NE556`, `SA556`, `TLC555xP/xD`, `LMC555xN/xM`,
  `ICM7555xP/xB`, `ICM7556`, `NE567`). Each pinout was checked against its data sheet.
- **TLC556** has no stock symbol. Its pinout (TLC556 table 4-1) matches the NE556 pin for
  pin, so it uses `Timer:NE556`.
- **LM567C** uses `Timer:NE567`. Pins 1-8 match (output filter, loop filter, input, V+,
  timing R, timing RC, GND, output).
- **NE565** uses the new custom symbol `terra_symbols_ic_analog:NE565`, drawn from the
  N-package pinout: V- 1, inputs 2/3, VCO out 4, phase-comparator VCO input 5, reference
  out 6, demodulated out 7, external R 8, external C 9, V+ 10. Pins 11-14 are hidden NC
  pins.
- Footprints are stock: `Package_DIP:DIP-8_W7.62mm`, `DIP-14_W7.62mm`,
  `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`, `SOIC-14_3.9x8.7mm_P1.27mm`.

## Results (2026-11-25)

| Family | Devices | Rows |
|---|---|---|
| Bipolar 555 (TI) | NE555, SA555, SE555, LM555 | 8 |
| Bipolar 556 (TI) | NE556, SA556 | 3 |
| CMOS 555 (TI) | TLC555 (C, I), LMC555 | 6 |
| CMOS 556 (TI) | TLC556 (C, I) | 4 |
| CMOS 555/556 (Renesas) | ICM7555, ICM7556 | 3 |
| Tone decoder (TI) | LM567C | 2 |
| PLL (Signetics) | NE565 | 1 |
| **Total** | | **27** |

`make ic_analog-generate && make ic_analog-build` builds 28 rows, counting the existing
PCA9306. Every symbol and footprint reference resolves. `uv run pytest tests/`, without
`test_cern_connectors.py` (it rebuilds CERN tables), gives 219 passed. Rows were
spot-checked against the sheets: supply range, temperatures, symbol and footprint.

**Left out:**
- **NE567, LM567 (military):** TI has no product page for either and sells only the
  LM567C. A Philips/onsemi NE567 could be added as Obsolete if a board needs it.
- **NE565D:** the SO-14 has a different ("non-standard") pinout. SE565 and the F
  (cerdip) codes are also left out.
- **SE556:** ceramic DIP only. **NA555/NA556:** not requested.
- **Ceramic, LCCC, TSSOP, VSSOP, SOP, SSOP and DSBGA codes:** not added.
- **ICM7555CBAZ:** a commercial-grade SOIC with no PDIP twin. **LMC555IMX/NOPB:** an
  industrial SOIC with no PDIP twin.
- **Microchip MIC1555 (SOT-23-5):** skipped. It has a different pinout and no stock
  symbol.

## Follow-ups

- Recheck lifecycle at Mouser/Digi-Key by hand. The TI and Renesas pages were the only
  sources that scripts could reach.
- Add a SOT-23 CMOS 555, such as the MIC1555, with a custom symbol if a design needs
  one.
