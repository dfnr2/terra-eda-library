#!/usr/bin/env python3
"""Nexperia BZV55 Zener diode family — SOD-80C glass MELF, 500 mW, grades B/C.

37 E24 nominal voltages (2.4 V to 75 V) x two tolerance grades (BZV55-B +/-2 %,
BZV55-C +/-5 %) = 74 parts. Per-type data from datasheet Tables 8 & 9; Vz and the
quoted rdif are at Iz=5 mA for 2V4..24 and Iz=2 mA for 27..75.
"""
from pathlib import Path
from _zener_family import emit

TYPES = {
    "2V4": {"test_current": "5mA", "impedance_max": 100, "capacitance": 450, "izsm": 6.0, "grades": {"B": [2.35, 2.45], "C": [2.2, 2.6]}},
    "2V7": {"test_current": "5mA", "impedance_max": 100, "capacitance": 450, "izsm": 6.0, "grades": {"B": [2.65, 2.75], "C": [2.5, 2.9]}},
    "3V0": {"test_current": "5mA", "impedance_max": 95, "capacitance": 450, "izsm": 6.0, "grades": {"B": [2.94, 3.06], "C": [2.8, 3.2]}},
    "3V3": {"test_current": "5mA", "impedance_max": 95, "capacitance": 450, "izsm": 6.0, "grades": {"B": [3.23, 3.37], "C": [3.1, 3.5]}},
    "3V6": {"test_current": "5mA", "impedance_max": 90, "capacitance": 450, "izsm": 6.0, "grades": {"B": [3.53, 3.67], "C": [3.4, 3.8]}},
    "3V9": {"test_current": "5mA", "impedance_max": 90, "capacitance": 450, "izsm": 6.0, "grades": {"B": [3.82, 3.98], "C": [3.7, 4.1]}},
    "4V3": {"test_current": "5mA", "impedance_max": 90, "capacitance": 450, "izsm": 6.0, "grades": {"B": [4.21, 4.39], "C": [4.0, 4.6]}},
    "4V7": {"test_current": "5mA", "impedance_max": 80, "capacitance": 300, "izsm": 6.0, "grades": {"B": [4.61, 4.79], "C": [4.4, 5.0]}},
    "5V1": {"test_current": "5mA", "impedance_max": 60, "capacitance": 300, "izsm": 6.0, "grades": {"B": [5.0, 5.2], "C": [4.8, 5.4]}},
    "5V6": {"test_current": "5mA", "impedance_max": 40, "capacitance": 300, "izsm": 6.0, "grades": {"B": [5.49, 5.71], "C": [5.2, 6.0]}},
    "6V2": {"test_current": "5mA", "impedance_max": 10, "capacitance": 200, "izsm": 6.0, "grades": {"B": [6.08, 6.32], "C": [5.8, 6.6]}},
    "6V8": {"test_current": "5mA", "impedance_max": 15, "capacitance": 200, "izsm": 6.0, "grades": {"B": [6.66, 6.94], "C": [6.4, 7.2]}},
    "7V5": {"test_current": "5mA", "impedance_max": 15, "capacitance": 150, "izsm": 4.0, "grades": {"B": [7.35, 7.65], "C": [7.0, 7.9]}},
    "8V2": {"test_current": "5mA", "impedance_max": 15, "capacitance": 150, "izsm": 4.0, "grades": {"B": [8.04, 8.36], "C": [7.7, 8.7]}},
    "9V1": {"test_current": "5mA", "impedance_max": 15, "capacitance": 150, "izsm": 3.0, "grades": {"B": [8.92, 9.28], "C": [8.5, 9.6]}},
    "10": {"test_current": "5mA", "impedance_max": 20, "capacitance": 90, "izsm": 3.0, "grades": {"B": [9.8, 10.2], "C": [9.4, 10.6]}},
    "11": {"test_current": "5mA", "impedance_max": 20, "capacitance": 85, "izsm": 2.5, "grades": {"B": [10.8, 11.2], "C": [10.4, 11.6]}},
    "12": {"test_current": "5mA", "impedance_max": 25, "capacitance": 85, "izsm": 2.5, "grades": {"B": [11.8, 12.2], "C": [11.4, 12.7]}},
    "13": {"test_current": "5mA", "impedance_max": 30, "capacitance": 80, "izsm": 2.5, "grades": {"B": [12.7, 13.3], "C": [12.4, 14.1]}},
    "15": {"test_current": "5mA", "impedance_max": 30, "capacitance": 75, "izsm": 2.0, "grades": {"B": [14.7, 15.3], "C": [13.8, 15.6]}},
    "16": {"test_current": "5mA", "impedance_max": 40, "capacitance": 75, "izsm": 1.5, "grades": {"B": [15.7, 16.3], "C": [15.3, 17.1]}},
    "18": {"test_current": "5mA", "impedance_max": 45, "capacitance": 70, "izsm": 1.5, "grades": {"B": [17.6, 18.4], "C": [16.8, 19.1]}},
    "20": {"test_current": "5mA", "impedance_max": 55, "capacitance": 60, "izsm": 1.5, "grades": {"B": [19.6, 20.4], "C": [18.8, 21.2]}},
    "22": {"test_current": "5mA", "impedance_max": 55, "capacitance": 60, "izsm": 1.25, "grades": {"B": [21.6, 22.4], "C": [20.8, 23.3]}},
    "24": {"test_current": "5mA", "impedance_max": 70, "capacitance": 55, "izsm": 1.25, "grades": {"B": [23.5, 24.5], "C": [22.8, 25.6]}},
    "27": {"test_current": "2mA", "impedance_max": 80, "capacitance": 50, "izsm": 1.0, "grades": {"B": [26.5, 27.5], "C": [25.1, 28.9]}},
    "30": {"test_current": "2mA", "impedance_max": 80, "capacitance": 50, "izsm": 1.0, "grades": {"B": [29.4, 30.6], "C": [28.0, 32.0]}},
    "33": {"test_current": "2mA", "impedance_max": 80, "capacitance": 45, "izsm": 0.9, "grades": {"B": [32.3, 33.7], "C": [31.0, 35.0]}},
    "36": {"test_current": "2mA", "impedance_max": 90, "capacitance": 45, "izsm": 0.8, "grades": {"B": [35.3, 36.7], "C": [34.0, 38.0]}},
    "39": {"test_current": "2mA", "impedance_max": 130, "capacitance": 45, "izsm": 0.7, "grades": {"B": [38.2, 39.8], "C": [37.0, 41.0]}},
    "43": {"test_current": "2mA", "impedance_max": 150, "capacitance": 40, "izsm": 0.6, "grades": {"B": [42.1, 43.9], "C": [40.0, 46.0]}},
    "47": {"test_current": "2mA", "impedance_max": 170, "capacitance": 40, "izsm": 0.5, "grades": {"B": [46.1, 47.9], "C": [44.0, 50.0]}},
    "51": {"test_current": "2mA", "impedance_max": 180, "capacitance": 40, "izsm": 0.4, "grades": {"B": [50.0, 52.0], "C": [48.0, 54.0]}},
    "56": {"test_current": "2mA", "impedance_max": 200, "capacitance": 40, "izsm": 0.3, "grades": {"B": [54.9, 57.1], "C": [52.0, 60.0]}},
    "62": {"test_current": "2mA", "impedance_max": 215, "capacitance": 35, "izsm": 0.3, "grades": {"B": [60.8, 63.2], "C": [58.0, 66.0]}},
    "68": {"test_current": "2mA", "impedance_max": 240, "capacitance": 35, "izsm": 0.25, "grades": {"B": [66.6, 69.4], "C": [64.0, 72.0]}},
    "75": {"test_current": "2mA", "impedance_max": 255, "capacitance": 35, "izsm": 0.2, "grades": {"B": [73.5, 76.5], "C": [70.0, 79.0]}},
}

if __name__ == "__main__":
    emit(
        Path(__file__).with_name("diodes_zener_generated_320_bzv55.sql"),
        Path(__file__).name,
        prefix="BZV55", package="SOD-80C",
        footprint="Diode_SMD:D_MiniMELF", power_rating="500mW",
        forward_voltage="0.9V",
        datasheet="${TERRA_EDA_LIB}/datasheets/nexperia/bzv55.pdf",
        temp_operating=(-65.0, 200.0), temp_storage=(-65.0, 200.0),
        extra_tags="melf", types=TYPES,
    )
