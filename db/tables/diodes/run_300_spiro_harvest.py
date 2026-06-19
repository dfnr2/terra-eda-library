#!/usr/bin/env python3
"""Harvest curated TVS/diode parts from the abc4-spiro mainboard into native terra.

These are specific curated parts (not a parametric sweep): each entry is a real
part pulled from the project's hand-maintained library, with its datasheet,
package, and footprint. The custom SM712 footprint was migrated into the
terra-diodes footprint lib; the SOD-123/SOD-523 parts use standard KiCad
footprints. Symbols use standard KiCad device/Diode symbols.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("diodes_generated_300_spiro_harvest.sql")
CREATED_BY = Path(__file__).name

# Columns we populate; the rest take schema defaults / NULL.
COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "diode_type", "voltage_rating", "power_rating",
]

PARTS = [
    {
        "mpn": "VESD05A1-02VHG3-08", "manufacturer": "Vishay",
        "package": "SOD-523", "value": "5V",
        "description": "Vishay VESD05A1-02V ESD protection TVS diode, 5V working, SOD-523",
        "datasheet": "https://www.vishay.com/docs/86129/vesd05a1-02v.pdf",
        "manufacturer_link": "https://www.vishay.com",
        "kicad_symbol": "Device:D_TVS",
        "kicad_footprint": "Diode_SMD:D_SOD-523",
        "pin_count": "2", "diode_type": "tvs",
        "voltage_rating": "5V", "power_rating": None,
        "keywords": "tvs,esd,protection",
    },
    {
        "mpn": "SMF18A", "manufacturer": "Littelfuse",
        "package": "SOD-123FL", "value": "18V 200W",
        "description": "Littelfuse SMF18A 18V 200W unidirectional TVS, SOD-123FL",
        "datasheet": "https://www.littelfuse.com/media?resourcetype=datasheets&itemid=7eb8a5b6-bdd0-4561-8f19-0c3cc6f9b2af&filename=tvs-smf-1103",
        "manufacturer_link": "https://www.littelfuse.com",
        "kicad_symbol": "Device:D_TVS",
        "kicad_footprint": "Diode_SMD:D_SOD-123F",
        "pin_count": "2", "diode_type": "tvs",
        "voltage_rating": "18V", "power_rating": "200W",
        "keywords": "tvs,protection",
    },
    {
        "mpn": "SMF6.0A", "manufacturer": "Littelfuse",
        "package": "SOD-123FL", "value": "6V 200W",
        "description": "Littelfuse SMF6.0A 6V 200W unidirectional TVS, SOD-123FL",
        "datasheet": "https://www.littelfuse.com/media?resourcetype=datasheets&itemid=7eb8a5b6-bdd0-4561-8f19-0c3cc6f9b2af&filename=tvs-smf-1103",
        "manufacturer_link": "https://www.littelfuse.com",
        "kicad_symbol": "terra-diodes:SMF6.0A_TVS_compact",
        "kicad_footprint": "Diode_SMD:D_SOD-123F",
        "pin_count": "2", "diode_type": "tvs",
        "voltage_rating": "6V", "power_rating": "200W",
        "keywords": "tvs,protection",
    },
    {
        "mpn": "SM712-02HTG", "manufacturer": "Littelfuse",
        "package": "SOT-23", "value": "SM712",
        "description": "Littelfuse SM712-02HTG asymmetric TVS diode array for RS-485 (7V/12V), SOT-23",
        "datasheet": "https://www.littelfuse.com/media?resourcetype=datasheets&itemid=8313a28c-8802-4d47-a2a7-e30b5b1f67d8&filename=littelfuse-tvs-diode-array-sm712-datasheet",
        "manufacturer_link": "https://www.littelfuse.com",
        "kicad_symbol": "terra-diodes:SM712-02HTG_compact",
        "kicad_footprint": "terra-diodes:SM71202HTG",
        "pin_count": "3", "diode_type": "tvs",
        "voltage_rating": "12V", "power_rating": None,
        "keywords": "tvs,array,rs-485,protection",
    },
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, int):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def part_locator(p):
    val = p["value"].lower().replace(" ", "-")
    return f"diode-{p['diode_type']}-{val}-{p['package'].lower()}"


def row(p):
    rec = {
        "unique_id": f"{p['manufacturer']}-{p['mpn']}",
        "part_locator": part_locator(p),
        "mpn": p["mpn"], "manufacturer": p["manufacturer"],
        "package": p["package"], "value": p["value"],
        "description": p["description"], "datasheet": p["datasheet"],
        "manufacturer_link": p["manufacturer_link"],
        "kicad_symbol": p["kicad_symbol"], "kicad_footprint": p["kicad_footprint"],
        "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2, "keywords": p["keywords"],
        "pin_count": p["pin_count"], "diode_type": p["diode_type"],
        "voltage_rating": p["voltage_rating"], "power_rating": p["power_rating"],
    }
    vals = ", ".join(sql(rec[c]) for c in COLS)
    return f"INSERT INTO diodes ({', '.join(COLS)}) VALUES ({vals});"


def main():
    lines = [
        "-- Terra EDA Library - diodes harvest from abc4-spiro mainboard",
        f"-- Curated TVS/diode parts ported as native terra rows. Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    lines += [row(p) for p in PARTS]
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
