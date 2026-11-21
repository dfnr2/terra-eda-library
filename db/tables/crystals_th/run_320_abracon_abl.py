#!/usr/bin/env python3
"""Abracon ABL series: HC-49/US (low-profile, 3.5 mm) through-hole crystals.

The jellybean modern through-hole crystal, same 4.88 mm lead spacing as HC-49/U.

Datasheet datasheets/abracon/abl-hc49us-crystal.pdf (rev. 03-31-23):
  - standard: 0 to 70 C, +/-50 ppm at 25 C, +/-50 ppm over temperature, 18 pF,
    3.579545-24 MHz fundamental and 24.01-70 MHz 3rd overtone, drive 100 uW typ /
    1000 uW max; Table 1 gives the ESR maximum by frequency and mode.
  - key "ABL-<f>MHz-<CL>-<ESR>-<temp><tol>-<stab>-<mode>": B = -20 to 70 C,
    2 = +/-20 ppm, F = fundamental AT above 24 MHz.

Codes: every ABL code Mouser stocks in the -B2 grade (and -B2F), checked
2026-11-20, all Active. Mouser lists the 4.194304 MHz part as ABL4.194304MHZB2; it
is written here as the key gives it, with Mouser's spelling as a keyword.

Symbol Device:Crystal; footprint Crystal:Crystal_HC49-4H_Vertical (same land
pattern; KiCad's HC49-4H outline is 0.5 mm taller than the ABL body).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import abracon_options, band, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_th_generated_320_abracon_abl.sql")
CREATED_BY = Path(__file__).name

STD = {"cl": 18, "temp": (0, 70), "tol": 50, "stab": 50}
ESR_FUND = [((3.579, 4.999), 180), ((5.0, 5.999), 120), ((6.0, 7.999), 100),
            ((8.0, 8.999), 80), ((9.0, 9.999), 60), ((10.0, 15.999), 50),
            ((16.0, 50.0), 40)]
ESR_3OT = [((24.01, 31.999), 100), ((32.0, 70.0), 80)]

CODES = """
ABL-3.579545MHZ-B2 ABL-3.6864MHZ-B2 ABL-4.096MHZ-B2 ABL-4.194304MHZ-B2
ABL-4.9152MHZ-B2 ABL-6.000MHZ-B2 ABL-7.3728MHZ-B2 ABL-8.000MHZ-B2 ABL-8.192MHZ-B2
ABL-9.8304MHZ-B2 ABL-11.0592MHZ-B2 ABL-12.000MHZ-B2 ABL-12.288MHZ-B2
ABL-14.31818MHZ-B2 ABL-14.7456MHZ-B2 ABL-16.000MHZ-B2 ABL-16.128MHZ-B2
ABL-16.384MHZ-B2 ABL-18.432MHZ-B2 ABL-19.6608MHZ-B2 ABL-20.000MHZ-B2
ABL-22.1184MHZ-B2 ABL-24.000MHZ-B2 ABL-24.576MHZ-B2F ABL-25.000MHZ-B2F
ABL-27.000MHZ-B2F ABL-32.000MHZ-B2 ABL-40.000MHZ-B2 ABL-40.000MHZ-B2F
ABL-48.000MHZ-B2
""".split()
MOUSER_SPELLING = {"ABL-4.194304MHZ-B2": "ABL4.194304MHZB2"}


def records():
    for mpn in CODES:
        _, f, opts = mpn.split("-", 2)
        mhz = float(f.removesuffix("MHZ"))
        cl, temp, tol, stab, fund = abracon_options(opts, STD)
        overtone = mhz > 24 and not fund
        yield row(
            created_by=CREATED_BY, manufacturer="Abracon", series="ABL", mpn=mpn,
            mhz=mhz, cl=cl, tolerance=tol, stability=stab,
            esr=band(ESR_3OT if overtone else ESR_FUND, mhz),
            mode="3rd overtone" if overtone else "fundamental", drive="1000µW max",
            temp=temp, package="HC-49/US", pins=2,
            footprint="Crystal:Crystal_HC49-4H_Vertical", symbol="Device:Crystal",
            datasheet="abracon/abl-hc49us-crystal.pdf",
            extra_keywords=["through-hole", "low profile"]
            + ([MOUSER_SPELLING[mpn]] if mpn in MOUSER_SPELLING else []))


def main():
    write(OUTPUT_FILE, "crystals_th", "Abracon ABL HC-49/US", CREATED_BY,
          list(records()))


if __name__ == "__main__":
    main()
