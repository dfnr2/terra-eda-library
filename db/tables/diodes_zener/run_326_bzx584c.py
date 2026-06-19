#!/usr/bin/env python3
"""Vishay BZX584C series small-signal Zener diodes — SOD-523, 200 mW, +/-5%.

30 nominal voltages (2.2 V to 36 V) in a single tolerance grade (BZX584C, +/-5%);
MPN has no dash (BZX584C5V1). Per-type Vz min/max and dynamic resistance from the
datasheet's electrical-characteristics table; Vz/ZZ are at Izt=5 mA for 2V2..24
and Izt=2 mA for 27..36. impedance_max = ZZ-at-Izt max. The Vishay datasheet lists
no diode capacitance, Izsm, or Vf, so those stay NULL.

Same SOD-523 land as Nexperia BZX585 (shares its part_locator per voltage).
"""
from pathlib import Path
from _zener_family import emit

# code: {test_current, impedance_max (ZZ at Izt max, ohms), grades:{C:[Vz_min, Vz_max]}}
TYPES = {
    "2V2": {"test_current": "5mA", "impedance_max": 120, "grades": {"C": [2.0, 2.4]}},
    "2V4": {"test_current": "5mA", "impedance_max": 100, "grades": {"C": [2.2, 2.6]}},
    "2V7": {"test_current": "5mA", "impedance_max": 100, "grades": {"C": [2.5, 2.9]}},
    "3V0": {"test_current": "5mA", "impedance_max": 100, "grades": {"C": [2.8, 3.2]}},
    "3V3": {"test_current": "5mA", "impedance_max": 95, "grades": {"C": [3.1, 3.5]}},
    "3V6": {"test_current": "5mA", "impedance_max": 95, "grades": {"C": [3.4, 3.8]}},
    "3V9": {"test_current": "5mA", "impedance_max": 90, "grades": {"C": [3.7, 4.1]}},
    "4V3": {"test_current": "5mA", "impedance_max": 90, "grades": {"C": [4.0, 4.6]}},
    "4V7": {"test_current": "5mA", "impedance_max": 80, "grades": {"C": [4.4, 5.0]}},
    "5V1": {"test_current": "5mA", "impedance_max": 60, "grades": {"C": [4.8, 5.4]}},
    "5V6": {"test_current": "5mA", "impedance_max": 40, "grades": {"C": [5.2, 6.0]}},
    "6V2": {"test_current": "5mA", "impedance_max": 10, "grades": {"C": [5.8, 6.6]}},
    "6V8": {"test_current": "5mA", "impedance_max": 15, "grades": {"C": [6.4, 7.2]}},
    "7V5": {"test_current": "5mA", "impedance_max": 15, "grades": {"C": [7.0, 7.9]}},
    "8V2": {"test_current": "5mA", "impedance_max": 15, "grades": {"C": [7.7, 8.7]}},
    "9V1": {"test_current": "5mA", "impedance_max": 15, "grades": {"C": [8.5, 9.6]}},
    "10": {"test_current": "5mA", "impedance_max": 20, "grades": {"C": [9.4, 10.6]}},
    "11": {"test_current": "5mA", "impedance_max": 20, "grades": {"C": [10.4, 11.6]}},
    "12": {"test_current": "5mA", "impedance_max": 25, "grades": {"C": [11.4, 12.7]}},
    "13": {"test_current": "5mA", "impedance_max": 30, "grades": {"C": [12.4, 14.1]}},
    "15": {"test_current": "5mA", "impedance_max": 30, "grades": {"C": [13.8, 15.6]}},
    "16": {"test_current": "5mA", "impedance_max": 40, "grades": {"C": [15.3, 17.1]}},
    "18": {"test_current": "5mA", "impedance_max": 45, "grades": {"C": [16.8, 19.1]}},
    "20": {"test_current": "5mA", "impedance_max": 55, "grades": {"C": [18.8, 21.2]}},
    "22": {"test_current": "5mA", "impedance_max": 55, "grades": {"C": [20.8, 23.3]}},
    "24": {"test_current": "5mA", "impedance_max": 70, "grades": {"C": [22.8, 25.6]}},
    "27": {"test_current": "2mA", "impedance_max": 80, "grades": {"C": [25.1, 28.9]}},
    "30": {"test_current": "2mA", "impedance_max": 80, "grades": {"C": [28.0, 32.0]}},
    "33": {"test_current": "2mA", "impedance_max": 80, "grades": {"C": [31.0, 35.0]}},
    "36": {"test_current": "2mA", "impedance_max": 90, "grades": {"C": [34.0, 38.0]}},
}

if __name__ == "__main__":
    emit(
        Path(__file__).with_name("diodes_zener_generated_326_bzx584c.sql"),
        Path(__file__).name,
        prefix="BZX584", package="SOD-523",
        footprint="Diode_SMD:D_SOD-523", power_rating="200mW",
        forward_voltage=None, dash=False, manufacturer="Vishay",
        manufacturer_link="https://www.vishay.com/en/product/85793/",
        datasheet="${TERRA_EDA_LIB}/datasheets/vishay/bzx584c.pdf",
        extra_tags="small-signal", types=TYPES,
    )
