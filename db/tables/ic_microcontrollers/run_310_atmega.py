#!/usr/bin/env python3
"""Microchip megaAVR (ATmega) 8-bit microcontroller family (active devices).

One row per (device x package). Symbols are KiCad's stock
MCU_Microchip_ATmega:<device>-<pkgsuffix>; footprints are KiCad standard.
Data-driven: DEVICES holds shared per-chip specs (+ lifecycle, datasheet URL),
VARIANTS the orderable packages -- extend both to grow the family.

Datasheets are kept as manufacturer URLs (not yet localized); see the repo's
download list. Specs are from the standard AVR data; obsolete/NRND-heavy lines
(ATmega8/16/32/64/128, 8515/8535, the LCD-driver series) are excluded.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_microcontrollers_generated_310_atmega.sql")
CREATED_BY = Path(__file__).name
SYMLIB = "MCU_Microchip_ATmega:"

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

DEFAULTS = dict(
    manufacturer="Microchip", rohs="Yes", allow_substitution="No", tracking="No",
    source=None, dump_priority=0, tier=2, core="AVR", architecture_bits=8,
    family="megaAVR", lifecycle_status="Active", usb_count=0, can_count=0,
    eth_count=0, dma_count=0, dac_count=0, adc_resolution="10-bit",
    sleep_current="0.1µA (power-down)",
    temp_operating_min=-40, temp_operating_max=85, supply_voltage_max=5.5,
)

# Datasheets. The 48/88/168/328 and 640..2561 family PDFs are downloaded locally
# (they cover the PA / Mega devices too); the rest are kept as manufacturer URLs
# pending download -- see the repo download list.
DS_328 = "${TERRA_EDA_LIB}/datasheets/microchip/atmega328p.pdf"
DS_328_URL = "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega48A-PA-88A-PA-168A-PA-328-P-DS-DS40002061B.pdf"
DS_328PB = "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega328PB-Data-Sheet-DS40001984B.pdf"
DS_48PB = "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega48PB-88PB-168PB-Data-Sheet-40001906C.pdf"
DS_MEGA = "${TERRA_EDA_LIB}/datasheets/microchip/atmega2560.pdf"
DS_644 = "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega164A_PA-324A_PA-644A_PA-1284_P_Data-Sheet-40002070B.pdf"
DS_324PB = "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega324PB-Data-Sheet-DS40001908A.pdf"
DS_U2 = "https://ww1.microchip.com/downloads/en/DeviceDoc/doc7799.pdf"
DS_U4 = "https://ww1.microchip.com/downloads/en/DeviceDoc/atmel-7766-8-bit-avr-atmega16u4-32u4_datasheet.pdf"
DS_M1 = "https://ww1.microchip.com/downloads/en/DeviceDoc/doc8209.pdf"
DS_0 = "https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega4808-4809-Data-Sheet-DS40002173A.pdf"
DS_406 = "https://ww1.microchip.com/downloads/en/DeviceDoc/doc2548.pdf"


def D(**kw):
    return kw


# device -> shared specs (overrides DEFAULTS)
DEVICES = {
    # --- 48/88/168/328 line ---
    "ATmega328P": D(flash_size="32KB", eeprom_size="1KB", ram_size="2KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=23,
        uart_count=1, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_328, special_features="watchdog, brown-out detect, internal RC oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega328p,arduino"),
    "ATmega168PA": D(flash_size="16KB", eeprom_size="512B", ram_size="1KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=23,
        uart_count=1, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_328, special_features="watchdog, brown-out detect, internal RC oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega168pa"),
    "ATmega88PA": D(flash_size="8KB", eeprom_size="512B", ram_size="1KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=23,
        uart_count=1, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_328, special_features="watchdog, brown-out detect, internal RC oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega88pa"),
    "ATmega48PA": D(flash_size="4KB", eeprom_size="256B", ram_size="512B", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=23,
        uart_count=1, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_328, special_features="watchdog, brown-out detect, internal RC oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega48pa"),
    # PB series: 2x UART/SPI/I2C, PTC touch
    "ATmega328PB": D(flash_size="32KB", eeprom_size="1KB", ram_size="2KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=27,
        uart_count=2, i2c_count=2, spi_count=2, timer_count=5, pwm_count=10,
        datasheet=DS_328PB, special_features="watchdog, brown-out detect, PTC touch, unique device ID",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega328pb"),
    "ATmega168PB": D(flash_size="16KB", eeprom_size="512B", ram_size="1KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=27,
        uart_count=2, i2c_count=2, spi_count=2, timer_count=4, pwm_count=9,
        datasheet=DS_48PB, special_features="watchdog, brown-out detect, PTC touch",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega168pb"),
    "ATmega88PB": D(flash_size="8KB", eeprom_size="512B", ram_size="1KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=27,
        uart_count=2, i2c_count=2, spi_count=2, timer_count=4, pwm_count=9,
        datasheet=DS_48PB, special_features="watchdog, brown-out detect, PTC touch",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega88pb"),
    "ATmega48PB": D(flash_size="4KB", eeprom_size="256B", ram_size="512B", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.2mA @ 1MHz/1.8V", gpio_count=27,
        uart_count=2, i2c_count=2, spi_count=2, timer_count=4, pwm_count=9,
        datasheet=DS_48PB, special_features="watchdog, brown-out detect, PTC touch",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega48pb"),
    # --- Mega (640/1280/2560) line ---
    "ATmega640": D(flash_size="64KB", eeprom_size="4KB", ram_size="8KB", max_clock="16MHz",
        supply_voltage_min=4.5, active_current="5mA @ 8MHz/5V", gpio_count=86,
        uart_count=4, i2c_count=1, spi_count=1, timer_count=6, pwm_count=15,
        datasheet=DS_MEGA, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega640"),
    "ATmega1280": D(flash_size="128KB", eeprom_size="4KB", ram_size="8KB", max_clock="16MHz",
        supply_voltage_min=4.5, active_current="5mA @ 8MHz/5V", gpio_count=86,
        uart_count=4, i2c_count=1, spi_count=1, timer_count=6, pwm_count=15,
        datasheet=DS_MEGA, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega1280,arduino-mega"),
    "ATmega2560": D(flash_size="256KB", eeprom_size="4KB", ram_size="8KB", max_clock="16MHz",
        supply_voltage_min=4.5, active_current="5mA @ 8MHz/5V", gpio_count=86,
        uart_count=4, i2c_count=1, spi_count=1, timer_count=6, pwm_count=15,
        datasheet=DS_MEGA, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega2560,arduino-mega"),
    "ATmega1281": D(flash_size="128KB", eeprom_size="4KB", ram_size="8KB", max_clock="16MHz",
        supply_voltage_min=4.5, active_current="5mA @ 8MHz/5V", gpio_count=54,
        uart_count=2, i2c_count=1, spi_count=1, timer_count=6, pwm_count=15,
        datasheet=DS_MEGA, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega1281"),
    "ATmega2561": D(flash_size="256KB", eeprom_size="4KB", ram_size="8KB", max_clock="16MHz",
        supply_voltage_min=4.5, active_current="5mA @ 8MHz/5V", gpio_count=54,
        uart_count=2, i2c_count=1, spi_count=1, timer_count=6, pwm_count=15,
        datasheet=DS_MEGA, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega2561"),
    # --- 164/324/644/1284 line ---
    "ATmega164PA": D(flash_size="16KB", eeprom_size="512B", ram_size="1KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.4mA @ 1MHz/1.8V", gpio_count=32,
        uart_count=2, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_644, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega164pa"),
    "ATmega324PA": D(flash_size="32KB", eeprom_size="1KB", ram_size="2KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.4mA @ 1MHz/1.8V", gpio_count=32,
        uart_count=2, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_644, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega324pa"),
    "ATmega324PB": D(flash_size="32KB", eeprom_size="1KB", ram_size="2KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.4mA @ 1MHz/1.8V", gpio_count=39,
        uart_count=3, i2c_count=2, spi_count=2, timer_count=5, pwm_count=10,
        datasheet=DS_324PB, special_features="watchdog, brown-out detect, JTAG, PTC touch",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega324pb"),
    "ATmega644PA": D(flash_size="64KB", eeprom_size="2KB", ram_size="4KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.4mA @ 1MHz/1.8V", gpio_count=32,
        uart_count=2, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_644, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega644pa"),
    "ATmega1284P": D(flash_size="128KB", eeprom_size="4KB", ram_size="16KB", max_clock="20MHz",
        supply_voltage_min=1.8, active_current="0.4mA @ 1MHz/1.8V", gpio_count=32,
        uart_count=2, i2c_count=1, spi_count=1, timer_count=3, pwm_count=6,
        datasheet=DS_644, special_features="watchdog, brown-out detect, JTAG",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,atmega1284p"),
    # --- USB (U2/U4) ---
    "ATmega16U2": D(flash_size="16KB", eeprom_size="512B", ram_size="512B", max_clock="16MHz",
        supply_voltage_min=1.8, active_current="0.3mA/MHz", gpio_count=22,
        uart_count=1, i2c_count=0, spi_count=1, usb_count=1, timer_count=2, pwm_count=4,
        adc_resolution=None, datasheet=DS_U2,
        special_features="USB 2.0 full-speed device, DFU bootloader",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,usb,atmega16u2"),
    "ATmega32U2": D(flash_size="32KB", eeprom_size="1KB", ram_size="1KB", max_clock="16MHz",
        supply_voltage_min=1.8, active_current="0.3mA/MHz", gpio_count=22,
        uart_count=1, i2c_count=0, spi_count=1, usb_count=1, timer_count=2, pwm_count=4,
        adc_resolution=None, datasheet=DS_U2,
        special_features="USB 2.0 full-speed device, DFU bootloader",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,usb,atmega32u2"),
    "ATmega32U4": D(flash_size="32KB", eeprom_size="1KB", ram_size="2.5KB", max_clock="16MHz",
        supply_voltage_min=2.7, active_current="0.3mA/MHz", gpio_count=26,
        uart_count=1, i2c_count=1, spi_count=1, usb_count=1, timer_count=4, pwm_count=7,
        datasheet=DS_U4, special_features="USB 2.0 full-speed device, on-chip PLL",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,usb,atmega32u4,arduino-leonardo"),
    # --- CAN/motor (M1) ---
    "ATmega16M1": D(flash_size="16KB", eeprom_size="512B", ram_size="1KB", max_clock="16MHz",
        supply_voltage_min=2.7, active_current="0.3mA/MHz", gpio_count=27,
        uart_count=1, i2c_count=0, spi_count=1, can_count=1, timer_count=3, pwm_count=6,
        dac_count=1, datasheet=DS_M1,
        special_features="CAN 2.0B, LIN, 12-bit PSC for motor control, analog comparators",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,can,lin,motor,atmega16m1"),
    "ATmega32M1": D(flash_size="32KB", eeprom_size="1KB", ram_size="2KB", max_clock="16MHz",
        supply_voltage_min=2.7, active_current="0.3mA/MHz", gpio_count=27,
        uart_count=1, i2c_count=0, spi_count=1, can_count=1, timer_count=3, pwm_count=6,
        dac_count=1, datasheet=DS_M1,
        special_features="CAN 2.0B, LIN, 12-bit PSC for motor control, analog comparators",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,can,lin,motor,atmega32m1"),
    "ATmega64M1": D(flash_size="64KB", eeprom_size="2KB", ram_size="4KB", max_clock="16MHz",
        supply_voltage_min=2.7, active_current="0.3mA/MHz", gpio_count=27,
        uart_count=1, i2c_count=0, spi_count=1, can_count=1, timer_count=3, pwm_count=6,
        dac_count=1, datasheet=DS_M1,
        special_features="CAN 2.0B, LIN, 12-bit PSC for motor control, analog comparators",
        keywords="mcu,microcontroller,avr,8-bit,megaavr,can,lin,motor,atmega64m1"),
    # --- megaAVR 0-series (AVRxt core) ---
    "ATmega3208": D(family="megaAVR 0-series", flash_size="32KB", eeprom_size="256B", ram_size="4KB",
        max_clock="20MHz", supply_voltage_min=1.8, active_current="3mA @ 10MHz/3.3V",
        gpio_count=27, uart_count=3, i2c_count=1, spi_count=1, timer_count=5, pwm_count=6,
        dac_count=1, datasheet=DS_0,
        special_features="AVRxt core, event system, CCL, 8-bit DAC, internal oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr-0,avrxt,atmega3208"),
    "ATmega3209": D(family="megaAVR 0-series", flash_size="32KB", eeprom_size="256B", ram_size="4KB",
        max_clock="20MHz", supply_voltage_min=1.8, active_current="3mA @ 10MHz/3.3V",
        gpio_count=41, uart_count=4, i2c_count=1, spi_count=1, timer_count=5, pwm_count=6,
        dac_count=1, datasheet=DS_0,
        special_features="AVRxt core, event system, CCL, 8-bit DAC, internal oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr-0,avrxt,atmega3209"),
    "ATmega4808": D(family="megaAVR 0-series", flash_size="48KB", eeprom_size="256B", ram_size="6KB",
        max_clock="20MHz", supply_voltage_min=1.8, active_current="3mA @ 10MHz/3.3V",
        gpio_count=27, uart_count=3, i2c_count=1, spi_count=1, timer_count=5, pwm_count=6,
        dac_count=1, datasheet=DS_0,
        special_features="AVRxt core, event system, CCL, 8-bit DAC, internal oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr-0,avrxt,atmega4808"),
    "ATmega4809": D(family="megaAVR 0-series", flash_size="48KB", eeprom_size="256B", ram_size="6KB",
        max_clock="20MHz", supply_voltage_min=1.8, active_current="3mA @ 10MHz/3.3V",
        gpio_count=41, uart_count=4, i2c_count=1, spi_count=1, timer_count=5, pwm_count=6,
        dac_count=1, datasheet=DS_0,
        special_features="AVRxt core, event system, CCL, 8-bit DAC, internal oscillator",
        keywords="mcu,microcontroller,avr,8-bit,megaavr-0,avrxt,atmega4809,arduino-nano-every"),
    # --- battery management (NRND) ---
    "ATmega406": D(family="Battery Management AVR", lifecycle_status="NRND",
        flash_size="40KB", eeprom_size="512B", ram_size="2KB", max_clock="1MHz",
        supply_voltage_min=4.0, supply_voltage_max=25.0, active_current="5mA active",
        sleep_current="1µA (power-save)", gpio_count=18, uart_count=0, i2c_count=1,
        spi_count=1, timer_count=2, pwm_count=1, adc_resolution="12-bit",
        datasheet=DS_406, special_features="battery management, cell balancing, coulomb counter",
        keywords="mcu,microcontroller,avr,8-bit,battery-management,li-ion,atmega406"),
}

# footprint shorthands (all grep-verified by the harvest agents)
DIP28 = "Package_DIP:DIP-28_W7.62mm"
DIP40 = "Package_DIP:DIP-40_W15.24mm"
TQFP32 = "Package_QFP:TQFP-32_7x7mm_P0.8mm"
TQFP44 = "Package_QFP:TQFP-44_10x10mm_P0.8mm"
TQFP48 = "Package_QFP:TQFP-48_7x7mm_P0.5mm"
TQFP64 = "Package_QFP:TQFP-64_14x14mm_P0.8mm"
TQFP100 = "Package_QFP:TQFP-100_14x14mm_P0.5mm"
LQFP48 = "Package_QFP:LQFP-48_7x7mm_P0.5mm"
QFN32 = "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm"
QFN32M1 = "Package_DFN_QFN:QFN-32-1EP_7x7mm_P0.65mm_EP4.65x4.65mm"
QFN28 = "Package_DFN_QFN:QFN-28-1EP_4x4mm_P0.45mm_EP2.6x2.6mm"
QFN44 = "Package_DFN_QFN:QFN-44-1EP_7x7mm_P0.5mm_EP5.15x5.15mm"
QFN44U4 = "Package_DFN_QFN:QFN-44-1EP_7x7mm_P0.5mm_EP5.2x5.2mm"
VQFN32 = "Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm"
UQFN48 = "Package_DFN_QFN:UQFN-48-1EP_6x6mm_P0.4mm_EP4.45x4.45mm"
UFBGA32 = "Package_BGA:UFBGA-32_4.0x4.0mm_Layout6x6_P0.5mm"
SSOP28 = "Package_SO:SSOP-28_5.3x10.2mm_P0.65mm"

# device -> [(package, mpn, pin_count, symbol_suffix, footprint, adc_count)]
VARIANTS = {
    "ATmega328P": [("PDIP-28", "ATMEGA328P-PU", "28", "ATmega328P-P", DIP28, 6),
                   ("TQFP-32", "ATMEGA328P-AU", "32", "ATmega328P-A", TQFP32, 8),
                   ("QFN-32", "ATMEGA328P-MU", "32", "ATmega328P-M", QFN32, 8),
                   ("QFN-28", "ATMEGA328P-MMH", "28", "ATmega328P-MM", QFN28, 6)],
    "ATmega168PA": [("PDIP-28", "ATMEGA168PA-PU", "28", "ATmega168PA-P", DIP28, 6),
                    ("TQFP-32", "ATMEGA168PA-AU", "32", "ATmega168PA-A", TQFP32, 8),
                    ("QFN-32", "ATMEGA168PA-MU", "32", "ATmega168PA-M", QFN32, 8),
                    ("QFN-28", "ATMEGA168PA-MMH", "28", "ATmega168PA-MM", QFN28, 6),
                    ("UFBGA-32", "ATMEGA168PA-CU", "32", "ATmega168PA-CC", UFBGA32, 8)],
    "ATmega88PA": [("PDIP-28", "ATMEGA88PA-PU", "28", "ATmega88PA-P", DIP28, 6),
                   ("TQFP-32", "ATMEGA88PA-AU", "32", "ATmega88PA-A", TQFP32, 8),
                   ("QFN-32", "ATMEGA88PA-MU", "32", "ATmega88PA-M", QFN32, 8),
                   ("QFN-28", "ATMEGA88PA-MMH", "28", "ATmega88PA-MM", QFN28, 6),
                   ("UFBGA-32", "ATMEGA88PA-CU", "32", "ATmega88PA-CC", UFBGA32, 8)],
    "ATmega48PA": [("PDIP-28", "ATMEGA48PA-PU", "28", "ATmega48PA-P", DIP28, 6),
                   ("TQFP-32", "ATMEGA48PA-AU", "32", "ATmega48PA-A", TQFP32, 8),
                   ("QFN-32", "ATMEGA48PA-MU", "32", "ATmega48PA-M", QFN32, 8),
                   ("QFN-28", "ATMEGA48PA-MMH", "28", "ATmega48PA-MM", QFN28, 6),
                   ("UFBGA-32", "ATMEGA48PA-CU", "32", "ATmega48PA-CC", UFBGA32, 8)],
    "ATmega328PB": [("TQFP-32", "ATMEGA328PB-AU", "32", "ATmega328PB-A", TQFP32, 8),
                    ("QFN-32", "ATMEGA328PB-MU", "32", "ATmega328PB-M", QFN32, 8)],
    "ATmega168PB": [("TQFP-32", "ATMEGA168PB-AU", "32", "ATmega168PB-A", TQFP32, 8),
                    ("QFN-32", "ATMEGA168PB-MU", "32", "ATmega168PB-M", QFN32, 8)],
    "ATmega88PB": [("TQFP-32", "ATMEGA88PB-AU", "32", "ATmega88PB-A", TQFP32, 8),
                   ("QFN-32", "ATMEGA88PB-MU", "32", "ATmega88PB-M", QFN32, 8)],
    "ATmega48PB": [("TQFP-32", "ATMEGA48PB-AU", "32", "ATmega48PB-A", TQFP32, 8),
                   ("QFN-32", "ATMEGA48PB-MU", "32", "ATmega48PB-M", QFN32, 8)],
    "ATmega640": [("TQFP-100", "ATMEGA640-16AU", "100", "ATmega640-16A", TQFP100, 16)],
    "ATmega1280": [("TQFP-100", "ATMEGA1280-16AU", "100", "ATmega1280-16A", TQFP100, 16)],
    "ATmega2560": [("TQFP-100", "ATMEGA2560-16AU", "100", "ATmega2560-16A", TQFP100, 16)],
    "ATmega1281": [("TQFP-64", "ATMEGA1281-16AU", "64", "ATmega1281-16A", TQFP64, 8)],
    "ATmega2561": [("TQFP-64", "ATMEGA2561-16AU", "64", "ATmega2561-16A", TQFP64, 8)],
    "ATmega164PA": [("PDIP-40", "ATMEGA164PA-PU", "40", "ATmega164PA-P", DIP40, 8),
                    ("TQFP-44", "ATMEGA164PA-AU", "44", "ATmega164PA-A", TQFP44, 8),
                    ("QFN-44", "ATMEGA164PA-MU", "44", "ATmega164PA-M", QFN44, 8)],
    "ATmega324PA": [("PDIP-40", "ATMEGA324PA-PU", "40", "ATmega324PA-P", DIP40, 8),
                    ("TQFP-44", "ATMEGA324PA-AU", "44", "ATmega324PA-A", TQFP44, 8),
                    ("QFN-44", "ATMEGA324PA-MU", "44", "ATmega324PA-M", QFN44, 8)],
    "ATmega324PB": [("TQFP-44", "ATMEGA324PB-AU", "44", "ATmega324PB-A", TQFP44, 8),
                    ("QFN-44", "ATMEGA324PB-MU", "44", "ATmega324PB-M", QFN44, 8)],
    "ATmega644PA": [("PDIP-40", "ATMEGA644PA-PU", "40", "ATmega644PA-P", DIP40, 8),
                    ("TQFP-44", "ATMEGA644PA-AU", "44", "ATmega644PA-A", TQFP44, 8),
                    ("QFN-44", "ATMEGA644PA-MU", "44", "ATmega644PA-M", QFN44, 8)],
    "ATmega1284P": [("PDIP-40", "ATMEGA1284P-PU", "40", "ATmega1284P-P", DIP40, 8),
                    ("TQFP-44", "ATMEGA1284P-AU", "44", "ATmega1284P-A", TQFP44, 8),
                    ("QFN-44", "ATMEGA1284P-MU", "44", "ATmega1284P-M", QFN44, 8)],
    "ATmega16U2": [("TQFP-32", "ATMEGA16U2-AU", "32", "ATmega16U2-A", TQFP32, 0),
                   ("QFN-32", "ATMEGA16U2-MU", "32", "ATmega16U2-M", QFN32, 0)],
    "ATmega32U2": [("TQFP-32", "ATMEGA32U2-AU", "32", "ATmega32U2-A", TQFP32, 0),
                   ("QFN-32", "ATMEGA32U2-MU", "32", "ATmega32U2-M", QFN32, 0)],
    "ATmega32U4": [("TQFP-44", "ATMEGA32U4-AU", "44", "ATmega32U4-A", TQFP44, 12),
                   ("QFN-44", "ATMEGA32U4-MU", "44", "ATmega32U4-M", QFN44U4, 12)],
    "ATmega16M1": [("TQFP-32", "ATMEGA16M1-AU", "32", "ATmega16M1-A", TQFP32, 11),
                   ("QFN-32", "ATMEGA16M1-MU", "32", "ATmega16M1-M", QFN32M1, 11)],
    "ATmega32M1": [("TQFP-32", "ATMEGA32M1-AU", "32", "ATmega32M1-A", TQFP32, 11),
                   ("QFN-32", "ATMEGA32M1-MU", "32", "ATmega32M1-M", QFN32M1, 11)],
    "ATmega64M1": [("TQFP-32", "ATMEGA64M1-AU", "32", "ATmega64M1-A", TQFP32, 11),
                   ("QFN-32", "ATMEGA64M1-MU", "32", "ATmega64M1-M", QFN32M1, 11)],
    "ATmega3208": [("TQFP-32", "ATMEGA3208-AFR", "32", "ATmega3208-A", TQFP32, 16),
                   ("VQFN-32", "ATMEGA3208-MFR", "32", "ATmega3208-M", VQFN32, 16),
                   ("SSOP-28", "ATMEGA3208-XF", "28", "ATmega3208-X", SSOP28, 14)],
    "ATmega3209": [("TQFP-48", "ATMEGA3209-AFR", "48", "ATmega3209-A", TQFP48, 16),
                   ("UQFN-48", "ATMEGA3209-MFR", "48", "ATmega3209-M", UQFN48, 16)],
    "ATmega4808": [("TQFP-32", "ATMEGA4808-AFR", "32", "ATmega4808-A", TQFP32, 16),
                   ("VQFN-32", "ATMEGA4808-MFR", "32", "ATmega4808-M", VQFN32, 16),
                   ("SSOP-28", "ATMEGA4808-XF", "28", "ATmega4808-X", SSOP28, 14)],
    "ATmega4809": [("TQFP-48", "ATMEGA4809-AFR", "48", "ATmega4809-A", TQFP48, 16),
                   ("UQFN-48", "ATMEGA4809-MFR", "48", "ATmega4809-M", UQFN48, 16)],
    "ATmega406": [("LQFP-48", "ATMEGA406-1AAU", "48", "ATmega406-1AA", LQFP48, 1)],
}


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lines = [
        "-- Terra EDA Library - Microchip megaAVR (ATmega) microcontrollers",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    seen = set()
    for device, base in DEVICES.items():
        for package, mpn, pin_count, sym, fp, adc in VARIANTS[device]:
            uid = f"Microchip-{mpn}"
            if uid in seen:
                raise SystemExit(f"duplicate unique_id: {uid}")
            seen.add(uid)
            pkgtoken = package.lower().replace(" ", "")
            row = {**DEFAULTS, **base,
                   "unique_id": uid, "value": device,
                   "part_locator": f"mcu-avr-{device.lower()}-{pkgtoken}",
                   "mpn": mpn, "package": package, "pin_count": pin_count,
                   "manufacturer_link": f"https://www.microchip.com/en-us/product/{device.lower()}",
                   "kicad_symbol": SYMLIB + sym, "kicad_footprint": fp, "adc_count": adc,
                   "description": f"8-bit AVR MCU, {base['flash_size']} Flash, "
                                  f"{base['ram_size']} SRAM, {package}"}
            vals = ", ".join(sql(row.get(c)) for c in COLS)
            lines.append(f"INSERT INTO ic_microcontrollers ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(seen)} rows across {len(DEVICES)} devices")


if __name__ == "__main__":
    main()
