# connectors: Molex Micro-Latch headers (53253 vertical, 53254 right-angle)

Bring the whole Micro-Latch PCB-header family into terra as fully-qualified parts,
every circuit count KiCad ships a footprint for, each with a Molex 3D model. KiCad
ships the 2D (footprints) but no 3D models for this family; terra supplies the 3D.

Triggered by J1/J2 on `abc4-spiro-hw/flow-sensor-adapter` rendering without a model:
they carry the legacy `terra_sym:Molex_Micro-Latch_53254-0470…` footprint, whose STEP
was never committed to main (it sits on the unmerged `add-legacy-3d-models` branch).

## Scope (agreed 2026-10-12)

- **Parts:** 28 rows. 53253-0270…1570 (vertical) and 53254-0270…1570 (right-angle),
  2–15 circuits, exactly the set of KiCad `Connector_Molex` footprints.
- **Suffix -xx70 only:** tin plating, tray, 3.50 mm PC tail. The -xx50 parts KiCad
  lists as "compatible alternatives" are skipped (status unconfirmed).
- **Table:** existing `connectors`. Generator `db/tables/connectors/run_320_molex_micro_latch.py`.
  The 532540470 row moves out of `run_310_cart_harvest.py` into it.
- **Symbol:** stock `Connector_Generic:Conn_01xNN` (Dave's call: generic connector symbol).
- **Footprints:** KiCad's stock footprints, vendored into
  `terra_footprints_connectors.pretty` with only the `(model …)` block rewritten, so
  pads stay identical to KiCad's. The generator's `--vendor-footprints` mode writes
  them from the installed KiCad library (a maintenance step; the output is committed).
- **3D models:** Molex STEPs in `assets/3dmodels/terra-connectors.3dshapes/<series>-<NN>70.stp`.
  Molex's site blocks scripted downloads (Akamai); fetch through Chrome.
- **Datasheet:** the Molex sales drawings (532530000-SD / 532540000-SD) parked in
  `datasheets/molex/`. Same download constraint as the models.

## Parameters

Family-wide, from Molex part-detail sheets (distributor mirrors of molex.com):

| Field | Value | Note |
|---|---|---|
| current_rating | 2.0 A per contact | all sheets agree |
| voltage_rating | 250 V | 2024 sheets (532540270, 532540670); pre-2022 sheets said 125 V. Same product spec 510650000-PS-000 |
| temp_operating | -55 … +105 °C | 2022+ sheets; older said -40 °C |
| plating | tin, 1.016 µm min | the -xx70 suffix |
| polarized / shroud | yes / 3-sided (partial) | |
| locking_mechanism | friction | "Lock to Mating Part: Yes"; Molex calls the mating housing "Friction Lock" |
| mates_with | 51065-NN00 receptacle housing, 50212 crimp terminals | |

## 3D placement

The current Molex STEPs put the origin at the body centre, so placement is a formula per
series: x = (circuits − 1) mm, then 53253 (y −2.55, z 7.30, rotate −90/−180/180) and
53254 (y 7.8, z 4.6, rotate 180/0/0). 53253-0270 only exists as an older export with a
different origin; it carries its own placement in `MODEL_OVERRIDES`.

Checked with FreeCAD for all 28: the STEP is transformed by KiCad's model matrix, the pin
tails below the board are sliced and compared with the pads (0.0 mm error), the body
matches the F.Fab outline, the housing seats at z = 0 and the tails end 3.50 mm below
(Molex's PC tail length). Heights above the board: 5.61 mm vertical, 4.2 mm right-angle.
The legacy hand placements (z 7.24 / 4.5) sank the housing 0.06 / 0.1 mm into the board.

## Results

- 28 rows build (`make verify` clean, 178 tests pass); 28 footprints vendored.
- 532540470 moved from `run_310_cart_harvest.py`; its hand-copied KiCad 9 footprint is
  replaced by the vendored KiCad 10 one (pads identical).
- 3D models: all 28, Molex's own models as exported by TraceParts (Molex's CAD portal).
  molex.com blocks scripted downloads, so they came from public GitHub mirrors:
  27 from `sakthiasthik/ad_library` (TraceParts 2024–25 exports; its 53254-0470 is
  byte-identical to the Molex file terra already had) and 53253-0270 from
  `its-villada/mCALCAN` (TraceParts 2021 export).
- Datasheets: Molex part sheets parked in place of the sales drawings (53253: 0532531170,
  2022; 53254: 532540270, 2024). Replace in place once the drawings can be fetched.
- The older 53254-0270/0370 STEPs in `legacy.3dshapes` (a third origin, 0.05–0.15 mm
  off the pads) are not reused.
