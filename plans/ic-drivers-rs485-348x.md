# ic_drivers: 3.3 V 348x RS-485/RS-422 transceivers

## Intent

Fill out the 3.3 V "348x" RS-485/RS-422 transceiver families next to the MAX3488E and
ISL83490 already in `ic_drivers`. They come from three vendors in near pin-for-pin
form, so a designer can pick a part by data rate, ESD rating and duplex without
leaving terra. The non-E ADM3488/ADM3490 were also on the CERN harvest worklist.

## Scope

Generator: `db/tables/ic_drivers/run_310_rs485_348x.py`.

| Family | Parts | Datasheet |
|---|---|---|
| ADI ADM348xE (±15 kV ESD) | ADM3483E, ADM3486E, ADM3488E, ADM3490E, ADM3491E | `analog-devices/adm3483e-adm3491e.pdf` (Rev. A) |
| ADI ADM3485E | ADM3485E | `analog-devices/adm3485e.pdf` (Rev. D) |
| ADI ADM348x | ADM3483, ADM3485, ADM3488, ADM3490, ADM3491 | `analog-devices/adm3483-adm3491.pdf` (Rev. E) |
| Renesas ISL8348x | ISL83483, ISL83485, ISL83488, ISL83491 (ISL83490 already in `run_300`) | `renesas/isl83483-isl83491.pdf` (FN6052 Rev. 5.00) |

- Each ordering guide's Pb-free base MPN (`…ARZ`, `…EARZ`, `…IBZ`) only. Reels,
  the leaded `ADM3485EAR` / `ADM3491AR` and the discontinued PDIPs are left out.
- The non-E family has no ADM3486.
- Lifecycle: Digi-Key/Arrow list the ARZ and EARZ parts as Active. One comparison site
  calls ADM3485EARZ obsolete, but Digi-Key and Arrow both show it Active. Recheck at the
  [[nexar-harvest]] sweep.

## Symbols and footprints

Choice follows the pinout, which is identical across vendors (checked against each
datasheet's pin table):

| Configuration | Pinout | Symbol | Footprint |
|---|---|---|---|
| Half duplex, 8-lead | RO ~RE DE DI GND A B VCC | `Interface_UART:ADM3485xR` | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| Full duplex, 8-lead | VCC RO DI GND Y Z B A | terra MAX3488E symbol, plus its `flipped` variant | same SOIC-8 |
| Full duplex + enables, 14-lead | NC RO ~RE DE DI GND GND NC Y Z B A VCC VCC | `Interface_UART:ADM3491ExR` | `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm` |

Terra only has the full-duplex 8-lead MAX3488E symbol, so the half-duplex and 14-lead
parts use stock KiCad. The stock `Interface_UART:ISL83491` was not used because it
omits the NC pins and has no footprint.

## Correction to existing rows

`ISL83490IBZ` (+flipped) in `run_300_terra_sym_harvest.py` carried a 2.5 Mbps data
rate. FN6052 Table 1 gives 10 Mbps, so the rate is now 10 Mbps and the datasheet
points at the local PDF. Its `unique_id` and symbol are unchanged.

## Results

- 20 rows: 15 parts, plus a `flipped` variant for each of the 5 full-duplex 8-lead
  parts.
- `cern-harvest-worklist.csv`: ADM3488AR and ADM3490AR marked `ic_drivers`.
