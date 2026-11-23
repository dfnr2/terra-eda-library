# connectors: EDAC 307 card-edge (307-044-558-202)

Needed by the Asteroids adapter (J1, the cabinet-harness connector). Generator
`db/tables/connectors/run_340_edac_307.py`.

## Scope (2026-11-05)

- **Part:** EDAC 307-044-558-202 only: 44 contacts (2x22), 0.156" contact spacing,
  0.200" row spacing, contact code 558, mounting code 202. Datasheet is EDAC's
  3-page 307/357 drawing, `datasheets/edac/307-044-558-202-card-edge-connector.pdf`.
- **Symbol:** `terra_symbols_connectors:EDAC_Card_Edge_2x22_P3.96mm`. Pins are named for
  the edge position (1-22, then A-Z without G/I/O/Q) to match the pad names.
- **Footprint:** `terra_footprints_connectors:EDAC_307-044-558-202_2x22_P3.96mm`, taken
  from the adapter project's "EDAC 44-pin edge 0.156 universal", with its STEP in
  `assets/3dmodels/terra-connectors.3dshapes/`.

## Open items

- **Orientation left blank.** The drawing's 90-degree bend note names contact codes 522
  and 540 only; this part is 558. Heilind lists it as right angle, the adapter's old
  BOM text says "right angle". Needs a look at the drawing against a real part.
- **Ratings are from the Heilind listing, not the drawing:** 5 A, 1800 VAC.
- **3D model is EDAC's 305-044-0521-202**, a different series and code, carried over
  from the adapter project. Placement is unverified against this part.
- **Footprint not checked against the drawing** (pad pitch, row spacing, hole sizes).
- **Not added, dropped (2026-11-09):** EDAC 305-044-558-202 and Sullins EBC22DKRA. No
  datasheets were found and the decision is to leave them out.
- **Asteroids J2 is not a purchased part.** In the adapter project it is gold fingers
  on the board's own copper (`edge 44-pin 0.156 inch`), so it needs no terra row.

## Per-pin row (2026-11-22)

`EDAC-307-044-558-202-pins` uses `terra_symbols_connectors:Conn_PerPin_EdgeLetter_2x22`
(see `plans/connectors-conventions.md`). The footprint keeps its EDAC 305 STEP.
