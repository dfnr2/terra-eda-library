#!/usr/bin/env python3
"""Emit the ic_drivers catalog harvested from terra_sym.kicad_sym as native rows.

These fourteen parts were previously the hand-converted ic_drivers_1_migrated.sql
dump (itself generated from terra_sym.kicad_sym). They are scripted here so a
schema change reapplies by rebuild and symbol/footprint variants share one
parameter set -- the "-flipped" pinout variants are the obvious example.

Only typos contradicted by a part's own other fields are corrected here (see the
inline notes). Judgement calls are intentionally left as-is for a later curation
pass: the `terra-ic-drivers:`-prefixed footprints point at a symbol library and need
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
    "temp_storage_max", "driver_type", "channels", "data_rate", "supply_voltage_min",
    "supply_voltage_max", "i_max_device", "i_max_channel", "output_type",
    "power_rating",
]

PARTS = [
    {
        # FIX: mpn carried a leading space (" SZNUD3124DMT1G") -> trimmed; unique_id follows.
        "unique_id": "ON Semi-SZNUD3124DMT1G",
        "part_locator": "IC_DRIVER DUAL FET DRIVER SZNUD3124DMT1G",
        "mpn": "SZNUD3124DMT1G", "manufacturer": "ON Semi",
        "value": "FET DRIVER DUAL SZNUD3124DMT1G",
        "description": "Dual MOSFET Relay driver SMT",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/onsemi/nud3124.pdf",
        "manufacturer_link": "https://www.onsemi.com/products/motor-control/motor-drivers/load-drivers-relay-drivers/nud3124",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER DUAL FET DRIVER SZNUD3124DMT1G",
        "kicad_footprint": "terra_footprints_ic_drivers:onsemi_SC-74-6_1.5x3.0mm_P0.95mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/ONSM/ONSM-E-A0015053231/ONSM-E-A0015053231-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "6",
        "temp_operating_min": -40, "temp_operating_max": 125, "i_max_device": "150 mA",
        # NUD3124/SZNUD3124 (NUD3124/D): inductive-load driver; SC-74 (CASE 318F)
        # is the dual version (two N-ch open-drain MOSFETs). ID = 150 mA continuous
        # per driver; output drains relay coils -> open-drain sink. No supply rail.
        "channels": 2, "i_max_channel": "150 mA", "output_type": "open-drain",
    },
    {
        "unique_id": "Renesas-ISL83490IBZ", "data_rate": "2.5 Mbps",
        "part_locator": "IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8",
        "mpn": "ISL83490IBZ", "manufacturer": "Renesas", "package": "soic-8",
        "value": "RS422",
        "description": "Full duplex RS-422 transciver, 2.5 Mbps, SOIC-8, 3.3V",
        "datasheet": ISL_DS, "manufacturer_link": ISL_LINK,
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": RNCC,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
        # ISL83490 (FN6052): single +3.3V supply, 3V-3.6V; full-duplex transceiver.
        "channels": 1, "supply_voltage_min": 3.0, "supply_voltage_max": 3.6,
    },
    {
        "unique_id": "Renesas-ISL83490IBZ-flipped", "data_rate": "2.5 Mbps",
        "part_locator": "IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8_flipped",
        "mpn": "ISL83490IBZ", "manufacturer": "Renesas", "variant": "flipped",
        "package": "soic-8", "value": "RS422",
        "description": "Full duplex RS-422 transciver, 2.5 Mbps, SOIC-8, 3.3V",
        "datasheet": ISL_DS, "manufacturer_link": ISL_LINK,
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER ISL834390 RS422 Tranceiver full duplex 3.3V soic-8_flipped",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": RNCC,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
        # flipped = same part as ISL83490IBZ; copy harvested values.
        "channels": 1, "supply_voltage_min": 3.0, "supply_voltage_max": 3.6,
    },
    {
        "unique_id": "Analog Devices-LTC2851IMS8",
        "part_locator": "IC_DRIVER LTC2851IMS8", "mpn": "LTC2851IMS8",
        "manufacturer": "Analog Devices", "package": "MSOP-8", "value": "LTC2851",
        "description": "RS232 transceiver 1 channel, 3v",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/analog-devices/ltc2851.pdf",
        "manufacturer_link": "https://www.analog.com/en/products/ltc2851.html",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER LTC2851IMS8",
        "kicad_footprint": "Package_SO:MSOP-8_3x3mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/ADI_5584_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "interface ic",
        # LTC2850/51/52 (285012fe): 3.3V RS485/RS422 transceiver, single full-duplex
        # channel; electrical specs at VCC = 3.0V-3.6V (VIL@3V, VIH@3.6V).
        "channels": 1, "supply_voltage_min": 3.0, "supply_voltage_max": 3.6,
    },
    {
        "unique_id": "Analog Devices-MAX3488EESA+", "data_rate": "250 kbps",
        "part_locator": "IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8",
        "mpn": "MAX3488EESA+", "manufacturer": "Analog Devices", "package": "soic-8",
        "value": "RS422",
        "description": "Full duplex RS-422 transceiver, 250 kbps, SOIC-8, 3.3V",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/analog-devices/max3483e-max3491e.pdf",
        "manufacturer_link": "https://www.analog.com/en/products/max3488e.html",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Maxim_6688_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
        # MAX3488E (MAX3483E-MAX3491E): single +3.3V full-duplex RS-485/422
        # transceiver; "Supply Voltage Range VCC 3.0-3.6V".
        "channels": 1, "supply_voltage_min": 3.0, "supply_voltage_max": 3.6,
    },
    {
        "unique_id": "Analog Devices-MAX3488EESA+-flipped", "data_rate": "250 kbps",
        "part_locator": "IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8 flipped",
        "mpn": "MAX3488EESA+", "manufacturer": "Analog Devices", "variant": "flipped",
        "package": "soic-8", "value": "RS422",
        "description": "Full duplex RS-422 transceiver, 250 kbps, SOIC-8, 3.3V",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/analog-devices/max3483e-max3491e.pdf",
        "manufacturer_link": "https://www.analog.com/en/products/max3488e.html",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8 flipped",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Maxim_6688_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
        # flipped = same part as MAX3488EESA+; mirror harvested values.
        "channels": 1, "supply_voltage_min": 3.0, "supply_voltage_max": 3.6,
    },
    {
        "unique_id": "MaxLinear-SP490ECN-L", "data_rate": "2.5 Mbps",
        "part_locator": "IC_DRIVER MaxLinear SP490E RS422 Tranceiver full duplex 5V soic-8",
        "mpn": "SP490ECN-L", "manufacturer": "MaxLinear", "package": "soic-8",
        "value": "RS422",
        "description": "Full duplex RS-422 transciver, 2.5 Mbps, SOIC-8",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/maxlinear/sp490e-sp491e.pdf",
        "manufacturer_link": "https://www.maxlinear.com/product/interface/serial-transceivers/rs-485-rs-422/sp490ers485-422/sp490e",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER MaxLinear SP490E RS422 Tranceiver full duplex 5V soic-8",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.maxlinear.com/pdf/downloadquality?basePartNumber=SP490E&partNumber=SP490ECN-L_TR",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": 0, "temp_operating_max": 70,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "ic driver",
        # SP490E (REV 1.0.2): 5V-only full-duplex RS-485/422 transceiver, single
        # driver/receiver; Supply Voltage 4.75-5.25V.
        "channels": 1, "supply_voltage_min": 4.75, "supply_voltage_max": 5.25,
    },
    {
        "unique_id": "NXP-PCA9306D",
        "part_locator": "IC_DRIVER SMBus level shifter 1v - 5v SOIC-8",
        "mpn": "PCA9306D", "manufacturer": "NXP", "package": "soic-8",
        "value": "PCA9306", "description": "SMBus level shifter, 1V - 5V",
        "datasheet": "https://www.nxp.com/docs/en/data-sheet/PCA9306.pdf",
        "manufacturer_link": "https://www.nxp.com/part/PCA9306D",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER SMBus level shifter 1v - 5v SOIC-8",
        "kicad_footprint": "terra_footprints_ic_drivers:TI_DCT0008A_SSOP-8_2.95x2.8mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/PHGL/PHGL-E-A0026066855/PHGL-E-A0026066855-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 105,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
        # PCA9306 (SCPS113O): 2-bit (SDA/SCL) bidirectional I2C/SMBus translator,
        # 1.2V-5.5V, open-drain pass-FET I/O.
        "channels": 2, "supply_voltage_min": 1.2, "supply_voltage_max": 5.5,
        "output_type": "open-drain",
    },
    {
        "unique_id": "Texas Instruments-PCA9306DCT",
        "part_locator": "IC_DRIVER SMBus level shifter 1v - 5v SSOP-8",
        "mpn": "PCA9306DCT", "manufacturer": "Texas Instruments", "package": "ssop-8",
        "value": "PCA9306", "description": "TI PCA9306DCT SMBus level shifter, 1V - 5V",
        "datasheet": "https://www.ti.com/lit/gpn/pca9306",
        "manufacturer_link": "https://www.ti.com/product/PCA9306?keyMatch=PCA9306",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER SMBus level shifter 1v - 5v SSOP-8",
        "kicad_footprint": "terra_footprints_ic_drivers:TI_DCT0008A_SSOP-8_2.95x2.8mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://www.ti.com/lit/cr/szzq088r/szzq088r.pdf?ts=1759503142967",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 105,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
        # PCA9306 (SCPS113O): 2-bit (SDA/SCL) bidirectional I2C/SMBus translator,
        # 1.2V-5.5V, open-drain pass-FET I/O.
        "channels": 2, "supply_voltage_min": 1.2, "supply_voltage_max": 5.5,
        "output_type": "open-drain",
    },
    {
        "unique_id": "Texas Instruments-ISO1412BDW", "data_rate": "500 kbps",
        "part_locator": "IC_DRIVER TI ISO1412BDW Full Duplex isolated RS422 driver",
        "mpn": "ISO1412BDW", "manufacturer": "Texas Instruments", "package": "SOIC (DW)",
        "value": "IC TI ISO1412BDW Full Duplex isolated RS422 driver",
        "description": "Full Duplex, isolated RS 422 Driver, 500 kbps, SMT",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/ti/iso14x2.pdf",
        "manufacturer_link": "https://www.ti.com/product/ISO1412",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER TI ISO1412BDW Full Duplex isolated RS422 driver",
        "kicad_footprint": "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": TI_ISO_CR,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "16",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        # ISO1412 (SLLSF22H): single isolated full-duplex RS-485/422 transceiver;
        # VCC1 (logic) 1.71-5.5V, VCC2 (bus) 3-5.5V.
        "channels": 1, "supply_voltage_min": 1.71, "supply_voltage_max": 5.5,
    },
    {
        "unique_id": "Texas Instruments-ISOW1412", "data_rate": "500 kbps",
        "part_locator": "IC_DRIVER TI ISO1412W Full Duplex isolated RS422 driver",
        "mpn": "ISOW1412", "manufacturer": "Texas Instruments", "package": "SOIC (DW)",
        "value": "IC TI ISO1412W Full Duplex isolated RS422 driver",
        "description": "Full Duplex, isolated RS 422 Driver, 500 kbps, SMT",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/ti/isow14x2.pdf",
        "manufacturer_link": "https://www.ti.com/product/ISOW1412",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER TI ISO1412W Full Duplex isolated RS422 driver",
        "kicad_footprint": "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": TI_ISO_CR,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "20",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        # ISOW1412 (ISOW14x2, SLLSF86C): single isolated full-duplex RS-485/422
        # transceiver with integrated DC-DC; VIO 1.71-5.5V, VDD 3-5.5V.
        "channels": 1, "supply_voltage_min": 1.71, "supply_voltage_max": 5.5,
    },
    {
        # ISO1432 = full-duplex 12 Mbps sibling of ISO1412, pin-identical (16-pin DW).
        # Reuses the ISO1412BDW symbol (electrically correct) until a dedicated
        # ISO1432 symbol is supplied.
        "unique_id": "Texas Instruments-ISO1432BDW", "data_rate": "12 Mbps",
        "part_locator": "IC_DRIVER TI ISO1432BDW Full Duplex isolated RS422 driver",
        "mpn": "ISO1432BDW", "manufacturer": "Texas Instruments", "package": "SOIC (DW)",
        "value": "IC TI ISO1432BDW Full Duplex isolated RS422 driver",
        "description": "Full Duplex, isolated RS-485/RS-422 transceiver, 12 Mbps, 5kVrms, SMT",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/ti/iso14x2.pdf",
        "manufacturer_link": "https://www.ti.com/product/ISO1432",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER TI ISO1412BDW Full Duplex isolated RS422 driver",
        "kicad_footprint": "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": TI_ISO_CR,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "16",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        "channels": 1, "supply_voltage_min": 1.71, "supply_voltage_max": 5.5,
    },
    {
        # ISOW1432 = full-duplex 12 Mbps sibling of ISOW1412 (integrated DC-DC),
        # pin-identical (20-pin DFM). Reuses the ISOW1412 symbol until a dedicated
        # ISOW1432 symbol is supplied.
        "unique_id": "Texas Instruments-ISOW1432", "data_rate": "12 Mbps",
        "part_locator": "IC_DRIVER TI ISOW1432 Full Duplex isolated RS422 driver",
        "mpn": "ISOW1432", "manufacturer": "Texas Instruments", "package": "SOIC (DW)",
        "value": "IC TI ISOW1432 Full Duplex isolated RS422 driver",
        "description": "Full Duplex isolated RS-485/RS-422 transceiver with integrated DC-DC, 12 Mbps, 5kVrms, SMT",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/ti/isow14x2.pdf",
        "manufacturer_link": "https://www.ti.com/product/ISOW1432",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER TI ISO1412W Full Duplex isolated RS422 driver",
        "kicad_footprint": "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
        "rohs": "Yes", "rohs_document_link": TI_ISO_CR,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "20",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        "channels": 1, "supply_voltage_min": 1.71, "supply_voltage_max": 5.5,
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
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER TXU0104 4-bit level shifter 1.8v - 5v TSSOP-14",
        "kicad_footprint": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0021022709/TXII-E-A0021022709-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "14",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
        # TXU0104 (SCES937B): 4-bit dual-rail level translator, each port 1.1-5.5V,
        # push-pull 3-state outputs, high drive up to 12mA at 5V.
        "channels": 4, "supply_voltage_min": 1.1, "supply_voltage_max": 5.5,
        "i_max_channel": "12 mA", "output_type": "push-pull, 3-state",
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
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER ULN2003A High current darlington array",
        "kicad_footprint": "Package_SO:SO-16_5.3x10.2mm_P1.27mm",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "Yes", "tracking": "Yes", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "16",
        "temp_operating_min": -40, "temp_operating_max": 85, "power_rating": "2.5A",
        # ULN2003A (SLRS027T): 7 NPN Darlington pairs, 500mA collector current per
        # output, open-collector outputs sinking to the common emitter.
        "channels": 7, "i_max_channel": "500 mA", "output_type": "open-collector sink",
    },
    {
        "unique_id": "NXP-SN74LV1T125DBV",
        "part_locator": "IC_DRIVER level shifter 1.8v - 5v SOT-23-5",
        "mpn": "SN74LV1T125DBV", "manufacturer": "NXP", "package": "SOT 23-5",
        "value": "SN74LV1T125DBV",
        "description": "Single Level Shifting Buffer 1.8V <> 5V",
        "datasheet": "https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758962409857",
        "manufacturer_link": "https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758919582957",
        "kicad_symbol": "terra_symbols_ic_drivers:IC_DRIVER level shifter 1.8v - 5v SOT-23-5",
        "kicad_footprint": "Package_TO_SOT_SMD:SOT-23-5",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0026917336/TXII-E-A0026917336-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "5",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150, "driver_type": "level shifter",
        # SN74LV1T125 (SCLS745D): single buffer gate level shifter, VCC 1.8-5.5V,
        # CMOS 3-state output.
        "channels": 1, "supply_voltage_min": 1.8, "supply_voltage_max": 5.5,
        "output_type": "push-pull, 3-state",
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
