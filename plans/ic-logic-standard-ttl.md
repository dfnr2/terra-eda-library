# ic_logic: standard (no-letter) 74xx TTL (`run_315_ttl_standard.py`)

Started 2026-11-24 for the OSI 470 port, which uses 7404, 7407, 7417, 7410, 7430, 7493,
74123 and 74390. Only the 74LS versions were in terra, and they aren't substitutes:

- **74123:** tw = 0.28·RT·Cext·(1 + 0.7/RT), with Rext 5-50 kΩ. The 74LS123 gives about
  0.45·RT·Cext and takes 5-260 kΩ. At 10 kΩ and 1000 pF that is 3.03 µs against 4.5 µs.
- **7404 in a crystal oscillator:** the input current and threshold behaviour that bias
  the circuit differ from the 74LS04.
- **Generally:** 16 mA IOL against 8 mA, different delays, and 1.6 mA input loading.

So the standard parts are their own rows: value `7404`, data-sheet timing, and
`allow_substitution = 'No'`.

## Why they were missing

`run_320_ttl_harvest.py` builds rows from KiCad's 74xx symbol library, which has
standard-TTL symbols only for 7400, 7402 and 7454. It also gave each of those an SOIC
row without checking, which is how SN7402D and SN7454 ended up marked Active. The
harvest now skips family `74`, and this generator owns it.

## Parts and lifecycle

Lifecycle comes from TI's package-option addendum at the back of each data sheet, TI's
product pages, and Mouser, all checked 2026-11-24.

| Part | Rows | Status |
|---|---|---|
| SN7400 | N, D | Active |
| SN7402 | N | Active (no SOIC in the addendum) |
| SN7404 | N, DR | Active; the SN7404D tube is Obsolete, so the reel code is used |
| SN7407 | N, DR | Active; SN7407D Obsolete |
| SN7417 | N, DR | Active; SN7417D Obsolete |
| SN74123 | N | Active |
| SN7410, SN7430, SN7454, SN7493A, SN74390 | N | Obsolete: not in the addendum, the TI page returns 404, and Mouser lists them as obsolete or not at all |

The obsolete parts are kept for restorations, which buy NOS or surplus stock, as
`plans/vintage-computer-parts.md` decides.

## Symbols

- **Stock symbols:** `74xx:7400`, `7402` and `7454`. The 7454 is the 2-2-2-2 AOI; the
  74LS54 is 2-3-3-2, so its symbol would be wrong.
- **The rest use the 74LS symbol with the same pinout:** 74LS04, 74LS07 (for both the
  7407 and 7417), 74LS10, 74LS30, 74LS93 (keeps VCC = 5 and GND = 10), 74LS123 and
  74LS390.
- **IEEE variants** where `74xx_IEEE` has the part: 7400, 7402, 7404, 7407, 7410, 7417,
  7430, 7454, 7493 and 74LS390.

## Data sheets (`datasheets/ti/`)

`sn7400.pdf`, `sn7402.pdf`, `sn7404.pdf`, `sn7407.pdf` (7407 and 7417), `sn74123.pdf`,
`sn74ls10.pdf` (7410), `sn74ls30.pdf` (7430), `sn54ls54.pdf` (7454), `sn74ls90.pdf`
(7493A) and `sn74ls390.pdf` (74390).

Most are 1983-88 scans. Their figures were read from page images and cross-checked: the
74123's K = 0.28 reproduces its printed 3.03 µs at 10 kΩ and 1000 pF.

## Results (2026-11-24)

- 11 devices, 15 ordering codes, 29 rows counting the IEEE variants. The 2 harvest rows that don't exist
  (SN7402D, SN7454D) and their IEEE twins are gone.

## Follow-ups

- Other standard-TTL parts as boards need them (7408, 7414, 7432, 7474, 7486, 74121,
  74154, 74161, 74175 ...). Add each to `DEVICES` with its TI data sheet and addendum
  status.
