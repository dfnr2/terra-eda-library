#!/usr/bin/env python3
"""Abracon ABS25 (8.0 x 3.8 mm) and ABS07 (3.2 x 1.5 mm): 32.768 kHz SMD
tuning-fork crystals.

Datasheets:
  - datasheets/abracon/abs25-32khz-crystal.pdf (revised 09-30-19): -40 to 85 C,
    +/-20 ppm at 25 C, 12.5 pF, ESR 50 kohm max, drive 1 uW max, turnover 25 C,
    coefficient -0.035 +/-0.01 ppm/C^2. Key "ABS25-<f>kHz-<CL>-<tol>-<pkg>": CL in
    pF if not 12.5 (e.g. 6); 1 = +/-10 ppm; blank = +/-20 ppm at 32.768 kHz.
    Electrode arrangement: crystal between pads 1 and 4, pads 2 and 3 not connected
    (floating).
  - datasheets/abracon/abs07-32khz-crystal.pdf: -40 to 85 C, +/-20 ppm, 12.5 pF,
    ESR 70 kohm max (-40 to 85 C), drive 0.5 uW max, coefficient -0.036 ppm/C^2
    typ. Key "ABS07-32.768kHz-<height>-<CL>-<tol>-<temp>-<pkg>": CL 9/7/6 pF
    (blank 12.5), tolerance 1 = +/-10 ppm, 4 = +/-30 ppm.

Codes: the 32.768 kHz ABS25 and ABS07 codes Mouser stocks, checked 2026-11-20, all
Active. Not generated: ABS07-32.768KHZ-1-T, because its "1" could be either the
0.65 mm height option or the +/-10 ppm tolerance (Mouser reads it as tolerance);
the 32.000 and 100.000 kHz ABS25 parts.

Symbols: Device:Crystal (ABS07); Device:Crystal_GND23 (ABS25: crystal on 1 and 4;
the floating pads 2 and 3 may be grounded). Footprints
Crystal:Crystal_SMD_Abracon_ABS25-4Pin_8.0x3.8mm and
Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm (stock 3215 land pattern).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from crystal_rows import row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("crystals_smt_generated_340_abracon_32khz.sql")
CREATED_BY = Path(__file__).name

FAMILIES = {
    "ABS25": dict(
        codes={"": (12.5, 20), "6": (6, 20), "1": (12.5, 10), "6-1": (6, 10)},
        esr=50000, drive="1µW max", coeff="-0.035ppm/°C²",
        package="SMD 8.0x3.8mm 4-pad", pins=4, symbol="Device:Crystal_GND23",
        footprint="Crystal:Crystal_SMD_Abracon_ABS25-4Pin_8.0x3.8mm",
        datasheet="abracon/abs25-32khz-crystal.pdf"),
    "ABS07": dict(
        codes={"": (12.5, 20), "9": (9, 20), "7": (7, 20), "6": (6, 20),
               "4": (12.5, 30), "7-1": (7, 10), "6-4": (6, 30), "9-4": (9, 30)},
        esr=70000, drive="0.5µW max", coeff="-0.036ppm/°C²",
        package="SMD 3.2x1.5mm 2-pad", pins=2, symbol="Device:Crystal",
        footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
        datasheet="abracon/abs07-32khz-crystal.pdf"),
}


def records():
    for series, fam in FAMILIES.items():
        for opts, (cl, tol) in fam["codes"].items():
            mpn = "-".join(p for p in (series, "32.768KHZ", opts, "T") if p)
            yield row(
                created_by=CREATED_BY, manufacturer="Abracon", series=series, mpn=mpn,
                mhz=0.032768, cl=cl, tolerance=tol, stability=fam["coeff"],
                esr=fam["esr"], mode="tuning fork", drive=fam["drive"],
                temp=(-40, 85), package=fam["package"], pins=fam["pins"],
                footprint=fam["footprint"], symbol=fam["symbol"],
                datasheet=fam["datasheet"],
                extra_keywords=["SMD", "watch crystal", "RTC", "real-time clock"])


def main():
    write(OUTPUT_FILE, "crystals_smt", "Abracon ABS25/ABS07 32.768 kHz", CREATED_BY,
          list(records()))


if __name__ == "__main__":
    main()
