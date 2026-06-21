#!/usr/bin/env python3
"""Emit the ic_drivers catalog harvested from terra_sym.kicad_sym as native rows.

These fourteen parts were previously the hand-converted ic_drivers_1_migrated.sql
dump (itself generated from terra_sym.kicad_sym). They are scripted here so a
schema change reapplies by rebuild and symbol/footprint variants share one
parameter set -- the "-flipped" pinout variants are the obvious example.

Only typos contradicted by a part's own other fields are corrected here (see the
inline notes). Judgement calls are intentionally left as-is for a later curation
pass: the `terra_sym:`-prefixed footprints point at a symbol library and need
real footprints; the SN74LV1T125 manufacturer is tagged NXP though the symbol and
datasheet are TI; several deep tail params (channels, supply voltage, output type)
are still NULL pending a datasheet harvest; ki_keywords are not yet pulled across.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_drivers_generated_300_terra_sym_harvest.sql")

RNCC = "https://4donline.ihs.com/images/VipMasterIC/IC/RNCC/RNCC-E-A0024639703/RNCC-E-A0024639703-1.pdf?hkey=6D0214268300F1406B835FE51CB13195"
ISL_LINK = "https://www.renesas.com/en/products/isl83490?srsltid=AfmBOorrhojJuPyDWNYh6-rDmOQmnBg03ja1MLg9s8OvA6xcdYZLD9Zv"
ISL_DS = "https://www.renesas.com/en/document/dst/isl83483-isl83485-isl83488-isl83490-isl83491-datasheet"
TI_ISO_CR = "https://www.ti.com/lit/cr/sszqqi4/sszqqi4.pdf?ts=1698698947760&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FISO1412"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "variant", "package",
    "value", "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution",
    "tracking", "standards_version", "source", "dump_priority", "tier",
    "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "driver_type", "i_max_device", "power_rating",
]

PARTS = [
    {
        # FIX: mpn carried a leading space (" SZNUD3124DMT1G") -> trimmed; unique_id follows.
        "unique_id": "ON Semi-SZNUD3124DMT1G",
        "part_locator": "IC_DRIVER DUAL FET DRIVER SZNUD3124DMT1G",
        "mpn": "SZNUD3124DMT1G", "manufacturer": "ON Semi",
        "value": "FET DRIVER DUAL SZNUD3124DMT1G",
        "description": "Dual MOSFET Relay driver SMT",
        "datasheet": "https://www.onsemi.com/download/data-sheet/pdf/nud3124-d.pdf",
        "manufacturer_link": "https://www.onsemi.com/products/motor-control/motor-drivers/load-drivers-relay-drivers/nud3124",
        "kicad_symbol": "terra_sym:IC_DRIVER DUAL FET DRIVER SZNUD3124DMT1G",
        "kicad_footprint": "terra_sym:SC-74-6_1.5x2.9mm_P0.95mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/ONSM/ONSM-E-A0015053231/ONSM-E-A0015053231-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "6",
        "temp_operating_min": -40, "temp_operating_max": 125, "i_max_device": "150 mA",
    },
    {
        "unique_id": "Renesas-ISL83490IBZ",
        "part_locator": "IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8",
        "mpn": "ISL83490IBZ", "manufacturer": "Renesas", "package": "soic-8",
        "value": "RS422",
        "description": "Full duplex RS-422 transciver, 2.5 Mbps, SOIC-8, 3.3V",
        "datasheet": ISL_DS, "manufacturer_link": ISL_LINK,
        "kicad_symbol": "terra_sym:IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": RNCC,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
    },
    {
        "unique_id": "Renesas-ISL83490IBZ-flipped",
        "part_locator": "IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8_flipped",
        "mpn": "ISL83490IBZ", "manufacturer": "Renesas", "variant": "flipped",
        "package": "soic-8", "value": "RS422",
        "description": "Full duplex RS-422 transciver, 2.5 Mbps, SOIC-8, 3.3V",
        "datasheet": ISL_DS, "manufacturer_link": ISL_LINK,
        "kicad_symbol": "terra_sym:IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8_flipped",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": RNCC,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
    },
    {
        "unique_id": "Analog Devices-LTC2851IMS8",
        "part_locator": "IC_DRIVER LTC2851IMS8", "mpn": "LTC2851IMS8",
        "manufacturer": "Analog Devices", "package": "MSOP-8", "value": "LTC2851",
        "description": "RS232 transceiver 1 channel, 3v",
        "datasheet": "https://www.analog.com/media/en/technical-documentation/data-sheets/285012fe.pdf",
        "manufacturer_link": "https://www.analog.com/en/products/ltc2851.html",
        "kicad_symbol": "terra_sym:IC_DRIVER LTC2851IMS8",
        "kicad_footprint": "Package_SO:MSOP-8_3x3mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/ADI_5584_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "interface ic",
    },
    {
        "unique_id": "Analog Devices-MAX3488EESA+",
        "part_locator": "IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8",
        "mpn": "MAX3488EESA+", "manufacturer": "Analog Devices", "package": "soic-8",
        "value": "RS422",
        "description": "Full duplex RS-422 transceiver, 250 kbps, SOIC-8, 3.3V",
        "datasheet": "https://www.analog.com/media/en/technical-documentation/data-sheets/MAX3483E-MAX3491E.pdf",
        "manufacturer_link": "https://www.analog.com/en/products/max3488e.html",
        "kicad_symbol": "terra_sym:IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Maxim_6688_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
    },
    {
        "unique_id": "Analog Devices-MAX3488EESA+-flipped",
        "part_locator": "IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8 flipped",
        "mpn": "MAX3488EESA+", "manufacturer": "Analog Devices", "variant": "flipped",
        "package": "soic-8", "value": "RS422",
        "description": "Full duplex RS-422 transceiver, 250 kbps, SOIC-8, 3.3V",
        "datasheet": "https://www.analog.com/media/en/technical-documentation/data-sheets/MAX3483E-MAX3491E.pdf",
        "manufacturer_link": "https://www.analog.com/en/products/max3488e.html",
        "kicad_symbol": "terra_sym:IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8 flipped",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Maxim_6688_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
    },
    {
        "unique_id": "MaxLinear-SP490ECN-L",
        "part_locator": "IC_DRIVER MaxLinear SP490E RS422 Tranceiver full duplex 5V soic-8",
        "mpn": "SP490ECN-L", "manufacturer": "MaxLinear", "package": "soic-8",
        "value": "RS422",
        "description": "Full duplex RS-422 transciver, 2.5 Mbps, SOIC-8",
        "datasheet": "https://www.analog.com/media/en/technical-documentation/data-sheets/MAX1487E-MAX491E.pdf",
        "manufacturer_link": "https://www.maxlinear.com/product/interface/serial-transceivers/rs485-422/sp490e",
        "kicad_symbol": "terra_sym:IC_DRIVER MaxLinear SP490E RS422 Tranceiver full duplex 5V soic-8",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.maxlinear.com/pdf/downloadquality?basePartNumber=SP490E&partNumber=SP490ECN-L_TR",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": 0, "temp_operating_max": 70,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
    },
    {
        "unique_id": "NXP-PCA9306D",
        "part_locator": "IC_DRIVER SMBus level shifter 1v - 5v SOIC-8",
        "mpn": "PCA9306D", "manufacturer": "NXP", "package": "soic-8",
        "value": "PCA9306", "description": "SMBus level shifter, 1V - 5V",
        "datasheet": "https://www.nxp.com/docs/en/data-sheet/PCA9306.pdf",
        "manufacturer_link": "https://www.nxp.com/part/PCA9306D",
        "kicad_symbol": "terra_sym:IC_DRIVER SMBus level shifter 1v - 5v SOIC-8",
        "kicad_footprint": "terra_sym:Texas_DCT0008A_SSOP-8_2.95x2.8mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/PHGL/PHGL-E-A0026066855/PHGL-E-A0026066855-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 105,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
    },
    {
        "unique_id": "Texas Instruments-PCA9306DCT",
        "part_locator": "IC_DRIVER SMBus level shifter 1v - 5v SSOP-8",
        "mpn": "PCA9306DCT", "manufacturer": "Texas Instruments", "package": "ssop-8",
        "value": "PCA9306", "description": "TI PCA9306DCT SMBus level shifter, 1V - 5V",
        "datasheet": "https://www.ti.com/lit/gpn/pca9306",
        "manufacturer_link": "https://www.ti.com/product/PCA9306?keyMatch=PCA9306",
        "kicad_symbol": "terra_sym:IC_DRIVER SMBus level shifter 1v - 5v SSOP-8",
        "kicad_footprint": "terra_sym:Texas_DCT0008A_SSOP-8_2.95x2.8mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.ti.com/lit/cr/szzq088r/szzq088r.pdf?ts=1759503142967",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 105,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
    },
    {
        "unique_id": "Texas Instruments-ISO1412BDW",
        "part_locator": "IC_DRIVER TI ISO1412BDW Full Duplex isolated RS422 driver",
        "mpn": "ISO1412BDW", "manufacturer": "Texas Instruments", "package": "SOIC (DW)",
        "value": "IC TI ISO1412BDW Full Duplex isolated RS422 driver",
        "description": "Full Duplex, isolated RS 422 Driver, 500 kbps, SMT",
        "datasheet": "https://www.ti.com/product/ISO1412/part-details/ISO1412BDW",
        "manufacturer_link": "https://www.ti.com/product/ISO1412/part-details/ISO1412BDW",
        "kicad_symbol": "terra_sym:IC_DRIVER TI ISO1412BDW Full Duplex isolated RS422 driver",
        "kicad_footprint": "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": TI_ISO_CR,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "16",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
    },
    {
        "unique_id": "Texas Instruments-ISOW1412",
        "part_locator": "IC_DRIVER TI ISO1412W Full Duplex isolated RS422 driver",
        "mpn": "ISOW1412", "manufacturer": "Texas Instruments", "package": "SOIC (DW)",
        "value": "IC TI ISO1412W Full Duplex isolated RS422 driver",
        "description": "Full Duplex, isolated RS 422 Driver, 500 kbps, SMT",
        "datasheet": "https://www.ti.com/lit/ds/symlink/isow1432.pdf",
        "manufacturer_link": "https://www.ti.com/product/ISOW1412",
        "kicad_symbol": "terra_sym:IC_DRIVER TI ISO1412W Full Duplex isolated RS422 driver",
        "kicad_footprint": "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": TI_ISO_CR,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "16",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
    },
    {
        # FIX: manufacturer "Texas Instrument" -> "Texas Instruments" (the other TI
        # rows spell it correctly); unique_id follows.
        "unique_id": "Texas Instruments-TXU0104PWR",
        "part_locator": "IC_DRIVER TXU0104 4-bit level shifter 1.8v - 5v TSSOP-14",
        "mpn": "TXU0104PWR", "manufacturer": "Texas Instruments", "package": "TSSOP-14",
        "value": "TXU0104",
        "description": "4-bit Level Shifting Buffer 1.8V <> 5V",
        "datasheet": "https://www.ti.com/lit/gpn/TXU0104",
        "manufacturer_link": "https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758919582957",
        "kicad_symbol": "terra_sym:IC_DRIVER TXU0104 4-bit level shifter 1.8v - 5v TSSOP-14",
        "kicad_footprint": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0021022709/TXII-E-A0021022709-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "14",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
    },
    {
        # FIX: mpn "UNL2003A" -> "ULN2003A" (the locator, value, symbol and datasheet
        # all say ULN2003A; UNL2003A is not a real part number). unique_id + the
        # "UNL2003A" in the description corrected too.
        "unique_id": "Texas Instruments-ULN2003A",
        "part_locator": "IC_DRIVER ULN2003A High current darlington array",
        "mpn": "ULN2003A", "manufacturer": "Texas Instruments", "package": "SOIC-16",
        "value": "ULN2003A High current darlington array",
        "description": "ULN2003A darlington array, high current",
        "datasheet": "https://www.ti.com/lit/ds/symlink/uln2003a.pdf?ts=1666037723636&ref_url=https%253A%252F%252Fwww.google.com%252F",
        "manufacturer_link": "https://www.ti.com/product/ULN2003A",
        "kicad_symbol": "terra_sym:IC_DRIVER ULN2003A High current darlington array",
        "kicad_footprint": "Package_SO:SO-16_5.3x10.2mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "Yes", "tracking": "Yes", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "16",
        "temp_operating_min": -40, "temp_operating_max": 85, "power_rating": "2.5A",
    },
    {
        "unique_id": "NXP-SN74LV1T125DBV",
        "part_locator": "IC_DRIVER level shifter 1.8v - 5v SOT-23-5",
        "mpn": "SN74LV1T125DBV", "manufacturer": "NXP", "package": "SOT 23-5",
        "value": "SN74LV1T125DBV",
        "description": "Single Level Shifting Buffer 1.8V <> 5V",
        "datasheet": "https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758962409857",
        "manufacturer_link": "https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758919582957",
        "kicad_symbol": "terra_sym:IC_DRIVER level shifter 1.8v - 5v SOT-23-5",
        "kicad_footprint": "Package_TO_SOT_SMD:SOT-23-5",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0026917336/TXII-E-A0026917336-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "5",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
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
        "-- Terra EDA Library - ic_drivers harvested from terra_sym.kicad_sym",
        f"-- Native terra rows scripted from the terra_sym source. Generated by {Path(__file__).name}.",
        "-- dump_priority=0: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_drivers ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
