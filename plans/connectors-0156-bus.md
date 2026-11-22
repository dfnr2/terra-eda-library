# connectors: 0.156" pin buses (TE MTA-156 round-post headers, Molex KK 156 41815 receptacles)

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
drawn for "0.045 square or round pin", so the two mate.

## Scope

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
0.125" tail; no lock. **No electrical or temperature ratings on the drawing**, so
`current_rating`, `voltage_rating` and the temperatures are blank (see follow-ups).

Molex 41815, from product specification PS-08-50-001 rev. U (cited by the drawing):

| Field | Value |
|---|---|
| voltage_rating | 600 V (UL; CSA 250 V) |
| current_rating | right angle and top entry 4.5 A brass / 5.0 A phosphor bronze; bottom entry 4.0 / 4.5 A |
| temp_operating | -40 to +80 °C brass, -40 to +105 °C phosphor bronze |
| housing | polyester, UL94V-0, natural |

## Footprints

KiCad ships footprints for neither family; both generators write theirs into
`terra_footprints_connectors` (shared code in `db/tables/connectors/_conn156.py`), pin 1
at the origin, row along +x, no 3D models.

- TE 640384: 1.60 mm drill (drawing: 0.060" +0.010/-0), 2.40 mm pads; body 0.250" deep,
  n x 0.156" long, posts on the centreline.
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
- `datasheets/molex/kk-156-41815-pcb-receptacle-sd.pdf` (molex.com 009482121_sd, all
  41815 builds)
- `datasheets/molex/kk-396-product-spec-ps-08-50-001.pdf` (already parked for KK 396)

## Follow-ups

- **TE ratings:** park the MTA-156 product specification 108-1051 (and catalog 82056)
  and fill current/voltage/temperature. Chrome blocked the second and later te.com
  downloads in one session (its multiple-downloads prompt).
- **Molex round-pin KK 396 headers:** series 3190 (with polarizing wall, 26-19-21x1,
  stocked at Mouser in many sizes) and 3192 (without) are a same-family round-post
  alternative to TE 640384. Not generated; needs their drawings.

## Results

- 155 rows (14 TE, 141 Molex); 56 footprints; `make verify` clean, 216 tests pass; every
  symbol and footprint resolves.
