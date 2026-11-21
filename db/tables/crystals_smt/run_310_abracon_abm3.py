#!/usr/bin/env python3
"""Abracon ABM3 (2-pad) and ABM3B (4-pad) series: 5.0 x 3.2 mm ceramic SMD crystals.

Datasheets:
  - datasheets/abracon/abm3-5032-crystal.pdf (rev. 04-25-22): standard -10 to
    60 C, +/-50 ppm at 25 C, +/-50 ppm over temperature, 18 pF, 8-54 MHz
    fundamental, drive 10 uW typ / 100 uW max; ESR max by frequency band.
  - datasheets/abracon/abm3b-5032-4pad-crystal.pdf (rev. U, 8/27/2024): same
    standard grade, 8-50 MHz fundamental; ESR max by band. Circuit diagram: crystal
    between pads 1 and 3, pads 2 and 4 to the lid (GND).
  - both keys "<series>-<f>MHz-<CL>-<ESR>-<temp><tol>-<stab>-<pkg>": B = -20 to
    70 C, 2 = +/-20 ppm, T = tape and reel.

Codes: every ABM3 and ABM3B code Mouser stocks in the -B2-T grade, checked
2026-11-20, all Active; all are below 50 MHz, so fundamental.

Symbols Device:Crystal (ABM3) and Device:Crystal_GND24 (ABM3B); footprints
Crystal:Crystal_SMD_Abracon_ABM3-2Pin_5.0x3.2mm and
Crystal:Crystal_SMD_Abracon_ABM3B-4Pin_5.0x3.2mm.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import abracon_options, band, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_smt_generated_310_abracon_abm3.sql")
CREATED_BY = Path(__file__).name

STD = {"cl": 18, "temp": (-10, 60), "tol": 50, "stab": 50}

FAMILIES = {
    "ABM3": dict(
        esr=[((8.0, 8.999), 140), ((9.0, 9.999), 120), ((10.0, 15.999), 60),
             ((16.0, 19.999), 40), ((20.0, 29.999), 30), ((30.0, 54.0), 25)],
        freqs="""12.000 13.560 14.31818 16.000 18.432 20.000 24.000 24.576 25.000
        27.000 28.6363 29.4912 30.000 40.000 48.000""".split(),
        package="SMD 5.0x3.2mm 2-pad", pins=2, symbol="Device:Crystal",
        footprint="Crystal:Crystal_SMD_Abracon_ABM3-2Pin_5.0x3.2mm",
        datasheet="abracon/abm3-5032-crystal.pdf"),
    "ABM3B": dict(
        esr=[((8.0, 9.999), 200), ((10.0, 11.999), 100), ((12.0, 15.999), 70),
             ((16.0, 50.0), 50)],
        freqs="""8.000 12.000 12.288 13.000 13.824 14.31818 15.360 16.000 16.384
        18.432 20.000 24.000 24.576 25.000 27.000 30.000 32.000 40.000
        48.000""".split(),
        package="SMD 5.0x3.2mm 4-pad", pins=4, symbol="Device:Crystal_GND24",
        footprint="Crystal:Crystal_SMD_Abracon_ABM3B-4Pin_5.0x3.2mm",
        datasheet="abracon/abm3b-5032-4pad-crystal.pdf"),
}


def records():
    for series, fam in FAMILIES.items():
        for f in fam["freqs"]:
            mpn = f"{series}-{f}MHZ-B2-T"
            mhz = float(f)
            cl, temp, tol, stab, _ = abracon_options("B2", STD)
            yield row(
                created_by=CREATED_BY, manufacturer="Abracon", series=series, mpn=mpn,
                mhz=mhz, cl=cl, tolerance=tol, stability=stab, esr=band(fam["esr"], mhz),
                mode="fundamental", drive="100µW max", temp=temp,
                package=fam["package"], pins=fam["pins"], footprint=fam["footprint"],
                symbol=fam["symbol"], datasheet=fam["datasheet"],
                extra_keywords=["SMD", "5032"])


def main():
    write(OUTPUT_FILE, "crystals_smt", "Abracon ABM3/ABM3B 5032", CREATED_BY,
          list(records()))


if __name__ == "__main__":
    main()
