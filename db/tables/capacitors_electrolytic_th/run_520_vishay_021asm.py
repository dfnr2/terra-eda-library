#!/usr/bin/env python3
"""Vishay BCcomponents 021 ASM axial aluminum electrolytics ("axial standard miniature").

Datasheet: Vishay document 28325, revision 16-Sep-16, parked at
datasheets/vishay/vishay-021asm-axial-aluminum-electrolytic.pdf. The 021 ASM is the
former Philips 2222 021 series, so restorations of 1970s-80s boards often name it by
its old 12NC (2222 021 xxxxx, kept in keywords). 6.3-100 V, 1-15000 uF, +/-20 %,
-40 to +85 C. Vishay points its retired ELM/EBM axial series at 021 ASM.

One row per Table 3 entry. The ordering code is MAL2021 + form + voltage + value:
form AA (loose axial in box) where Table 3 has one, which is case 10x30 and up;
otherwise form BA (taped in box, ammopack, straight leads). Ripple current is the
100 Hz / 85 C rating; ESR is Table 3's 100 Hz value. Endurance follows the life code
(L1 1000 h, L2 2000 h, L3 5000 h at 85 C; Table 4). Not a low-ESR part, so low_esr is
set to 'no' explicitly (the column defaults to 'yes').

Footprints are KiCad's stock CP_Axial ones, which match the data sheet's case sizes
and minimum bend pitch (Table 1 F min) one for one; their 3D models come with them.
Plan: plans/capacitors-electrolytic-th-general-purpose.md.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from passive_units import unit_value, sim_params  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("capacitors_electrolytic_th_generated_520_vishay_021asm.sql")
CREATED_BY = Path(__file__).name
MANUFACTURER = "Vishay"
DATASHEET = "${TERRA_EDA_LIB}/datasheets/vishay/vishay-021asm-axial-aluminum-electrolytic.pdf"
SYMBOL = "Device:CP"

# Table 1: nominal case D x L -> (minimum lead bend pitch F mm, KiCad footprint)
CASE = {
    "4.5x10": (15.0, "CP_Axial_L10.0mm_D4.5mm_P15.00mm_Horizontal"),
    "6x10": (15.0, "CP_Axial_L10.0mm_D6.0mm_P15.00mm_Horizontal"),
    "8x11": (15.0, "CP_Axial_L11.0mm_D8.0mm_P15.00mm_Horizontal"),
    "6.5x18": (25.0, "CP_Axial_L18.0mm_D6.5mm_P25.00mm_Horizontal"),
    "8x18": (25.0, "CP_Axial_L18.0mm_D8.0mm_P25.00mm_Horizontal"),
    "10x18": (25.0, "CP_Axial_L18.0mm_D10.0mm_P25.00mm_Horizontal"),
    "10x25": (30.0, "CP_Axial_L25.0mm_D10.0mm_P30.00mm_Horizontal"),
    "10x30": (35.0, "CP_Axial_L30.0mm_D10.0mm_P35.00mm_Horizontal"),
    "12.5x30": (35.0, "CP_Axial_L30.0mm_D12.5mm_P35.00mm_Horizontal"),
    "15x30": (35.0, "CP_Axial_L30.0mm_D15.0mm_P35.00mm_Horizontal"),
    "18x30": (35.0, "CP_Axial_L30.0mm_D18.0mm_P35.00mm_Horizontal"),
    "18x38": (44.0, "CP_Axial_L38.0mm_D18.0mm_P44.00mm_Horizontal"),
    "21x38": (44.0, "CP_Axial_L38.0mm_D21.0mm_P44.00mm_Horizontal"),
}

ENDURANCE = {"L1": "1000h@85\u00b0C", "L2": "2000h@85\u00b0C", "L3": "5000h@85\u00b0C"}
FORM = {"AA": "loose axial leads in box", "BA": "taped in box (ammopack)"}
VOLT_DIGIT = {"3": 6.3, "4": 10, "5": 16, "6": 25, "7": 40, "8": 63, "9": 100}

# (rated V, cap uF, case DxL, ripple mA 100 Hz/85 C, leakage uA 5 min, tan delta 100 Hz,
#  ESR ohm 100 Hz, Z ohm 10 kHz, life code, form, ordering code), from Table 3
FAMILY = [
    (6.3, "470", "8x11", 260, 10, 0.25, 0.850, 0.640, "L1", "BA", "MAL202133471E3"),
    (6.3, "1000", "8x18", 440, 17, 0.25, 0.400, 0.500, "L1", "BA", "MAL202133102E3"),
    (6.3, "2200", "10x25", 710, 32, 0.29, 0.210, 0.160, "L1", "BA", "MAL202190589E3"),
    (10, "100", "4.5x10", 100, 6, 0.20, 3.200, 2.000, "L1", "BA", "MAL202134101E3"),
    (10, "220", "6x10", 160, 8.4, 0.20, 1.500, 0.910, "L1", "BA", "MAL202134221E3"),
    (10, "330", "8x11", 230, 11, 0.20, 1.000, 0.610, "L1", "BA", "MAL202134331E3"),
    (10, "470", "6.5x18", 310, 13, 0.20, 0.680, 0.430, "L1", "BA", "MAL202134471E3"),
    (10, "680", "8x18", 400, 18, 0.20, 0.470, 0.290, "L1", "BA", "MAL202134681E3"),
    (10, "1000", "10x18", 550, 24, 0.20, 0.320, 0.200, "L1", "BA", "MAL202134102E3"),
    (10, "1500", "10x25", 690, 34, 0.23, 0.250, 0.180, "L1", "BA", "MAL202190525E3"),
    (10, "1500", "10x30", 740, 34, 0.23, 0.245, 0.180, "L3", "AA", "MAL202114152E3"),
    (10, "2200", "12.5x30", 980, 48, 0.25, 0.177, 0.095, "L3", "AA", "MAL202114222E3"),
    (10, "3300", "12.5x30", 1090, 70, 0.27, 0.128, 0.095, "L3", "AA", "MAL202114332E3"),
    (10, "4700", "15x30", 1320, 98, 0.29, 0.100, 0.070, "L3", "AA", "MAL202114472E3"),
    (10, "6800", "18x30", 1590, 140, 0.34, 0.079, 0.065, "L3", "AA", "MAL202114682E3"),
    (10, "10000", "18x38", 2090, 204, 0.40, 0.064, 0.040, "L3", "AA", "MAL202114103E3"),
    (10, "15000", "21x38", 2250, 304, 0.50, 0.054, 0.035, "L3", "AA", "MAL202114153E3"),
    (16, "68", "4.5x10", 90, 6.2, 0.16, 3.800, 2.400, "L1", "BA", "MAL202135689E3"),
    (16, "150", "6x10", 140, 8.8, 0.16, 1.700, 1.100, "L1", "BA", "MAL202135151E3"),
    (16, "220", "8x11", 210, 11, 0.16, 1.200, 0.730, "L1", "BA", "MAL202135221E3"),
    (16, "330", "6.5x18", 290, 15, 0.16, 0.770, 0.480, "L1", "BA", "MAL202135331E3"),
    (16, "470", "8x18", 380, 19, 0.16, 0.550, 0.340, "L1", "BA", "MAL202135471E3"),
    (16, "680", "10x18", 500, 26, 0.16, 0.380, 0.240, "L1", "BA", "MAL202135681E3"),
    (16, "1000", "10x25", 660, 36, 0.16, 0.260, 0.180, "L1", "BA", "MAL202190518E3"),
    (16, "1000", "10x30", 700, 36, 0.16, 0.260, 0.175, "L3", "AA", "MAL202115102E3"),
    (16, "1500", "12.5x30", 950, 52, 0.19, 0.205, 0.095, "L3", "AA", "MAL202115152E3"),
    (16, "2200", "12.5x30", 1040, 74, 0.21, 0.150, 0.095, "L3", "AA", "MAL202115222E3"),
    (16, "3300", "15x30", 1290, 110, 0.23, 0.111, 0.070, "L3", "AA", "MAL202115332E3"),
    (16, "4700", "18x30", 1560, 154, 0.25, 0.087, 0.065, "L3", "AA", "MAL202115472E3"),
    (16, "6800", "18x38", 2040, 222, 0.30, 0.070, 0.040, "L3", "AA", "MAL202115682E3"),
    (16, "10000", "21x38", 2170, 324, 0.36, 0.058, 0.035, "L3", "AA", "MAL202115103E3"),
    (25, "47", "4.5x10", 80, 6.4, 0.14, 4.800, 2.600, "L1", "BA", "MAL202136479E3"),
    (25, "100", "6x10", 150, 9, 0.14, 2.300, 1.200, "L1", "BA", "MAL202136101E3"),
    (25, "150", "8x11", 190, 12, 0.14, 1.500, 0.800, "L1", "BA", "MAL202190535E3"),
    (25, "150", "6.5x18", 210, 12, 0.14, 1.500, 0.800, "L1", "BA", "MAL202136151E3"),
    (25, "220", "6.5x18", 250, 15, 0.14, 1.000, 0.550, "L1", "BA", "MAL202136221E3"),
    (25, "330", "8x18", 340, 21, 0.14, 0.680, 0.360, "L1", "BA", "MAL202136331E3"),
    (25, "470", "10x18", 450, 28, 0.14, 0.480, 0.260, "L1", "BA", "MAL202136471E3"),
    (25, "680", "10x25", 560, 38, 0.14, 0.330, 0.180, "L1", "BA", "MAL202190528E3"),
    (25, "680", "10x30", 640, 38, 0.14, 0.323, 0.175, "L3", "AA", "MAL202116681E3"),
    (25, "1000", "12.5x30", 840, 54, 0.14, 0.220, 0.095, "L3", "AA", "MAL202116102E3"),
    (25, "1500", "12.5x30", 950, 79, 0.17, 0.179, 0.095, "L3", "AA", "MAL202116152E3"),
    (25, "2200", "15x30", 1180, 114, 0.19, 0.132, 0.070, "L3", "AA", "MAL202116222E3"),
    (25, "3300", "18x30", 1470, 169, 0.21, 0.099, 0.065, "L3", "AA", "MAL202116332E3"),
    (25, "4700", "18x38", 1920, 239, 0.23, 0.079, 0.040, "L3", "AA", "MAL202116472E3"),
    (25, "6800", "21x38", 2070, 344, 0.28, 0.064, 0.035, "L3", "AA", "MAL202116682E3"),
    (40, "22", "4.5x10", 60, 5.8, 0.11, 8.000, 3.200, "L2", "BA", "MAL202137229E3"),
    (40, "47", "6x10", 110, 7.8, 0.11, 3.800, 1.500, "L2", "BA", "MAL202137479E3"),
    (40, "100", "8x11", 170, 12, 0.11, 1.800, 0.700, "L2", "BA", "MAL202190538E3"),
    (40, "100", "6.5x18", 190, 12, 0.11, 1.800, 0.700, "L2", "BA", "MAL202137101E3"),
    (40, "150", "8x18", 250, 16, 0.11, 1.100, 0.470, "L2", "BA", "MAL202137151E3"),
    (40, "220", "10x18", 330, 22, 0.11, 0.800, 0.320, "L2", "BA", "MAL202137221E3"),
    (40, "330", "10x25", 430, 30, 0.11, 0.530, 0.210, "L2", "BA", "MAL202137331E3"),
    (40, "470", "10x25", 520, 42, 0.11, 0.370, 0.180, "L2", "BA", "MAL202190515E3"),
    (40, "470", "10x30", 590, 42, 0.12, 0.404, 0.175, "L3", "AA", "MAL202117471E3"),
    (40, "680", "12.5x30", 800, 58, 0.12, 0.297, 0.110, "L3", "AA", "MAL202117681E3"),
    (40, "1000", "12.5x30", 900, 84, 0.12, 0.190, 0.110, "L3", "AA", "MAL202117102E3"),
    (40, "1500", "15x30", 1120, 124, 0.15, 0.159, 0.070, "L3", "AA", "MAL202117152E3"),
    (40, "2200", "18x30", 1390, 180, 0.17, 0.118, 0.065, "L3", "AA", "MAL202117222E3"),
    (40, "3300", "18x38", 1810, 268, 0.19, 0.090, 0.040, "L3", "AA", "MAL202117332E3"),
    (40, "4700", "21x38", 1940, 380, 0.21, 0.072, 0.035, "L3", "AA", "MAL202117472E3"),
    (63, "1.0", "4.5x10", 12, 4.1, 0.09, 150.0, 55.00, "L2", "BA", "MAL202138108E3"),
    (63, "2.2", "4.5x10", 21, 4.3, 0.09, 65.00, 25.00, "L2", "BA", "MAL202138228E3"),
    (63, "3.3", "4.5x10", 25, 4.4, 0.09, 44.00, 17.00, "L2", "BA", "MAL202138338E3"),
    (63, "4.7", "4.5x10", 31, 4.6, 0.09, 31.00, 12.00, "L2", "BA", "MAL202138478E3"),
    (63, "10", "4.5x10", 50, 5.3, 0.08, 13.00, 5.500, "L2", "BA", "MAL202138109E3"),
    (63, "15", "4.5x10", 55, 5.9, 0.08, 8.500, 3.700, "L2", "BA", "MAL202138159E3"),
    (63, "22", "6x10", 90, 6.8, 0.08, 5.800, 2.500, "L2", "BA", "MAL202138229E3"),
    (63, "33", "6x10", 100, 8.2, 0.08, 3.900, 1.700, "L2", "BA", "MAL202138339E3"),
    (63, "47", "8x11", 140, 10, 0.08, 2.700, 1.200, "L2", "BA", "MAL202190542E3"),
    (63, "47", "6.5x18", 150, 10, 0.08, 2.700, 1.200, "L2", "BA", "MAL202138479E3"),
    (63, "68", "8x11", 160, 13, 0.08, 1.900, 0.810, "L2", "BA", "MAL202190545E3"),
    (63, "68", "6.5x18", 170, 13, 0.08, 1.900, 0.810, "L2", "BA", "MAL202138689E3"),
    (63, "100", "8x18", 250, 17, 0.08, 1.300, 0.550, "L2", "BA", "MAL202138101E3"),
    (63, "150", "10x18", 320, 23, 0.08, 0.850, 0.370, "L2", "BA", "MAL202138151E3"),
    (63, "220", "10x25", 430, 32, 0.08, 0.600, 0.250, "L2", "BA", "MAL202190512E3"),
    (63, "220", "10x30", 480, 32, 0.08, 0.614, 0.260, "L3", "AA", "MAL202118221E3"),
    (63, "330", "12.5x30", 610, 46, 0.08, 0.409, 0.190, "L3", "AA", "MAL202118331E3"),
    (63, "470", "12.5x30", 700, 63, 0.08, 0.287, 0.130, "L3", "AA", "MAL202118471E3"),
    (63, "680", "15x30", 890, 90, 0.08, 0.199, 0.095, "L3", "AA", "MAL202118681E3"),
    (63, "1000", "18x30", 1170, 130, 0.08, 0.135, 0.075, "L3", "AA", "MAL202118102E3"),
    (63, "1500", "18x38", 1530, 193, 0.11, 0.122, 0.045, "L3", "AA", "MAL202118152E3"),
    (63, "2200", "21x38", 1780, 281, 0.13, 0.099, 0.040, "L3", "AA", "MAL202118222E3"),
    (100, "1.0", "4.5x10", 14, 4.2, 0.08, 130.0, 90.00, "L2", "BA", "MAL202139108E3"),
    (100, "2.2", "4.5x10", 20, 4.4, 0.08, 58.00, 41.00, "L2", "BA", "MAL202139228E3"),
    (100, "4.7", "4.5x10", 30, 4.9, 0.08, 27.00, 19.00, "L2", "BA", "MAL202139478E3"),
    (100, "10", "6x10", 65, 6, 0.08, 13.00, 9.000, "L2", "BA", "MAL202139109E3"),
    (100, "15", "8x11", 77, 7, 0.08, 8.500, 6.000, "L2", "BA", "MAL202190548E3"),
    (100, "15", "6.5x18", 85, 7, 0.08, 8.500, 6.000, "L2", "BA", "MAL202139159E3"),
    (100, "22", "8x11", 95, 8.4, 0.08, 5.800, 4.100, "L2", "BA", "MAL202190552E3"),
    (100, "22", "6.5x18", 100, 8.4, 0.08, 5.800, 4.100, "L2", "BA", "MAL202139229E3"),
    (100, "33", "6.5x18", 120, 10.6, 0.08, 3.900, 2.700, "L2", "BA", "MAL202139339E3"),
    (100, "47", "8x18", 160, 13.4, 0.08, 2.700, 1.900, "L2", "BA", "MAL202139479E3"),
    (100, "68", "10x18", 220, 17.6, 0.08, 1.900, 1.300, "L2", "BA", "MAL202139689E3"),
    (100, "100", "10x25", 300, 24, 0.08, 1.300, 0.900, "L2", "BA", "MAL202190532E3"),
    (100, "100", "10x30", 340, 24, 0.07, 1.150, 1.000, "L3", "AA", "MAL202119101E3"),
    (100, "150", "12.5x30", 490, 34, 0.07, 0.645, 0.610, "L3", "AA", "MAL202119151E3"),
    (100, "220", "12.5x30", 560, 48, 0.08, 0.610, 0.560, "L3", "AA", "MAL202119221E3"),
    (100, "330", "15x30", 740, 70, 0.09, 0.420, 0.400, "L3", "AA", "MAL202119331E3"),
    (100, "470", "18x30", 980, 98, 0.09, 0.310, 0.290, "L3", "AA", "MAL202119471E3"),
    (100, "680", "18x38", 1260, 140, 0.09, 0.195, 0.180, "L3", "AA", "MAL202119681E3"),
    (100, "1000", "21x38", 1470, 204, 0.10, 0.160, 0.150, "L3", "AA", "MAL202119102E3"),
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "sim_params",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "capacitance", "tolerance", "voltage_rating", "esr_ohm", "ripple_current_ma",
    "diameter_mm", "length_mm", "lead_spacing_mm", "endurance_hours",
    "low_esr", "polarized",
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def check(v, cap, form, code):
    """MAL2021 + form digit + voltage digit + value (2 digits and a multiplier digit,
    where 8 means x0.1 and 9 means x1) + E3. The 905xx codes are a separate numbering and carry nothing to check."""
    tail = code[7:12]
    if tail.startswith("9"):
        return
    form_digit = {"AA": "1", "BA": "3"}[form]
    digits, mult = int(tail[2:4]), int(tail[4])
    val = digits * {8: 0.1, 9: 1}.get(mult, 10 ** mult)
    if tail[0] != form_digit or VOLT_DIGIT[tail[1]] != v or abs(val - float(cap)) > 1e-9:
        raise SystemExit(f"{code}: ordering code does not match {cap} uF {v} V form {form}")


def row(v, cap, case, ripple, leak, tan, esr, z, life, form, code):
    check(v, cap, form, code)
    cap = f"{float(cap):g}"
    pitch, fp = CASE[case]
    dia, length = (float(x) for x in case.split("x"))
    vs = f"{v:g}V"
    twelve_nc = f"2222 021 {code[7:12]}"
    rec = {
        "unique_id": f"Vishay-{code}",
        "part_locator": f"cap-elec-{cap}uf-{v:g}v-axial-d{dia:g}",
        "mpn": code, "manufacturer": MANUFACTURER, "package": "Axial",
        "value": unit_value(f"{cap}u", "F"), "sim_params": sim_params("C", f"{cap}u"),
        "description": (f"Vishay BCcomponents 021 ASM {cap}\u00b5F {vs} \u00b120% axial aluminum "
                        f"electrolytic, 85\u00b0C {ENDURANCE[life].split('@')[0]}, "
                        f"{dia:g}\u00d7{length:g}mm, {FORM[form]}, tan\u03b4 {tan:g}, "
                        f"Z {z:g}\u03a9 at 10kHz"),
        "datasheet": DATASHEET,
        "manufacturer_link": "https://www.vishay.com/en/product/28325/",
        "kicad_symbol": SYMBOL, "kicad_footprint": f"Capacitor_THT:{fp}",
        "lifecycle_status": "Active", "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
        "keywords": (f"capacitor,electrolytic,aluminum,axial,general purpose,85C,vishay,"
                     f"BCcomponents,021 ASM,philips,{twelve_nc},{code}"),
        "pin_count": "2",
        "temp_operating_min": -40.0, "temp_operating_max": 85.0,
        "capacitance": f"{cap}\u00b5F", "tolerance": "20%", "voltage_rating": vs,
        "esr_ohm": f"{esr:g}\u03a9", "ripple_current_ma": f"{ripple}mA",
        "diameter_mm": dia, "length_mm": length, "lead_spacing_mm": pitch,
        "endurance_hours": ENDURANCE[life], "low_esr": "no", "polarized": "yes",
    }
    vals = ", ".join(sql(rec[c]) for c in COLS)
    return f"INSERT INTO capacitors_electrolytic_th ({', '.join(COLS)}) VALUES ({vals});"


def main():
    if not (Path(__file__).resolve().parents[3] / DATASHEET.replace("${TERRA_EDA_LIB}/", "")).exists():
        raise SystemExit(f"datasheet missing: {DATASHEET}")
    codes = [p[-1] for p in FAMILY]
    dupes = sorted({c for c in codes if codes.count(c) > 1})
    if dupes:
        raise SystemExit(f"duplicate ordering codes: {dupes}")
    lines = [
        "-- Terra EDA Library - Vishay BCcomponents 021 ASM axial aluminum electrolytics",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    lines += [row(*p) for p in FAMILY]
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(FAMILY)} parts")


if __name__ == "__main__":
    main()
