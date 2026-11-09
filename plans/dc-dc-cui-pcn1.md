# dc_dc_converters: CUI PCN1-S family + discontinued PDM1-S5-D15-S

New table for isolated DC-DC converter modules. Needed by the Asteroids adapter (VR1,
`PDM1-S5-D15-S`). Generator `db/tables/dc_dc_converters/run_300_cui_pcn1_pdm1.py`,
type fragment `db/schema/types/dc_dc.sql`.

## Scope (2026-11-06)

- **PCN1-S, all 18 models** from `datasheets/cui/PCN1-S.pdf` (2025-04-24): 5/12/24 V in;
  5/12/15 V single and +/-5/12/15 V dual out; all 1 W, 1500 Vdc, unregulated.
- **PDM1-S5-D15-S only** from `datasheets/cui/PDM1-S.pdf`. The sheet is stamped
  DISCONTINUED, so `lifecycle_status = 'Obsolete'`, and `bom_comment` names the
  replacement. The other PDM1-S models are not listed.
- **Symbols:** `terra_symbols_dc_dc_converters:DCDC_Isolated_Single` (pins 1,2,4,6) and
  `DCDC_Isolated_Dual` (pins 1,2,4,5,6).
- **Footprints** (`terra_footprints_dc_dc_converters`), vendored from the adapter's
  `CONV_PDM1-S5-D15-S`: `CUI_PCN1-S_SIP-5_P2.54mm` (6.1 mm body; used by the 5/12 V PCN1-S
  models and by the PDM1-S5-D15-S) and `CUI_PCN1-S24_SIP-5_P2.54mm` (7.2 mm body, 24 V
  models). The PDM1-S and PCN1-S have the same pad pattern (pins 1,2,4,5,6 at 2.54 mm)
  and pinout, so they share one footprint; only the body differs (6.0 vs 6.1 mm).

## Open items

- **Replacement confirmed (2026-11-09):** `PCN1-S5-D15-S`. The adapter uses both the +15 V
  and -15 V outputs to power the op-amp, so the +/-15 V dual is the like-for-like part
  (not the 12 V single, which was named earlier). The adapter BOM text for VR1 ("15 Vdc,
  0.067 A") is left as the description; terra carries the PCN1-S MPN.
- **Footprint geometry is approximate.** Pads are the adapter's (1.508 mm pad, 1.0 mm
  drill; the PCN datasheet recommends 0.8 mm hole, 1.5 mm pad). Body outlines for the
  two PCN footprints are re-drawn from the datasheet's 6.1/7.2 mm widths but not
  checked against its layout drawing.
- **3D model:** `CUI_PCN1-S_SIP-5` uses CUI's PCN1-S5-D15-S model (CC BY-ND 4.0, kept unmodified, see the 3dshapes README); its
  offset (7.62, 1.475, 0), rotate (-90, 0, 0) was checked by rendering a test board in
  kicad-cli. It is the dual-output model, so single-output parts show a pin 5 that does
  not exist. `CUI_PCN1-S24_SIP-5` has no model (the 24 V body is 7.2 mm wide).
- Single models list pin count 4 (no pin 5); the footprint still carries pad 5.
