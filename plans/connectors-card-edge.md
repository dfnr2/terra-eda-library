# connectors: card-edge sockets for vintage buses (`run_380_card_edge.py`)

Part of `plans/vintage-computer-parts.md` phase 8. Follows `plans/connectors-conventions.md`:
each part has a `-pins` per-pin row, and every footprint has a generated 3D model.

## Sources

**Drawings.** EDAC's four ordering guides, downloaded from files.edac.net on
2026-11-22 into `datasheets/edac/`:

| Guide | Pitch | Rows | Insulator height | Series |
|---|---|---|---|---|
| `edac-346-396-card-edge-0125-ordering-guide.pdf` | 0.125" | 0.250" | 0.600" | 346 green DAP / 396 black |
| `edac-345-395-card-edge-0100-ordering-guide.pdf` | 0.100" | 0.200" | 0.600" | 345 / 395 |
| `edac-305-315-355-card-edge-0156-ordering-guide.pdf` | 0.156" | 0.140" | 0.470" | 305 / 355 |
| `edac-307-357-card-edge-0156-ordering-guide.pdf` | 0.156" | 0.200" | 0.473" | 307 / 357 |

**Which part each machine used** (from research on 2026-11-22):

| Machine | Socket | Source |
|---|---|---|
| S-100 | EDAC 346-100-520-202 (green) | s100computers.com extender-board page: "Mouser stocks them (587-346-100)" |
| S-100 | EDAC 396-100-520-202 (black) | Herb Johnson's S-100 connector page |
| Apple II slot | EDAC 345-050-520-202 (green with lugs, original) | applefritter.com/node/32398 |
| Apple II ][+ slot | EDAC 395-050-520-201 (black, no lugs) | applefritter.com/node/32398 |
| KIM-1 application/expansion | EDAC 305-044 | wfd3 KIM-1 breakout names 305-044-500-202, the wire-hole build; the PC-tail 520 build is generated |
| AIM-65 J1/J3, Apple I expansion | 2x22 on 0.156" | Pinout matches the KIM-1; no MPN documented |

## Scope

The generator writes 56 parts, plus their `-pins` twins: 112 rows. All are dual row,
vertical, contact code 520 (PC tail).

- **S-100:** 346-100-520-202 and 396-100-520-202.
- **Apple II:** 345-050-520-202 and 395-050-520-201.
- **0.156":** every size on the 305/355 and 307/357 drawings.
  - 305/355: 2x6, 10, 12, 15, 18, 22, 24, 25, 28, 30, 36 and 43.
  - 307/357: 2x6, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 36, 43 and 44.
  - All use mounting code 202 (flush lugs, 3.25 mm holes).
  - The 2x22 parts carry the KIM-1/AIM-65/Apple I keywords.
- **Not generated:**
  - The offset-lug builds (-802): their lugs stand 4.3 mm off the board, so they need
    a different footprint.
  - Wire-hole (500), wire-wrap and right-angle codes.
  - Sullins EBA50DRTH (Altair, 0.140" rows): only a third-party copy of the drawing
    was found.
  - Sullins EBM22DRXH.
  - The S-100 rows use 0.250" spacing. The Altair and Poly-88 used about 0.140", which
    needs the Sullins part.

## Pad numbering

Pads follow each machine's convention, not the socket's moulded markings:

| Bus | Row 1 (y = 0) | Facing row | Whole symbol | Per-pin symbol |
|---|---|---|---|---|
| S-100 | 1-50 | 51-100 (1 faces 51) | `Conn_CardEdge_2x50_TopBottom` (custom; stock has no 2x50 Top_Bottom) | `Conn_PerPin_100` |
| Apple II | 1-25 | 50-26 (1 faces 50) | stock `Conn_02x25_Counter_Clockwise` | `Conn_PerPin_50` |
| 0.156", up to 22 per row | 1-N | A.. without G/I/O/Q | `Conn_CardEdge_2xNN_NumberLetter` | `Conn_PerPin_EdgeLetter_2xNN` |
| 0.156", over 22 per row | 1-N | N+1-2N | stock `Conn_02xNN_Top_Bottom`, or custom `_TopBottom` above 2x40 | `Conn_PerPin_NN` |

The custom symbols are written by `_connkit.dual_column_symbol` in the stock
Connector_Generic style.

## Footprints and models

- **Footprints:** one per MPN, `EDAC_<mpn>_2xNN_P<pitch>mm_Vertical`.
  - Pin 1 is at the origin and the facing row is at +y.
  - Mounting holes are 3.25 mm NPTH on the row centreline at DIM B.
  - Drills: 1.1 mm for 0.100"/0.125" (drawing 0.042" +0.004); 1.3 mm for 0.156"
    (0.050" +0.004).
  - The F.Fab outline shows overall length A, with the body ends at C.
- **Models:**
  - Insulator: card slot of length D and depth from the drawing, about 2 mm wide.
  - Lugs at the drawing's lug height.
  - Tails: the 520 length, approximate cross-section.
  - Colour: green or black by series.

## Ratings, from each guide's specification table

| | 0.125" / 0.100" | 0.156" |
|---|---|---|
| Current | 3 A | 5 A |
| Dielectric withstand | 1500 / 1200 V AC | 1800 V AC |
| Contact resistance | 10 mΩ | 10 mΩ |
| Insulation resistance | 5000 MΩ | 5000 MΩ |
| Operating temperature | -40 to +105 °C | -40 to +105 °C |
| Flammability | UL94V-0 | UL94V-0 |

## Follow-ups

- **Lifecycle checked at Mouser on 2026-11-23:** all 56 MPNs have a Mouser product
  page with a factory lead time (9-17 weeks), and none is marked obsolete, end of life
  or NRND, so every row stays `Active` and no size was dropped.
  - In stock: the S-100 and Apple II sockets (346-100, 396-100, 345-050, 395-050),
    most 305 sizes, 307-044 (503), 357-044 (325), and a few other 307/357 sizes.
  - Non-stocked but orderable: most 355 and 357 sizes and several 307 sizes.
  - Digi-Key still showed a bot check, so only Mouser was used.
- **Which side is the component side** is unconfirmed for S-100 (1-50) and Apple II
  (1-25), so it's left to the board designer. Which row sits at y = 0 doesn't change the
  part.
- Sullins parts, for the Altair 0.140" S-100, if a drawing turns up.

## Results (2026-11-22)

- 112 rows and 56 footprints and models.
- Symbols added:
  - 8 `Conn_CardEdge_2xNN_NumberLetter`
  - 3 `Conn_CardEdge_2xNN_TopBottom`
  - per-pin symbols for 48, 50, 56, 60, 72, 86, 88 and 100 pins
  - `EdgeLetter` per-pin symbols for 2x6 to 2x20
- `make verify` is clean: 219 tests pass.
- A KiCad 3D render of S-100, Apple II, KIM 2x22 and a 2x43 looked right.
