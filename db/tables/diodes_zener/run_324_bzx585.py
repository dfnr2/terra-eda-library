#!/usr/bin/env python3
"""Nexperia BZX585 Zener diode family — SOD-523 (SC-79) ultra-small SMD, 300 mW.

37 E24 nominal voltages x two tolerance grades (BZX585-B +/-2 %, -C +/-5 %).
Per-type data from the datasheet's per-type tables. Vz and the quoted rdif are at
Iz=5 mA for 2V4..24 and Iz=2 mA for 27..75.
"""
from pathlib import Path
from _zener_family import emit

TYPES = {
    "2V4": {"test_current": "5mA", "impedance_max": 100, "capacitance": 450, "izsm": 6.0, "grades": {"B": [2.35, 2.45], "C": [2.28, 2.52]}},
    "2V7": {"test_current": "5mA", "impedance_max": 100, "capacitance": 440, "izsm": 6.0, "grades": {"B": [2.65, 2.75], "C": [2.57, 2.84]}},
    "3V0": {"test_current": "5mA", "impedance_max": 95, "capacitance": 425, "izsm": 6.0, "grades": {"B": [2.94, 3.06], "C": [2.85, 3.15]}},
    "3V3": {"test_current": "5mA", "impedance_max": 95, "capacitance": 410, "izsm": 6.0, "grades": {"B": [3.23, 3.37], "C": [3.14, 3.47]}},
    "3V6": {"test_current": "5mA", "impedance_max": 90, "capacitance": 390, "izsm": 6.0, "grades": {"B": [3.53, 3.67], "C": [3.42, 3.78]}},
    "3V9": {"test_current": "5mA", "impedance_max": 90, "capacitance": 370, "izsm": 6.0, "grades": {"B": [3.82, 3.98], "C": [3.71, 4.10]}},
    "4V3": {"test_current": "5mA", "impedance_max": 90, "capacitance": 350, "izsm": 6.0, "grades": {"B": [4.21, 4.39], "C": [4.09, 4.52]}},
    "4V7": {"test_current": "5mA", "impedance_max": 80, "capacitance": 325, "izsm": 6.0, "grades": {"B": [4.61, 4.79], "C": [4.47, 4.94]}},
    "5V1": {"test_current": "5mA", "impedance_max": 60, "capacitance": 300, "izsm": 6.0, "grades": {"B": [5.00, 5.20], "C": [4.85, 5.36]}},
    "5V6": {"test_current": "5mA", "impedance_max": 40, "capacitance": 275, "izsm": 6.0, "grades": {"B": [5.49, 5.71], "C": [5.32, 5.88]}},
    "6V2": {"test_current": "5mA", "impedance_max": 10, "capacitance": 250, "izsm": 6.0, "grades": {"B": [6.08, 6.32], "C": [5.89, 6.51]}},
    "6V8": {"test_current": "5mA", "impedance_max": 15, "capacitance": 215, "izsm": 6.0, "grades": {"B": [6.66, 6.94], "C": [6.46, 7.14]}},
    "7V5": {"test_current": "5mA", "impedance_max": 10, "capacitance": 170, "izsm": 4.0, "grades": {"B": [7.35, 7.65], "C": [7.13, 7.88]}},
    "8V2": {"test_current": "5mA", "impedance_max": 10, "capacitance": 150, "izsm": 4.0, "grades": {"B": [8.04, 8.36], "C": [7.79, 8.61]}},
    "9V1": {"test_current": "5mA", "impedance_max": 10, "capacitance": 120, "izsm": 3.0, "grades": {"B": [8.92, 9.28], "C": [8.65, 9.56]}},
    "10": {"test_current": "5mA", "impedance_max": 10, "capacitance": 110, "izsm": 3.0, "grades": {"B": [9.80, 10.20], "C": [9.50, 10.50]}},
    "11": {"test_current": "5mA", "impedance_max": 10, "capacitance": 110, "izsm": 2.5, "grades": {"B": [10.78, 11.22], "C": [10.45, 11.55]}},
    "12": {"test_current": "5mA", "impedance_max": 10, "capacitance": 105, "izsm": 2.5, "grades": {"B": [11.76, 12.24], "C": [11.40, 12.60]}},
    "13": {"test_current": "5mA", "impedance_max": 10, "capacitance": 105, "izsm": 2.5, "grades": {"B": [12.74, 13.26], "C": [12.35, 13.65]}},
    "15": {"test_current": "5mA", "impedance_max": 15, "capacitance": 100, "izsm": 2.0, "grades": {"B": [14.70, 15.30], "C": [14.25, 15.75]}},
    "16": {"test_current": "5mA", "impedance_max": 40, "capacitance": 90, "izsm": 1.5, "grades": {"B": [15.68, 16.32], "C": [15.20, 16.80]}},
    "18": {"test_current": "5mA", "impedance_max": 45, "capacitance": 80, "izsm": 1.5, "grades": {"B": [17.64, 18.36], "C": [17.10, 18.90]}},
    "20": {"test_current": "5mA", "impedance_max": 55, "capacitance": 70, "izsm": 1.5, "grades": {"B": [19.60, 20.40], "C": [19.00, 21.00]}},
    "22": {"test_current": "5mA", "impedance_max": 55, "capacitance": 60, "izsm": 1.25, "grades": {"B": [21.56, 22.44], "C": [20.90, 23.10]}},
    "24": {"test_current": "5mA", "impedance_max": 70, "capacitance": 55, "izsm": 1.25, "grades": {"B": [23.52, 24.48], "C": [22.80, 25.20]}},
    "27": {"test_current": "2mA", "impedance_max": 80, "capacitance": 50, "izsm": 1.0, "grades": {"B": [26.46, 27.54], "C": [25.65, 28.35]}},
    "30": {"test_current": "2mA", "impedance_max": 80, "capacitance": 50, "izsm": 1.0, "grades": {"B": [29.40, 30.60], "C": [28.50, 31.50]}},
    "33": {"test_current": "2mA", "impedance_max": 80, "capacitance": 45, "izsm": 0.9, "grades": {"B": [32.34, 33.66], "C": [31.35, 34.65]}},
    "36": {"test_current": "2mA", "impedance_max": 90, "capacitance": 45, "izsm": 0.8, "grades": {"B": [35.28, 36.72], "C": [34.20, 37.80]}},
    "39": {"test_current": "2mA", "impedance_max": 130, "capacitance": 45, "izsm": 0.7, "grades": {"B": [38.22, 39.78], "C": [37.05, 40.95]}},
    "43": {"test_current": "2mA", "impedance_max": 150, "capacitance": 40, "izsm": 0.6, "grades": {"B": [42.14, 43.86], "C": [40.85, 45.15]}},
    "47": {"test_current": "2mA", "impedance_max": 170, "capacitance": 40, "izsm": 0.5, "grades": {"B": [46.06, 47.94], "C": [44.65, 49.35]}},
    "51": {"test_current": "2mA", "impedance_max": 180, "capacitance": 40, "izsm": 0.4, "grades": {"B": [49.98, 52.02], "C": [48.45, 53.55]}},
    "56": {"test_current": "2mA", "impedance_max": 200, "capacitance": 40, "izsm": 0.3, "grades": {"B": [54.88, 57.12], "C": [53.20, 58.80]}},
    "62": {"test_current": "2mA", "impedance_max": 215, "capacitance": 35, "izsm": 0.3, "grades": {"B": [60.76, 63.24], "C": [58.90, 65.10]}},
    "68": {"test_current": "2mA", "impedance_max": 240, "capacitance": 35, "izsm": 0.25, "grades": {"B": [66.64, 69.36], "C": [64.60, 71.40]}},
    "75": {"test_current": "2mA", "impedance_max": 255, "capacitance": 35, "izsm": 0.2, "grades": {"B": [73.50, 76.50], "C": [71.25, 78.75]}},
}

if __name__ == "__main__":
    emit(
        Path(__file__).with_name("diodes_zener_generated_324_bzx585.sql"),
        Path(__file__).name,
        prefix="BZX585", package="SOD-523",
        footprint="Diode_SMD:D_SOD-523", power_rating="300mW",
        forward_voltage="1.1V",
        datasheet="${TERRA_EDA_LIB}/datasheets/nexperia/bzx585.pdf",
        types=TYPES,
    )
