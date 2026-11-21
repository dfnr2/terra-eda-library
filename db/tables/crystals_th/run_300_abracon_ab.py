#!/usr/bin/env python3
"""Abracon AB series: HC-49/U (tall, 13.46 mm) through-hole crystals.

The vintage holder: the HC-49/U body and 4.88 mm lead spacing drop into the
HC-18/U and HC-49/U positions of 1975-85 boards.

Datasheet datasheets/abracon/ab-hc49u-crystal.pdf (rev. 10.29.2018):
  - standard: 0 to 70 C, +/-50 ppm at 25 C, +/-100 ppm over temperature, 18 pF,
    1.8432-24 MHz fundamental and 24.01-66 MHz 3rd overtone, drive 100 uW typ /
    1000 uW max; Table 1 gives the ESR maximum by frequency.
  - key "AB-<f>MHz-<CL>-<ESR>-<temp><tol>-<stab>-<mode>": B = -20 to 70 C,
    2 = +/-20 ppm, 4 = +/-30 ppm, F = fundamental AT above 24 MHz; blanks are
    standard.

Codes: every AB code Mouser stocks in its standard -B2 grade (and -B2F above
24 MHz, -B4 for 17.734475 MHz), checked 2026-11-20, all Active; plus
AB-4.433619MHZ (standard grade), the PAL colour-burst frequency. Mouser prints
AB-17.734475-B4 without "MHZ" and it is kept that way.

Symbol Device:Crystal; footprint Crystal:Crystal_HC49-U_Vertical.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import abracon_options, band, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_th_generated_300_abracon_ab.sql")
CREATED_BY = Path(__file__).name

STD = {"cl": 18, "temp": (0, 70), "tol": 50, "stab": 100}
# Table 1: (MHz band) -> ESR max, fundamental; 3rd overtone is 40 ohm.
ESR_FUND = [((1.8432, 1.999), 750), ((2.0, 2.399), 550), ((2.4, 2.999), 350),
            ((3.0, 3.699), 200), ((3.7, 4.199), 100), ((4.2, 4.899), 70),
            ((4.9, 5.999), 50), ((6.0, 7.999), 40), ((8.0, 9.999), 35),
            ((10.0, 12.499), 30), ((12.5, 50.0), 25)]
ESR_3OT = 40

CODES = """
AB-1.8432MHZ-B2 AB-2.000MHZ-B2 AB-3.579545MHZ-B2 AB-3.6864MHZ-B2 AB-4.000MHZ-B2
AB-4.433619MHZ AB-4.9152MHZ-B2 AB-5.000MHZ-B2 AB-6.000MHZ-B2 AB-7.3728MHZ-B2
AB-8.000MHZ-B2 AB-8.192MHZ-B2 AB-10.000MHZ-B2 AB-11.0592MHZ-B2 AB-12.000MHZ-B2
AB-12.288MHZ-B2 AB-14.31818MHZ-B2 AB-14.7456MHZ-B2 AB-16.000MHZ-B2
AB-17.734475-B4 AB-18.432MHZ-B2 AB-19.6608MHZ-B2 AB-20.000MHZ-B2
AB-22.1184MHZ-B2 AB-24.000MHZ-B2 AB-24.576MHZ-B2F AB-25.000MHZ-B2F
AB-27.000MHZ-B2F AB-32.000MHZ-B2 AB-32.768MHZ-B2 AB-48.000MHZ-B2 AB-50.000MHZ-B2
""".split()


def records():
    for mpn in CODES:
        _, f, *opts = mpn.split("-")
        mhz = float(f.removesuffix("MHZ"))
        cl, temp, tol, stab, fund = abracon_options("-".join(opts) or "", STD)
        overtone = mhz > 24 and not fund
        yield row(
            created_by=CREATED_BY, manufacturer="Abracon", series="AB", mpn=mpn,
            mhz=mhz, cl=cl, tolerance=tol, stability=stab,
            esr=ESR_3OT if overtone else band(ESR_FUND, mhz),
            mode="3rd overtone" if overtone else "fundamental", drive="1000µW max",
            temp=temp, package="HC-49/U", pins=2,
            footprint="Crystal:Crystal_HC49-U_Vertical", symbol="Device:Crystal",
            datasheet="abracon/ab-hc49u-crystal.pdf", extra_keywords=["through-hole"])


def main():
    write(OUTPUT_FILE, "crystals_th", "Abracon AB HC-49/U", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
