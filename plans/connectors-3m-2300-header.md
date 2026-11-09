# connectors: 3M 2300 pin strip header (2303-6111-TG)

Needed by the Asteroids adapter (J3, J4). Generator
`db/tables/connectors/run_350_3m_2300.py`; datasheet `datasheets/3m/ts0766.pdf`
(TS-0766-B, 2008-08-04).

## Scope (2026-11-09)

- **Part:** 3M 2303-6111-TG only: one row, 3 pins, 0.100" pitch, straight, 0.230" pin,
  0.120" solder tails, 10 uin gold. Decoded from the sheet's `23XX-6XXX-XX` ordering
  table. The adapter schematic spells it `2303-6111TG`; the sheet and Digi-Key use the
  hyphenated form, which is the MPN here (the schematic spelling is in the keywords).
- **Symbol / footprint:** stock `Connector_Generic:Conn_01x03` and
  `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical`.
- **Ratings** from the sheet: 3 A, 100 VRMS withstanding, insulation resistance
  > 5e9 ohm, -55 to +105 C, UL94 V-0.
- **RoHS = No:** the solder tails are 90/10 tin-lead.

## Open items

- **Lifecycle is from a search snippet:** Digi-Key Canada lists the part obsolete. The 3M,
  Digi-Key and Mouser pages block automated fetches, so it is unconfirmed from 3M. The row
  is `Obsolete`; check a distributor page and fix the row if it is still active.
- **Replacement: TE 87224-3** (chosen 2026-11-09; see `connectors-te-87224-header.md`),
  recorded in `bom_comment`. Same 0.025in post and gold contact area, but a longer post
  (8.08 mm vs 5.84 mm) and a stackable housing, so check the adapter's J3/J4 clearance.
  Molex 22-28-4030 (breakaway, tin) is the other 1x3 option in terra.
- Hole size: stock footprint has 1.0 mm holes; the sheet recommends 1.02 mm (1.0 mm for the
  kinked end tails on other variants).
- The sheet covers the whole 2300 family (1 and 2 row, straight and right angle, other
  platings and pin counts); only this part is listed.
