# NXP PCA9632 LED driver and 9536 I/O expanders

## Scope

**PCA9632, all three packages, in `led_drivers`** (`run_310_nxp_pca9632.py`). Source: NXP
data sheet Rev. 6 (21 Sep 2021), `datasheets/nxp/pca9632.pdf`.

| MPN | Package | Footprint | Address |
|---|---|---|---|
| PCA9632DP1 | TSSOP8 (SOT505-1) | `Package_SO:TSSOP-8_3x3mm_P0.65mm` | fixed 0x62 |
| PCA9632DP2 | TSSOP10 (SOT552-1) | `Package_SO:TSSOP-10_3x3mm_P0.5mm` | 0x60-0x63 (A0/A1) |
| PCA9632TK | HVSON8 (SOT908-1) | `Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.5mm_EP1.66x2.38mm` (approximate) | fixed 0x62 |

- MPNs are NXP type numbers. The orderable codes are PCA9632DP1,118, PCA9632DP2Z and
  PCA9632TK,118.
- DP2 lifecycle: the DP2,118 reel was discontinued by DN 202104010, replaced by DP2Z.
  DN 202507021 then fully withdrew DP2Z (LTB 13 Jul 2026), and RN 202606037 (2 Jul 2026)
  reactivated it. All three packages are treated as Active.
- `driver_topology = 'switch'`: the outputs are PWM sinks (25 mA sink, 10 mA source),
  not regulated current sources. LED current is set by an external resistor.
- Symbols `terra_symbols_led_drivers:PCA9632DP1/DP2/TK` follow the stock
  `Driver_LED:PCA9531PW` layout. The TK symbol stacks the exposed pad (pad 9) onto VSS
  as `[5,9]`.
- **Approximate footprint:** the TK uses the LT "DD" DFN-8 3x3 land pattern, which has
  the same body, pitch and leads. Its EP land (1.66 x 2.38 mm) is slightly larger than
  NXP's pad (1.5 x 2.1 mm nominal, 1.65 x 2.25 mm max). An exact SOT908-1 footprint can
  replace it later, in the `PARTS` table.

**9536 4-bit I2C GPIO expanders, in `ic_drivers`** (`run_320_i2c_io_expanders.py`,
`driver_type = 'io expander'`). `ic_drivers` already holds the I2C interface parts
(PCA9306 level shifters), so no new table or columns were needed.

| MPN | Package | Symbol | Notes |
|---|---|---|---|
| PCA9536DP | TSSOP8 | stock `Interface_Expansion:PCA9536DP` | 2.3-5.5 V, 400 kHz, -40..85 C |
| TCA9536DGKR | VSSOP-8 | `terra_symbols_ic_drivers:TCA9536DGK` | 1.65-5.5 V, 1 MHz, P3/INT, -40..125 C |

- Both parts have the same pinout and the same fixed address (0x41).
- The TCA9536 symbol is the stock PCA9536DP layout with TI pin names (P0-P2, P3/INT,
  GND, VCC).
- Left out: the PCA9536D (SO8), fully withdrawn by DN 202507021 (LTB 13 Apr 2026);
  the PCA9536TK (HVSON8); the TCA9536DTMR (X2SON-8).

## Results

- led_drivers: +3 rows (13 total). ic_drivers: +2 rows.
- `make && make verify` clean.

## Follow-ups

- Make an exact SOT908-1 footprint for PCA9632TK (and PCA9536TK if it is added).
- Candidate families: see the list in the session summary (PCA9634/PCA9635/PCA9685,
  TLC59108/TLC59116, PCA9955B/PCA9956B, LP5009/LP5012/LP5562).
