#!/usr/bin/env python3
"""Bourns 3296: 3/8" square 25-turn cermet trimpots, all five pin styles.

The classic multiturn trimmer of 1975-85 boards (SWTPC, S-100 and test gear) and
still the jellybean one.

Datasheet datasheets/bourns/3296-trimpot.pdf:
  - 10 ohm to 2 Mohm (standard resistance table), +/-10 %, 0.5 W at 70 C (300 V
    max), +/-100 ppm/C, -55 to 125 C, 25 turns nominal, cermet.
  - key "3296<style>-1-<code><pkg>LF": -1 = standard product, <code> from the
    standard resistance table, blank packaging = tube, LF = 100 % tin (RoHS).
  - pin styles: W (top adjust, pins in line), Y (top adjust, staggered), P, X and
    Z (side adjust).

Codes: every standard-table value in each style, tube, LF. All are listed Active
at Mouser (checked 2026-11-21); some were on order rather than in stock that day.

Symbol Device:R_Potentiometer_Trim (1 and 3 the ends, 2 the wiper, as Bourns:
1 CCW, 2 wiper, 3 CW); footprints the stock Potentiometer_THT:Potentiometer_Bourns_3296*.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _pot import BOURNS_CODES, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("potentiometers_th_generated_300_bourns_3296.sql")
CREATED_BY = Path(__file__).name

# style -> (adjustment, KiCad footprint)
STYLES = {
    "W": ("top", "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical"),
    "Y": ("top", "Potentiometer_THT:Potentiometer_Bourns_3296Y_Vertical"),
    "P": ("side", "Potentiometer_THT:Potentiometer_Bourns_3296P_Horizontal"),
    "X": ("side", "Potentiometer_THT:Potentiometer_Bourns_3296X_Horizontal"),
    "Z": ("side", "Potentiometer_THT:Potentiometer_Bourns_3296Z_Horizontal"),
}

# style -> standard-table codes generated (all listed Active at Mouser, 2026-11-21).
STOCKED = {s: list(BOURNS_CODES) for s in STYLES}


def records():
    for style, codes in STOCKED.items():
        adjustment, footprint = STYLES[style]
        for code in codes:
            yield row(
                created_by=CREATED_BY, manufacturer="Bourns", series="3296",
                style=f"3296{style}", mpn=f"3296{style}-1-{code}LF",
                ohms=BOURNS_CODES[code], tolerance="±10%", power="1/2W",
                temp_coeff="±100ppm/°C", composition="Cermet", turns=25,
                adjustment=adjustment, temp=(-55, 125),
                package=f"Trimpot 3/8in square 3296{style}", footprint=footprint,
                datasheet="bourns/3296-trimpot.pdf")


def main():
    write(OUTPUT_FILE, "Bourns 3296", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
