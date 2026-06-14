#!/usr/bin/env python3
"""Harvest curated connectors from the abc4-spiro-cart cartridge board into terra.

All four carry custom footprints migrated into the terra-connectors footprint lib;
symbols use standard KiCad Connector_Generic symbols. The Tag-Connect TC2030 is a
legless PCB footprint for the TC2030-IDC programming cable (the schematic symbol has
no MPN; assigned TC2030-IDC-NL here).

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("connectors_generated_310_cart_harvest.sql")
CREATED_BY = Path(__file__).name

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "tags", "pin_count",
    "connector_category", "connector_family", "connector_series", "connector_type",
    "positions", "rows", "pitch_mm", "orientation", "termination_type", "gender",
    "signal_type", "mating_part_hint",
]

PARTS = [
    {
        "mpn": "TC2030-IDC-NL", "manufacturer": "Tag-Connect", "value": "DEBUG",
        "description": "Tag-Connect TC2030-IDC-NL legless PCB footprint for the TC2030-IDC 6-pin programming/debug cable (ARM)",
        "datasheet": "https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2030-CTX_1.pdf",
        "kicad_symbol": "Connector_Generic:Conn_02x03_Odd_Even",
        "kicad_footprint": "terra-connectors:Tag-Connect_TC2030-IDC_2x03_P1.27mm_Vertical",
        "connector_category": "programming", "connector_family": "Tag-Connect TC2030",
        "connector_series": "TC2030", "connector_type": "footprint",
        "positions": 6, "rows": 2, "pitch_mm": 1.27, "orientation": "vertical",
        "termination_type": "SMT", "gender": None, "signal_type": "signal",
        "mating_part_hint": "TC2030-IDC cable", "pin_count": "6", "tags": "connector,programming,debug",
    },
    {
        "mpn": "532540470", "manufacturer": "Molex", "value": "connector",
        "description": "Molex Micro-Latch 53254-0470 1x4 2.00mm right-angle header, through-hole",
        "datasheet": "https://www.molex.com/en-us/products/part-detail/532540470?display=pdf",
        "kicad_symbol": "Connector_Generic:Conn_01x04",
        "kicad_footprint": "terra-connectors:Molex_Micro-Latch_53254-0470_1x04_P2.00mm_Horizontal",
        "connector_category": "wire-to-board", "connector_family": "Molex Micro-Latch",
        "connector_series": "53254", "connector_type": "header",
        "positions": 4, "rows": 1, "pitch_mm": 2.0, "orientation": "right-angle",
        "termination_type": "Through Hole", "gender": "male", "signal_type": "signal",
        "mating_part_hint": None, "pin_count": "4", "tags": "connector,header",
    },
    {
        "mpn": "5600200320", "manufacturer": "Molex", "value": "Solenoid",
        "description": "Molex DuraClick 560020-0320 1x3 2.00mm vertical header, SMT",
        "datasheet": "https://www.molex.com/webdocs/datasheets/pdf/en-us/5600200320_PCB_HEADERS.pdf",
        "kicad_symbol": "Connector_Generic:Conn_01x03",
        "kicad_footprint": "terra-connectors:Molex_5600200320_3pin_DuraClick_SMT",
        "connector_category": "wire-to-board", "connector_family": "Molex DuraClick",
        "connector_series": "560020", "connector_type": "header",
        "positions": 3, "rows": 1, "pitch_mm": 2.0, "orientation": "vertical",
        "termination_type": "SMT", "gender": "male", "signal_type": "power",
        "mating_part_hint": None, "pin_count": "3", "tags": "connector,header",
    },
    {
        "mpn": "829-22-008-20-002101", "manufacturer": "Mill-Max", "value": "8 pins",
        "description": "Mill-Max 829-22-008-20-002101 1x8 spring-loaded (pogo) pin connector, right-angle",
        "datasheet": "https://www.mill-max.com/products/datasheet/sockets/829-22-008-20-002101",
        "kicad_symbol": "Connector_Generic:Conn_01x08",
        "kicad_footprint": "terra-connectors:MillMax_829-22-004-20-002101_pogo_RA_8pin",
        "connector_category": "board-to-board", "connector_family": "Mill-Max 829 Spring Pin",
        "connector_series": "829", "connector_type": "spring-pin",
        "positions": 8, "rows": 1, "pitch_mm": 2.54, "orientation": "right-angle",
        "termination_type": "Through Hole", "gender": "male", "signal_type": "signal",
        "mating_part_hint": None, "pin_count": "8", "tags": "connector,pogo,spring-pin",
    },
]

MFR_LINK = {
    "Tag-Connect": "https://www.tag-connect.com",
    "Molex": "https://www.molex.com",
    "Mill-Max": "https://www.mill-max.com",
}


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def row(p):
    rec = {
        "unique_id": f"{p['manufacturer'].replace(' ', '_')}-{p['mpn']}",
        "part_locator": f"conn-{p['connector_type']}-{p['positions']}pos-{p['connector_series'].lower()}",
        "package": None, "manufacturer_link": MFR_LINK.get(p["manufacturer"]),
        "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
    }
    rec.update(p)
    vals = ", ".join(sql(rec.get(c)) for c in COLS)
    return f"INSERT INTO connectors ({', '.join(COLS)}) VALUES ({vals});"


def main():
    lines = [
        "-- Terra EDA Library - connectors harvest from abc4-spiro-cart cartridge board",
        f"-- Curated connector parts ported as native terra rows. Generated by {CREATED_BY}.",
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
