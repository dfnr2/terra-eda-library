#!/usr/bin/env python3
"""Harvest a curated set of Texas Instruments amplifiers into native terra.

Datasheet-driven: each part's electrical parameters come from its TI datasheet,
filed in the central store at ${TERRA_EDA_LIB}/datasheets/ti/<part>.pdf. The
datasheet path is set inline here -- the generator is the source of truth; the
built DB is never patched afterward.

Structure: BASE holds the shared per-part specs (keyed by schematic Value);
VARIANTS lists the common through-hole and SMD packages offered for each part.
main() emits one row per (part x package): same Value/datasheet/specs, distinct
mpn / package / footprint / symbol. So a designer can place the LM358 in DIP-8
or SOIC-8 etc. straight from the schematic.

Packages: every footprint and symbol below was grep-verified against the KiCad
9 libraries. Rows that still need work are marked `REVIEW` in the variant's
`note` and carry a NULL symbol or footprint:
  - OPA549 (power): TO-263 footprint ok but the stand-in symbol's pinout is for
    an 8-pin op-amp, not the 11-lead power package; TO-220-7 has no generic
    KiCad footprint.
  - THS4551 VSSOP-8: no KiCad symbol matches the VSSOP-8 (DGK) FDA pinout (only
    the VQFN-16 RGT symbol exists).

Symbol stand-ins (parts with no dedicated KiCad symbol) reuse a same-pinout
standard symbol; the schematic Value carries the real part name. They are
flagged `stand-in` in the variant note.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import re
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_opamp_generated_320_ti_opamps.sql")
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
    "power_rating",
]

# Fields shared by every part in this set; merged in before emit (see main()).
DEFAULTS = {
    "manufacturer": "Texas Instruments",
    "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
    "source": None, "dump_priority": 0, "tier": 2, "power_rating": None,
}

# Footprint shorthands (all grep-verified present in KiCad 9 libraries).
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
DIP8 = "Package_DIP:DIP-8_W7.62mm"
DIP14 = "Package_DIP:DIP-14_W7.62mm"
VSSOP8 = "Package_SO:VSSOP-8_3x3mm_P0.65mm"
TSSOP8 = "Package_SO:TSSOP-8_3x3mm_P0.65mm"
TSSOP14 = "Package_SO:TSSOP-14_4.4x5mm_P0.65mm"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"
HSOIC8_PP = "Package_SO:Texas_R-PDSO-G8_EP2.95x4.9mm_Mask2.4x3.1mm"
VQFN16 = "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm"
TO263_7 = "Package_TO_SOT_SMD:TO-263-7_TabPin8"

# Per-part electrical/identity specs, keyed by schematic Value. Description is
# package-generic; main() appends the package.
BASE = {
    "LM358": dict(
        description="Texas Instruments LM358 dual general-purpose op-amp, 0.7MHz GBW, 3-30V single / ±1.5-15V dual supply",
        manufacturer_link="https://www.ti.com/product/LM358",
        keywords="opamp,dual,general-purpose,bipolar,single-supply,ground-sensing,lm358",
        amplifier_type="general-purpose", input_type="bipolar", channels=2,
        gain_bandwidth="0.7MHz", slew_rate="0.5V/µs", input_offset="±2mV",
        input_offset_drift="±3.5µV/°C", input_bias_current="±20nA", input_noise="40nV/√Hz",
        cmrr="80dB", psrr="100dB", quiescent_current="0.35mA", output_current="±40mA",
        rail_to_rail="no", positive_rail="V+ -1.5V", negative_rail="V- (GND)",
        supply_voltage_min=3.0, supply_voltage_max=30.0),
    "LM324": dict(
        description="Texas Instruments LM324 quad general-purpose op-amp, 1.2MHz GBW, single-supply 3-30V",
        manufacturer_link="https://www.ti.com/product/LM324",
        keywords="opamp,quad,general-purpose,bipolar,single-supply,low-power,lm324",
        amplifier_type="general-purpose", input_type="bipolar", channels=4,
        gain_bandwidth="1.2MHz", slew_rate="0.5V/µs", input_offset="3mV",
        input_offset_drift=None, input_bias_current="-20nA", input_noise="35nV/√Hz",
        cmrr="65dB", psrr="100dB", quiescent_current="175µA", output_current="20mA",
        rail_to_rail="no", positive_rail="V+ -1.5V", negative_rail="V- (GND)",
        supply_voltage_min=3.0, supply_voltage_max=30.0),
    "LM741": dict(
        description="Texas Instruments LM741 general-purpose op-amp, 1.5MHz GBW, ±18V supply",
        manufacturer_link="https://www.ti.com/product/LM741",
        keywords="opamp,single,general-purpose,bipolar,lm741",
        amplifier_type="general-purpose", input_type="bipolar", channels=1,
        gain_bandwidth="1.5MHz", slew_rate="0.5V/µs", input_offset="2mV",
        input_offset_drift=None, input_bias_current="80nA", input_noise=None,
        cmrr="90dB", psrr="96dB", quiescent_current="1.7mA", output_current="25mA",
        rail_to_rail="no", positive_rail="V+ -2V", negative_rail="V- +2V",
        supply_voltage_min=20.0, supply_voltage_max=36.0),
    "NE5532": dict(
        description="Texas Instruments NE5532 dual low-noise audio op-amp, 12MHz GBW, 5nV/√Hz, ±15V",
        manufacturer_link="https://www.ti.com/product/NE5532",
        keywords="opamp,dual,audio,low-noise,bipolar,ne5532",
        amplifier_type="audio", input_type="bipolar", channels=2,
        gain_bandwidth="12MHz", slew_rate="5V/µs", input_offset="0.5mV",
        input_offset_drift=None, input_bias_current="200nA", input_noise="5nV/√Hz",
        cmrr="100dB", psrr="100dB", quiescent_current="3mA", output_current="38mA",
        rail_to_rail="no", positive_rail="V+ -2V", negative_rail="V- +2V",
        supply_voltage_min=10.0, supply_voltage_max=44.0),
    "OP07": dict(
        description="Texas Instruments OP07 precision single op-amp, 60µV Vos, ±3-18V",
        manufacturer_link="https://www.ti.com/product/OP07",
        keywords="opamp,single,precision,bipolar,low-offset,low-noise,op07",
        amplifier_type="precision", input_type="bipolar", channels=1,
        gain_bandwidth="0.6MHz", slew_rate="0.3V/µs", input_offset="±60µV",
        input_offset_drift="±0.5µV/°C", input_bias_current="±1.8nA", input_noise="10.3nV/√Hz",
        cmrr="120dB", psrr="7µV/V", quiescent_current="2.7mA", output_current=None,
        rail_to_rail="no", positive_rail="±12.8V", negative_rail="±12.8V",
        supply_voltage_min=6.0, supply_voltage_max=36.0),
    "TL072": dict(
        description="Texas Instruments TL072 dual JFET-input op-amp, 3MHz GBW, ±2.25-18V supply",
        manufacturer_link="https://www.ti.com/product/TL072",
        keywords="opamp,dual,jfet,fet-input,audio,tl072",
        amplifier_type="jfet", input_type="JFET", channels=2,
        gain_bandwidth="3MHz", slew_rate="20V/µs", input_offset="±3mV",
        input_offset_drift="±18µV/°C", input_bias_current="65pA", input_noise="37nV/√Hz",
        cmrr="100dB", psrr="100dB", quiescent_current="1.4mA", output_current=None,
        rail_to_rail="no", positive_rail="(V+)-1.5V", negative_rail="(V-)+1.5V",
        supply_voltage_min=4.5, supply_voltage_max=36.0),
    "TL081": dict(
        description="Texas Instruments TL081 single JFET-input op-amp, 5.25MHz GBW, ±2.25-20V supply",
        manufacturer_link="https://www.ti.com/product/TL081",
        keywords="opamp,single,jfet,fet-input,general-purpose,tl081",
        amplifier_type="jfet", input_type="JFET", channels=1,
        gain_bandwidth="5.25MHz", slew_rate="20V/µs", input_offset="3mV",
        input_offset_drift="±18µV/°C", input_bias_current="65pA", input_noise="37nV/√Hz",
        cmrr="100dB", psrr="100dB", quiescent_current="1.4mA", output_current=None,
        rail_to_rail="no", positive_rail="(V+)-1.5V", negative_rail="(V-)+1.5V",
        supply_voltage_min=4.5, supply_voltage_max=40.0),
    "TL082": dict(
        description="Texas Instruments TL082 dual JFET-input op-amp, 5.25MHz GBW, ±2.25-20V supply",
        manufacturer_link="https://www.ti.com/product/TL082",
        keywords="opamp,dual,jfet,fet-input,general-purpose,tl082",
        amplifier_type="jfet", input_type="JFET", channels=2,
        gain_bandwidth="5.25MHz", slew_rate="20V/µs", input_offset="3mV",
        input_offset_drift="±18µV/°C", input_bias_current="65pA", input_noise="37nV/√Hz",
        cmrr="70dB", psrr="70dB", quiescent_current="1.4mA", output_current="10mA",
        rail_to_rail="no", positive_rail="(V+)-1.5V", negative_rail="(V-)+1.5V",
        supply_voltage_min=4.5, supply_voltage_max=40.0),
    "TL084": dict(
        description="Texas Instruments TL084 quad JFET-input op-amp, 5.25MHz GBW, ±2.25-20V supply",
        manufacturer_link="https://www.ti.com/product/TL084",
        keywords="opamp,quad,jfet,fet-input,general-purpose,tl084",
        amplifier_type="jfet", input_type="JFET", channels=4,
        gain_bandwidth="5.25MHz", slew_rate="20V/µs", input_offset="3mV",
        input_offset_drift="±18µV/°C", input_bias_current="65pA", input_noise="37nV/√Hz",
        cmrr="100dB", psrr="100dB", quiescent_current="1.4mA", output_current="±26mA",
        rail_to_rail="no", positive_rail="(V+)-1.5V", negative_rail="(V-)+1.5V",
        supply_voltage_min=4.5, supply_voltage_max=40.0),
    "OPA1612": dict(
        description="Texas Instruments OPA1612 dual ultralow-noise (1.1nV/√Hz) audio op-amp, 40MHz GBW, ±2.25-18V",
        manufacturer_link="https://www.ti.com/product/OPA1612",
        keywords="opamp,dual,audio,low-noise,low-distortion,bipolar,opa1612",
        amplifier_type="audio", input_type="bipolar", channels=2,
        gain_bandwidth="40MHz", slew_rate="27V/µs", input_offset="±100µV",
        input_offset_drift="1µV/°C", input_bias_current="±60nA", input_noise="1.1nV/√Hz",
        cmrr="120dB", psrr="0.1µV/V", quiescent_current="3.6mA", output_current="±30mA",
        rail_to_rail="RRO", positive_rail=None, negative_rail=None,
        supply_voltage_min=4.5, supply_voltage_max=36.0),
    "OPA211": dict(
        description="Texas Instruments OPA211 single low-noise (1.1nV/√Hz) precision op-amp, 80MHz GBW, RRO, ±2.25-18V",
        manufacturer_link="https://www.ti.com/product/OPA211",
        keywords="opamp,single,precision,low-noise,bipolar,rail-to-rail-output,opa211",
        amplifier_type="precision", input_type="bipolar", channels=1,
        gain_bandwidth="80MHz", slew_rate="27V/µs", input_offset="±30µV",
        input_offset_drift="±0.35µV/°C", input_bias_current="±60nA", input_noise="1.1nV/√Hz",
        cmrr="120dB", psrr="0.1µV/V", quiescent_current="3.6mA", output_current="30mA",
        rail_to_rail="RRO", positive_rail="(V+)-0.2V", negative_rail="(V-)+0.2V",
        supply_voltage_min=4.5, supply_voltage_max=36.0),
    "OPA2387": dict(
        description="Texas Instruments OPA2387 dual zero-drift CMOS op-amp, ±0.25µV Vos, 5.7MHz GBW, RRO",
        manufacturer_link="https://www.ti.com/product/OPA2387",
        keywords="opamp,dual,zero-drift,precision,cmos,rail-to-rail-output,low-offset,opa2387",
        amplifier_type="zero-drift", input_type="CMOS", channels=2,
        gain_bandwidth="5.7MHz", slew_rate="2.8V/µs", input_offset="±0.25µV",
        input_offset_drift="±0.003µV/°C", input_bias_current="±30pA", input_noise="8.5nV/√Hz",
        cmrr="150dB", psrr="0.05µV/V", quiescent_current="570µA", output_current="±55mA",
        rail_to_rail="RRO", positive_rail="(V+)-0.075V", negative_rail="(V-)+0.075V",
        supply_voltage_min=1.7, supply_voltage_max=5.5),
    "OPA340": dict(
        description="Texas Instruments OPA340 single rail-to-rail I/O CMOS op-amp, 5.5MHz GBW, 2.5-5.5V",
        manufacturer_link="https://www.ti.com/product/OPA340",
        keywords="opamp,single,rrio,cmos,rail-to-rail,general-purpose,opa340",
        amplifier_type="general-purpose", input_type="CMOS", channels=1,
        gain_bandwidth="5.5MHz", slew_rate="6V/µs", input_offset="±150µV",
        input_offset_drift="±2.5µV/°C", input_bias_current="±0.2pA", input_noise="25nV/√Hz",
        cmrr="92dB", psrr="92dB", quiescent_current="750µA", output_current="±50mA",
        rail_to_rail="RRIO", positive_rail="(V+)+0.3V", negative_rail="(V-)-0.3V",
        supply_voltage_min=2.5, supply_voltage_max=5.5),
    "OPA388": dict(
        description="Texas Instruments OPA388 single zero-drift, zero-crossover RRIO op-amp, ±0.25µV Vos, 10MHz GBW",
        manufacturer_link="https://www.ti.com/product/OPA388",
        keywords="opamp,single,zero-drift,precision,zero-crossover,rrio,opa388",
        amplifier_type="zero-drift", input_type="CMOS", channels=1,
        gain_bandwidth="10MHz", slew_rate="5V/µs", input_offset="±0.25µV",
        input_offset_drift="±0.005µV/°C", input_bias_current="±30pA", input_noise="7nV/√Hz",
        cmrr="138dB", psrr="0.1µV/V", quiescent_current="1.7mA", output_current="±60mA",
        rail_to_rail="RRIO", positive_rail="(V+)+1mV", negative_rail="(V-)-5mV",
        supply_voltage_min=2.5, supply_voltage_max=5.5),
    "OPA627": dict(
        description="Texas Instruments OPA627 precision difet (JFET) single op-amp, 16MHz GBW, 100µV max Vos, 5pA max Ib",
        manufacturer_link="https://www.ti.com/product/OPA627",
        keywords="opamp,single,precision,jfet,difet,low-noise,opa627",
        amplifier_type="precision", input_type="JFET", channels=1,
        gain_bandwidth="16MHz", slew_rate="55V/µs", input_offset="±100µV",
        input_offset_drift="0.8µV/°C", input_bias_current="±1pA", input_noise="4.5nV/√Hz",
        cmrr="110dB", psrr="116dB", quiescent_current="7mA", output_current="±45mA",
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=9.0, supply_voltage_max=36.0),
    "OPA657": dict(
        description="Texas Instruments OPA657 single 1.6GHz wideband JFET-input voltage-feedback op-amp, 4.8nV/√Hz, 700V/µs",
        manufacturer_link="https://www.ti.com/product/OPA657",
        keywords="opamp,single,high-speed,wideband,jfet,voltage-feedback,low-noise,opa657",
        amplifier_type="high-speed", input_type="JFET", channels=1,
        gain_bandwidth="1.6GHz", slew_rate="700V/µs", input_offset="±250µV",
        input_offset_drift="±2µV/°C", input_bias_current="±2pA", input_noise="4.8nV/√Hz",
        cmrr="89dB", psrr="80dB", quiescent_current="14mA", output_current="70mA",
        rail_to_rail="no", positive_rail="+3.9V", negative_rail="-3.9V",
        supply_voltage_min=8.0, supply_voltage_max=12.0),
    "OPA847": dict(
        description="Texas Instruments OPA847 single wideband ultralow-noise (0.85nV/√Hz) voltage-feedback op-amp, 3.9GHz GBW",
        manufacturer_link="https://www.ti.com/product/OPA847",
        keywords="opamp,single,high-speed,wideband,low-noise,voltage-feedback,shutdown,opa847",
        amplifier_type="high-speed", input_type="bipolar", channels=1,
        gain_bandwidth="3.9GHz", slew_rate="950V/µs", input_offset="±0.1mV",
        input_offset_drift="±0.25µV/°C", input_bias_current="-19µA", input_noise="0.85nV/√Hz",
        cmrr="110dB", psrr="100dB", quiescent_current="18.1mA", output_current="100mA",
        rail_to_rail="no", positive_rail="+3.5V", negative_rail="-3.5V",
        supply_voltage_min=8.0, supply_voltage_max=12.0),
    "THS3491": dict(
        description="Texas Instruments THS3491 single 900MHz high-power current-feedback amplifier, 8000V/µs, ±420mA output",
        manufacturer_link="https://www.ti.com/product/THS3491",
        keywords="amplifier,single,high-speed,current-feedback,cfb,high-power,line-driver,ths3491",
        amplifier_type="high-speed", input_type="bipolar", channels=1,
        gain_bandwidth="900MHz", slew_rate="8000V/µs", input_offset="±1mV",
        input_offset_drift=None, input_bias_current="±20µA", input_noise="1.7nV/√Hz",
        cmrr="60dB", psrr="70dB", quiescent_current="16.8mA", output_current="±420mA",
        rail_to_rail="no", positive_rail=None, negative_rail=None,
        supply_voltage_min=14.0, supply_voltage_max=32.0),
    "THS4551": dict(
        description="Texas Instruments THS4551 fully-differential amplifier, 150MHz, low-noise precision ADC driver",
        manufacturer_link="https://www.ti.com/product/THS4551",
        keywords="amplifier,fully-differential,fda,adc-driver,low-noise,precision,ths4551",
        amplifier_type="fully-differential", input_type="CMOS", channels=1,
        gain_bandwidth="135MHz", slew_rate="220V/µs", input_offset="±50µV",
        input_offset_drift="±0.4µV/°C", input_bias_current="1µA", input_noise="3.3nV/√Hz",
        cmrr="110dB", psrr="110dB", quiescent_current="1.37mA", output_current="±65mA",
        rail_to_rail="RRO", positive_rail=None, negative_rail=None,
        supply_voltage_min=2.7, supply_voltage_max=5.4),
    "OPA549": dict(
        description="Texas Instruments OPA549 single high-voltage high-current power op-amp, 8A continuous output",
        manufacturer_link="https://www.ti.com/product/OPA549",
        keywords="opamp,single,power,high-current,high-voltage,8a,current-limit,thermal-shutdown,opa549",
        amplifier_type="power", input_type="bipolar", channels=1,
        gain_bandwidth="0.9MHz", slew_rate="9V/µs", input_offset="±1mV",
        input_offset_drift="±20µV/°C", input_bias_current="-100nA", input_noise="70nV/√Hz",
        cmrr="95dB", psrr="100dB", quiescent_current="26mA", output_current="8A",
        rail_to_rail="no", positive_rail="(V+)-2.3V", negative_rail="(V-)+0.2V",
        supply_voltage_min=8.0, supply_voltage_max=60.0,
        power_rating="89W (infinite heat sink); θJC 1.4°C/W; TJ(max) 150°C"),
    "INA333": dict(
        description="Texas Instruments INA333 micro-power (50µA) zero-drift precision instrumentation amplifier, RRO, gain set by Rg",
        manufacturer_link="https://www.ti.com/product/INA333",
        keywords="instrumentation-amplifier,in-amp,single,precision,zero-drift,low-power,rail-to-rail-output,ina333",
        amplifier_type="instrumentation", input_type="CMOS", channels=1,
        gain_bandwidth="150kHz@G=1", slew_rate="0.16V/µs", input_offset="±25µV",
        input_offset_drift="0.1µV/°C", input_bias_current="±70pA", input_noise="50nV/√Hz",
        cmrr="100dB", psrr="100dB", quiescent_current="50µA", output_current="±5mA",
        rail_to_rail="RRO", positive_rail="(V+)-0.05V", negative_rail="(V-)+0.05V",
        supply_voltage_min=1.8, supply_voltage_max=5.5),
    "INA828": dict(
        description="Texas Instruments INA828 precision 3-op-amp instrumentation amplifier, 50µV Vos, 7nV/√Hz, gain set by Rg",
        manufacturer_link="https://www.ti.com/product/INA828",
        keywords="instrumentation-amplifier,in-amp,single,precision,3-op-amp,low-noise,ina828",
        amplifier_type="instrumentation", input_type="bipolar", channels=1,
        gain_bandwidth="2MHz@G=1", slew_rate="1.2V/µs", input_offset="50µV",
        input_offset_drift="0.5µV/°C", input_bias_current="0.15nA", input_noise="7nV/√Hz",
        cmrr="100dB", psrr="120dB", quiescent_current="600µA", output_current="±18mA",
        rail_to_rail="no", positive_rail="(V+)-0.15V", negative_rail="(V-)+0.15V",
        supply_voltage_min=4.5, supply_voltage_max=36.0),
}

# Common through-hole + SMD packages per part. Each entry:
#   (package, mpn, pin_count, kicad_symbol, kicad_footprint, note)
# kicad_symbol/kicad_footprint = None means "not available in KiCad -> needs work".
SI = "Amplifier_Operational:"        # shorthand for symbol library prefix
INST = "Amplifier_Instrumentation:"
VARIANTS = {
    "LM358": [
        ("SOIC-8", "LM358DR", "8", SI+"LM358", SOIC8, ""),
        ("PDIP-8", "LM358P", "8", SI+"LM358", DIP8, "through-hole"),
        ("VSSOP-8", "LM358DGKR", "8", SI+"LM358", VSSOP8, ""),
        ("TSSOP-8", "LM358PWR", "8", SI+"LM358", TSSOP8, ""),
    ],
    "LM324": [
        ("SOIC-14", "LM324DR", "14", SI+"LM324", SOIC14, ""),
        ("PDIP-14", "LM324N", "14", SI+"LM324", DIP14, "through-hole"),
        ("TSSOP-14", "LM324PWR", "14", SI+"LM324", TSSOP14, ""),
    ],
    "LM741": [
        ("SOIC-8", "LM741CD", "8", SI+"LM741", SOIC8, ""),
        ("PDIP-8", "LM741CN", "8", SI+"LM741", DIP8, "through-hole"),
    ],
    "NE5532": [
        ("SOIC-8", "NE5532DR", "8", SI+"NE5532", SOIC8, ""),
        ("PDIP-8", "NE5532P", "8", SI+"NE5532", DIP8, "through-hole"),
    ],
    "OP07": [
        ("SOIC-8", "OP07CDR", "8", SI+"OP07", SOIC8, ""),
        ("PDIP-8", "OP07CP", "8", SI+"OP07", DIP8, "through-hole"),
    ],
    "TL072": [
        ("SOIC-8", "TL072CDR", "8", SI+"TL072", SOIC8, ""),
        ("PDIP-8", "TL072CP", "8", SI+"TL072", DIP8, "through-hole"),
        ("TSSOP-8", "TL072CPWR", "8", SI+"TL072", TSSOP8, ""),
    ],
    "TL081": [
        ("SOIC-8", "TL081CDR", "8", SI+"TL081", SOIC8, ""),
        ("PDIP-8", "TL081CP", "8", SI+"TL081", DIP8, "through-hole"),
    ],
    "TL082": [
        ("SOIC-8", "TL082CDR", "8", SI+"TL082", SOIC8, ""),
        ("PDIP-8", "TL082CP", "8", SI+"TL082", DIP8, "through-hole"),
        ("TSSOP-8", "TL082CPWR", "8", SI+"TL082", TSSOP8, ""),
    ],
    "TL084": [
        ("SOIC-14", "TL084CDR", "14", SI+"TL084", SOIC14, ""),
        ("PDIP-14", "TL084CN", "14", SI+"TL084", DIP14, "through-hole"),
        ("TSSOP-14", "TL084CPWR", "14", SI+"TL084", TSSOP14, ""),
    ],
    "OPA1612": [
        ("SOIC-8", "OPA1612AIDR", "8", SI+"OPA1612AxD", SOIC8, ""),
        ("VSSOP-8", "OPA1612AIDGKR", "8", SI+"OPA1612AxD", VSSOP8, ""),
    ],
    "OPA211": [
        ("SOIC-8", "OPA211IDR", "8", SI+"OPA197xD", SOIC8, "stand-in symbol (generic single, same pinout)"),
        ("VSSOP-8", "OPA211IDGKR", "8", SI+"OPA197xDGK", VSSOP8, "stand-in symbol (generic single, same pinout)"),
    ],
    "OPA2387": [
        ("SOIC-8", "OPA2387IDR", "8", SI+"OPA2277", SOIC8, "stand-in symbol (generic dual, same pinout)"),
        ("VSSOP-8", "OPA2387IDGKR", "8", SI+"OPA2277", VSSOP8, "stand-in symbol (generic dual, same pinout)"),
    ],
    "OPA340": [
        ("SOT-23-5", "OPA340NA/250", "5", SI+"OPA340NA", SOT235, ""),
        ("SOIC-8", "OPA340UA", "8", SI+"OPA340UA", SOIC8, ""),
        ("PDIP-8", "OPA340PA", "8", SI+"OPA340P", DIP8, "through-hole"),
    ],
    "OPA388": [
        ("SOT-23-5", "OPA388IDBVR", "5", SI+"OPA197xDBV", SOT235, "stand-in symbol (generic single, same pinout)"),
        ("SOIC-8", "OPA388IDR", "8", SI+"OPA197xD", SOIC8, "stand-in symbol (generic single, same pinout)"),
    ],
    "OPA627": [
        ("SOIC-8", "OPA627AU", "8", SI+"OPA197xD", SOIC8, "stand-in symbol (generic single, same pinout)"),
        ("PDIP-8", "OPA627AP", "8", SI+"OPA197xD", DIP8, "through-hole; stand-in symbol (generic single, same pinout)"),
    ],
    "OPA657": [
        ("SOIC-8", "OPA657UB", "8", SI+"OPA197xD", SOIC8, "stand-in symbol (generic single, same pinout)"),
        ("SOT-23-5", "OPA657NB", "5", SI+"OPA197xDBV", SOT235, "stand-in symbol (generic single, same pinout)"),
    ],
    "OPA847": [
        ("SOIC-8", "OPA847IDR", "8", SI+"OPA847xD", SOIC8, ""),
        ("SOT-23-5", "OPA847IDBVR", "5", SI+"OPA847xDBV", SOT235, ""),
    ],
    "THS3491": [
        ("HSOIC-8 (PowerPAD)", "THS3491IDDAR", "8", SI+"THS3491xDDA", HSOIC8_PP, ""),
    ],
    "THS4551": [
        ("VQFN-16", "THS4551IRGTR", "16", "Amplifier_Difference:THS4551xRGT", VQFN16, ""),
        ("VSSOP-8", "THS4551IDGKR", "8", None, VSSOP8, "REVIEW: no KiCad symbol for the VSSOP-8 (DGK) FDA pinout"),
    ],
    "OPA549": [
        ("TO-263 (DDPAK)", "OPA549S/2K5", "11", SI+"OPA197xD", TO263_7,
         "REVIEW: stand-in symbol is an 8-pin op-amp; verify TO-263-7 pad mapping vs 11-lead power pinout"),
        ("TO-220-7", "OPA549T", "11", SI+"OPA197xD", None,
         "REVIEW: no generic KiCad TO-220-7 footprint; stand-in symbol pinout differs"),
    ],
    "INA333": [
        ("VSSOP-8", "INA333AIDGKR", "8", INST+"INA333xxDGK", VSSOP8, ""),
    ],
    "INA828": [
        ("SOIC-8", "INA828IDR", "8", INST+"INA128", SOIC8, "stand-in symbol (INA128, standard in-amp pinout)"),
        ("TSSOP-8", "INA828IPWR", "8", INST+"INA128", TSSOP8, "stand-in symbol (INA128, standard in-amp pinout)"),
    ],
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
        "-- Terra EDA Library - curated Texas Instruments op-amp / amplifier set",
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
            uid = f"Texas_Instruments-{mpn}"
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
