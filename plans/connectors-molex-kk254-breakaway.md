# connectors: Molex KK 254 breakaway pin headers (series 42375, vertical)

A terra part for KiCad's generic 0.1" pin header,
`Connector_PinHeader_2.54mm:PinHeader_1xNN_P2.54mm_Vertical`. The Molex KK 254
breakaway header is a plain 0.64 mm square-post strip, so it uses KiCad's stock
footprint and its shipped 3D model directly; nothing is vendored.

## Scope (2026-10-12)

- **Parts:** Molex 22-28-4NNx, NN = 02…36 circuits (the series range; 1 circuit is not
  listed). Generator `db/tables/connectors/run_330_molex_kk254_breakaway.py`.
- **Variants** (last digit), behind `ENABLED_VARIANTS`:
  - `0` tin, 6.09 mm mating pin (on)
  - `3` 0.38 µm gold selective, 6.09 mm mating pin (on; 22-28-4043 is the part Dave picked)
  - `1` / `4` (8.13 mm mating pin) and `5`–`8` (0.76 µm gold, other tails) exist for
    some counts but are unverified across the range; off.
- **Symbol / footprint:** `Connector_Generic:Conn_01xNN`,
  `Connector_PinHeader_2.54mm:PinHeader_1xNN_P2.54mm_Vertical`. Checked that every
  footprint, its 3D model and the symbol exist in KiCad 10 for 2…36.

## Parameters

From the Molex part sheet for 22-28-4040 (2021, mirrored by Chip-Dip):

| Field | Value |
|---|---|
| current_rating / voltage_rating | 4.0 A / 500 V (some distributors print 250 V) |
| housing | black high-temperature thermoplastic, UL94-V0 |
| polarized / lock / shroud | no / none / unshrouded |
| PC tail | 3.18 mm, pin-in-paste (SMC) capable, wave 235 °C 5 s |
| mating_family | KK crimp housings 2695, 6471, 7880; KK PC board connector 4455 |
| temp_operating | blank: the sheet defers to PS-10-07-001 (sources quote −40…+80 and −40…+105 °C) |

## Datasheet

`datasheets/molex/kk-254-42375-breakaway-header.pdf` is the Molex part sheet for
22-28-4040, parked until the sales drawing SD-42375-001 can be fetched from molex.com
(scripted downloads are blocked); replace it in place.

## Results

- 70 rows (35 counts x tin/gold) build; `make verify` clean, 178 tests pass.
- Served by the HTTP library as `terra:Molex-22284043` etc.
