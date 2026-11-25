# voltage_regulator — classic through-hole linear regulators

**Date:** 2026-11-25
**Status:** Done — 52 parts across three generators (29 fixed, 7 adjustable, 16 LDO); see Results
**Scope:** populate the existing `voltage_regulator` table (previously only the two
LT3045 rows from `run_300_adi_regulators.py`) with the hobby/small-project
through-hole regulators: 78xx/79xx families, the LM317 adjustable family and the
723, and the common through-hole LDOs. Through-hole only; SMD twins are out of scope.

## Motivation

Terra had no general-purpose regulators. These are the parts people reach for first
on a new board, and KiCad's stock `Regulator_Linear` library already draws most of
them. What it lacks is the fully-qualified part: an orderable MPN, the datasheet, a
symbol whose pin map has been checked against that datasheet, and the parametric
tail.

## Sources

Datasheets are parked in the central store (Git LFS) and referenced as
`${TERRA_EDA_LIB}/datasheets/<mfr>/<slug>.pdf`:

| Family | Datasheet |
|---|---|
| MC7800 (1 A +) | `datasheets/onsemi/mc7800-d.pdf` (Rev. 29, Nov 2021) |
| MC7900 (1 A −) | `datasheets/onsemi/mc7900-d.pdf` (Rev. 21, Oct 2021) |
| MC78L00A (100 mA +) | `datasheets/onsemi/mc78l00a-d.pdf` |
| MC79L00A (100 mA −) | `datasheets/onsemi/mc79l00-d.pdf` |
| MC78M00 (500 mA +) | `datasheets/onsemi/mc78m00-d.pdf` |
| MC79M00 (500 mA −) | `datasheets/onsemi/mc79m00-d.pdf` |
| LM317 (onsemi) | `datasheets/onsemi/lm317-d.pdf` |
| LM317L | `datasheets/ti/lm317l.pdf` (SLCS144G, Aug 2026) |
| LM317HV | `datasheets/ti/lm317hv.pdf` (SNVS773D) |
| LM337 (LMx37) | `datasheets/ti/lm337.pdf` (SLVS047L) |
| LM338 | `datasheets/ti/lm338.pdf` (SNVS771D) |
| LM350 | `datasheets/ti/lm350-n.pdf` (SNVS772B) |
| µA723 | `datasheets/ti/ua723.pdf` (SLVS057D) |
| LM2940 / LM2940C | `datasheets/ti/lm2940-n.pdf` (Rev. J) |
| LM1117 | `datasheets/ti/lm1117.pdf` (Rev. Q) |
| LP2950-N | `datasheets/ti/lp2950-n.pdf` (Rev. Q) |

ST and ADI were not used (their sites block scripted downloads). The CERN tables and
`plans/cern-harvest-worklist.csv` were not used.

**Lifecycle (checked 2026-11-25).** Mouser returned "Access denied" and Digi-Key 403
to scripted fetches, so status comes from the manufacturers' live product pages
instead: onsemi's per-OPN `itemCondition` on each family page
(`onsemi.com/products/standard-products/ldo-voltage-regulators/<family>`) and TI's
per-orderable `marketingStatusDescription` on `ti.com/product/<part>`. Every emitted
MPN was Active there. Re-check against a distributor when one can be fetched.

## Decisions

- **One orderable per voltage.** The commercial grade (C / AC, TJ 0 to 125 °C) in its
  bulk or rail through-hole code. No tape-and-reel, A (tighter-tolerance) or B
  (−40 °C) twins, except where the C grade is gone (MC79M12 → `MC79M12BTG`).
- **Only Active, datasheet-listed voltages.** A voltage is emitted only when the
  datasheet's ordering table lists it in the through-hole package *and* the vendor
  page shows that OPN Active. Dropped:
  - MC78xx: 06 and 10 V have no TO-220 entry in the datasheet; `MC7806CTG` is
    Obsolete.
  - MC79xx: `MC7908CTG`, `MC7924CTG` Obsolete.
  - MC78Mxx: 06, 08, 09, 18, 20, 24 V TO-220 all Obsolete (05/12/15 kept).
  - MC79Mxx: 05 and 08 V Obsolete; `MC79M12CTG` Obsolete (B grade kept).
  - **TI LM317 TO-220** (`LM317KCS` / `LM317KCSE3`) is NOT RECOMMENDED FOR NEW
    DESIGNS, so the LM317 TO-220 row is **onsemi `LM317TG`** (Active).
  - **LM337L TO-92**: TI now orders it only in SOIC; onsemi does not make it. Omitted.
  - **LM723 DIP-14**: TI's LM723 folder orders only the TO-100 can. The DIP-14 row is
    TI's **`UA723CN`** (Active, the same 723 die and 14-pin pinout).
  - LM350: still Active at TI as `LM350T/NOPB` (LM350-N folder), so it is included.
- **LM2940 both grades.** `LM2940T-x` (−40 to 125 °C, 60 V transient; 5, 8, 9, 10,
  12 V) and `LM2940CT-x` (0 to 125 °C, 45 V transient; 5, 9, 12, 15 V) are distinct
  orderables sharing one datasheet.
- **LP2950**: the LP2950-N C grade, `LP2950CZ-3.0/3.3/5.0` (±1 %, bulk TO-92). The
  newer TI LP2950 (`LP2950-30LP` …) offers its 5 V only on tape-and-reel.
- **Spec transcription.** The 25 °C limits from the grade's own column. `line_regulation`
  and `load_regulation` quote typ/max and the test range. `accuracy` is the 25 °C
  output window with its percentage (arithmetic from the window, rounded to 0.1 %); for
  adjustables it is the VREF window. `input_voltage_min` is the low end of the input
  range over which the full-load output or line regulation is specified;
  `input_voltage_max` is the absolute-maximum input for the 78/79 families and the
  recommended maximum for the LDOs (LM2940 26 V, LM1117 15 V, LP2950 30 V). NULL where
  the datasheet gives nothing (e.g. MC79L00A typicals, adjustables' dropout).
- **Floating adjustables** (LM317/317L/317HV/337/338/350) are specified by
  input-output differential, not absolute input, so `input_voltage_min/max` are NULL
  and the differential range goes in the description.
- **Negative regulators are signed.** `output_voltage` '−5V'; `input_voltage_min` is
  the most negative allowed input (−35 V) and `input_voltage_max` the least negative
  (−7 V). LM337: `output_voltage_min` −37, `output_voltage_max` −1.2.
- **Names.** `value` is the schematic name (`MC7805`, `LM317`, `LM2940-5.0`,
  `LM1117-ADJ`, `uA723`). `part_locator` is `reg-linear-<v>-<i>-<pkg>`,
  `reg-linear-neg<v>-…`, `reg-adj-<range>-<i>-<pkg>` or `reg-ldo-<v>-<i>-<pkg>`.
  `regulator_type` is `linear` for the 78/79/317 families and the 723, `LDO` for
  LM2940, LM1117 and LP2950.

## Symbols and footprints

Each row records its datasheet's 3-pin pinout, and `_vreg.check_pinouts` fails the
generator unless the KiCad symbol's pins 1–3 have the same roles (IN/OUT/GND/ADJ). Nothing
is borrowed without that check passing.

| Family | Datasheet pinout (1-2-3) | Symbol |
|---|---|---|
| MC78xx TO-220 | IN-GND-OUT | `LM78xx_TO220` per voltage |
| MC79xx TO-220 | GND-IN-OUT | `MC79xx` |
| MC78Lxx TO-92 | OUT-GND-IN | `MC78Lxx_TO92` (`L78L09_TO92` for 9 V) |
| MC79Lxx TO-92 | GND-IN-OUT | `LM79L05/12/15_TO92`; 18/24 V reuse `LM79L05_TO92` |
| MC78Mxx TO-220 | IN-GND-OUT | `LM78M05_TO220` for all three |
| MC79Mxx TO-220 | GND-IN-OUT | `MC79M12_TO220`, `MC79M15_TO220` |
| LM317 / LM317HV TO-220 | ADJ-OUT-IN | `LM317_TO-220` |
| **LM317L TO-92 (TI LP)** | **IN-OUT-ADJ** | **custom `terra_symbols_voltage_regulator:LM317LxLP`** |
| LM337 TO-220 | ADJ-IN-OUT | `LM337_TO220` |
| LM338 / LM350 TO-220 | ADJ-OUT-IN | `LM350_TO220` (no stock LM338 symbol) |
| µA723 DIP-14 | (14-pin, checked by hand) | `LM723_DIP14` |
| LM2940 TO-220 | IN-GND-OUT | `LM2937xT` |
| LM1117T TO-220 | GND-OUT-IN / ADJ-OUT-IN | `LM1117T-2.5/3.3/5.0/ADJ` |
| LP2950 TO-92 | OUT-GND-IN | `LP2950-x_TO92` |

**Pinout mismatch found:** TI's LM317L LP package is pinned 1=IN, 2=OUT, 3=ADJ
(datasheet Table 4-1 and the LP drawing), the reverse of KiCad's `LM317L_TO92`
(1=ADJ, 2=VO, 3=VI, the National/onsemi Z-package order). The custom `LM317LxLP` is
the stock symbol with pins 1 and 3 renumbered. The stock symbol would be correct for
onsemi's `LM317LZG`, if that part is ever added.

Footprints are stock: `Package_TO_SOT_THT:TO-220-3_Vertical`, `TO-92_Inline`,
`Package_DIP:DIP-14_W7.62mm`. The LM1117T stock symbols default to a horizontal
TO-220; rows use the vertical one like every other TO-220 row.

## Architecture

- `db/tables/voltage_regulator/_vreg.py`: shared columns, `write()`, the datasheet
  existence check, the symbol pin-map check and `tol()` for the accuracy string.
- `run_310_onsemi_fixed.py`: MC7800/7900/78L00A/79L00A/78M00/79M00.
- `run_320_adjustable.py`: LM317 (onsemi), LM317L, LM317HV, LM337, LM338, LM350, µA723.
- `run_330_ti_ldo.py`: LM2940/LM2940C, LM1117, LP2950.
- `kicad_symbols/terra_symbols_voltage_regulator.kicad_sym`: `LM317LxLP`; registered in
  `kicad_symbols/sym-lib-table` by `make lib-tables`.

**Schema.** `voltage_regulator` (like `voltage_reference`) predates `table_map.json`
registration: its `_0_schema.sql` was hand-written in commit 480d0111, so the drift
test does not cover it and there is no `db/schema/types/voltage_regulator.sql`. Its
first 41 columns match `core.sql` exactly and the tier default is 2, so registering it
is a pure formalisation (copy the tail into a type fragment, add the `table_map.json`
entry and a `PAIRS` line, run `make schema`, which drops the `DROP TABLE` line and the
comments). Left as a follow-up rather than done here; no columns were added.

## Build & verify

```
make voltage_regulator-clean        # after editing _vreg.py
make voltage_regulator-generate && make voltage_regulator-build
make lib-tables                     # registers terra_symbols_voltage_regulator
pytest -q tests/
```

## Results

`db/voltage_regulator.db` builds with 54 rows (2 LT3045 + 52 new):

| Generator | Family | Rows |
|---|---|---|
| `run_310_onsemi_fixed.py` | MC78xx (05 08 09 12 15 18 24) | 7 |
| | MC79xx (05 06 12 15 18) | 5 |
| | MC78Lxx (05 08 09 12 15 18 24) | 7 |
| | MC79Lxx (05 12 15 18 24) | 5 |
| | MC78Mxx (05 12 15) | 3 |
| | MC79Mxx (12 15) | 2 |
| `run_320_adjustable.py` | LM317, LM317L, LM317HV, LM337, LM338, LM350, µA723 | 7 |
| `run_330_ti_ldo.py` | LM2940T (5 8 9 10 12) + LM2940CT (5 9 12 15) | 9 |
| | LM1117T (2.5 3.3 5.0 ADJ) | 4 |
| | LP2950CZ (3.0 3.3 5.0) | 3 |

All 52 are Active; no row has a NULL symbol or footprint (no REVIEW rows). Every
3-pin row's symbol pin map passed the check. `pytest -q tests/` passes 219 tests.
Spot-checked against the datasheets: MC7805CTG, MC79L24ACPG, LM317TG, LM2940CT-15/NOPB,
UA723CN, LM1117T-5.0/NOPB, LP2950CZ-3.0/NOPB.

## Follow-ups

- Register `voltage_regulator` (and `voltage_reference`) in `table_map.json` with a
  type fragment (see Schema above).
- SMD twins (DPAK/D2PAK/SOT-223/SOIC) and the A (tighter-tolerance) and B
  (−40 °C) grades as option axes.
- onsemi `LM317LZG` (TO-92, stock `LM317L_TO92` pinout) as a second LM317L source.
- An LM337L TO-92 source, if an Active through-hole one turns up.
- Re-check lifecycle at Digi-Key or Mouser when a scripted or manual fetch works.
- The MC79L18/24 rows use the `LM79L05_TO92` symbol (same pinout; `value`
  overrides the label). Per-voltage derived symbols could follow if wanted.
