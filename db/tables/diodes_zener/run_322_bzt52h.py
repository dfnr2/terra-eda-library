#!/usr/bin/env python3
"""Nexperia BZT52H Zener diode family — SOD-123F flat lead, 830 mW, grades A/B/C.

37 E24 nominal voltages x three tolerance grades (BZT52H-A +/-1 %, -B +/-2 %,
-C +/-5 %). Per-type data from the datasheet's per-type tables. Vz and the quoted
rdif are at Iz=5 mA for 2V4..24 and Iz=2 mA for 27..75.
"""
from pathlib import Path
from _zener_family import emit

TYPES = {
    "2V4": {"test_current": "5mA", "impedance_max": 85, "capacitance": 450, "izsm": 6.0, "grades": {"A": [2.37, 2.43], "B": [2.35, 2.45], "C": [2.20, 2.60]}},
    "2V7": {"test_current": "5mA", "impedance_max": 83, "capacitance": 450, "izsm": 6.0, "grades": {"A": [2.67, 2.73], "B": [2.65, 2.75], "C": [2.50, 2.90]}},
    "3V0": {"test_current": "5mA", "impedance_max": 95, "capacitance": 450, "izsm": 6.0, "grades": {"A": [2.97, 3.03], "B": [2.94, 3.06], "C": [2.80, 3.20]}},
    "3V3": {"test_current": "5mA", "impedance_max": 95, "capacitance": 450, "izsm": 6.0, "grades": {"A": [3.26, 3.34], "B": [3.23, 3.37], "C": [3.10, 3.50]}},
    "3V6": {"test_current": "5mA", "impedance_max": 95, "capacitance": 450, "izsm": 6.0, "grades": {"A": [3.56, 3.64], "B": [3.53, 3.67], "C": [3.40, 3.80]}},
    "3V9": {"test_current": "5mA", "impedance_max": 95, "capacitance": 450, "izsm": 6.0, "grades": {"A": [3.86, 3.94], "B": [3.82, 3.98], "C": [3.70, 4.10]}},
    "4V3": {"test_current": "5mA", "impedance_max": 95, "capacitance": 450, "izsm": 6.0, "grades": {"A": [4.25, 4.35], "B": [4.21, 4.39], "C": [4.00, 4.60]}},
    "4V7": {"test_current": "5mA", "impedance_max": 78, "capacitance": 300, "izsm": 6.0, "grades": {"A": [4.65, 4.75], "B": [4.61, 4.79], "C": [4.40, 5.00]}},
    "5V1": {"test_current": "5mA", "impedance_max": 60, "capacitance": 300, "izsm": 6.0, "grades": {"A": [5.04, 5.16], "B": [5.00, 5.20], "C": [4.80, 5.40]}},
    "5V6": {"test_current": "5mA", "impedance_max": 40, "capacitance": 300, "izsm": 6.0, "grades": {"A": [5.54, 5.66], "B": [5.49, 5.71], "C": [5.20, 6.00]}},
    "6V2": {"test_current": "5mA", "impedance_max": 10, "capacitance": 200, "izsm": 6.0, "grades": {"A": [6.13, 6.27], "B": [6.08, 6.32], "C": [5.80, 6.60]}},
    "6V8": {"test_current": "5mA", "impedance_max": 8, "capacitance": 200, "izsm": 6.0, "grades": {"A": [6.73, 6.87], "B": [6.66, 6.94], "C": [6.40, 7.20]}},
    "7V5": {"test_current": "5mA", "impedance_max": 10, "capacitance": 150, "izsm": 4.0, "grades": {"A": [7.42, 7.58], "B": [7.35, 7.65], "C": [7.00, 7.90]}},
    "8V2": {"test_current": "5mA", "impedance_max": 10, "capacitance": 150, "izsm": 4.0, "grades": {"A": [8.11, 8.29], "B": [8.04, 8.36], "C": [7.70, 8.70]}},
    "9V1": {"test_current": "5mA", "impedance_max": 10, "capacitance": 150, "izsm": 3.0, "grades": {"A": [9.00, 9.20], "B": [8.92, 9.28], "C": [8.50, 9.60]}},
    "10": {"test_current": "5mA", "impedance_max": 10, "capacitance": 90, "izsm": 3.0, "grades": {"A": [9.90, 10.10], "B": [9.80, 10.20], "C": [9.40, 10.60]}},
    "11": {"test_current": "5mA", "impedance_max": 10, "capacitance": 85, "izsm": 2.5, "grades": {"A": [10.89, 11.11], "B": [10.80, 11.20], "C": [10.40, 11.60]}},
    "12": {"test_current": "5mA", "impedance_max": 10, "capacitance": 85, "izsm": 2.5, "grades": {"A": [11.88, 12.12], "B": [11.80, 12.20], "C": [11.40, 12.70]}},
    "13": {"test_current": "5mA", "impedance_max": 10, "capacitance": 80, "izsm": 2.5, "grades": {"A": [12.87, 13.13], "B": [12.70, 13.30], "C": [12.40, 14.10]}},
    "15": {"test_current": "5mA", "impedance_max": 15, "capacitance": 75, "izsm": 2.0, "grades": {"A": [14.85, 15.15], "B": [14.70, 15.30], "C": [13.80, 15.60]}},
    "16": {"test_current": "5mA", "impedance_max": 20, "capacitance": 75, "izsm": 1.5, "grades": {"A": [15.84, 16.16], "B": [15.70, 16.30], "C": [15.30, 17.10]}},
    "18": {"test_current": "5mA", "impedance_max": 20, "capacitance": 70, "izsm": 1.5, "grades": {"A": [17.82, 18.18], "B": [17.60, 18.40], "C": [16.80, 19.10]}},
    "20": {"test_current": "5mA", "impedance_max": 20, "capacitance": 60, "izsm": 1.5, "grades": {"A": [19.80, 20.20], "B": [19.60, 20.40], "C": [18.80, 21.20]}},
    "22": {"test_current": "5mA", "impedance_max": 25, "capacitance": 60, "izsm": 1.25, "grades": {"A": [21.78, 22.22], "B": [21.60, 22.40], "C": [20.80, 23.30]}},
    "24": {"test_current": "5mA", "impedance_max": 30, "capacitance": 55, "izsm": 1.25, "grades": {"A": [23.76, 24.24], "B": [23.50, 24.50], "C": [22.80, 25.60]}},
    "27": {"test_current": "2mA", "impedance_max": 40, "capacitance": 50, "izsm": 1.0, "grades": {"A": [26.73, 27.27], "B": [26.50, 27.50], "C": [25.10, 28.90]}},
    "30": {"test_current": "2mA", "impedance_max": 40, "capacitance": 50, "izsm": 1.0, "grades": {"A": [29.70, 30.30], "B": [29.40, 30.60], "C": [28.00, 32.00]}},
    "33": {"test_current": "2mA", "impedance_max": 40, "capacitance": 45, "izsm": 0.9, "grades": {"A": [32.67, 33.33], "B": [32.30, 33.70], "C": [31.00, 35.00]}},
    "36": {"test_current": "2mA", "impedance_max": 60, "capacitance": 45, "izsm": 0.8, "grades": {"A": [35.64, 36.36], "B": [35.30, 36.70], "C": [34.00, 38.00]}},
    "39": {"test_current": "2mA", "impedance_max": 75, "capacitance": 45, "izsm": 0.7, "grades": {"A": [38.61, 39.39], "B": [38.20, 39.80], "C": [37.00, 41.00]}},
    "43": {"test_current": "2mA", "impedance_max": 80, "capacitance": 40, "izsm": 0.6, "grades": {"A": [42.57, 43.43], "B": [42.10, 43.90], "C": [40.00, 46.00]}},
    "47": {"test_current": "2mA", "impedance_max": 90, "capacitance": 40, "izsm": 0.5, "grades": {"A": [46.53, 47.47], "B": [46.10, 47.90], "C": [44.00, 50.00]}},
    "51": {"test_current": "2mA", "impedance_max": 100, "capacitance": 40, "izsm": 0.4, "grades": {"A": [50.49, 51.51], "B": [50.00, 52.00], "C": [48.00, 54.00]}},
    "56": {"test_current": "2mA", "impedance_max": 120, "capacitance": 40, "izsm": 0.3, "grades": {"A": [55.44, 56.56], "B": [54.90, 57.10], "C": [52.00, 60.00]}},
    "62": {"test_current": "2mA", "impedance_max": 140, "capacitance": 35, "izsm": 0.3, "grades": {"A": [61.38, 62.62], "B": [60.80, 63.20], "C": [58.00, 66.00]}},
    "68": {"test_current": "2mA", "impedance_max": 160, "capacitance": 35, "izsm": 0.25, "grades": {"A": [67.32, 68.68], "B": [66.60, 69.40], "C": [64.00, 72.00]}},
    "75": {"test_current": "2mA", "impedance_max": 175, "capacitance": 35, "izsm": 0.2, "grades": {"A": [74.25, 75.75], "B": [73.50, 76.50], "C": [70.00, 79.00]}},
}

if __name__ == "__main__":
    emit(
        Path(__file__).with_name("diodes_zener_generated_322_bzt52h.sql"),
        Path(__file__).name,
        prefix="BZT52H", package="SOD-123F",
        footprint="Diode_SMD:D_SOD-123F", power_rating="830mW",
        forward_voltage="0.9V",
        datasheet="${TERRA_EDA_LIB}/datasheets/nexperia/bzt52h.pdf",
        types=TYPES,
    )
