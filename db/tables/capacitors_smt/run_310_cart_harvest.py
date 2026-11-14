#!/usr/bin/env python3
"""Harvest a curated Murata MLCC from the abc4-spiro-cart board into capacitors_smt.

GRM155Z71A105KE01D (1uF X7R 0402 10V) is a Murata specialty part -- Samsung's CL
line tops out at 6.3V for 1uF/X7R/0402, so the generated Samsung family can't cover
it. Ported here as a single validated part from its datasheet
(datasheets/murata/grm155z71a105ke01.pdf). A full Murata GRM15 family generator
would need a Murata parametric catalog CSV (the datasheet gives the part-number
convention but no lineup of which combinations exist).

Murata ZRB15 low-acoustic-noise MLCCs (X5R, 1005M/0402, interposer board). The first,
ZRB15XR61A106ME01D (10uF 10V), is used by the cartridge board's C4, C6 and C18. Each type
number has its own datasheet in datasheets/murata/ (ZRB15XR61A106ME01, ...A475ME01,
...60J475ME01, ...60J106ME12, ZRB157R61C225KE11); the sheets give the part-number system but no
lineup, so only parts with a datasheet on disk are listed. Packing code D (180mm reel, 8000
pcs) only; J (330mm reel, 30000 pcs) is also orderable. Reflow only. The datasheets have no RoHS
statement, so rohs is NULL. Not listed (no datasheet found on murata.com): ZRB15XR61A475KE01D,
ZRB15XC80J106ME05D.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parents[3] / "tools"))
from passive_units import unit_value, sim_params  # noqa: E402
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("capacitors_smt_generated_310_cart_harvest.sql")
CREATED_BY = Path(__file__).name

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "sim_params",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "voltage_rating_v", "tolerance", "cap_type", "dielectric_class", "polarized",
    "temp_operating_min", "temp_operating_max", "height_max_mm",
]

PARTS = [
    {
        "unique_id": "Murata-GRM155Z71A105KE01D",
        "part_locator": "cap-mlcc-1u-10v-x7r-0402",
        "mpn": "GRM155Z71A105KE01D", "manufacturer": "Murata",
        "package": "0402", "value": unit_value("1u", "F"), "sim_params": sim_params("C", "1u"),
        "description": "Murata GRM155Z71A105KE01D 1uF X7R 10V +/-10% MLCC, 0402",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/murata/grm155z71a105ke01.pdf",
        "manufacturer_link": "https://www.murata.com/en-us/products/productdetail?partno=GRM155Z71A105KE01%23",
        "kicad_symbol": "Device:C",
        "kicad_footprint": "Capacitor_SMD:C_0402_1005Metric",
        "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
        "keywords": "capacitor,mlcc", "pin_count": "2",
        "voltage_rating_v": 10.0, "tolerance": "10%", "cap_type": "MLCC",
        "dielectric_class": "X7R", "polarized": "No",
        "temp_operating_min": -55.0, "temp_operating_max": 125.0,
    },
]

# Murata ZRB15 low-acoustic-noise MLCCs on an interposer board, 1005M (0402), X5R, reflow
# only, packing code D (180mm reel, 8000 pcs). Each type number has its own datasheet.
# Height max is the T maximum from each datasheet's dimension table.
ZRB_BASE = {
    "manufacturer": "Murata", "package": "0402", "kicad_symbol": "Device:C",
    "kicad_footprint": "Capacitor_SMD:C_0402_1005Metric",
    "rohs": None, "allow_substitution": "No", "tracking": "No",
    "source": None, "dump_priority": 0, "tier": 2, "pin_count": "2",
    "cap_type": "MLCC", "dielectric_class": "X5R", "polarized": "No",
    "temp_operating_min": -55.0, "temp_operating_max": 85.0,
}
ZRB_PARTS = [
    # (mpn, capacitance, volts, tolerance %, height max mm, datasheet file)
    ("ZRB15XR61A106ME01D", "10u", 10.0, 20, 0.85, "ZRB15XR61A106ME01-01A-EN.pdf"),
    ("ZRB15XR61A475ME01D", "4.7u", 10.0, 20, 0.80, "ZRB15XR61A475ME01-02A-EN.pdf"),
    ("ZRB15XR60J475ME01D", "4.7u", 6.3, 20, 0.80, "ZRB15XR60J475ME01-02A-EN.pdf"),
    ("ZRB15XR60J106ME12D", "10u", 6.3, 20, 0.80, "ZRB15XR60J106ME12-01A-EN.pdf"),
    ("ZRB157R61C225KE11D", "2.2u", 16.0, 10, 0.85, "ZRB157R61C225KE11-01A-EN.pdf"),
]


def zrb_part(mpn, cap, volts, tol, height, sheet):
    v = f"{volts:g}"
    return {
        **ZRB_BASE,
        "unique_id": f"Murata-{mpn}",
        "part_locator": f"cap-mlcc-{cap}-{v}v-x5r-0402",
        "mpn": mpn, "value": unit_value(cap, "F"), "sim_params": sim_params("C", cap),
        "description": (f"Murata {mpn} {unit_value(cap, 'F')} X5R {v}V +/-{tol}% low-acoustic-noise "
                        "MLCC on interposer board, 0402 (1005M), reflow only"),
        "datasheet": f"${{TERRA_EDA_LIB}}/datasheets/murata/{sheet}",
        "manufacturer_link": f"https://www.murata.com/en-us/products/productdetail?partno={mpn[:-1]}%23",
        "keywords": f"capacitor,mlcc,low-acoustic-noise,ceramic,X5R,{cap.replace('u', 'uF')},{v}V,0402,ZRB15",
        "voltage_rating_v": volts, "tolerance": f"{tol}%", "height_max_mm": height,
    }


PARTS += [zrb_part(*z) for z in ZRB_PARTS]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lines = [
        "-- Terra EDA Library - Murata MLCC harvest from abc4-spiro-cart board",
        f"-- Curated specialty MLCC ported as a native terra row. Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO capacitors_smt ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
