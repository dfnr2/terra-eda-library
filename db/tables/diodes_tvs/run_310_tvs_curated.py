#!/usr/bin/env python3
"""Curated non-SMF TVS parts, migrated out of the `diodes` table into diodes_tvs.

These are individually-sourced ESD/TVS parts (not a parametric series): the Vishay
VESD05A1 low-cap ESD diode, the Littelfuse SM712 asymmetric RS-485 array (3-pin,
custom symbol), and the ST ESDA18-1K. ESDA18-1K is unidirectional (its datasheet
says so) and was wrongly on the bidirectional Device:D_TVS — corrected here to
terra-diodes:D_TVS_unidir.

Datasheets are still web URLs (pre-dating the local-store rule); backfill to the
central store on the next pass. Generated: dump_priority=0, source=NULL.
"""
from pathlib import Path
from _tvs import insert, write

PARTS = [
    {
        "unique_id": "Vishay-VESD05A1-02VHG3-08",
        "part_locator": "tvs-5v-bidi-sod523",
        "mpn": "VESD05A1-02VHG3-08", "manufacturer": "Vishay",
        "package": "SOD-523", "value": "5V bidi",
        "description": "Vishay VESD05A1-02V ESD protection TVS diode, 5V working, SOD-523",
        "datasheet": "https://www.vishay.com/docs/86129/vesd05a1-02v.pdf",
        "manufacturer_link": "https://www.vishay.com",
        "kicad_symbol": "Device:D_TVS", "kicad_footprint": "Diode_SMD:D_SOD-523",
        "pin_count": "2", "directionality": "bidirectional", "standoff_voltage": "5V",
        "keywords": "tvs,esd,protection,bidi,low-capacitance",
    },
    {
        "unique_id": "Littelfuse-SM712-02HTG",
        "part_locator": "tvs-array-rs485-sot23",
        "mpn": "SM712-02HTG", "manufacturer": "Littelfuse",
        "package": "SOT-23", "value": "SM712",
        "description": "Littelfuse SM712-02HTG asymmetric TVS diode array for RS-485 (7V/12V), SOT-23",
        "datasheet": "https://www.littelfuse.com/media?resourcetype=datasheets&itemid=8313a28c-8802-4d47-a2a7-e30b5b1f67d8&filename=littelfuse-tvs-diode-array-sm712-datasheet",
        "manufacturer_link": "https://www.littelfuse.com",
        "kicad_symbol": "terra-diodes:SM712-02HTG_compact",
        "kicad_footprint": "terra-diodes:SM71202HTG",
        "pin_count": "3", "directionality": "bidirectional", "standoff_voltage": "12V",
        "keywords": "tvs,array,rs-485,protection,bidi",
    },
    {
        "unique_id": "STMicroelectronics-ESDA18-1K",
        "part_locator": "tvs-18v-uni-sod523",
        "mpn": "ESDA18-1K", "manufacturer": "STMicroelectronics",
        "package": "SOD-523", "value": "18V uni",
        "description": "STMicroelectronics ESDA18-1K unidirectional TVS / ESD protection diode, 18V working, SOD-523",
        "datasheet": "https://www.st.com/resource/en/datasheet/esda18-1k.pdf",
        "manufacturer_link": "https://www.st.com",
        "kicad_symbol": "terra-diodes:D_TVS_unidir", "kicad_footprint": "Diode_SMD:D_SOD-523",
        "pin_count": "2", "directionality": "unidirectional", "standoff_voltage": "18V",
        "keywords": "tvs,esd,protection,uni",
    },
    {
        # Re-homed from the diodes table, where it was the junk 'Unknown-UNKNOWN'
        # row. Identified as the Nexperia PESD3V3L4UW low-cap quad ESD array.
        "unique_id": "Nexperia-PESD3V3L4UW",
        "part_locator": "esd-array-4ch-3v3-uni-sot665",
        "mpn": "PESD3V3L4UW", "manufacturer": "Nexperia",
        "package": "SOT-665", "value": "3.3V ESD array",
        "description": "Nexperia PESD3V3L4UW low-capacitance quadruple unidirectional ESD protection array, 3.3V, common anode, SOT-665",
        "datasheet": "https://assets.nexperia.com/documents/data-sheet/PESDXL4UF_G_W.pdf",
        "manufacturer_link": "https://www.nexperia.com",
        "kicad_symbol": "terra_sym:DIODE_ARRAY PESD3V3L4UW",
        "kicad_footprint": "Package_TO_SOT_SMD:SOT-665",
        "pin_count": "6", "directionality": "unidirectional", "standoff_voltage": "3.3V",
        "channels": 4,
        "keywords": "esd,array,protection,low-capacitance,common-anode,4-channel",
    },
]


def rows():
    out = []
    for p in PARTS:
        rec = dict(p)
        rec.update(rohs="Yes", allow_substitution="No", tracking="No",
                   source=None, dump_priority=0, tier=2,
                   temp_operating_min=-65.0, temp_operating_max=150.0,
                   temp_storage_min=-65.0, temp_storage_max=150.0)
        out.append(insert(rec))
    return out


if __name__ == "__main__":
    write(
        Path(__file__).with_name("diodes_tvs_generated_310_tvs_curated.sql"),
        Path(__file__).name, rows(),
        "Curated non-SMF TVS (VESD05A1, SM712, ESDA18-1K) migrated from diodes",
    )
