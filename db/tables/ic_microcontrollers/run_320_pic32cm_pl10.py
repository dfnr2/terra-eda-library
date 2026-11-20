#!/usr/bin/env python3
"""Microchip PIC32CM6408PL10 5V Arm Cortex-M0+ microcontrollers (PIC32CM PL10 family).

Source: PIC32CM6408PL10028/032/048/064 Data Sheet, DS40002667A (2025, marked
Preliminary), datasheets/microchip/PIC32CM6408PL10-028-032-048-064-DataSheet-
DS40002667.pdf. Only the 64 KB devices are in this sheet; the 32 KB (3204) and
128 KB (1216) family members are in other datasheets and are not generated.

One row per ordering code in Table 41-1 for tube/tray packing (no T = tape and
reel), both temperature grades: I = -40 to 85 C, E = -40 to 125 C. All are Active
on Digi-Key and "In Production" on microchip.com (checked 2026-11-20).

Symbols: custom, in terra_symbols_ic_microcontrollers (pin tables in _pinouts.py,
from section 2.3), one per package layout. The 28-pin VQFN is numbered differently
from the SSOP/SPDIP. VQFN symbols carry the exposed pad as a passive EP pin, because
the datasheet does not say what it connects to.

Footprints are stock KiCad. All match the package drawings (chapter 39) except the
28-pin VQFN (3LW, 4x4 mm, 0.4 mm pitch, 2.65 mm pad): KiCad has no 2.65 mm-pad
version, so it uses QFN-28-1EP_4x4mm_P0.4mm_EP2.4x2.4mm, whose pad land is 0.25 mm
smaller. Replace it in PACKAGES if an exact footprint is made.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_microcontrollers_generated_320_pic32cm_pl10.sql")
CREATED_BY = Path(__file__).name
SYMLIB = "terra_symbols_ic_microcontrollers:"
DATASHEET = ("${TERRA_EDA_LIB}/datasheets/microchip/"
             "PIC32CM6408PL10-028-032-048-064-DataSheet-DS40002667.pdf")

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "family", "core", "architecture_bits", "max_clock", "active_current",
    "sleep_current", "supply_voltage_min", "supply_voltage_max",
    "flash_size", "eeprom_size", "ram_size", "gpio_count", "uart_count",
    "i2c_count", "spi_count", "usb_count", "can_count", "eth_count",
    "timer_count", "pwm_count", "dma_count", "adc_count", "adc_resolution",
    "dac_count", "special_features",
]

# Shared by every device (datasheet front page, Table 2-1, chapter 37).
COMMON = dict(
    manufacturer="Microchip", rohs="Yes", allow_substitution="No", tracking="No",
    source=None, dump_priority=0, tier=2, lifecycle_status="Active",
    datasheet=DATASHEET, family="PIC32CM PL10", core="Arm Cortex-M0+",
    architecture_bits=32, max_clock="24MHz", active_current="5.2mA @ 24MHz/3V",
    sleep_current="2µA (standby)", supply_voltage_min=1.8, supply_voltage_max=5.5,
    flash_size="64KB", eeprom_size=None, ram_size="8KB",
    # Two SERCOMs, each USART/SPI/I2C; only SERCOM0 does I2C.
    uart_count=2, i2c_count=1, spi_count=2, usb_count=0, can_count=0, eth_count=0,
    # TC0-2 (2 channels each) and TCC0 (4 channels); DMAC with 2 channels.
    timer_count=4, pwm_count=10, dma_count=2, adc_resolution="12-bit", dac_count=0,
)

# Device -> (I/O pins, ADC channels = PTC channels), from Table 2-1.
DEVICES = {
    "PIC32CM6408PL10028": (22, 16),
    "PIC32CM6408PL10032": (26, 20),
    "PIC32CM6408PL10048": (41, 25),
    "PIC32CM6408PL10064": (55, 29),
}

# Device -> [(package code, package, symbol suffix, footprint)], from Table 41-1.
PACKAGES = {
    "PIC32CM6408PL10028": [
        ("SP", "SPDIP-28", "028-SS_SP", "Package_DIP:DIP-28_W7.62mm"),
        ("SS", "SSOP-28", "028-SS_SP", "Package_SO:SSOP-28_5.3x10.2mm_P0.65mm"),
        ("3LW", "VQFN-28", "028-3LW",
         "Package_DFN_QFN:QFN-28-1EP_4x4mm_P0.4mm_EP2.4x2.4mm"),  # approximate EP
    ],
    "PIC32CM6408PL10032": [
        ("PT", "TQFP-32", "032-PT", "Package_QFP:TQFP-32_7x7mm_P0.8mm"),
        ("QZB", "VQFN-32", "032-QZB", "Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm"),
    ],
    "PIC32CM6408PL10048": [
        ("PT", "TQFP-48", "048-PT", "Package_QFP:TQFP-48_7x7mm_P0.5mm"),
        ("6MX", "VQFN-48", "048-6MX", "Package_DFN_QFN:VQFN-48-1EP_6x6mm_P0.4mm_EP4.1x4.1mm"),
    ],
    "PIC32CM6408PL10064": [
        ("PT", "TQFP-64", "064-PT", "Package_QFP:TQFP-64_10x10mm_P0.5mm"),
        ("5LX", "VQFN-64", "064-5LX", "Package_DFN_QFN:VQFN-64-1EP_9x9mm_P0.5mm_EP5.4x5.4mm"),
    ],
}

TEMPS = {"I": (-40, 85), "E": (-40, 125)}


def records():
    for device, (gpio, adc) in DEVICES.items():
        pins = device[-3:].lstrip("0")
        for code, package, sym, fp in PACKAGES[device]:
            for grade, (tmin, tmax) in TEMPS.items():
                mpn = f"{device}-{grade}/{code}"
                features = (f"5V operation, multi-voltage I/O (VDDIO2), PTC touch ({adc} ch), "
                            "2 analog comparators, CCL (4 LUTs), RTC, event system, "
                            "1KB high-endurance flash (10k cycles), SWD")
                yield {
                    **COMMON,
                    "unique_id": f"Microchip-{mpn}", "mpn": mpn, "value": device,
                    "part_locator": f"mcu-cortex-m0plus-{device.lower()}-{package.lower()}",
                    "package": package, "pin_count": pins,
                    "manufacturer_link": f"https://www.microchip.com/en-us/product/{device}",
                    "kicad_symbol": f"{SYMLIB}PIC32CM6408PL10{sym}", "kicad_footprint": fp,
                    "temp_operating_min": tmin, "temp_operating_max": tmax,
                    "gpio_count": gpio, "adc_count": adc, "special_features": features,
                    "description": (f"32-bit Arm Cortex-M0+ MCU, 64KB Flash, 8KB SRAM, "
                                    f"1.8-5.5V, 24MHz, {gpio} I/O, {package}, "
                                    f"{tmin} to {tmax}C"),
                    "keywords": ("mcu,microcontroller,pic32cm,pl10,cortex-m0+,arm,32-bit,5v,"
                                 f"{device.lower()},ptc,touch"),
                }


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    recs = list(records())
    ids = [r["unique_id"] for r in recs]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"duplicate unique_id: {dupes}")
    lines = [
        "-- Terra EDA Library - Microchip PIC32CM PL10 (PIC32CM6408PL10) microcontrollers",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_microcontrollers ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} parts")


if __name__ == "__main__":
    main()
