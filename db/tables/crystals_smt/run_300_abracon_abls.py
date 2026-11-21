#!/usr/bin/env python3
"""Abracon ABLS series: HC-49/US SMD crystals (11.4 x 4.7 x 4.2 mm).

Datasheet datasheets/abracon/abls-hc49us-smd-crystal.pdf (drawing 450669 rev. AD):
  - standard: 0 to 70 C, +/-50 ppm at 25 C, +/-50 ppm over temperature, 18 pF,
    3.579545-24 MHz fundamental and 24.01-75 MHz 3rd overtone, drive 100 uW typ /
    1000 uW max; Table 1 gives the ESR maximum by frequency and mode.
  - key "ABLS-<f>MHz-<CL>-<ESR>-<temp><tol>-<stab>-<mode>-<pkg>": B = -20 to
    70 C, 2 = +/-20 ppm, F = fundamental AT above 24 MHz, T = tape and reel.

Codes: every ABLS code Mouser stocks in the -B2-T grade (and -B2F-T), checked
2026-11-20, all Active.

Symbol Device:Crystal; footprint Crystal:Crystal_SMD_HC49-SD.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import abracon_options, band, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_smt_generated_300_abracon_abls.sql")
CREATED_BY = Path(__file__).name

STD = {"cl": 18, "temp": (0, 70), "tol": 50, "stab": 50}
ESR_FUND = [((3.579545, 4.999), 180), ((5.0, 5.999), 120), ((6.0, 7.999), 100),
            ((8.0, 8.999), 80), ((9.0, 9.999), 60), ((10.0, 15.999), 50),
            ((16.0, 50.0), 40)]
ESR_3OT = [((24.01, 31.999), 100), ((32.0, 75.0), 80)]

FREQS_B2 = """3.579545 3.6864 4.000 4.9152 5.000 7.3728 8.000 8.192 10.000 11.0592
12.000 12.288 14.31818 14.7456 16.000 18.432 19.6608 20.000 22.1184 24.000 32.000
48.000 49.152""".split()
FREQS_B2F = "24.576 25.000 27.000".split()


def records():
    codes = ([f"ABLS-{f}MHZ-B2-T" for f in FREQS_B2]
             + [f"ABLS-{f}MHZ-B2F-T" for f in FREQS_B2F])
    for mpn in codes:
        _, f, opts = mpn.split("-", 2)
        mhz = float(f.removesuffix("MHZ"))
        cl, temp, tol, stab, fund = abracon_options(opts.removesuffix("-T"), STD)
        overtone = mhz > 24 and not fund
        yield row(
            created_by=CREATED_BY, manufacturer="Abracon", series="ABLS", mpn=mpn,
            mhz=mhz, cl=cl, tolerance=tol, stability=stab,
            esr=band(ESR_3OT if overtone else ESR_FUND, mhz),
            mode="3rd overtone" if overtone else "fundamental", drive="1000µW max",
            temp=temp, package="HC-49/US SMD", pins=2,
            footprint="Crystal:Crystal_SMD_HC49-SD", symbol="Device:Crystal",
            datasheet="abracon/abls-hc49us-smd-crystal.pdf", extra_keywords=["SMD"])


def main():
    write(OUTPUT_FILE, "crystals_smt", "Abracon ABLS HC-49/US SMD", CREATED_BY,
          list(records()))


if __name__ == "__main__":
    main()
