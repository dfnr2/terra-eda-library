# capacitors_th: KEMET Goldmax 300-series radial MLCC (C0G + X8L)

**Date:** 2026-11-09
**Status:** Done, 8,759 rows (7,647 C0G + 1,112 X8L) plus 13 custom footprints
**Scope:** add the conformally coated radial Goldmax families to `capacitors_th`.
Needed by the Asteroids adapter (`C315C101J3G5TA`, `C320C475K3N5TA91707301`).
Generator `db/tables/capacitors_th/run_310_kemet_goldmax.py`, catalog
`goldmax_catalog.json` (regenerate with `_goldmax_transcribe.py`).

## Sources

- `datasheets/kemet/KEM_C1049_GOLDMAX_C0G.pdf` (2025-08-05): C0G, 25-250 V, commercial.
- `datasheets/kemet/KEM_C1093_GOLDMAX_X8L.pdf` (2026-01-29): X8L, 25-50 V, commercial and
  automotive (AEC-Q200).

## How it is built

- The datasheet's capacitance-range waterfalls give availability per **size group**
  (cap x voltage), not per style. Every style in a group is orderable at every cell, so
  the generator expands style x capacitance x voltage x tolerance x grade x packaging.
  `_goldmax_transcribe.py` reads the PDFs (`pdftotext -layout`), maps each cell to its
  voltage column by position, and aborts if any code disagrees with its row's capacitance.
- The generator decodes every MPN back (style, capacitance code, tolerance) and fails on
  a mismatch, and fails on a duplicate `unique_id`.
- MPN: `C<style>C<cap code><tol><volt code><G|N>5TA[9170][C-spec]`. Only the 100% matte
  Sn lead finish (`T`) is listed.

## Defaults (config block at the top of the generator)

| Axis | C0G | X8L |
|---|---|---|
| Tolerance | D (below 10 pF), J | K |
| Grade | commercial | commercial + automotive (9170) |
| Packaging | bulk | bulk + 12in tape and reel 7301 |

F/G/K (C0G), J/M (X8L), 7303/7305/7317 packaging are toggles. C321 and C331 are bulk only.

## Footprints

`terra_footprints_capacitors_th`, written by the generator: pads at the datasheet lead
spacing (2.54 / 5.08 / 6.35 / 10.16 mm), drill = lead + 0.3 mm, body outline from the
length (L) and thickness (T) maximums. One per (spacing, L, T): 13. Lead bending (straight,
shoulder, kink, snap-in) does not change the PCB footprint, so it is only in the
description. C32X parts at 4.7 uF and up use T = 4.07 mm per the datasheet footnote.

## Open items

- **No 3D model.**
- Drill and pad sizes are my choice (lead + 0.3 mm, drill + 0.8 mm), not from the
  datasheet, which gives no land pattern.
- Footprint outline uses datasheet maximums, so it is a keep-out, not the nominal body.
- Only commercial/automotive Goldmax C0G and X8L. Other Goldmax dielectrics (X7R, X5R) and
  the 200/400-series are not added.
- The adapter's C320 is labelled 10 uF but its MPN is 4.7 uF (the sheet has nothing
  larger at 25 V); see the adapter conversation.
