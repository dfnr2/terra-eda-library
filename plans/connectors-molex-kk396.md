# connectors: Molex KK 396 friction-lock headers (41791 vertical, 41792 right-angle)

The 3.96 mm (0.156") KK header of SWTPC, S-100 power harnesses and arcade boards, still
in production. Part of `plans/vintage-computer-parts.md` phase 8.

## Scope (2026-11-21)

- **Parts:** 34 rows. 26-60-4020…4180 (41791, vertical) and 26-60-5020…5180 (41792,
  right-angle), 2–18 circuits: exactly the set of KiCad `Connector_Molex` KK-396
  footprints. Generator `db/tables/connectors/run_370_molex_kk396.py`.
- **Suffix 0 only:** tin plating. The 41791 drawing also lists a 3 suffix for every
  size; not generated.
- **MPN:** the printed part number (26-60-4020), as distributors list it; the catalog
  number (0026604020) and engineering number (41791-0002) are keywords.
- **Symbol / footprint:** `Connector_Generic:Conn_01xNN`;
  `Connector_Molex:Molex_KK-396_A-4179x-00NN_1xNN_P3.96mm_{Vertical,Horizontal}`, with
  KiCad's own 3D models. Nothing vendored.
- **Not generated:** the crimp housings (2139, 3069, 41695, 6442) and terminals. They
  have no board footprint, and no earlier connector family carries its cable-side
  parts; `mating_family` and `mates_with` name them instead. Add them as rows if a BOM
  needs them.

## Parameters

From product specification PS-08-50-001 rev. U (2021-11-24) unless noted:

| Field | Value | Note |
|---|---|---|
| current_rating | 7.0 A | agency single-circuit rating, both series |
| voltage_rating | 600 V | UL and section 4.1; CSA lists 250 V |
| temp_operating | -40 … +80 °C | brass pins (phos-bronze terminals: to +105 °C) |
| housing | natural polyester, UL94-V0 | part pages |
| polarized / lock | yes / friction lock | part pages |
| PC tail | 3.56 mm (41791), 3.96 mm (41792) | part pages |

Molex's own part pages disagree on ratings: 26604020 says 5.0 A / 600 V, 26605020 says
7.0 A / 250 V, and the 2021 part sheet for 26604020 says 7.0 A / 250 V. The 5 A figure
matches the spec's brass crimp-terminal rating; the rows follow the spec.

## Datasheets

Fetched from molex.com through Chrome (scripted downloads time out) and parked in
`datasheets/molex/`:
- `kk-396-41791-vertical-header-sd.pdf` (026604020_sd, SDA-41791-000, all sizes)
- `kk-396-41792-right-angle-header-sd.pdf` (026605020_sd)
- `kk-396-product-spec-ps-08-50-001.pdf`

## Results

- 34 rows build; `make verify` clean, 216 tests pass.
- All 34 Active at Molex and listed at Mouser on 2026-11-21; 26-60-5120, -5140, -5160
  and -5170 had no stock that day.
