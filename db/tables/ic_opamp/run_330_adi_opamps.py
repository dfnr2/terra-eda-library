#!/usr/bin/env python3
"""Harvest a curated set of Analog Devices / Linear Technology amplifiers.

Datasheet-driven, same shape as run_320 (the TI set): shared electrical specs in
BASE (keyed by schematic Value), common through-hole + SMD packages in VARIANTS,
one emitted row per (part x package). Datasheets are filed in the central store
at datasheets/analog-devices/*.pdf; a few sheets are shared by a family
(ada4528 -> ADA4528-1/-2, ada4898 -> ADA4898-1/-2, lt1112 -> LT1112/LT1114).

KiCad symbols: dedicated symbols exist for AD797, ADA4898-1/-2, and LTC6362
(FDA); everything else reuses a same-pinout stand-in (OPA197xD / OPA197xDGK /
OPA197xDBV single, OPA2277 dual, OPA4197xD quad, INA128 in-amp, LTC6362 for its
sibling LTC6363). Stand-ins carry the real part name in the schematic Value and
are noted below. All symbols/footprints were grep-verified against KiCad 9.

SPICE: AD844 and ADA4898 ship portable .SUBCKT macromodels (the only ADI/LT
parts here that do); they are stored at spice/analog-devices/*.cir and wired via
the sim_* columns. Both models expose a 6th node beyond a 5-pin op-amp symbol
(AD844 TZ/compensation, ADA4898 PD), so the pin map is recorded for finalizing
in KiCad's sim dialog -- see the REVIEW note. The LTspice .asc files for the LT
parts are not portable to ngspice and are left parked in staging.

One row needs work (NULL symbol): LT1115 SOIC-16W (wide-16 single-op-amp pinout
has no matching KiCad symbol). The generator prints it on every run.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import re
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_opamp_generated_330_adi_opamps.sql")
CREATED_BY = Path(__file__).name

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "variant", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "amplifier_type", "input_type", "channels", "gain_bandwidth", "slew_rate",
    "input_offset", "input_offset_drift", "input_bias_current", "input_noise",
    "cmrr", "psrr", "quiescent_current", "output_current", "rail_to_rail",
    "positive_rail", "negative_rail", "supply_voltage_min", "supply_voltage_max",
    "power_rating", "sim_model_type", "sim_device", "sim_pins", "sim_model_file",
    "sim_params",
]

DEFAULTS = {
    "manufacturer": "Analog Devices",
    "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
    "source": None, "dump_priority": 0, "tier": 2, "power_rating": None,
    "sim_model_type": None, "sim_device": None, "sim_pins": None,
    "sim_model_file": None, "sim_params": None,
}

# Footprints (grep-verified in KiCad 9).
DIP8 = "Package_DIP:DIP-8_W7.62mm"
DIP14 = "Package_DIP:DIP-14_W7.62mm"
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
SOIC16W = "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm"
SOIC8EP = "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm"
MSOP8 = "Package_SO:MSOP-8_3x3mm_P0.65mm"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"

# Symbols (grep-verified). Stand-ins reuse a same-pinout standard symbol.
S1 = "Amplifier_Operational:OPA197xD"       # single, 8-pin (SOIC/PDIP)
S1MS = "Amplifier_Operational:OPA197xDGK"    # single, MSOP-8
S1SOT = "Amplifier_Operational:OPA197xDBV"   # single, SOT-23-5
D2 = "Amplifier_Operational:OPA2277"         # dual, 8-pin
Q4 = "Amplifier_Operational:OPA4197xD"       # quad, 14-pin
INA = "Amplifier_Instrumentation:INA128"     # in-amp, 8-pin
AD797sym = "Amplifier_Operational:AD797"
ADA4898_1 = "Amplifier_Operational:ADA4898-1YRDZ"
ADA4898_2 = "Amplifier_Operational:ADA4898-2"
LTC6362sym = "Amplifier_Operational:LTC6362xMS8"

SI = "(generic single, same pinout)"
SD = "(generic dual, same pinout)"
SQ = "(generic quad, same pinout)"

BASE = {
    "LT1028": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1028.pdf",
        description="Analog Devices LT1028 ultralow-noise (0.85nV/√Hz) precision op-amp, 75MHz GBW, ±40µV offset, ±4-22V supply",
        manufacturer_link="https://www.analog.com/en/products/lt1028.html",
        keywords="opamp,single,precision,ultralow-noise,low-noise,bipolar,lt1028",
        amplifier_type="precision", input_type="bipolar", channels=1,
        gain_bandwidth="75MHz", slew_rate="15V/µs", input_offset="±40µV",
        input_offset_drift="0.8µV/°C", input_bias_current="±25nA", input_noise="0.85nV/√Hz",
        cmrr="126dB", psrr="133dB", quiescent_current="7.4mA", output_current="±25mA",
        rail_to_rail="no", positive_rail="+13V", negative_rail="-13V",
        supply_voltage_min=8.0, supply_voltage_max=44.0),
    "LT1115": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1115.pdf",
        description="Analog Devices LT1115 ultralow-noise (0.9nV/√Hz) low-distortion audio op-amp, 40MHz GBW, ±18V supply",
        manufacturer_link="https://www.analog.com/en/products/lt1115.html",
        keywords="opamp,single,audio,low-noise,low-distortion,bipolar,lt1115",
        amplifier_type="audio", input_type="bipolar", channels=1,
        gain_bandwidth="40MHz", slew_rate="15V/µs", input_offset="50µV",
        input_offset_drift="0.5µV/°C", input_bias_current="±50nA", input_noise="0.9nV/√Hz",
        cmrr="123dB", psrr="126dB", quiescent_current="8.5mA", output_current="27mA",
        rail_to_rail="no", positive_rail="+16.5V", negative_rail="-16.5V",
        supply_voltage_min=9.0, supply_voltage_max=44.0),
    "LT1818": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1818.pdf",
        description="Analog Devices LT1818 400MHz, 2500V/µs wideband single op-amp, ±5V supply",
        manufacturer_link="https://www.analog.com/en/products/lt1818.html",
        keywords="opamp,single,high-speed,wideband,video,bipolar,lt1818",
        amplifier_type="high-speed", input_type="bipolar", channels=1,
        gain_bandwidth="400MHz", slew_rate="2500V/µs", input_offset="0.2mV",
        input_offset_drift="10µV/°C", input_bias_current="-2µA", input_noise="6nV/√Hz",
        cmrr="85dB", psrr="97dB", quiescent_current="9mA", output_current="±70mA",
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.0, supply_voltage_max=12.6),
    "LT1812": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1812.pdf",
        description="Analog Devices LT1812 100MHz, 750V/µs low-power high-speed single op-amp, ±2.5-6.3V supply",
        manufacturer_link="https://www.analog.com/en/products/lt1812.html",
        keywords="opamp,single,high-speed,voltage-feedback,video,bipolar,lt1812",
        amplifier_type="high-speed", input_type="bipolar", channels=1,
        gain_bandwidth="100MHz", slew_rate="750V/µs", input_offset="0.4mV",
        input_offset_drift="10µV/°C", input_bias_current="-0.9µA", input_noise="8nV/√Hz",
        cmrr="85dB", psrr="97dB", quiescent_current="3mA", output_current="±60mA",
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=5.0, supply_voltage_max=12.6),
    "LT1167": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1167.pdf",
        description="Analog Devices LT1167 single-resistor gain-programmable precision instrumentation amplifier, 40µV offset, 0.9mA, ±2.3-18V",
        manufacturer_link="https://www.analog.com/en/products/lt1167.html",
        keywords="instrumentation-amplifier,in-amp,single,precision,single-resistor-gain,low-power,lt1167",
        amplifier_type="instrumentation", input_type="bipolar", channels=1,
        gain_bandwidth="1MHz@G=1", slew_rate="1.2V/µs", input_offset="40µV",
        input_offset_drift="0.3µV/°C", input_bias_current="350pA", input_noise="7.5nV/√Hz",
        cmrr="115dB", psrr="120dB", quiescent_current="0.9mA", output_current="27mA",
        rail_to_rail="no", positive_rail="(V+)-1.2V", negative_rail="(V-)+1.1V",
        supply_voltage_min=4.6, supply_voltage_max=36.0),
    "LT6018": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt6018.pdf",
        description="Analog Devices LT6018 33V ultralow-noise (1.2nV/√Hz) precision op-amp, 50µV offset, 15MHz GBW, ±4-16.5V",
        manufacturer_link="https://www.analog.com/en/products/lt6018.html",
        keywords="opamp,single,precision,low-noise,high-voltage,bipolar,lt6018",
        amplifier_type="precision", input_type="bipolar", channels=1,
        gain_bandwidth="15MHz", slew_rate="30V/µs", input_offset="±7µV",
        input_offset_drift="±0.2µV/°C", input_bias_current="±60nA", input_noise="1.2nV/√Hz",
        cmrr="133dB", psrr="140dB", quiescent_current="7.2mA", output_current="40mA",
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=8.0, supply_voltage_max=33.0),
    "LT6016": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt6016.pdf",
        description="Analog Devices LT6016 dual 3.2MHz over-the-top precision RRIO op-amp, ±25µV offset, 315µA/amp, 3-50V supply",
        manufacturer_link="https://www.analog.com/en/products/lt6016.html",
        keywords="opamp,dual,precision,over-the-top,rail-to-rail,low-power,high-voltage,bipolar,lt6016",
        amplifier_type="precision", input_type="bipolar", channels=2,
        gain_bandwidth="3.2MHz", slew_rate="0.75V/µs", input_offset="±25µV",
        input_offset_drift="0.75µV/°C", input_bias_current="±2nA", input_noise="18nV/√Hz",
        cmrr="126dB", psrr="126dB", quiescent_current="315µA", output_current="25mA",
        rail_to_rail="RRIO", positive_rail=None, negative_rail=None,
        supply_voltage_min=3.0, supply_voltage_max=50.0),
    "LTC2057": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ltc2057.pdf",
        description="Analog Devices LTC2057 single zero-drift precision op-amp, 4µV offset, 0.015µV/°C drift, 1.5MHz GBW, RRO, 4.75-36V",
        manufacturer_link="https://www.analog.com/en/products/ltc2057.html",
        keywords="opamp,single,zero-drift,precision,chopper,rail-to-rail-output,ltc2057",
        amplifier_type="zero-drift", input_type="CMOS", channels=1,
        gain_bandwidth="1.5MHz", slew_rate="0.45V/µs", input_offset="±4µV",
        input_offset_drift="0.015µV/°C", input_bias_current="30pA", input_noise="11nV/√Hz",
        cmrr="150dB", psrr="160dB", quiescent_current="0.8mA", output_current="26mA",
        rail_to_rail="RRO", positive_rail=None, negative_rail=None,
        supply_voltage_min=4.75, supply_voltage_max=36.0),
    "LTC2050": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ltc2050.pdf",
        description="Analog Devices LTC2050 single zero-drift chopper precision op-amp, 3µV max offset, RRO, 2.7-6V single supply",
        manufacturer_link="https://www.analog.com/en/products/ltc2050.html",
        keywords="opamp,single,zero-drift,chopper,precision,rail-to-rail-output,ltc2050",
        amplifier_type="zero-drift", input_type="CMOS", channels=1,
        gain_bandwidth="3MHz", slew_rate="2V/µs", input_offset="±0.5µV",
        input_offset_drift="0.01µV/°C", input_bias_current="±20pA", input_noise="1.5µVp-p",
        cmrr="130dB", psrr="130dB", quiescent_current="0.8mA", output_current=None,
        rail_to_rail="RRO", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.7, supply_voltage_max=6.0),
    "LTC6362": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ltc6362.pdf",
        description="Analog Devices LTC6362 precision low-power RRIO fully-differential amplifier / SAR ADC driver, 1mA, 2.8-5.25V",
        manufacturer_link="https://www.analog.com/en/products/ltc6362.html",
        keywords="amplifier,fully-differential,fda,adc-driver,sar,rail-to-rail,low-power,precision,ltc6362",
        amplifier_type="fully-differential", input_type="CMOS", channels=1,
        gain_bandwidth="180MHz", slew_rate="45V/µs", input_offset="50µV",
        input_offset_drift="0.9µV/°C", input_bias_current="±75nA", input_noise="3.9nV/√Hz",
        cmrr="98dB", psrr="105dB", quiescent_current="1mA", output_current="35mA",
        rail_to_rail="RRIO", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.8, supply_voltage_max=5.25),
    "LTC6363": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ltc6363.pdf",
        description="Analog Devices LTC6363 precision low-power fully-differential amplifier / ADC driver, 500MHz, 2.9nV/√Hz, 2.8-11V",
        manufacturer_link="https://www.analog.com/en/products/ltc6363.html",
        keywords="amplifier,fully-differential,fda,adc-driver,precision,low-power,ltc6363",
        amplifier_type="fully-differential", input_type="CMOS", channels=1,
        gain_bandwidth="500MHz", slew_rate="75V/µs", input_offset="25µV",
        input_offset_drift="0.45µV/°C", input_bias_current="-0.5µA", input_noise="2.9nV/√Hz",
        cmrr="110dB", psrr="125dB", quiescent_current="1.75mA", output_current="75mA",
        rail_to_rail="RRO", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.8, supply_voltage_max=11.0),
    "AD797": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ad797.pdf",
        description="Analog Devices AD797 ultralow-noise (0.9nV/√Hz) low-distortion precision audio op-amp, 110MHz, ±5-15V",
        manufacturer_link="https://www.analog.com/en/products/ad797.html",
        keywords="opamp,single,ultralow-noise,low-distortion,precision,audio,bipolar,ad797",
        amplifier_type="audio", input_type="bipolar", channels=1,
        gain_bandwidth="110MHz", slew_rate="20V/µs", input_offset="25µV",
        input_offset_drift="0.2µV/°C", input_bias_current="0.25µA", input_noise="0.9nV/√Hz",
        cmrr="130dB", psrr="130dB", quiescent_current="8.2mA", output_current="50mA",
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=10.0, supply_voltage_max=36.0),
    "AD844": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ad844.pdf",
        description="Analog Devices AD844 60MHz current-feedback (CFB) single op-amp with TZ pin, 2000V/µs, ±4.5-18V",
        manufacturer_link="https://www.analog.com/en/products/ad844.html",
        keywords="opamp,single,high-speed,current-feedback,cfb,transimpedance,video,bipolar,ad844",
        amplifier_type="high-speed", input_type="bipolar", channels=1,
        gain_bandwidth="60MHz", slew_rate="2000V/µs", input_offset="50µV",
        input_offset_drift="1µV/°C", input_bias_current="200nA", input_noise="2nV/√Hz",
        cmrr=None, psrr=None, quiescent_current="6.5mA", output_current="80mA",
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=9.0, supply_voltage_max=36.0,
        sim_model_type="SUBCKT", sim_device="AD844", sim_pins="+IN -IN V+ V- OUT TZ",
        sim_model_file="${TERRA_EDA_LIB}/spice/analog-devices/ad844.cir",
        sim_params="REVIEW: 6-node CFB model (extra TZ/comp node); finalize pin map in KiCad sim dialog"),
    "ADA4528-1": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ada4528.pdf",
        description="Analog Devices ADA4528-1 single ultralow-noise zero-drift RRIO op-amp, 2.5µV offset, 5.6nV/√Hz, 4MHz, 2.2-5.5V",
        manufacturer_link="https://www.analog.com/en/products/ada4528-1.html",
        keywords="opamp,single,zero-drift,precision,low-noise,rrio,rail-to-rail,ada4528-1",
        amplifier_type="zero-drift", input_type="CMOS", channels=1,
        gain_bandwidth="3.4MHz", slew_rate="0.5V/µs", input_offset="0.3µV",
        input_offset_drift="0.002µV/°C", input_bias_current="90pA", input_noise="5.9nV/√Hz",
        cmrr="160dB", psrr="150dB", quiescent_current="1.5mA", output_current="±40mA",
        rail_to_rail="RRIO", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.2, supply_voltage_max=5.5),
    "ADA4528-2": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ada4528.pdf",
        description="Analog Devices ADA4528-2 dual ultralow-noise zero-drift RRIO op-amp, 2.5µV offset, 5.6nV/√Hz, 4MHz, 2.2-5.5V",
        manufacturer_link="https://www.analog.com/en/products/ada4528-2.html",
        keywords="opamp,dual,zero-drift,precision,low-noise,rrio,rail-to-rail,ada4528-2",
        amplifier_type="zero-drift", input_type="CMOS", channels=2,
        gain_bandwidth="3.4MHz", slew_rate="0.5V/µs", input_offset="0.3µV",
        input_offset_drift="0.002µV/°C", input_bias_current="125pA", input_noise="5.9nV/√Hz",
        cmrr="160dB", psrr="150dB", quiescent_current="1.5mA", output_current="±40mA",
        rail_to_rail="RRIO", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.2, supply_voltage_max=5.5),
    "ADA4898-1": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ada4898.pdf",
        description="Analog Devices ADA4898-1 single high-voltage ultralow-noise (0.9nV/√Hz) unity-gain-stable op-amp, 65MHz, ±5-16V",
        manufacturer_link="https://www.analog.com/en/products/ada4898-1.html",
        keywords="opamp,single,high-speed,low-noise,voltage-feedback,unity-gain-stable,bipolar,ada4898-1",
        amplifier_type="high-speed", input_type="bipolar", channels=1,
        gain_bandwidth="65MHz", slew_rate="55V/µs", input_offset="20µV",
        input_offset_drift="1µV/°C", input_bias_current="-0.1µA", input_noise="0.9nV/√Hz",
        cmrr="126dB", psrr="107dB", quiescent_current="7.9mA", output_current="40mA",
        rail_to_rail="no", positive_rail="+12.7V", negative_rail="-12.8V",
        supply_voltage_min=9.0, supply_voltage_max=33.0,
        sim_model_type="SUBCKT", sim_device="ADA4898", sim_pins="+IN -IN V+ V- OUT PD",
        sim_model_file="${TERRA_EDA_LIB}/spice/analog-devices/ada4898.cir",
        sim_params="REVIEW: 6-node model (extra PD node); finalize pin map in KiCad sim dialog"),
    "ADA4898-2": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ada4898.pdf",
        description="Analog Devices ADA4898-2 dual high-voltage ultralow-noise (0.9nV/√Hz) unity-gain-stable op-amp, 65MHz, ±5-16V",
        manufacturer_link="https://www.analog.com/en/products/ada4898-2.html",
        keywords="opamp,dual,high-speed,low-noise,voltage-feedback,unity-gain-stable,bipolar,ada4898-2",
        amplifier_type="high-speed", input_type="bipolar", channels=2,
        gain_bandwidth="65MHz", slew_rate="55V/µs", input_offset="20µV",
        input_offset_drift="1µV/°C", input_bias_current="-0.1µA", input_noise="0.9nV/√Hz",
        cmrr="126dB", psrr="107dB", quiescent_current="7.9mA", output_current="40mA",
        rail_to_rail="no", positive_rail="+12.7V", negative_rail="-12.8V",
        supply_voltage_min=9.0, supply_voltage_max=33.0),
    "LT1112": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1112.pdf",
        description="Analog Devices LT1112 dual low-power precision op-amp, 60µV max offset, 250pA bias, 320µA/amp, ±1-20V",
        manufacturer_link="https://www.analog.com/en/products/lt1112.html",
        keywords="opamp,dual,precision,low-power,low-offset,low-bias,bipolar,lt1112",
        amplifier_type="precision", input_type="bipolar", channels=2,
        gain_bandwidth="750kHz", slew_rate="0.3V/µs", input_offset="20µV",
        input_offset_drift="0.5µV/°C", input_bias_current="±70pA", input_noise="0.3µVp-p",
        cmrr="136dB", psrr="126dB", quiescent_current="350µA", output_current=None,
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.0, supply_voltage_max=40.0),
    "LT1114": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1112.pdf",
        description="Analog Devices LT1114 quad low-power precision op-amp, 60µV max offset, 250pA bias, 320µA/amp, ±1-20V",
        manufacturer_link="https://www.analog.com/en/products/lt1114.html",
        keywords="opamp,quad,precision,low-power,low-offset,low-bias,bipolar,lt1114",
        amplifier_type="precision", input_type="bipolar", channels=4,
        gain_bandwidth="750kHz", slew_rate="0.3V/µs", input_offset="20µV",
        input_offset_drift="0.5µV/°C", input_bias_current="±70pA", input_noise="0.3µVp-p",
        cmrr="136dB", psrr="126dB", quiescent_current="350µA", output_current=None,
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.0, supply_voltage_max=40.0),
}

# (package, mpn, pin_count, kicad_symbol, kicad_footprint, note)
VARIANTS = {
    "LT1028": [("PDIP-8", "LT1028CN8", "8", S1, DIP8, f"through-hole; stand-in symbol {SI}"),
               ("SOIC-8", "LT1028CS8", "8", S1, SOIC8, f"stand-in symbol {SI}")],
    "LT1115": [("PDIP-8", "LT1115CN8", "8", S1, DIP8, f"through-hole; stand-in symbol {SI}"),
               ("SOIC-16W", "LT1115CSW", "16", None, SOIC16W, "REVIEW: wide-16 single-op-amp pinout, no matching KiCad symbol")],
    "LT1818": [("SOT-23-5", "LT1818CS5", "5", S1SOT, SOT235, f"stand-in symbol {SI}"),
               ("SOIC-8", "LT1818CS8", "8", S1, SOIC8, f"stand-in symbol {SI}")],
    "LT1812": [("SOT-23-5", "LT1812IS5", "5", S1SOT, SOT235, f"stand-in symbol {SI}"),
               ("SOIC-8", "LT1812IS8", "8", S1, SOIC8, f"stand-in symbol {SI}")],
    "LT1167": [("PDIP-8", "LT1167CN8", "8", INA, DIP8, "through-hole; stand-in symbol (INA128, standard in-amp pinout)"),
               ("SOIC-8", "LT1167CS8", "8", INA, SOIC8, "stand-in symbol (INA128, standard in-amp pinout)")],
    "LT6018": [("SOIC-8", "LT6018IS8", "8", S1, SOIC8, f"stand-in symbol {SI}")],
    "LT6016": [("MSOP-8", "LT6016IMS8", "8", D2, MSOP8, f"stand-in symbol {SD}")],
    "LTC2057": [("SOIC-8", "LTC2057HS8", "8", S1, SOIC8, f"stand-in symbol {SI}"),
                ("MSOP-8", "LTC2057HMS8", "8", S1MS, MSOP8, f"stand-in symbol {SI}")],
    "LTC2050": [("SOT-23-5", "LTC2050HS5", "5", S1SOT, SOT235, f"stand-in symbol {SI}"),
                ("SOIC-8", "LTC2050IS8", "8", S1, SOIC8, f"stand-in symbol {SI}")],
    "LTC6362": [("MSOP-8", "LTC6362CMS8", "8", LTC6362sym, MSOP8, "")],
    "LTC6363": [("MSOP-8", "LTC6363IMS8", "8", LTC6362sym, MSOP8, "stand-in symbol (LTC6362, same FDA pinout)")],
    "AD797": [("PDIP-8", "AD797ANZ", "8", AD797sym, DIP8, "through-hole"),
              ("SOIC-8", "AD797ARZ", "8", AD797sym, SOIC8, "")],
    "AD844": [("PDIP-8", "AD844ANZ", "8", S1, DIP8, f"through-hole; stand-in symbol {SI}; TZ pin not on symbol"),
              ("SOIC-8", "AD844ARZ", "8", S1, SOIC8, f"stand-in symbol {SI}; TZ pin not on symbol")],
    "ADA4528-1": [("MSOP-8", "ADA4528-1ARMZ", "8", S1MS, MSOP8, f"stand-in symbol {SI}")],
    "ADA4528-2": [("MSOP-8", "ADA4528-2ARMZ", "8", D2, MSOP8, f"stand-in symbol {SD}")],
    "ADA4898-1": [("SOIC-8-EP", "ADA4898-1YRDZ", "8", ADA4898_1, SOIC8EP, "")],
    "ADA4898-2": [("SOIC-8-EP", "ADA4898-2YRDZ", "8", ADA4898_2, SOIC8EP, "")],
    "LT1112": [("PDIP-8", "LT1112CN8", "8", D2, DIP8, f"through-hole; stand-in symbol {SD}"),
               ("SOIC-8", "LT1112CS8", "8", D2, SOIC8, f"stand-in symbol {SD}")],
    "LT1114": [("PDIP-14", "LT1114CN", "14", Q4, DIP14, f"through-hole; stand-in symbol {SQ}"),
               ("SOIC-14", "LT1114CS", "14", Q4, SOIC14, f"stand-in symbol {SQ}")],
}

LOC_TYPE = {"instrumentation": "inamp", "fully-differential": "fda"}


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lines = [
        "-- Terra EDA Library - curated Analog Devices / Linear Technology amplifier set",
        f"-- Datasheet-driven native terra rows, one per (part x package).",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    seen, needs_work = set(), []
    for value, base in BASE.items():
        loc = LOC_TYPE.get(base["amplifier_type"], "opamp")
        for package, mpn, pin_count, ksym, kfp, note in VARIANTS[value]:
            uid = f"Analog_Devices-{mpn}"
            if uid in seen:
                raise SystemExit(f"duplicate unique_id: {uid}")
            seen.add(uid)
            pkgtoken = re.sub(r"[^a-z0-9]+", "-", package.lower()).strip("-")
            row = {**DEFAULTS, **base,
                   "unique_id": uid,
                   "part_locator": f"ic-{loc}-{base['channels']}ch-{pkgtoken}",
                   "mpn": mpn, "variant": package, "package": package, "value": value,
                   "description": f"{base['description']}, {package}",
                   "kicad_symbol": ksym, "kicad_footprint": kfp, "pin_count": pin_count}
            if ksym is None or kfp is None:
                needs_work.append(f"{value} {package}: {note}")
            vals = ", ".join(sql(row.get(c)) for c in COLS)
            lines.append(f"INSERT INTO ic_opamp ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(seen)} rows across {len(BASE)} parts")
    if needs_work:
        print(f"  {len(needs_work)} row(s) need work (NULL symbol/footprint):")
        for w in needs_work:
            print(f"    - {w}")


if __name__ == "__main__":
    main()
