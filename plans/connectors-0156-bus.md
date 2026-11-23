# connectors: 0.156" pin buses (TE MTA-156 and Molex KK 396 round-pin headers, Molex KK 156 41815 receptacles)

The backplane and card connectors of the OSI 48-line bus and the SWTPC SS-50/SS-30
buses. Part of `plans/vintage-computer-parts.md` phase 8.

## What the machines used (2026-11-21)

| Bus | Layout | Backplane / motherboard (male) | Card (female) |
|---|---|---|---|
| OSI 48-line | 4 x 12-pin, 0.156" | Molex 26-60-2120 (KK 396 41771, square post) | Molex 09-52-3121 right angle / 09-52-3123 vertical (series 2145, obsolete) |
| SWTPC SS-50 / SS-30 | 5 / 3 x 10-pin, one pin pulled as the index key | TE 1-640384-0 | Molex 09-48-2101 (41815) |

Sources: osiweb `public/misc/osi-replacement-parts.txt`; the Corsham SS-50 specification
(retrotechnology.com/restore/ss50_corsham.html). The SWTPC part numbers come from that
one source only.

**Round pins on the male side** (Dave, 2026-11-21): TE MTA-156 640384, plain, straight,
0.045" round post, in place of the square-post KK 396 headers. The 41815 receptacle is
drawn for "0.045 square or round pin", so the two mate. Molex's own round-pin KK 396
headers (series 3190 and 3192) were added on 2026-11-22 as a same-brand alternative.

## Scope

- `run_372_molex_kk396_round_pin.py`: Molex KK 396 round-pin headers, **38 rows**.
  Series 3190 (26-19-2NN1, polarizing back wall, 11.43 mm pin): 14 sizes, 3-18. Series
  3192 (26-20-2NNS, flat end-stackable wafer): 15 with 11.43 mm pins, 8 with 16.18 mm, 1
  (26-20-2096) with 32.51 mm. Every code on the drawings that is Active on its Molex part
  page and listed at Mouser (26-20-2072 under Mouser's typo "2620-2072"). Not generated:
  the 26-21 (17.47 mm) column, which Mouser doesn't list, and the 3190 voided-circuit
  38-00-xxxx builds. Molex's series charts omit several Active codes, so each code was
  checked on its own part page.
- `run_390_te_mta156_round_post.py`: TE 640384, **2-15 positions, 14 rows**. The drawing
  lists 2-24; it marks 22-24 obsolete and TE's product pages mark 16-21 OBSOLETE (Mouser
  still had stock of 20 and 21). All 14 Active at TE and listed at Mouser (7, 10, 11, 13,
  15 non-stocked).
- `run_395_molex_kk156_41815.py`: Molex 41815, **141 rows**. The drawing (SDA-41815, 11
  sheets) has three entry styles (right angle, top entry, bottom entry) in several
  terminal/plating/ramp builds. Generated: every tin build (197 and P909) with no voided
  circuits and hooks intact, limited to the 141 of those 196 codes Mouser lists (none
  flagged obsolete). Gold builds skipped by request. Right angle 49, top entry 44,
  bottom entry 48.
- Symbols: stock `Connector_Generic:Conn_01xNN`. The SS-50 index key (a pulled post) is
  not modelled.

## Parameters

TE 640384, from drawing ENG_CD_640384 rev AB: 0.045" round copper-alloy post, tin;
glass-filled polyester housing, UL94V-0, natural; 0.400" post above the 0.125" housing,
0.125" tail; no lock. Ratings from system product specification 108-1051 rev J sec. 3.3:
**600 V AC, -55 to +105 °C**. **7 A** from catalog 82056 (MTA-156 performance data, PDF
page 26: "7 amp max. for MTA-156 Connector"), the mated-system figure; the header page
gives none of its own. The spec's base curve (14.24 A for a 30 °C rise at 18 AWG) is a
single-circuit maximum before derating.

Molex 3190/3192, from drawings SDAE-3190-NXX rev AD2 and SDAE-3192-NX rev L2 and product
specification PS-99020-0087 (cited by both): nylon housing **UL94V-2**, natural; brass
pins, matte tin over nickel; **600 V** (spec sec. 4.1); **-40 to +80 °C** with brass
(sec. 4.3); **7.0 A** from Molex's part pages (the spec rates only the crimp and PCB
receptacles; the pages give 250 V, the CSA figure). Mates with 3069 crimp housings per
the part pages, and with the 41815 receptacles.

Molex 41815, from product specification PS-08-50-001 rev. U (cited by the drawing):

| Field | Value |
|---|---|
| voltage_rating | 600 V (UL; CSA 250 V) |
| current_rating | right angle and top entry 4.5 A brass / 5.0 A phosphor bronze; bottom entry 4.0 / 4.5 A |
| temp_operating | -40 to +80 °C brass, -40 to +105 °C phosphor bronze |
| housing | polyester, UL94V-0, natural |

## Footprints

KiCad ships footprints for none of these families; the generators write theirs into
`terra_footprints_connectors` (shared code in `db/tables/connectors/_conn156.py`), pin 1
at the origin, row along +x. Each references a generated 3D model and each part has a
`-pins` per-pin symbol row (2026-11-22, `plans/connectors-conventions.md`).

- TE 640384: 1.60 mm drill (drawing: 0.060" +0.010/-0), 2.40 mm pads; body 0.250" deep,
  n x 0.156" long, posts on the centreline.
- Molex 3190/3192 (`Molex_KK-396_{3190,3192}_1xNN_P3.96mm_Vertical`): 1.52 mm drill
  (drawing 1.52 +0.05/-0.08), 2.40 mm pads; housing 6.9 mm deep with the pins on its
  centreline, 1.98 mm from each end. On 3190 a F.Fab line marks the back wall (1.6 mm,
  scaled from the side view) on the -y side, as KiCad draws KK 396 41791. One footprint
  per series and size, plus `_Pin16.18mm` / `_Pin32.51mm` copies for the long-pin 3192
  builds so their 3D models show the real pin (same land pattern). Model: housing 4.45
  mm high (DIM C - DIM D - tail), 3190 wall 9.12 mm.
- 41815 right angle (`_Horizontal`): 1.52 mm holes (drill 1.55); board edge 7.87 mm from
  the hole row, marked on F.Fab; housing 11.4 mm deep, overhanging the edge 1.91 mm.
- 41815 top entry (`_Vertical`): 1.52 mm holes; outline scaled from the drawing's dashed
  top view, **approximate**.
- 41815 bottom entry (`_Vertical_BottomEntry`): 1.02 mm tail holes (drill 1.05) and a
  2.54 mm NPTH 3.35 mm away under each circuit for the mating pin; outline scaled from
  the side view, **approximate**.

Rendered with `kicad-cli fp export svg` and checked against the drawings' PCB layouts.

## Datasheets

- `datasheets/te/ENG_CD_640384_AB.pdf` (te.com, through Chrome)
- `datasheets/te/te-108-1051-mta156-product-spec.pdf` (MTA-156 system spec, rev J)
- `datasheets/te/te-82056-mta-cst100-sl156-catalog.pdf` (catalog 82056, 08/18)
- `datasheets/molex/kk-396-3190-round-pin-header-sd.pdf` (026192121_sd, all 3190 codes)
- `datasheets/molex/kk-396-3192-round-pin-header-sd.pdf` (026202121_sd, all 3192 codes)
- `datasheets/molex/kk-396-round-pin-product-spec-ps-99020-0087.pdf`
- `datasheets/molex/kk-156-41815-pcb-receptacle-sd.pdf` (molex.com 009482121_sd, all
  41815 builds)
- `datasheets/molex/kk-396-product-spec-ps-08-50-001.pdf` (already parked for KK 396)

## Follow-ups

- ~~**TE current rating**~~ Done 2026-11-22: 7 A from catalog 82056.
- ~~**3D models and per-pin symbols**~~ Done 2026-11-22, see
  `plans/connectors-conventions.md`. The 41815 models are block approximations scaled
  from the drawing's side views.
- **Mouser is dropping 3190:** Mouser marks every 3190 code except 26-19-2041
  "discontinued with no replacement" (2026-11-22), while Molex and Digi-Key show Active
  (Digi-Key 16-week lead time). Recheck lifecycle before relying on 3190.

## Results

- 155 rows (14 TE, 141 Molex); 56 footprints; `make verify` clean, 216 tests pass; every
  symbol and footprint resolves.
- 2026-11-22: +38 Molex 3190/3192 rows and 30 footprints; TE rows gain voltage and
  temperature. 193 rows in all; `make verify` clean, 216 tests pass.
- 2026-11-22: TE current 7 A (catalog 82056). Every part gained a `-pins` twin (386
  rows from these three generators), every footprint a generated 3D model; 9 long-pin
  3192 footprints added, `Molex_KK-396_3192_1x17_P3.96mm_Vertical` dropped.
