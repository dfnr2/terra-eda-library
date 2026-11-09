# connectors: TE Connectivity 87224 MOD II header (1-40 positions)

Chosen as the replacement for the obsolete 3M 2303-6111-TG on the Asteroids adapter's
J3/J4 (`connectors-3m-2300-header.md`). Generator
`db/tables/connectors/run_360_te_87224.py`; drawing `datasheets/te/ENG_CD_87224_M.pdf`
(rev M, 2021-05-07; AutoCAD drawing, no text layer).

## Scope (2026-11-09)

- **Whole family on the drawing:** 40 parts, 87224-1 (1 position) to 4-87224-0 (40).
  Part number `<tens>-87224-<units>`, tens prefix omitted below 10.
  The drawing's "positions" column is the count: 87224-3 is 3 positions.
- **Not added:** 4-87224-3, a 3-position part the drawing marks obsolete (single-tube
  packaging).
- **Geometry (drawing):** 0.025in square posts on 0.100in centres; 8.08 mm post above the
  housing with a 5.08 mm gold contact area; 3.18 mm tail (ref); 0.89 mm +/-0.08 mm holes.
- **Finish/materials (drawing):** 15 uin gold in the contact area, gold flash on the solder
  area, all over 50 uin nickel; phosphor-bronze post; black flame-retardant thermoplastic.
- **Symbol / footprint:** stock `Connector_Generic:Conn_01x<NN>` and
  `Connector_PinHeader_2.54mm:PinHeader_1x<NN>_P2.54mm_Vertical`.

## Open items

- **No ratings.** The drawing has no current, voltage, temperature, flammability or RoHS
  statement, so those columns are blank (not guessed). `rohs` is NULL.
- **Lifecycle `Active` is assumed:** the only obsolete mark on the drawing is 4-87224-3.
  Not checked against a distributor.
- **Hole size:** stock footprint has 1.0 mm holes; the drawing recommends 0.89 mm.
- **Stackable housing:** the post is much longer than a standard 0.100in header; check
  clearance against the 3M part it replaces on the adapter (5.84 mm post).
