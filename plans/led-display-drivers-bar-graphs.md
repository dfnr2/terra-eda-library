# led_drivers display drivers + optoelectronics_led DIP bar graphs

**Date:** 2026-11-25
**Status:** Done — 15 display drivers + 12 bar-graph arrays; see Results
**Scope:** add the classic LED display drivers (TI LM3914/15/16, ADI/Maxim
MAX7219/MAX7221, Renesas/Intersil ICM7218A-D) to the existing `led_drivers` table,
and 10-segment DIP LED bar-graph arrays (Broadcom HDSP-48xx/HLCP-J100, Kingbright
DC10) to the existing `optoelectronics_led` table. No new table or type fragment.

## Motivation

The dot/bar drivers, MAX72xx and ICM7218 are the standard ways to drive bar graphs
and multiplexed 7-segment displays on vintage-style and hobby boards, and the
HDSP-48xx/DC10 arrays are what they usually drive. Neither was in terra.

## Decisions

- **Tables.** Both families fit existing tails: `led_drivers` (type `led_drivers`)
  and `optoelectronics_led` (type `leds`). No schema change.
- **Obsolete classics kept.** LM3914/15/16 are all obsolete but documented; emitted
  with `lifecycle_status='Obsolete'`. LM3914V (PLCC-20) was wanted only if active and
  is obsolete, so it is not emitted. ICM7218 A/C/D are obsolete and emitted for the
  same reason (B is active).
- **MAX72xx ordering codes.** The eight C/E-grade PDIP (`NG`) and wide-SO (`WG`)
  lead-free (`+`) codes. The `ERG` CERDIP codes in the ordering table are dropped:
  the Rev 6 package section only lists PDIP N24+1 and SOIC W24+1, and no distributor
  carries them. Tape-and-reel `+T` codes are not emitted.
- **ICM7218.** The four base `xIJI` codes; the `R5254` Pb-free variants are not
  emitted (DIJIR5254 is "no longer available"). `rohs` is NULL for the base codes
  (only the R5254 codes are marked e3 in the sheet).
- **Bar graphs.** Single-colour 20-pin arrays only. Kingbright's bi-colour DC10EGWA
  and DC10SURKCGKWA are 30-pin, three-row parts with no stock symbol or footprint;
  deferred (see Follow-ups). HDSP-4820 is not in the current Broadcom sheet and is
  not emitted.
- **Kingbright MPNs** use the Kingbright USA / Digi-Key form without the hyphen
  (`DC10EWA`), matching the parked spec sheets; the hyphenated `DC-10EWA` alias is in
  `keywords`.
- **Datasheets** in the local store, referenced via `${TERRA_EDA_LIB}`.

## Field interpretation — led_drivers tail for display drivers

The tail was written for switching/linear current drivers; for display drivers:

| Column | LM3914/15/16 | MAX7219/MAX7221 | ICM7218A-D |
|---|---|---|---|
| `driver_topology` | linear | linear | linear |
| `channels` | 10 (one output per LED) | 64 (8 digits x 8 segments) | 64 (8 x 8) |
| `output_current` | programmable range (2-30 / 1-30 mA) | 40 mA seg / 320 mA digit sink | typ peak seg / digit |
| `output_voltage_max` | 25 V (output-driver abs max) | NULL | NULL |
| `switching_freq` | NULL | 800 Hz scan (typ) | 250 Hz per-digit scan |
| `dimming_method` | analog (ref current) | pwm (16-step intensity) | none |
| `interface` | none (analog input) | spi | parallel |
| `current_accuracy` | NULL | 3% (segment matching) | NULL |

`channels` counts independently addressable LEDs; the digit/segment split is in
the description.

## Symbols and footprints

| Part | Symbol | Footprint | Check |
|---|---|---|---|
| LM3914/15/16N-1 | stock `Driver_LED:LM3914N` | `Package_DIP:DIP-18_W7.62mm` | all three sheets' connection diagrams match the stock pins 1-18 |
| MAX7219 | stock `Driver_LED:MAX7219` | DIP-24 W7.62 / SOIC-24W | pins 1-24 match the Rev 6 pin configuration |
| MAX7221 | stock `Driver_LED:MAX7221xNG` / `MAX7221xWG` | DIP-24 W7.62 / SOIC-24W | same, `~CS` on pin 12 |
| ICM7218A-D | new `terra_symbols_led_drivers:ICM7218A..D` | `Package_DIP:DIP-28_W15.24mm` (F28.6, eA 0.600") | drawn from `db/tables/led_drivers/_pinouts.py` with `tools/make_dip_symbol.py` |
| HDSP-48xx, HLCP-J100 | stock `LED:<part>` | stock `Display:<part>` (with 3D) | 10 units, unit n = A pin n / K pin 21-n, matches the internal circuit diagram |
| Kingbright DC10 | stock `LED:HDSP-4830` | stock `Display:HDSP-48xx` | identical pinout (anodes 1-10, cathodes 20-11), checked on every DC10 sheet |

- **No custom bar-graph symbol was drawn.** KiCad's stock `LED` library already has
  per-part HDSP-4830/4832/4836/4840/4850/HLCP-J100 symbols with the right pinout.
  The Kingbright parts reuse `LED:HDSP-4830` (pin-identical, colour-neutral
  graphics).
- **ICM7218 pinout note.** The C/D pin-description table lists DA0-DA2 as "10, 6, 5"
  and ID0-ID3 as "14, 13, 11, 12" — MSB-first. The pin-configuration drawings (and
  the A/B table) give DA0=5, DA1=6, DA2=10, ID0=12, ID1=11, ID2=13, ID3=14, which
  the symbols follow.
- **DC10 footprint is approximate.** Same 25.4 x 10.16 mm body and 2.54 mm pitch as
  the HDSP-48xx, but Kingbright specifies 7.5 mm (0.295") row spacing and 1.0 mm
  holes vs the stock footprint's 7.62 mm rows and 0.914 mm drill. The 0.12 mm row
  difference is taken up by the leads. `DC10_FOOTPRINT` in `run_330_bar_graphs.py`
  is the single place to swap in an exact footprint.
- **SPICE.** Bar-graph rows set `sim_device`/`sim_pins` NULL; the table default
  (`D`, `1=K 2=A`) describes a two-pin LED and would be wrong for a 20-pin array.

## Lifecycle (checked 2026-11-25)

| MPN | Status | Source |
|---|---|---|
| LM3914N-1/NOPB | Obsolete | ti.com product page (OBSOLETE); Digi-Key LM3914N-1 Obsolete |
| LM3915N-1/NOPB | Obsolete | TI product page removed; RS "discontinued"; Digi-Key zero stock/no price |
| LM3916N-1/NOPB | Obsolete | TI product page removed (404) |
| MAX7221CNG+/CWG+/ENG+/EWG+ | Active | Digi-Key |
| MAX7219EWG+ | Active | Digi-Key |
| MAX7219CNG+/CWG+/ENG+ | Active | Digi-Key lists and prices them (status not rendered); Production per ADI via Octopart/Arrow |
| ICM7218BIJI | Active | renesas.com part page |
| ICM7218AIJI / CIJI / DIJI | Obsolete | renesas.com part pages; Digi-Key AIJI Obsolete |
| HDSP-4830/4832/4836/4840/4850, HLCP-J100 | Active | Digi-Key |
| DC10CGKWA, DC10EWA, DC10GWA, DC10SURKWA, DC10SYKWA, DC10YWA | Active | Digi-Key |

Mouser and direct Digi-Key curl requests are bot-blocked; Digi-Key was read through
a fetch proxy.

## Datasheets

| File | Document |
|---|---|
| `datasheets/ti/lm3914.pdf` | TI SNVS761B, Mar 2013 (ti.com) |
| `datasheets/ti/lm3915.pdf` | National DS005104, 2004 (TI no longer hosts LM3915; copy from komponenten.es.aau.dk) |
| `datasheets/ti/lm3916.pdf` | TI SNVS762B, Mar 2013 (SparkFun mirror; ti.com symlink now redirects) |
| `datasheets/maxim/max7219-max7221.pdf` | Maxim 19-4452 Rev 6, 8/21 (ece-classes.usc.edu mirror; analog.com and datasheets.maximintegrated.com time out) |
| `datasheets/renesas/icm7218.pdf` | Renesas FN3159 Rev 4.00, May 2016 (renesas.com) |
| `datasheets/broadcom/hdsp-48xx-hlcp-j100.pdf` | Broadcom AV02-1798EN, July 8 2024 (docs.broadcom.com) |
| `datasheets/kingbright/dc10*.pdf` | Kingbright USA spec sheets (kingbrightusa.com/images/catalog/SPEC/) |

## Results

- `db/tables/led_drivers/run_320_display_drivers.py` → 15 rows: LM3914/15/16 (3),
  MAX7219 (4), MAX7221 (4), ICM7218A-D (4). MAX72xx temp grade / package decoded
  from the MPN and checked against each row.
- `db/tables/led_drivers/_pinouts.py` + 4 new symbols in
  `kicad_symbols/terra_symbols_led_drivers.kicad_sym`.
- `db/tables/optoelectronics_led/run_330_bar_graphs.py` → 12 rows: Broadcom 6,
  Kingbright 6. Kingbright colour decoded from the MPN suffix and checked.
- `make led_drivers-generate/-build`, `make optoelectronics_led-generate/-build`
  clean; `pytest tests/` 219 passed. Every footprint and datasheet path resolves.

## Follow-ups

- **Kingbright bi-colour DC10EGWA / DC10SURKCGKWA** (Active at Digi-Key): 30 pins in
  three rows; per segment n, red anode on pin 21-n, green anode on pin n, common
  cathode on pin 20+n (from the internal circuit diagram). Needs a custom 10 x
  dual-LED symbol and a custom 3-row footprint; the drawing's row spacing (5.0 /
  2.5 mm) and which row holds pins 21-30 should be confirmed before drawing it.
- Exact DC10 footprint (7.5 mm rows, 1.0 mm holes) if the HDSP-48xx approximation
  ever matters.
- Lite-On LTA-1000 series bar graphs (optional, not done).
- Maxim's own plastic ICM7218 (ICM7218AIPI+ etc., the suggested alternate for the
  obsolete Renesas CERDIP parts) — separate datasheet, not covered here.
