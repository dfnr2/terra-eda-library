# diodes_zener: onsemi MM5Z series

Adds the onsemi MM5Z standard-tolerance Zener family (SOD-523, 500 mW), asked for
by MPN as MM5Z18VT1G.

## Scope

- **Source:** datasheet MM5Z2V4T1/D Rev. 19 (April 2025), parked at
  `datasheets/onsemi/mm5z2v4t1.pdf`.
- **Table:** existing `diodes_zener`, via the shared `_zener_family.emit()` helper.
  The helper gained an `mpn_format` hook because onsemi MPNs don't follow
  prefix + grade + code (`MM5Z18VT1G`, not `MM5Z-C18`).
- **Parts:** 2.4 V to 47 V (32 types), T1G (3,000/reel) commercial orderables.
- **Off by default:**
  - 51–75 V (5 types) are marked "Contact Sales" in the datasheet
    (`INCLUDE_CONTACT_SALES`).
  - T5G 8,000-piece reels (`REEL_SUFFIX`).
  - SZMM5Z AEC-Q101 parts. Same specs, but they'd need an automotive keyword or
    description, which the helper doesn't support yet.
- **Symbol/footprint:** stock `Device:D_Zener` + `Diode_SMD:D_SOD-523`. Pin 1 is
  the cathode, which matches both.
- **Tolerance:** one grade, recorded as 5% (grade C), as for Vishay BZX584C.
- **manufacturer_link:** onsemi's Zener category page. The site has no per-part URL
  that resolves without JavaScript.

## Results

- 32 rows generated. Spot-checked 2V4, 5V1, 18, 27 and 47 against the datasheet
  (Vz window, IZT, ZZT, C).
- Shares `part_locator` per voltage with Nexperia BZX585 and Vishay BZX584C.
- Follow-up: manufacturer spelling is inconsistent across tables (`OnSemi`,
  `ON Semi`, `ON SEMICONDUCTOR`). This family uses the current brand, `onsemi`.
