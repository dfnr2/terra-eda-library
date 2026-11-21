#!/usr/bin/env python3
"""Abracon ABM10 series: 2.5 x 2.0 mm ceramic SMD crystals (4-pad).

Datasheet datasheets/abracon/abm10-2520-crystal.pdf (revised 04.21.15):
  - standard: -10 to 60 C, +/-20 ppm at 25 C, +/-30 ppm over temperature, 10 pF,
    12-55 MHz fundamental, drive 10 uW typ / 100 uW max; Table 1 ESR max 250 ohm
    to 15.999 MHz, 150 to 19.999, 100 to 29.999, 70 to 55 MHz.
  - key "ABM10-<f>MHz-<CL>-<ESR>-<tol>-<temp+stab>-<pkg>": the temperature and
    stability options combine into one code (E20 = -20 to 70 C +/-20 ppm, D30 =
    -40 to 85 C +/-30 ppm); tolerance and CL blank = standard; T = 1k reel,
    T3 = 3k reel.
  - top view: crystal between pads 1 and 3, pads 2 and 4 GND.

Codes: every ABM10 code Mouser stocks in the -E20-T and -D30-T3 grades, checked
2026-11-20, all Active.

Symbol Device:Crystal_GND24; footprint Crystal:Crystal_SMD_Abracon_ABM10-4Pin_2.5x2.0mm.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import band, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_smt_generated_330_abracon_abm10.sql")
CREATED_BY = Path(__file__).name

ESR = [((12.0, 15.999), 250), ((16.0, 19.999), 150), ((20.0, 29.999), 100),
       ((30.0, 55.0), 70)]
GRADES = {  # option -> (temp range, stability ppm, packaging suffix)
    "E20": ((-20, 70), 20, "T"),
    "D30": ((-40, 85), 30, "T3"),
}
FREQS = {
    "E20": """16.000 16.384 18.432 19.200 20.000 22.1184 24.000 24.576 25.000
    27.000 30.000 40.000 48.000""".split(),
    "D30": """16.000 16.384 18.432 19.200 20.000 22.1184 24.000 25.000 26.000
    27.000 30.000 32.000 40.000 48.000""".split(),
}


def records():
    for grade, freqs in FREQS.items():
        temp, stab, pkg = GRADES[grade]
        for f in freqs:
            mhz = float(f)
            yield row(
                created_by=CREATED_BY, manufacturer="Abracon", series="ABM10",
                mpn=f"ABM10-{f}MHZ-{grade}-{pkg}", mhz=mhz, cl=10, tolerance=20,
                stability=stab, esr=band(ESR, mhz), mode="fundamental",
                drive="100µW max", temp=temp, package="SMD 2.5x2.0mm 4-pad", pins=4,
                footprint="Crystal:Crystal_SMD_Abracon_ABM10-4Pin_2.5x2.0mm",
                symbol="Device:Crystal_GND24",
                datasheet="abracon/abm10-2520-crystal.pdf",
                extra_keywords=["SMD", "2520"])


def main():
    write(OUTPUT_FILE, "crystals_smt", "Abracon ABM10 2520", CREATED_BY,
          list(records()))


if __name__ == "__main__":
    main()
