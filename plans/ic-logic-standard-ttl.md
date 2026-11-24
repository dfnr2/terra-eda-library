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

## OSI parts lists (added 2026-11-24)

The SAMS Computerfacts manuals for the C1P, C2/C3 and C4P in `~/vsrc/osiweb` have OCR'd
parts lists. Their IC numbers were extracted and checked against terra.

**Added** (each with its TI data sheet, read from the scans):
- **Standard TTL:** 7401, 7403, 7408, 7414, 7420, 7438, 7473, 7474, 7475, 7476, 7492A,
  74125, 74148, 74151A, 74155, 74157, 74163, 74164, 74165, 74174, 74175, 74193 and 74393.
- **Schottky TTL:** 74S10, 74S20 and 74S138A, as `logic_family = '74S'`. Their output
  levels differ: IOL 20 mA, VOH 2.7 V, VOL 0.5 V.

**Lifecycle:**
- **Active:** SN7414N/DR, SN7438N/DR, SN74S10N, SN74S20N and SN74S138AN/D. Each is in
  TI's addendum and has a TI product page.
- **Obsolete:** all the others. Their product pages return 404, and the 74125 and
  74165 sheets say "obsolete and no longer supplied".

**Things a schematic can trip on:**
- **7473 and 7476:** master-slave (pulse-triggered), while the 74LS73A and 74LS76A are
  negative-edge-triggered. The row descriptions say so.
- **7401:** its outputs are on pins 1, 4, 10 and 13. `74xx:74LS01` matches.
- **74164:** IOL is 8 mA. It uses `74xx:74HC164`, which has the same pinout.

**Added from data sheets Dave supplied** (TI documents, from datasheet-archive
mirrors; all three Obsolete):
- **SN74154:** 24-pin, 0.6 in DIP (`sn74154.pdf`, SDLS056).
- **SN74111:** dual J-K master-slave with data lockout (`sn74111.pdf`, SDLS038).
  KiCad has no symbol for it, so `terra_symbols_ic_logic:74111` is KiCad's 74LS76
  body with its pins renumbered to the 74111 pinout. KiCad plots both units.
- **SN74S113A** (`sn74s113a.pdf`, D2661): the C2/C3 list prints "SN74113N", but
  TI's 113 exists only as the 74S113 and 74LS113.

**Left out:**
- **74138, 74139:** the lists' plain "74138" and "74139" are LS or S parts; TI made no
  standard 74138 or 74139.
- **OCR noise:** the 7411, 7415, 7423, 7464 and 7477 hits were cross-reference or
  memory-size text.

## Results (2026-11-24, OSI additions)

- 40 devices, 80 rows, counting the IEEE variants.

## Follow-ups

- Other standard-TTL parts as boards need them (7432, 7486, 74121, 74161 ...). Add
  each to `DEVICES` with its TI data sheet and addendum status.
