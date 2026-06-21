#!/usr/bin/env python3
"""Emit the curated LED-driver catalog as native terra rows.

These ten parts were previously hand-authored as static SQL (led_drivers_1_source.sql).
They are now scripted so a schema change is reapplied by a rebuild, footprint/symbol
variants can be added without duplicating the parameter set, and site preferences
(symbol style, ported symbols) are a one-line edit rather than per-row SQL surgery.

`source` preserves each part's provenance (terra_sym symbol library vs CERN promotion).
Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("led_drivers_generated_300_curated.sql")

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "source", "dump_priority",
    "tier", "created_by", "pin_count", "component_height", "keywords",
    "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "driver_topology", "channels", "output_current",
    "supply_voltage_min", "supply_voltage_max", "output_voltage_max",
    "switching_freq", "dimming_method", "interface", "current_accuracy",
]

PARTS = [
    {
        "unique_id": "Diodes, Inc-AL8843Q",
        "part_locator": "LED DRIVER Diodes Inc AL8843Q",
        "mpn": "AL8843Q", "manufacturer": "Diodes, Inc", "package": "SO-8EP",
        "value": "LED DRIVER Diodes Inc AL8843Q",
        "description": "LED Driver 40V 3A Step-down",
        "datasheet": "https://www.diodes.com/assets/Datasheets/AL8843Q.pdf",
        "manufacturer_link": "https://www.diodes.com/part/view/AL8843Q/",
        "kicad_symbol": "terra_sym:LED DRIVER Diodes Inc AL8843Q",
        "kicad_footprint": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias",
        "lifecycle_status": "Active", "rohs": "Yes", "source": "terra_sym",
        "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 150,
        "temp_storage_min": -65, "temp_storage_max": 150,
        "driver_topology": "buck", "channels": 1, "output_current": "3A",
        "supply_voltage_min": 4.5, "supply_voltage_max": 40.0,
        "switching_freq": "1MHz", "dimming_method": "pwm", "interface": "none",
        "current_accuracy": "±4%",
    },
    {
        # IS32LT3954 is a Lumissil (ISSI) part, not Diodes Inc -- the legacy row
        # mislabelled the manufacturer. Corrected here (also fixes the unique_id).
        "unique_id": "Lumissil-IS32LT3954",
        "part_locator": "LED DRIVER Lumissil IS32LT3954",
        "mpn": "IS32LT3954", "manufacturer": "Lumissil", "package": "SO-8EP",
        "value": "LED DRIVER Lumissil IS32LT3954",
        "description": "LED Driver 40V 3A Step-down",
        "datasheet": "http://www.lumissil.com/assets/pdf/core/IS32LT3954_DS.pdf",
        "manufacturer_link": "http://www.lumissil.com/home",
        "kicad_symbol": "terra_sym:LED DRIVER Lumissil IS32LT3954",
        "kicad_footprint": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias",
        "lifecycle_status": "Active", "rohs": "Yes", "source": "terra_sym",
        "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        "driver_topology": "buck", "channels": 1, "output_current": "3A",
        "supply_voltage_min": 4.5, "supply_voltage_max": 38.0,
        "dimming_method": "pwm", "interface": "none",
    },
    {
        "unique_id": "Texas Instruments-LM3410XMY/NOPB",
        "part_locator": "LED DRIVER Texas Instruments LM3410XMY/NOPB",
        "mpn": "LM3410XMY/NOPB", "manufacturer": "Texas Instruments",
        "package": "MSOP Powerpad 8",
        # legacy value carried a "{slash}" escape artifact; restored to "/".
        "value": "LED DRIVER Texas Instruments LM3410XMY/NOPB",
        "description": "LED Driver 24V 2.8A constant current w/internal compensation",
        "datasheet": "https://www.ti.com/lit/gpn/LM3410",
        "manufacturer_link": "https://www.ti.com/store/ti/en/p/product/?p=LM3410XMY/NOPB",
        "kicad_symbol": "terra_sym:LED DRIVER Texas Instruments LM3410XMY/NOPB",
        "kicad_footprint": "terra_sym:LM3410XMY_NOPB",
        "lifecycle_status": "Active", "rohs": "Yes", "source": "terra_sym",
        "dump_priority": 0, "tier": 2, "pin_count": "8",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "driver_topology": "boost", "channels": 1, "output_current": "2.8A",
        "supply_voltage_min": 2.7, "supply_voltage_max": 5.5,
        "output_voltage_max": "24V", "switching_freq": "1.6MHz",
        "dimming_method": "pwm", "interface": "none", "current_accuracy": "20%",
    },
    {
        "unique_id": "MAXIM-MAX3967AETG", "part_locator": "MAX3967AETG+",
        "mpn": "MAX3967AETG", "manufacturer": "MAXIM", "package": "QFN24",
        "value": "270Mbps SFP LED Driver",
        "description": "270Mbps SFP LED Driver",
        "datasheet": "MAX3967AETG+.pdf", "manufacturer_link": "",
        "kicad_symbol": "terra-led-drivers:MAX3967A",
        "kicad_footprint": "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.65x2.65mm",
        "lifecycle_status": "Active", "rohs": "no", "source": "cern_promoted",
        "dump_priority": 0, "tier": 2, "created_by": "cern_import",
        "pin_count": "25", "component_height": "0.8mm", "keywords": "analog",
        "driver_topology": "linear", "channels": 1, "output_current": "100mA",
        "supply_voltage_min": 2.97, "supply_voltage_max": 5.5,
        "dimming_method": "none", "interface": "none",
    },
    {
        "unique_id": "ST MICROELECTRONICS-STCS05DR", "part_locator": "STCS05DR",
        "mpn": "STCS05DR", "manufacturer": "ST MICROELECTRONICS", "package": "SOIC8",
        "value": "0.5A max Constant Current LED Driver",
        "description": "0.5A max Constant Current LED Driver",
        "datasheet": "STCS05DR.pdf", "manufacturer_link": "",
        "kicad_symbol": "terra-led-drivers:STCS05",
        "kicad_footprint": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        "lifecycle_status": "Active", "rohs": "no", "source": "cern_promoted",
        "dump_priority": 0, "tier": 2, "created_by": "cern_import",
        "pin_count": "8", "component_height": "1.75mm", "keywords": "analog",
        "driver_topology": "linear", "channels": 1, "output_current": "0.5A",
        "supply_voltage_min": 4.5, "supply_voltage_max": 40.0,
        "dimming_method": "pwm", "interface": "none", "current_accuracy": "±10%",
    },
    {
        "unique_id": "TEXAS INSTRUMENTS-TLC5920DL", "part_locator": "TLC5920DLG4",
        "mpn": "TLC5920DL", "manufacturer": "TEXAS INSTRUMENTS", "package": "SSOP48",
        "value": "16x8 Bit LED Driver/Controller",
        "description": "16x8 Bit LED Driver/Controller",
        "datasheet": "TLC5920DLG4.pdf", "manufacturer_link": "",
        "kicad_symbol": "terra-led-drivers:TLC5920",
        "kicad_footprint": "Package_SO:SSOP-48_7.5x15.9mm_P0.635mm",
        "lifecycle_status": "Active", "rohs": "no", "source": "cern_promoted",
        "dump_priority": 0, "tier": 2, "created_by": "cern_import",
        "pin_count": "48", "component_height": "2.79mm", "keywords": "analog",
        "driver_topology": "linear", "channels": 16, "output_current": "30mA",
        "supply_voltage_min": 4.5, "supply_voltage_max": 5.5,
        "output_voltage_max": "5.5V", "dimming_method": "none",
        "interface": "spi", "current_accuracy": "±6%",
    },
    {
        "unique_id": "TEXAS INSTRUMENTS-TLC5925IDW", "part_locator": "TLC5925IDWR",
        "mpn": "TLC5925IDW", "manufacturer": "TEXAS INSTRUMENTS", "package": "SOIC24",
        "value": "Low-Power 16-Channel Constant-Current LED Sink Driver",
        "description": "Low-Power 16-Channel Constant-Current LED Sink Driver",
        "datasheet": "TLC5925IDWR.pdf", "manufacturer_link": "",
        "kicad_symbol": "terra-led-drivers:TLC5925",
        "kicad_footprint": "Package_SO:SOIC-24W_7.5x15.4mm_P1.27mm",
        "lifecycle_status": "Active", "rohs": "no", "source": "cern_promoted",
        "dump_priority": 0, "tier": 2, "created_by": "cern_import",
        "pin_count": "24", "component_height": "2.65mm", "keywords": "analog",
        "driver_topology": "linear", "channels": 16, "output_current": "45mA",
        "supply_voltage_min": 3.0, "supply_voltage_max": 5.5,
        "output_voltage_max": "17V", "dimming_method": "none",
        "interface": "spi", "current_accuracy": "±6%",
    },
    {
        "unique_id": "TEXAS INSTRUMENTS-TLC5971RGE", "part_locator": "TLC5971RGE",
        "mpn": "TLC5971RGE", "manufacturer": "TEXAS INSTRUMENTS", "package": "QFN24",
        "value": "12-Channel, 16-Bit, Enhanced Spectrum, PWM, RGB, LED Driver With 3.3-V Linear Regulator",
        "description": "12-Channel, 16-Bit, Enhanced Spectrum, PWM, RGB, LED Driver With 3.3-V Linear Regulator",
        "datasheet": "TLC5971.pdf", "manufacturer_link": "",
        "kicad_symbol": "Driver_LED:TLC5971RGE",
        "kicad_footprint": "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.65x2.65mm",
        "lifecycle_status": "Active", "rohs": "no", "source": "cern_promoted",
        "dump_priority": 0, "tier": 2, "created_by": "cern_import",
        "pin_count": "25", "component_height": "1.00mm", "keywords": "analog",
        "driver_topology": "linear", "channels": 12, "output_current": "60mA",
        "supply_voltage_min": 3.0, "supply_voltage_max": 17.0,
        "output_voltage_max": "17V", "dimming_method": "pwm",
        "interface": "spi", "current_accuracy": "±1%",
    },
    {
        "unique_id": "ON SEMICONDUCTOR-NSI45015W", "part_locator": "NSI45015W",
        "mpn": "NSI45015W", "manufacturer": "ON SEMICONDUCTOR", "package": "SOD-123",
        "value": "Constant Current Regulator & LED Driver (CRD)",
        "description": "Constant Current Regulator & LED Driver (CRD)",
        "datasheet": "NSI45015W.pdf", "manufacturer_link": "",
        "kicad_symbol": "terra-diodes:Diode_CRD",
        "kicad_footprint": "Diode_SMD:D_SOD-123",
        "lifecycle_status": "Active", "rohs": "no", "source": "cern_promoted",
        "dump_priority": 0, "tier": 2, "created_by": "cern_import",
        "pin_count": "2", "component_height": "1.35mm", "keywords": "diode",
        "driver_topology": "linear", "channels": 1, "output_current": "15mA",
        "supply_voltage_min": 1.8, "supply_voltage_max": 45.0,
        "output_voltage_max": "45V", "dimming_method": "none",
        "interface": "none", "current_accuracy": "±20%",
    },
    {
        "unique_id": "ON SEMICONDUCTOR-NSI50010Y", "part_locator": "NSI50010YT1G",
        "mpn": "NSI50010Y", "manufacturer": "ON SEMICONDUCTOR", "package": "SOD-123",
        "value": "Constant Current Regulator & LED Driver (CRD)",
        "description": "Constant Current Regulator & LED Driver (CRD)",
        "datasheet": "NSI50010YT1G.pdf", "manufacturer_link": "",
        "kicad_symbol": "terra-diodes:Diode_CRD",
        "kicad_footprint": "Diode_SMD:D_SOD-123",
        "lifecycle_status": "Active", "rohs": "no", "source": "cern_promoted",
        "dump_priority": 0, "tier": 2, "created_by": "cern_import",
        "pin_count": "2", "component_height": "1.35mm", "keywords": "diode",
        "driver_topology": "linear", "channels": 1, "output_current": "10mA",
        "supply_voltage_min": 1.8, "supply_voltage_max": 50.0, "output_voltage_max": "50V",
        "dimming_method": "none", "interface": "none", "current_accuracy": "±30%",
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
        "-- Terra EDA Library - curated LED-driver catalog",
        f"-- Native terra rows scripted from the curated set. Generated by {Path(__file__).name}.",
        "-- dump_priority=0: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO led_drivers ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
