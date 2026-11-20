# Microchip PIC32CM PL10 microcontrollers

**Date:** 2026-11-20
**Status:** done (see Results)
**Why:** Dave is using these 5V Cortex-M0+ parts for the unified retro keyboard
project.

## Scope

`ic_microcontrollers`, `run_320_pic32cm_pl10.py`. Source: PIC32CM6408PL10028/032/048/064
Data Sheet, DS40002667A (2025, Preliminary), in `datasheets/microchip/`.

- Only the 64 KB / 8 KB devices, PIC32CM6408PL10 in 28/32/48/64 pins: the datasheet
  covers only these. The 32 KB (PIC32CM3204PL10) and 128 KB (PIC32CM1216PL10) family
  members have their own datasheets and can be added the same way.
- Every tube/tray ordering code in Table 41-1, both temperature grades
  (I = -40 to 85 C, E = -40 to 125 C). Tape-and-reel (T) codes are left out.

## Results

18 rows: 28-pin SPDIP/SSOP/VQFN, 32-pin TQFP/VQFN, 48-pin TQFP/VQFN, 64-pin TQFP/VQFN,
each in -I and -E. The generated codes match Table 41-1 exactly.

- **Lifecycle:** all Active on Digi-Key, "In Production" on microchip.com (2026-11-20).
- **Parameters:** 24 MHz, 1.8-5.5 V, 64 KB flash (a 1 KB high-endurance region,
  10k cycles), 8 KB SRAM, 2 SERCOMs (USART/SPI; I2C on SERCOM0 only), 3 TC + TCC0,
  12-bit ADC and PTC with 16/20/25/29 channels, I/O 22/26/41/55. Active 5.2 mA at
  24 MHz, standby 2 µA.
- **Symbols:** 8 new symbols in `terra_symbols_ic_microcontrollers`, one per package
  layout, generated from the section 2.3 pin table (`db/tables/ic_microcontrollers/
  _pinouts.py`) with `tools/make_dip_symbol.py`:
  - The 28-pin VQFN numbering differs from the SSOP/SPDIP; 32/48/64-pin TQFP and VQFN
    share numbering.
  - Supplies VDD, AVDD, VDDIO2 (top) and GND, AGND (bottom); repeated VDD/GND pins are
    stacked. Pin names carry the fixed functions: PA20/SWDIO, PA31/SWCLK,
    PA30/~RESET, PA24/XTAL32K1, PA25/XTAL32K2, PA23/VREFA.
  - The VQFN exposed pad is a separate passive `EP` pin: the datasheet never says
    what it connects to.
  - `make_dip_symbol.py` gained a `pas` (passive) pin type for it.
- **Footprints:** stock KiCad, matching the chapter 39 drawings, except the 28-pin
  VQFN (see Follow-ups).

## Follow-ups

- **Approximate footprint:** the 28-pin VQFN (3LW, 4x4 mm, 0.4 mm pitch, 2.65 mm pad)
  uses `QFN-28-1EP_4x4mm_P0.4mm_EP2.4x2.4mm`; KiCad has no 2.65 mm-pad version. Make an
  exact one if that package is used.
- **EP connection:** confirm with Microchip (or a later datasheet revision) whether the
  VQFN exposed pad should go to GND, then stack it onto GND in `_pinouts.py`.
- The datasheet is Preliminary; recheck parameters against the final revision.
