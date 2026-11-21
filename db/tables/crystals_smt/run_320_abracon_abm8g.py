#!/usr/bin/env python3
"""Abracon ABM8G series: 3.2 x 2.5 mm ceramic SMD crystals (4-pad).

Datasheet datasheets/abracon/abm8g-3225-crystal.pdf (revised 08.13.15):
  - standard: -10 to 60 C, +/-50 ppm at 25 C, +/-50 ppm over temperature, 10 pF,
    12-50 MHz fundamental, drive 10 uW typ / 100 uW max; ESR max 120 ohm at
    12.000 MHz, 80 to 20 MHz, 60 to 28 MHz, 50 to 50 MHz.
  - key "ABM8G-<f>MHz-<CL>-<ESR>-<temp><tol>-<stab>-<pkg>": D = -40 to 85 C,
    2 = +/-20 ppm, Y = +/-30 ppm, T = tape and reel (1k).
  - top view: crystal between pads 1 and 3, pads 2 and 4 GND.

Codes: every ABM8G code Mouser stocks in the -18-D2Y-T grade (18 pF, -40 to
85 C), its best-stocked grade, checked 2026-11-20, all Active.

Symbol Device:Crystal_GND24; footprint Crystal:Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import abracon_options, band, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_smt_generated_320_abracon_abm8g.sql")
CREATED_BY = Path(__file__).name

STD = {"cl": 10, "temp": (-10, 60), "tol": 50, "stab": 50}
ESR = [((12.0, 12.0), 120), ((12.001, 20.0), 80), ((20.001, 28.0), 60),
       ((28.001, 50.0), 50)]
FREQS = """12.000 12.288 13.000 13.560 14.31818 14.7456 16.000 16.384 18.432 20.000
22.1184 24.000 25.000 26.000 27.000 28.63636 30.000 48.000""".split()


def records():
    for f in FREQS:
        mpn = f"ABM8G-{f}MHZ-18-D2Y-T"
        mhz = float(f)
        cl, temp, tol, stab, _ = abracon_options("18-D2Y", STD)
        yield row(
            created_by=CREATED_BY, manufacturer="Abracon", series="ABM8G", mpn=mpn,
            mhz=mhz, cl=cl, tolerance=tol, stability=stab, esr=band(ESR, mhz),
            mode="fundamental", drive="100µW max", temp=temp,
            package="SMD 3.2x2.5mm 4-pad", pins=4,
            footprint="Crystal:Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm",
            symbol="Device:Crystal_GND24", datasheet="abracon/abm8g-3225-crystal.pdf",
            extra_keywords=["SMD", "3225"])


def main():
    write(OUTPUT_FILE, "crystals_smt", "Abracon ABM8G 3225", CREATED_BY,
          list(records()))


if __name__ == "__main__":
    main()
