#!/usr/bin/env python3
"""ECS HC-49UX (HC-49/U) through-hole crystals and the ECS-10-13-1XH 1 MHz crystal.

ECS fills two gaps in the Abracon AB rows:
  - series-resonant crystals, which the 8224 and 8284 clock generators call for
    (fundamental, series resonant); Abracon stocks AB only with an 18 pF load;
  - vintage frequencies AB is not stocked in: 2.048, 2.4576 (Altair 88-2SIO),
    3.93216 (OSI C1P), 4.032, 4.096, 4.194304, 4.433618 (PAL), 5.0688, 6.5536,
    9.216, 9.8304 and 18.000 MHz (8224 at 2 MHz, IMSAI), 10.738635 MHz (3x NTSC
    colour burst, TMS9918), plus 1.000 MHz (KIM-1).

Datasheet datasheets/ecs/hc-49ux-crystal.pdf (Rev. 2017):
  - standard: -10 to 70 C, +/-30 ppm at 25 C, +/-50 ppm over temperature, drive
    1.0 mW max; the ESR table gives the maximum by frequency, fundamental to
    30 MHz and 3rd overtone above.
  - key "ECS-<abbr>-<CL>-1X": <abbr> from the datasheet's Developed Frequencies
    table (transcribed below; a code not in it fails), <CL> in pF or S = series,
    1X = HC-49UX.
datasheets/ecs/ecs-10-13-1xh-1mhz-crystal.pdf: 1.000 MHz, 13 pF, +/-100 ppm, +/-100
ppm over 0 to 60 C, SL cut fundamental, 3000 ohm max, 500 uW max, HC-49/U.

Codes: every series-resonant (-S-1X) code at a developed frequency, and every
parallel code at a developed frequency that AB is not stocked in, as stocked at
Mouser 2026-11-20 (all Active); plus ECS-107-S-1X, whose abbreviation 107 =
10.738635 MHz is not in the developed table but is how ECS and Mouser list it. Mouser lists ECS-100-S-1X with a 20 pF load; the
key says series, and the key is used.

Symbol Device:Crystal; footprint Crystal:Crystal_HC49-U_Vertical.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import band, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_th_generated_310_ecs_hc49ux.sql")
CREATED_BY = Path(__file__).name
DATASHEET = "ecs/hc-49ux-crystal.pdf"

# Developed Frequencies table: abbreviation -> MHz.
DEVELOPED = {
    "18": 1.8432, "20": 2.0, "20.48": 2.048, "24": 2.4576, "30": 3.0, "32": 3.2768,
    "35": 3.579545, "36": 3.6864, "39": 3.93216, "40": 4.0, "40.3": 4.032,
    "41": 4.096, "42": 4.194304, "44": 4.433618, "49": 4.9152, "50": 5.0,
    "51": 5.0688, "60": 6.0, "65": 6.5536, "73": 7.3728, "80": 8.0, "92.1": 9.216,
    "98.3": 9.8304, "100": 10.0, "110": 11.0, "110.5": 11.0592, "120": 12.0,
    "122.8": 12.288, "143": 14.31818, "147.4": 14.7456, "150": 15.0, "160": 16.0,
    "180": 18.0, "184": 18.432, "196.6": 19.6608, "200": 20.0, "221": 22.1184,
    "240": 24.0, "480": 48.0,
}
EXTRA = {"107": 10.738635}  # stocked ECS code outside the developed table
ESR = [((1.8, 1.999), 750), ((2.0, 2.399), 500), ((2.4, 2.999), 300),
       ((3.0, 3.199), 200), ((3.2, 3.699), 120), ((3.7, 4.199), 100),
       ((4.2, 4.899), 70), ((4.9, 4.999), 55), ((5.0, 5.999), 50), ((6.0, 7.999), 40),
       ((8.0, 9.999), 35), ((10.0, 12.499), 30), ((12.5, 15.999), 25),
       ((16.0, 30.0), 20), ((30.001, 100.0), 40)]

SERIES = """
ECS-18-S-1X ECS-20-S-1X ECS-30-S-1X ECS-35-S-1X ECS-36-S-1X ECS-40-S-1X
ECS-49-S-1X ECS-50-S-1X ECS-51-S-1X ECS-60-S-1X ECS-73-S-1X ECS-80-S-1X
ECS-92.1-S-1X ECS-98.3-S-1X ECS-100-S-1X ECS-110-S-1X ECS-110.5-S-1X ECS-120-S-1X
ECS-122.8-S-1X ECS-143-S-1X ECS-147.4-S-1X ECS-150-S-1X ECS-160-S-1X ECS-180-S-1X
ECS-184-S-1X ECS-196.6-S-1X ECS-200-S-1X ECS-240-S-1X ECS-480-S-1X ECS-107-S-1X
""".split()
PARALLEL_GAPS = """
ECS-20.48-12-1X ECS-24-32-1X ECS-39-17-1X ECS-40.3-20-1X ECS-41-20-1X
ECS-42-12-1X ECS-44-20-1X ECS-51-20-1X ECS-65-12-1X ECS-92.1-20-1X ECS-98.3-20-1X
ECS-180-20-1X
""".split()

COMMON = dict(created_by=CREATED_BY, manufacturer="ECS", package="HC-49/U", pins=2,
              footprint="Crystal:Crystal_HC49-U_Vertical", symbol="Device:Crystal")


def records():
    for mpn in SERIES + PARALLEL_GAPS:
        _, abbr, cl, pkg = mpn.split("-")
        assert pkg == "1X", mpn
        mhz = DEVELOPED.get(abbr) or EXTRA[abbr]
        yield row(
            **COMMON, series="HC-49UX", mpn=mpn, mhz=mhz,
            cl="S" if cl == "S" else float(cl), tolerance=30, stability=50,
            esr=band(ESR, mhz), mode="3rd overtone" if mhz > 30 else "fundamental",
            drive="1000µW max", temp=(-10, 70), datasheet=DATASHEET,
            extra_keywords=["through-hole"] + (["series resonant"] if cl == "S" else []))
    yield row(
        **COMMON, series="HC-49U", mpn="ECS-10-13-1XH", mhz=1.0, cl=13.0,
        tolerance=100, stability=100, esr=3000, mode="fundamental", drive="500µW max",
        temp=(0, 60), datasheet="ecs/ecs-10-13-1xh-1mhz-crystal.pdf",
        extra_keywords=["through-hole", "SL cut"])


def main():
    write(OUTPUT_FILE, "crystals_th", "ECS HC-49UX", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
