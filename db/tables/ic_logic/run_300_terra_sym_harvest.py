#!/usr/bin/env python3
"""Emit the ic_logic catalog harvested from terra_sym.kicad_sym as native rows.

These four parts were recovered from the terra_sym.kicad_sym source. They are
scripted here so a schema change reapplies by rebuild rather than a hand re-edit.

Only a typo contradicted by a part's own other fields is corrected here: the
SN74LVC1G139 row was tagged manufacturer "Texas Instrument" (the other three
rows spell it "Texas Instruments"); the spelling and its unique_id are fixed.

Deferred curation: the corrected SN74LVC1G139 row still carries
gate_function='level shifter', which is wrong -- it is a 2-to-4 line decoder --
and its value 'SN74LV1G139' is missing a 'C'. The SN74LVC1G123DCU and
SN74LVC1G139DCU rows are sparse (no package, footprint or temperatures). The
deep tail (logic_family, propagation_delay, supply_voltage) is unfilled across
all rows and needs a datasheet harvest.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_logic_generated_300_terra_sym_harvest.sql")

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package",
    "value", "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution",
    "tracking", "standards_version", "source", "dump_priority", "tier",
    "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "gate_function", "logic_family", "channels",
    "propagation_delay", "supply_voltage_min", "supply_voltage_max",
]

PARTS = [
    {
        "unique_id": "Texas Instruments-SN74LVC1G123",
        "part_locator": "IC_LOGIC 74LVC1G123",
        "mpn": "SN74LVC1G123", "manufacturer": "Texas Instruments", "package": "mssop-8",
        "value": "74LVC1G123",
        "description": "Single Retrigerrable Monostabile Multivibrator, Low-Voltage CMOS",
        "datasheet": "https://www.ti.com/lit/gpn/sn74lvc1g123",
        "manufacturer_link": "https://www.ti.com/product/SN74LVC1G123",
        "kicad_symbol": "terra-ic-logic:IC_LOGIC 74LVC1G123",
        "kicad_footprint": "Package_SO:MSOP-8_3x3mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "Yes", "tracking": "yes", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        "gate_function": "monostable multivibrator", "logic_family": "LVC",
        "channels": 1, "propagation_delay": "8 ns max at 3.3 V",
        "supply_voltage_min": 1.65, "supply_voltage_max": 5.5,
    },
    {
        "unique_id": "Texas Instruments-SN74LVC1G123DCU",
        "part_locator": "IC_LOGIC 74LVC1G123d",
        "mpn": "SN74LVC1G123DCU", "manufacturer": "Texas Instruments",
        "value": "74LVC1G123d",
        "description": "Single Retrigerrable Monostabile Multivibrator, Low-Voltage CMOS",
        "datasheet": "http://www.ti.com/lit/ds/symlink/sn74lvc1g123.pdf",
        "kicad_symbol": "terra-ic-logic:IC_LOGIC 74LVC1G123d",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "gate_function": "monostable multivibrator", "logic_family": "LVC",
        "channels": 1, "propagation_delay": "8 ns max at 3.3 V",
        "supply_voltage_min": 1.65, "supply_voltage_max": 5.5,
    },
    {
        "unique_id": "Texas Instruments-SN74LVC1G139DCU",
        "part_locator": "IC_LOGIC 74LVC1G139",
        "mpn": "SN74LVC1G139DCU", "manufacturer": "Texas Instruments",
        "value": "74LVC1G139",
        "description": "Single 2-to-4-line decoder",
        "datasheet": "www.ti.com/lit/ds/symlink/sn74lvc1g139.pdf",
        "kicad_symbol": "terra-ic-logic:IC_LOGIC 74LVC1G139",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "gate_function": "2-to-4 line decoder/demux", "logic_family": "LVC",
        "channels": 1, "propagation_delay": "4.9 ns max at 3.3 V, 15 pF",
        "supply_voltage_min": 1.65, "supply_voltage_max": 5.5,
    },
    {
        # FIX: manufacturer "Texas Instrument" -> "Texas Instruments" (the other
        # three rows spell it correctly); unique_id follows. Does not collide with
        # Texas Instruments-SN74LVC1G139DCU (different MPN suffix).
        "unique_id": "Texas Instruments-SN74LVC1G139",
        "part_locator": "IC_LOGIC TI SN74LV1G139 2-to-4 line decoder",
        "mpn": "SN74LVC1G139", "manufacturer": "Texas Instruments", "package": "SM8",
        "value": "SN74LV1G139",
        "description": "Single 2-to-4-line decoder",
        "datasheet": "https://www.ti.com/lit/gpn/sn74lvc1g139",
        "manufacturer_link": "https://www.ti.com/product/SN74LVC1G139?keyMatch=SN74LVC1G139&tisearch=universal_search&usecase=GPN-ALT",
        "kicad_symbol": "terra-ic-logic:IC_LOGIC TI SN74LV1G139 2-to-4 line decoder",
        "kicad_footprint": "Package_TO_SOT_SMD:SOT-23-5",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0026917336/TXII-E-A0026917336-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "5",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        "gate_function": "2-to-4 line decoder/demux", "logic_family": "LVC",
        "channels": 1, "propagation_delay": "4.9 ns max at 3.3 V, 15 pF",
        "supply_voltage_min": 1.65, "supply_voltage_max": 5.5,
    },
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lines = [
        "-- Terra EDA Library - ic_logic harvested from terra_sym.kicad_sym",
        f"-- Native terra rows scripted from the terra_sym source. Generated by {Path(__file__).name}.",
        "-- dump_priority=0: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_logic ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
