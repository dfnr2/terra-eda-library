#!/usr/bin/env python3
"""Small-signal Schottky diodes in DO-35: BAT85S, BAT43, 1N5711.

onsemi makes none of these, so each comes from its current maker:
  - Vishay BAT85S (datasheets/vishay/bat85s.pdf, doc 85513 Rev 2.2, 07-Nov-2024):
    VR 30 V, IF 200 mA, IFSM 5 A (10 ms), VF 320 mV at 1 mA / 400 mV at 10 mA /
    800 mV at 100 mA, CD 10 pF, trr 5 ns, Tj 125 C. The original BAT85 is Nexperia's
    and is non-stocked at Mouser; BAT85S is Vishay's current DO-35 part.
  - Vishay BAT43 (datasheets/vishay/bat42-bat43.pdf, doc 85660 Rev 2.2, 12-May-2025):
    VRRM 30 V, IF 200 mA, IFSM 4 A, Ptot 200 mW, VF 330 mV at 2 mA / 450 mV at 15 mA /
    1 V at 200 mA, CD 7 pF typ, trr 5 ns, Tamb -65 to +125 C. ST's BAT43 is obsolete.
  - Microchip (ex-Microsemi) 1N5711 (datasheets/microchip/1n5711-1n5712-schottky-lds-0040.pdf,
    T4-LDS-0040 Rev 4, 2013): V(BR) 70 V min, VRWM 50 V, IO 33 mA, VF 0.41 V at 1 mA /
    1.0 V at 15 mA, IR 200 nA at 50 V, C 2 pF, TJ -65 to +150 C. Vishay's and ST's
    1N5711 are obsolete. The sheet's "-1" suffix marks the metallurgically bonded
    build; the stocked commercial code is plain 1N5711, which is tin-lead (the e3
    RoHS option is non-stocked), so rohs = 'No'.

Codes are the ones Mouser had in stock on 2026-11-24: BAT85S-TAP, BAT43-TAP (ammo; the
-TR reels are non-stocked or ordered alike), 1N5711. All Active.

Symbols: stock Diode:BAT85 (BAT85S has the same two pins), Diode:BAT43, Diode:1N5711;
footprint DO-35 at 7.62 mm. Plan: plans/diodes-th.md.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _diodes_th import PKG, check_datasheets, write  # noqa: E402

OUTPUT_FILE = HERE / "diodes_th_generated_310_small_schottky.sql"
CREATED_BY = Path(__file__).name

COMMON = {
    "package": "DO-35", "kicad_footprint": PKG["DO-35"], "pin_count": "2",
    "lifecycle_status": "Active", "allow_substitution": "Yes", "tracking": "No",
    "created_by": CREATED_BY, "diode_type": "schottky",
}

PARTS = [
    dict(COMMON, unique_id="Vishay-BAT85S-TAP", mpn="BAT85S-TAP", manufacturer="Vishay",
         value="BAT85S", kicad_symbol="Diode:BAT85", rohs="Yes",
         datasheet="${TERRA_EDA_LIB}/datasheets/vishay/bat85s.pdf",
         manufacturer_link="https://www.vishay.com/en/product/85513/",
         part_locator="diode-schottky-30v-200ma-do35",
         description=("Small-signal Schottky diode BAT85S, 30V, 200mA, IFSM 5A, "
                      "VF 320mV @ 1mA / 400mV @ 10mA, CD 10pF, trr 5ns, DO-35, ammo pack"),
         keywords="diode,schottky,small signal,BAT85,BAT85S,BAT85S-TAP,DO-35,axial,through-hole",
         voltage_rating="30V", forward_voltage="400mV @ 10mA", forward_current="200mA",
         current_rating="200mA", temp_operating_max=125.0,
         temp_storage_min=-65.0, temp_storage_max=150.0),
    dict(COMMON, unique_id="Vishay-BAT43-TAP", mpn="BAT43-TAP", manufacturer="Vishay",
         value="BAT43", kicad_symbol="Diode:BAT43", rohs="Yes",
         datasheet="${TERRA_EDA_LIB}/datasheets/vishay/bat42-bat43.pdf",
         manufacturer_link="https://www.vishay.com/en/product/85660/",
         part_locator="diode-schottky-30v-200ma-do35",
         description=("Small-signal Schottky diode BAT43, 30V, 200mA, IFSM 4A, "
                      "VF 330mV @ 2mA / 450mV @ 15mA, CD 7pF, trr 5ns, 200mW, DO-35, ammo pack"),
         keywords="diode,schottky,small signal,BAT43,BAT43-TAP,DO-35,axial,through-hole",
         voltage_rating="30V", forward_voltage="450mV @ 15mA", forward_current="200mA",
         current_rating="200mA", power_rating="200mW",
         temp_operating_min=-65.0, temp_operating_max=125.0,
         temp_storage_min=-65.0, temp_storage_max=150.0),
    dict(COMMON, unique_id="Microchip-1N5711", mpn="1N5711", manufacturer="Microchip",
         value="1N5711", kicad_symbol="Diode:1N5711", rohs="No",
         datasheet="${TERRA_EDA_LIB}/datasheets/microchip/1n5711-1n5712-schottky-lds-0040.pdf",
         manufacturer_link=None,
         part_locator="diode-schottky-70v-33ma-do35",
         description=("Small-signal Schottky barrier diode 1N5711, V(BR) 70V min, VRWM 50V, "
                      "IO 33mA, VF 0.41V @ 1mA / 1.0V @ 15mA, IR 200nA @ 50V, C 2pF, "
                      "hermetic glass DO-35"),
         keywords="diode,schottky,small signal,RF,detector,1N5711,DO-35,axial,through-hole",
         voltage_rating="50V", forward_voltage="1.0V @ 15mA", forward_current="33mA",
         current_rating="33mA",
         temp_operating_min=-65.0, temp_operating_max=150.0,
         temp_storage_min=-65.0, temp_storage_max=150.0),
]


def main():
    check_datasheets(PARTS)
    write(OUTPUT_FILE, "small-signal Schottky diodes, DO-35", CREATED_BY, PARTS)


if __name__ == "__main__":
    main()
