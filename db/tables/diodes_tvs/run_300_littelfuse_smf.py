#!/usr/bin/env python3
"""Littelfuse SMF series — 200 W TVS diodes in SOD-123FL.

Each standoff voltage is offered unidirectional (SMFxxA) and, through 85 V,
bidirectional (SMFxxCA); 90 V and up are uni-only. 45 voltages -> 83 parts.
Per-type Vbr/Ipp/Vc/IR from the datasheet table; Ppp is the 200 W family rating.
Unidirectional parts use the custom `terra-diodes:D_TVS_unidir` symbol;
bidirectional parts use the stock `Device:D_TVS` (bowtie).
"""
from pathlib import Path
from _tvs import insert, write

FOOTPRINT = "Diode_SMD:D_SOD-123F"          # SOD-123FL flat-lead
DATASHEET = "${TERRA_EDA_LIB}/datasheets/littelfuse/tvs-smf.pdf"
LINK = "https://www.littelfuse.com/products/tvs-diodes/surface-mount/smf.aspx"
UNI_SYM = "terra-diodes:D_TVS_unidir"
BIDI_SYM = "Device:D_TVS"

# code, Vbr_min, Vbr_max, IT(mA), Vrwm(V str), IR(uA), Ipp(A), Vc(V), has_bidi
SMF = [
    ("5.0", 6.40, 7.00, 10, "5.0", 400, 21.7, 9.2, True),
    ("6.0", 6.67, 7.37, 10, "6.0", 400, 19.4, 10.3, True),
    ("6.5", 7.22, 7.98, 10, "6.5", 250, 17.9, 11.2, True),
    ("7.0", 7.78, 8.60, 10, "7.0", 100, 16.7, 12.0, True),
    ("7.5", 8.33, 9.21, 1, "7.5", 50, 15.5, 12.9, True),
    ("8.0", 8.89, 9.83, 1, "8.0", 25, 14.7, 13.6, True),
    ("8.5", 9.44, 10.40, 1, "8.5", 10, 13.9, 14.4, True),
    ("9.0", 10.00, 11.10, 1, "9.0", 2.5, 13.0, 15.4, True),
    ("10", 11.10, 12.30, 1, "10", 2.5, 11.8, 17.0, True),
    ("11", 12.20, 13.50, 1, "11", 2.5, 11.0, 18.2, True),
    ("12", 13.30, 14.70, 1, "12", 2.5, 10.1, 19.9, True),
    ("13", 14.40, 15.90, 1, "13", 1.0, 9.3, 21.5, True),
    ("14", 15.60, 17.20, 1, "14", 1.0, 8.6, 23.2, True),
    ("15", 16.70, 18.50, 1, "15", 1.0, 8.2, 24.4, True),
    ("16", 17.80, 19.70, 1, "16", 1.0, 7.7, 26.0, True),
    ("17", 18.90, 20.90, 1, "17", 1.0, 7.2, 27.6, True),
    ("18", 20.00, 22.10, 1, "18", 1.0, 6.8, 29.2, True),
    ("20", 22.20, 24.50, 1, "20", 1.0, 6.2, 32.4, True),
    ("22", 24.40, 26.90, 1, "22", 1.0, 5.6, 35.5, True),
    ("24", 26.70, 29.50, 1, "24", 1.0, 5.1, 38.9, True),
    ("26", 28.90, 31.90, 1, "26", 1.0, 4.8, 42.1, True),
    ("28", 31.10, 34.40, 1, "28", 1.0, 4.4, 45.4, True),
    ("30", 33.30, 36.80, 1, "30", 1.0, 4.1, 48.4, True),
    ("33", 36.70, 40.60, 1, "33", 1.0, 3.8, 53.3, True),
    ("36", 40.00, 44.20, 1, "36", 1.0, 3.4, 58.1, True),
    ("40", 44.40, 49.10, 1, "40", 1.0, 3.1, 64.5, True),
    ("43", 47.80, 52.80, 1, "43", 1.0, 2.9, 69.4, True),
    ("45", 50.00, 55.30, 1, "45", 1.0, 2.8, 72.7, True),
    ("48", 53.30, 58.90, 1, "48", 1.0, 2.6, 77.4, True),
    ("51", 56.70, 62.70, 1, "51", 1.0, 2.4, 82.4, True),
    ("54", 60.00, 66.30, 1, "54", 1.0, 2.3, 87.1, True),
    ("58", 64.40, 71.20, 1, "58", 1.0, 2.1, 93.6, True),
    ("60", 66.70, 73.70, 1, "60", 1.0, 2.1, 96.8, True),
    ("64", 71.10, 78.60, 1, "64", 1.0, 1.9, 103.0, True),
    ("70", 77.80, 86.00, 1, "70", 1.0, 1.7, 113.0, True),
    ("75", 83.30, 92.10, 1, "75", 1.0, 1.6, 121.0, True),
    ("78", 86.70, 95.80, 1, "78", 1.0, 1.6, 126.0, True),
    ("85", 94.40, 104.00, 1, "85", 1.0, 1.5, 137.0, True),
    ("90", 100.00, 111.00, 1, "90", 1.0, 1.2, 146.0, False),
    ("100", 111.00, 123.00, 1, "100", 1.0, 1.1, 162.0, False),
    ("110", 122.00, 135.00, 1, "110", 1.0, 1.1, 177.0, False),
    ("120", 133.00, 147.00, 1, "120", 1.0, 1.0, 193.0, False),
    ("130", 144.00, 159.00, 1, "130", 1.0, 1.0, 209.0, False),
    ("150", 167.00, 185.00, 1, "150", 1.0, 0.8, 243.0, False),
    ("160", 178.00, 197.00, 1, "160", 1.0, 0.8, 259.0, False),
]

VARIANTS = [("unidirectional", "A", "uni", UNI_SYM),
            ("bidirectional", "CA", "bidi", BIDI_SYM)]


def rows():
    out = []
    for code, vbrmin, vbrmax, it, vrwm, ir, ipp, vc, has_bidi in SMF:
        for direction, suffix, short, sym in VARIANTS:
            if direction == "bidirectional" and not has_bidi:
                continue
            mpn = f"SMF{code}{suffix}"
            out.append(insert({
                "unique_id": f"Littelfuse-{mpn}",
                "part_locator": f"tvs-{vrwm}v-{short}-sod123f",
                "mpn": mpn, "manufacturer": "Littelfuse",
                "package": "SOD-123FL", "value": f"{vrwm}V {short}",
                "description": (
                    f"Littelfuse {mpn} {vrwm}V {direction} TVS, 200W peak pulse, "
                    "SOD-123FL"
                ),
                "datasheet": DATASHEET, "manufacturer_link": LINK,
                "kicad_symbol": sym, "kicad_footprint": FOOTPRINT,
                "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
                "source": None, "dump_priority": 0, "tier": 2,
                "keywords": f"tvs,protection,esd,surge,{short},{vrwm}v,200w",
                "pin_count": "2",
                "temp_operating_min": -65.0, "temp_operating_max": 150.0,
                "temp_storage_min": -65.0, "temp_storage_max": 150.0,
                "directionality": direction,
                "standoff_voltage": f"{vrwm}V",
                "breakdown_voltage_min": vbrmin, "breakdown_voltage_max": vbrmax,
                "breakdown_test_current": f"{it}mA",
                "clamping_voltage": f"{vc}V",
                "peak_pulse_current": f"{ipp}A", "peak_pulse_power": "200W",
                "leakage_current": f"{ir}uA", "capacitance": None,
            }))
    return out


if __name__ == "__main__":
    write(
        Path(__file__).with_name("diodes_tvs_generated_300_littelfuse_smf.sql"),
        Path(__file__).name, rows(),
        "Littelfuse SMF 200W TVS (SOD-123FL), unidirectional + bidirectional",
    )
