#!/usr/bin/env python3
"""Molex Micro-Latch 2.00 mm wire-to-board PCB headers: 53253 vertical, 53254 right-angle.

Every circuit count KiCad ships a footprint for (2-15), -xx70 suffix only (tin,
tray, 3.50 mm PC tail); the -xx50 "compatible alternatives" are skipped. Symbols are
stock Connector_Generic. KiCad ships the footprints but no 3D models, so the
footprints are vendored into terra_footprints_connectors with a Molex STEP attached.

    python3 run_320_molex_micro_latch.py                      # write the SQL
    python3 run_320_molex_micro_latch.py --vendor-footprints  # rewrite the footprints

Plan and parameter sources: plans/connectors-molex-micro-latch.md.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "connectors_generated_320_molex_micro_latch.sql"
CREATED_BY = Path(__file__).name

CIRCUITS = range(2, 16)

# Placement of the Molex STEPs (origin at body centre) on KiCad's footprint, pad 1 at
# the footprint origin: x offset is (circuits - 1) mm, the rest is fixed per series.
# Checked by slicing the placed model: pin tails land on the pads, the housing seats
# at z = 0 and the tails end 3.50 mm below it (Molex's PC tail length).
SERIES = {
    "53253": {
        "orientation": "vertical", "kicad_suffix": "Vertical",
        "model_yz": (-2.55, 7.3), "model_rotate": (-90, -180, 180),
        "height": "5.61mm",
        "datasheet": "micro-latch-53253-vertical-header.pdf",
    },
    "53254": {
        "orientation": "right-angle", "kicad_suffix": "Horizontal",
        "model_yz": (7.8, 4.6), "model_rotate": (180, 0, 0),
        "height": "4.2mm",
        "datasheet": "micro-latch-53254-right-angle-header.pdf",
    },
}

# Models exported with an older Molex origin: full (offset, rotate) placement.
MODEL_OVERRIDES = {
    "53253-0270": ((1.0, -0.325, 2.75), (90, 180, 180)),
}

MODEL_DIR = "terra-connectors.3dshapes"
FOOTPRINT_LIB = "terra_footprints_connectors"

# Family-wide ratings, from Molex part-detail sheets (2024 revisions where they differ).
FAMILY = {
    "connector_category": "wire-to-board", "connector_family": "Molex Micro-Latch",
    "connector_type": "header", "rows": 1, "pitch_mm": 2.0,
    "termination_type": "Through Hole", "gender": "male",
    "polarized": "yes", "keying_detail": "3-sided shroud",
    "locking_mechanism": "friction", "shielding": "unshielded", "color": "natural",
    "current_rating": 2.0, "voltage_rating": 250.0, "signal_type": "signal",
    "mating_family": "Molex Micro-Latch 51065 receptacle housings",
    "temp_operating_min": -55.0, "temp_operating_max": 105.0,
}

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "value", "description",
    "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "component_height", "temp_operating_min", "temp_operating_max",
    "connector_category", "connector_family", "connector_series", "connector_type",
    "positions", "rows", "pitch_mm", "orientation", "termination_type", "gender",
    "polarized", "keying_detail", "locking_mechanism", "shielding", "color",
    "current_rating", "voltage_rating", "signal_type", "mating_family", "mates_with",
]


def parts():
    """One dict per orderable header, in series then circuit order."""
    for series, s in SERIES.items():
        for n in CIRCUITS:
            pn = f"{series}-{n:02d}70"   # Molex's printed part number
            mpn = f"{series}{n:02d}70"   # Molex's catalog number
            footprint = f"Molex_Micro-Latch_{pn}_1x{n:02d}_P2.00mm_{s['kicad_suffix']}"
            yield {
                **FAMILY,
                "unique_id": f"Molex-{mpn}",
                "part_locator": f"conn-header-{n}pos-{series}",
                "mpn": mpn, "manufacturer": "Molex", "value": pn,
                "description": (
                    f"Molex Micro-Latch {pn} 2.00mm pitch wire-to-board header, 1x{n:02d}, "
                    f"{s['orientation']}, through-hole, tin plating, 3-sided shroud"
                ),
                "datasheet": f"${{TERRA_EDA_LIB}}/datasheets/molex/{s['datasheet']}",
                "manufacturer_link": f"https://www.molex.com/en-us/products/part-detail/{mpn}",
                "kicad_symbol": f"Connector_Generic:Conn_01x{n:02d}",
                "kicad_footprint": f"{FOOTPRINT_LIB}:{footprint}",
                "lifecycle_status": "Active", "rohs": "Yes",
                "allow_substitution": "No", "tracking": "No",
                "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
                "keywords": (
                    f"connector,header,molex,micro-latch,wire-to-board,2.00mm,"
                    f"{s['orientation']},{pn},{mpn}"
                ),
                "pin_count": str(n), "component_height": s["height"],
                "connector_series": series, "positions": n,
                "orientation": s["orientation"],
                "mates_with": f"51065-{n:02d}00 receptacle housing with 50212 crimp terminals",
                # not columns: footprint vendoring inputs
                "_footprint": footprint,
                "_model": f"{MODEL_DIR}/{pn}.stp",
                "_placement": MODEL_OVERRIDES.get(
                    pn, ((n - 1, *s["model_yz"]), s["model_rotate"])),
            }


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def insert(p):
    vals = ", ".join(sql(p[c]) for c in COLS)
    return f"INSERT INTO connectors ({', '.join(COLS)}) VALUES ({vals});"


def write_sql(rows):
    ids = [p["unique_id"] for p in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        sys.exit(f"duplicate unique_id: {dupes}")
    lines = [
        "-- Terra EDA Library - Molex Micro-Latch PCB headers (53253 vertical, 53254 right-angle)",
        f"-- Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
        *(insert(p) for p in rows),
        "",
        "COMMIT;",
        "",
    ]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} parts")


def vendor_footprints(rows):
    sys.path.insert(0, str(ROOT))
    from tools.vendor_footprint import vendor_footprint
    for p in rows:
        vendor_footprint("Connector_Molex", p["_footprint"], FOOTPRINT_LIB,
                         p["_model"], *p["_placement"])
    print(f"Vendored {len(rows)} footprints into {FOOTPRINT_LIB}.pretty")


def report_missing_assets(rows):
    """Name the STEP models and datasheets not yet in the repo."""
    missing = sorted({p["_model"] for p in rows
                      if not (ROOT / "assets" / "3dmodels" / p["_model"]).exists()})
    missing += sorted({p["datasheet"] for p in rows
                       if not (ROOT / p["datasheet"].replace("${TERRA_EDA_LIB}/", "")).exists()})
    if missing:
        print(f"WARNING: {len(missing)} assets missing:")
        for m in missing:
            print(f"  {m}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vendor-footprints", action="store_true",
                    help="rewrite the vendored footprints from the installed KiCad library")
    args = ap.parse_args()
    rows = list(parts())
    if args.vendor_footprints:
        vendor_footprints(rows)
    else:
        write_sql(rows)
    report_missing_assets(rows)


if __name__ == "__main__":
    main()
