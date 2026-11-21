#!/usr/bin/env python3
"""Abracon AB26T series: 32.768 kHz tuning-fork watch crystals, 2.1 x 6.2 mm cylinder.

The through-hole real-time-clock crystal (MM58167, MSM5832 and later RTCs).

Datasheet datasheets/abracon/ab26t-32khz-cylinder-crystal.pdf:
  - standard: 32.768 kHz, -10 to 60 C, +/-20 ppm at 25 C, 12.5 pF, ESR 35 kohm max,
    drive 1.0 uW max, turnover 25 +/-5 C, temperature coefficient
    -0.034 +/-0.006 ppm/C^2 (parabolic, so frequency_stability carries the
    coefficient).
  - key "AB26T-<f>-<CL>-<temp>": CL in pF if not 12.5 (e.g. 6); temp E = 0 to
    70 C, B = -20 to 70 C.

Codes: the four AB26T 32.768 kHz codes Mouser stocks, checked 2026-11-20, all
Active.

Symbol Device:Crystal; footprint Crystal:Crystal_C26-LF_D2.1mm_L6.5mm_Vertical.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_th_generated_330_abracon_ab26t.sql")
CREATED_BY = Path(__file__).name

TEMP = {"": (-10, 60), "E": (0, 70), "B": (-20, 70)}
# mpn -> (CL pF, temp option)
CODES = {
    "AB26T-32.768KHZ": (12.5, ""),
    "AB26T-32.768KHZ-6": (6, ""),
    "AB26T-32.768KHZ-E": (12.5, "E"),
    "AB26T-32.768KHZ-6-B": (6, "B"),
}


def records():
    for mpn, (cl, t) in CODES.items():
        yield row(
            created_by=CREATED_BY, manufacturer="Abracon", series="AB26T", mpn=mpn,
            mhz=0.032768, cl=cl, tolerance=20, stability="-0.034ppm/°C²", esr=35000,
            mode="tuning fork", drive="1µW max", temp=TEMP[t],
            package="Cylinder 2.1x6.2mm", pins=2,
            footprint="Crystal:Crystal_C26-LF_D2.1mm_L6.5mm_Vertical",
            symbol="Device:Crystal",
            datasheet="abracon/ab26t-32khz-cylinder-crystal.pdf",
            extra_keywords=["through-hole", "watch crystal", "RTC", "real-time clock",
                            "MM58167", "MSM5832"])


def main():
    write(OUTPUT_FILE, "crystals_th", "Abracon AB26T 32.768 kHz", CREATED_BY,
          list(records()))


if __name__ == "__main__":
    main()
