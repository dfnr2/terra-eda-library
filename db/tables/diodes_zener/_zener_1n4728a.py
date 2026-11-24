"""Shared table and row builder for the 1 W 1N4728A-1N4764A Zener series (DO-41).

DATA is transcribed from Central Semiconductor's 1N4728A THRU 1N4764A sheet (R2,
14-October 2013), which covers all 37 types. onsemi's 1N4728A-1N4758A sheet
(1N4736AT/D Rev. 10, August 2021) lists 28 of them, and its figures match this table
on every value.

The last current column is the non-repetitive peak reverse (surge) current, IZSM in
onsemi's sheet (8.3 ms square wave). Central's sheet heads the same numbers "maximum
DC current IZM", but 1380 mA for a 1 W, 3.3 V part is far beyond PD/VZ (about
300 mA), so it is recorded as the surge rating.

Used by run_331_central_1n4728a.py and run_332_onsemi_1n4728a.py.
"""
from _zener_family import COLS, _sql

FOOTPRINT = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"

# type: (VZ min, nom, max, IZT mA, ZZT ohm, ZZK ohm, IZK mA, IR uA, VR V, IZSM mA,
#        temperature coefficient %/C)
DATA = {
    "1N4728A": (3.135, 3.3, 3.465, 76, 10, 400, 1.0, 100, 1.0, 1380, "-0.08 to -0.05"),
    "1N4729A": (3.420, 3.6, 3.780, 69, 10, 400, 1.0, 100, 1.0, 1260, "-0.08 to -0.05"),
    "1N4730A": (3.705, 3.9, 4.095, 64, 9.0, 400, 1.0, 50, 1.0, 1190, "-0.07 to -0.02"),
    "1N4731A": (4.085, 4.3, 4.515, 58, 9.0, 400, 1.0, 10, 1.0, 1070, "-0.07 to -0.01"),
    "1N4732A": (4.465, 4.7, 4.935, 53, 8.0, 500, 1.0, 10, 1.0, 970, "-0.03 to +0.04"),
    "1N4733A": (4.845, 5.1, 5.355, 49, 7.0, 550, 1.0, 10, 1.0, 890, "-0.01 to +0.04"),
    "1N4734A": (5.320, 5.6, 5.880, 45, 5.0, 600, 1.0, 10, 2.0, 810, "0 to +0.045"),
    "1N4735A": (5.890, 6.2, 6.510, 41, 2.0, 700, 1.0, 10, 3.0, 730, "+0.01 to +0.055"),
    "1N4736A": (6.460, 6.8, 7.140, 37, 3.5, 700, 1.0, 10, 4.0, 660, "+0.015 to +0.06"),
    "1N4737A": (7.125, 7.5, 7.875, 34, 4.0, 700, 0.5, 10, 5.0, 605, "+0.02 to +0.065"),
    "1N4738A": (7.790, 8.2, 8.610, 31, 4.5, 700, 0.5, 10, 6.0, 550, "+0.03 to +0.07"),
    "1N4739A": (8.645, 9.1, 9.555, 28, 5.0, 700, 0.5, 10, 7.0, 500, "+0.035 to +0.075"),
    "1N4740A": (9.500, 10, 10.50, 25, 7.0, 700, 0.25, 10, 7.6, 454, "+0.04 to +0.08"),
    "1N4741A": (10.45, 11, 11.55, 23, 8.0, 700, 0.25, 5.0, 8.4, 414, "+0.045 to +0.08"),
    "1N4742A": (11.40, 12, 12.60, 21, 9.0, 700, 0.25, 5.0, 9.1, 380, "+0.045 to +0.085"),
    "1N4743A": (12.35, 13, 13.65, 19, 10, 700, 0.25, 5.0, 9.9, 344, "+0.05 to +0.085"),
    "1N4744A": (14.25, 15, 15.75, 17, 14, 700, 0.25, 5.0, 11.4, 304, "+0.055 to +0.09"),
    "1N4745A": (15.20, 16, 16.80, 15.5, 16, 700, 0.25, 5.0, 12.2, 285, "+0.055 to +0.09"),
    "1N4746A": (17.10, 18, 18.90, 14, 20, 750, 0.25, 5.0, 13.7, 250, "+0.06 to +0.09"),
    "1N4747A": (19.00, 20, 21.00, 12.5, 22, 750, 0.25, 5.0, 15.2, 225, "+0.06 to +0.09"),
    "1N4748A": (20.90, 22, 23.10, 11.5, 23, 750, 0.25, 5.0, 16.7, 205, "+0.06 to +0.095"),
    "1N4749A": (22.80, 24, 25.20, 10.5, 25, 750, 0.25, 5.0, 18.2, 190, "+0.06 to +0.095"),
    "1N4750A": (25.65, 27, 28.35, 9.5, 35, 750, 0.25, 5.0, 20.6, 170, "+0.06 to +0.095"),
    "1N4751A": (28.50, 30, 31.50, 8.5, 40, 1000, 0.25, 5.0, 22.8, 150, "+0.06 to +0.095"),
    "1N4752A": (31.35, 33, 34.65, 7.5, 45, 1000, 0.25, 5.0, 25.1, 135, "+0.06 to +0.095"),
    "1N4753A": (34.20, 36, 37.80, 7.0, 50, 1000, 0.25, 5.0, 27.4, 125, "+0.06 to +0.095"),
    "1N4754A": (37.05, 39, 40.95, 6.5, 60, 1000, 0.25, 5.0, 29.7, 115, "+0.06 to +0.095"),
    "1N4755A": (40.85, 43, 45.15, 6.0, 70, 1500, 0.25, 5.0, 32.7, 110, "+0.06 to +0.095"),
    "1N4756A": (44.65, 47, 49.35, 5.5, 80, 1500, 0.25, 5.0, 35.8, 95, "+0.06 to +0.095"),
    "1N4757A": (48.45, 51, 53.55, 5.0, 95, 1500, 0.25, 5.0, 38.8, 90, "+0.06 to +0.095"),
    "1N4758A": (53.20, 56, 58.80, 4.5, 110, 2000, 0.25, 5.0, 42.6, 80, "+0.06 to +0.095"),
    "1N4759A": (58.90, 62, 65.10, 4.0, 125, 2000, 0.25, 5.0, 47.1, 70, "+0.06 to +0.095"),
    "1N4760A": (64.60, 68, 71.40, 3.7, 150, 2000, 0.25, 5.0, 51.7, 65, "+0.06 to +0.095"),
    "1N4761A": (71.25, 75, 78.75, 3.3, 175, 2000, 0.25, 5.0, 56.0, 60, "+0.06 to +0.095"),
    "1N4762A": (77.90, 82, 86.10, 3.0, 200, 3000, 0.25, 5.0, 62.2, 55, "+0.06 to +0.095"),
    "1N4763A": (86.45, 91, 95.55, 2.8, 250, 3000, 0.25, 5.0, 69.2, 50, "+0.06 to +0.095"),
    "1N4764A": (95.00, 100, 105.0, 2.5, 350, 3000, 0.25, 5.0, 76.0, 45, "+0.06 to +0.095"),
}


def rows(*, manufacturer, short, types, mpn, packing_text, datasheet, link=None,
         created_by):
    """One row per type in `types`; mpn(type) gives the ordering code."""
    for jedec in types:
        vmin, vnom, vmax, izt, zzt, zzk, izk, ir, vr, izsm, tc = DATA[jedec]
        # The nominal sits mid-window: a transcription slip would break this.
        if not (vmin < vnom < vmax and abs((vmin + vmax) / 2 - vnom) < 0.01):
            raise SystemExit(f"{jedec}: VZ window {vmin}-{vmax} does not centre on {vnom}")
        vz = f"{vnom:g}V"
        code = mpn(jedec)
        yield {
            "unique_id": f"{short}-{code.replace(' ', '-')}",
            "part_locator": f"diode-zener-{vz.lower().replace('.', 'v').rstrip('v')}"
                            "-do41",
            "mpn": code, "manufacturer": manufacturer, "package": "DO-41",
            "value": jedec,
            "description": (f"{short} {jedec} Zener diode {vz} +/-5% @ {izt:g}mA, 1W, "
                            f"ZZT {zzt:g} ohm max, ZZK {zzk:g} ohm @ {izk:g}mA, "
                            f"IR {ir:g}uA max @ {vr:g}V, IZSM {izsm}mA, TC {tc}%/C, "
                            f"DO-41 axial, {packing_text(jedec)}, Pb-free"),
            "datasheet": datasheet, "manufacturer_link": link,
            "kicad_symbol": "Device:D_Zener", "kicad_footprint": FOOTPRINT,
            "rohs": "Yes", "allow_substitution": "Yes", "tracking": "No",
            "source": None, "dump_priority": 0, "tier": 2,
            "keywords": f"zener,voltage-regulator,through-hole,axial,DO-41,1W,5%,{jedec},{vz}",
            "pin_count": "2",
            "temp_operating_min": -65.0, "temp_operating_max": 200.0,
            "temp_storage_min": -65.0, "temp_storage_max": 200.0,
            "zener_voltage": vz, "zener_voltage_min": vmin, "zener_voltage_max": vmax,
            "tolerance": "5%", "test_current": f"{izt:g}mA", "power_rating": "1W",
            "forward_voltage": "1.2V @ 200mA", "impedance_max": float(zzt),
            "capacitance": None, "peak_reverse_current": f"{izsm / 1000:g}A",
        }


def write(output_file, title, created_by, datasheet_root, datasheet, recs):
    if not (datasheet_root / datasheet.replace("${TERRA_EDA_LIB}/", "")).is_file():
        raise SystemExit(f"missing datasheet {datasheet}")
    ids = [r["unique_id"] for r in recs]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate unique_id")
    lines = [
        f"-- Terra EDA Library - {title}",
        f"-- Generated by {created_by}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(_sql(r[c]) for c in COLS)
        lines.append(f"INSERT INTO diodes_zener ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    output_file.write_text("\n".join(lines))
    print(f"Generated {output_file.name}: {len(recs)} parts")
