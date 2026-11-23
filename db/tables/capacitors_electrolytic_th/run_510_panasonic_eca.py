#!/usr/bin/env python3
"""Panasonic M-A series (ECA-xxM) general-purpose radial aluminum electrolytics.

Datasheet: the M-A pages of Panasonic's aluminum electrolytic capacitor catalog
(2025.9 edition, pages 81-85, dated 01-Sep-25), parked at
datasheets/panasonic/panasonic-m-a-series-radial-aluminum-electrolytic.pdf with the
catalog cover. The classic 85 C, 2000 h general-purpose radial: 6.3-450 V,
2.2-22000 uF, +/-20 %. The catalog flags the series "Some part numbers are
discontinued" and marks seven 160-400 V rows EOL; those are left out (EOL below).
Every remaining row was checked as listed at Mouser on 2026-11-23.

Ripple current is the catalog's 120 Hz / 85 C rating; tan delta (120 Hz / 20 C) goes
in the description. The catalog gives no ESR, so esr_ohm stays blank. This is not a
low-ESR part, so low_esr is set to 'no' explicitly (the column defaults to 'yes').

Part numbers are written with the hyphen distributors and Panasonic's product pages
use (ECA-1HM101); the catalog prints them without (ECA1HM101), so both go in keywords.
The bulk straight-lead part number is used; taped versions add a suffix (B, I, E).
Footprints are KiCad's stock CP_Radial ones by diameter and the catalog lead space.
Plan: plans/capacitors-electrolytic-th-general-purpose.md.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from passive_units import unit_value, sim_params  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("capacitors_electrolytic_th_generated_510_panasonic_eca.sql")
CREATED_BY = Path(__file__).name
MANUFACTURER = "Panasonic"
DATASHEET = "${TERRA_EDA_LIB}/datasheets/panasonic/panasonic-m-a-series-radial-aluminum-electrolytic.pdf"
SYMBOL = "Device:CP"

# catalog voltage code -> rated volts
VOLTS = {"0J": 6.3, "1A": 10, "1C": 16, "1E": 25, "1V": 35, "1H": 50, "1J": 63,
         "2A": 100, "2C": 160, "2D": 200, "2E": 250, "2V": 350, "2G": 400, "2W": 450}

# rows the catalog marks EOL ("End of life"); kept here so the omission is visible
EOL = {"ECA2CM331", "ECA2CM471", "ECA2DM221", "ECA2DM331", "ECA2EM221",
       "ECA2VM101", "ECA2GM101"}

# (catalog part no., cap uF, diameter mm, length mm, ripple mA rms 120 Hz/85 C,
#  tan delta 120 Hz/20 C, lead dia mm, lead space mm), from the characteristics list
FAMILY = [
    ("ECA0JM221", "220", 5.0, 11.0, 240, 0.28, 0.5, 2.0),
    ("ECA0JM471", "470", 6.3, 11.2, 380, 0.28, 0.5, 2.5),
    ("ECA0JM102", "1000", 8.0, 11.5, 580, 0.28, 0.6, 3.5),
    ("ECA0JM222", "2200", 10.0, 16.0, 890, 0.30, 0.6, 5.0),
    ("ECA0JM332", "3300", 10.0, 20.0, 1020, 0.32, 0.6, 5.0),
    ("ECA0JM472", "4700", 12.5, 20.0, 1170, 0.34, 0.6, 5.0),
    ("ECA0JM682", "6800", 12.5, 25.0, 1270, 0.38, 0.6, 5.0),
    ("ECA0JM103", "10000", 16.0, 25.0, 1450, 0.46, 0.8, 7.5),
    ("ECA0JM153", "15000", 16.0, 31.5, 1700, 0.56, 0.8, 7.5),
    ("ECA0JM223", "22000", 18.0, 35.5, 1900, 0.70, 0.8, 7.5),
    ("ECA1AM331", "330", 6.3, 11.2, 330, 0.24, 0.5, 2.5),
    ("ECA1AM102", "1000", 10.0, 12.5, 630, 0.24, 0.6, 5.0),
    ("ECA1AM222", "2200", 10.0, 20.0, 920, 0.26, 0.6, 5.0),
    ("ECA1AM332", "3300", 12.5, 20.0, 1090, 0.28, 0.6, 5.0),
    ("ECA1AM472", "4700", 12.5, 25.0, 1200, 0.30, 0.6, 5.0),
    ("ECA1AM682", "6800", 16.0, 25.0, 1400, 0.34, 0.8, 7.5),
    ("ECA1AM103", "10000", 16.0, 31.5, 1600, 0.42, 0.8, 7.5),
    ("ECA1AM153", "15000", 18.0, 35.5, 1850, 0.52, 0.8, 7.5),
    ("ECA1CM100", "10", 5.0, 11.0, 30, 0.20, 0.5, 2.0),
    ("ECA1CM220", "22", 5.0, 11.0, 75, 0.20, 0.5, 2.0),
    ("ECA1CM330", "33", 5.0, 11.0, 110, 0.20, 0.5, 2.0),
    ("ECA1CM470", "47", 5.0, 11.0, 130, 0.20, 0.5, 2.0),
    ("ECA1CM101", "100", 5.0, 11.0, 180, 0.20, 0.5, 2.0),
    ("ECA1CM221", "220", 6.3, 11.2, 280, 0.20, 0.5, 2.5),
    ("ECA1CM471", "470", 8.0, 11.5, 440, 0.20, 0.6, 3.5),
    ("ECA1CM102", "1000", 10.0, 16.0, 680, 0.20, 0.6, 5.0),
    ("ECA1CM222", "2200", 12.5, 20.0, 1000, 0.22, 0.6, 5.0),
    ("ECA1CM332", "3300", 12.5, 25.0, 1200, 0.24, 0.6, 5.0),
    ("ECA1CM472", "4700", 16.0, 25.0, 1360, 0.26, 0.8, 7.5),
    ("ECA1CM682", "6800", 16.0, 31.5, 1600, 0.30, 0.8, 7.5),
    ("ECA1CM103", "10000", 18.0, 35.5, 1800, 0.38, 0.8, 7.5),
    ("ECA1EM101", "100", 6.3, 11.2, 180, 0.16, 0.5, 2.5),
    ("ECA1EM331", "330", 8.0, 11.5, 390, 0.16, 0.6, 3.5),
    ("ECA1EM471", "470", 10.0, 12.5, 480, 0.16, 0.6, 5.0),
    ("ECA1EM102", "1000", 10.0, 20.0, 850, 0.16, 0.6, 5.0),
    ("ECA1EM222", "2200", 12.5, 25.0, 1200, 0.18, 0.6, 5.0),
    ("ECA1EM332", "3300", 16.0, 25.0, 1300, 0.20, 0.8, 7.5),
    ("ECA1EM472", "4700", 16.0, 31.5, 1500, 0.22, 0.8, 7.5),
    ("ECA1EM682", "6800", 18.0, 35.5, 1750, 0.26, 0.8, 7.5),
    ("ECA1VM100", "10", 5.0, 11.0, 60, 0.12, 0.5, 2.0),
    ("ECA1VM470", "47", 5.0, 11.0, 130, 0.14, 0.5, 2.0),
    ("ECA1VM101", "100", 6.3, 11.2, 210, 0.14, 0.5, 2.5),
    ("ECA1VM221", "220", 8.0, 11.5, 350, 0.14, 0.6, 3.5),
    ("ECA1VM331", "330", 10.0, 12.5, 440, 0.14, 0.6, 5.0),
    ("ECA1VM471", "470", 10.0, 16.0, 550, 0.14, 0.6, 5.0),
    ("ECA1VM102", "1000", 12.5, 20.0, 900, 0.14, 0.6, 5.0),
    ("ECA1VM222", "2200", 16.0, 25.0, 1250, 0.16, 0.8, 7.5),
    ("ECA1VM332", "3300", 16.0, 31.5, 1400, 0.18, 0.8, 7.5),
    ("ECA1VM472", "4700", 18.0, 35.5, 1600, 0.20, 0.8, 7.5),
    ("ECA1HM2R2", "2.2", 5.0, 11.0, 20, 0.12, 0.5, 2.0),
    ("ECA1HM3R3", "3.3", 5.0, 11.0, 35, 0.12, 0.5, 2.0),
    ("ECA1HM4R7", "4.7", 5.0, 11.0, 45, 0.12, 0.5, 2.0),
    ("ECA1HM100", "10", 5.0, 11.0, 65, 0.12, 0.5, 2.0),
    ("ECA1HM220", "22", 5.0, 11.0, 100, 0.12, 0.5, 2.0),
    ("ECA1HM330", "33", 5.0, 11.0, 110, 0.12, 0.5, 2.0),
    ("ECA1HM470", "47", 6.3, 11.2, 130, 0.12, 0.5, 2.5),
    ("ECA1HM101", "100", 8.0, 11.5, 250, 0.12, 0.6, 3.5),
    ("ECA1HM221", "220", 10.0, 12.5, 400, 0.12, 0.6, 5.0),
    ("ECA1HM331", "330", 10.0, 16.0, 500, 0.12, 0.6, 5.0),
    ("ECA1HM471", "470", 10.0, 20.0, 650, 0.12, 0.6, 5.0),
    ("ECA1HM102", "1000", 12.5, 25.0, 1050, 0.12, 0.6, 5.0),
    ("ECA1HM222", "2200", 16.0, 31.5, 1300, 0.14, 0.8, 7.5),
    ("ECA1HM332", "3300", 18.0, 35.5, 1500, 0.16, 0.8, 7.5),
    ("ECA1JM100", "10", 5.0, 11.0, 70, 0.11, 0.5, 2.0),
    ("ECA1JM220", "22", 5.0, 11.0, 105, 0.11, 0.5, 2.0),
    ("ECA1JM330", "33", 6.3, 11.2, 130, 0.11, 0.5, 2.5),
    ("ECA1JM470", "47", 6.3, 11.2, 160, 0.11, 0.5, 2.5),
    ("ECA1JM101", "100", 8.0, 11.5, 270, 0.11, 0.6, 3.5),
    ("ECA1JM221", "220", 10.0, 16.0, 450, 0.11, 0.6, 5.0),
    ("ECA1JM331", "330", 10.0, 20.0, 550, 0.11, 0.6, 5.0),
    ("ECA1JM471", "470", 12.5, 20.0, 750, 0.11, 0.6, 5.0),
    ("ECA1JM102", "1000", 16.0, 25.0, 1100, 0.11, 0.8, 7.5),
    ("ECA1JM222", "2200", 18.0, 35.5, 1400, 0.13, 0.8, 7.5),
    ("ECA2AM2R2", "2.2", 5.0, 11.0, 30, 0.10, 0.5, 2.0),
    ("ECA2AM3R3", "3.3", 5.0, 11.0, 40, 0.10, 0.5, 2.0),
    ("ECA2AM4R7", "4.7", 5.0, 11.0, 50, 0.10, 0.5, 2.0),
    ("ECA2AM100", "10", 5.0, 11.0, 70, 0.10, 0.5, 2.0),
    ("ECA2AM220", "22", 6.3, 11.2, 115, 0.10, 0.5, 2.5),
    ("ECA2AM330", "33", 8.0, 11.5, 145, 0.10, 0.6, 3.5),
    ("ECA2AM470", "47", 8.0, 11.5, 180, 0.10, 0.6, 3.5),
    ("ECA2AM101", "100", 10.0, 16.0, 350, 0.10, 0.6, 5.0),
    ("ECA2AM221", "220", 12.5, 20.0, 550, 0.10, 0.6, 5.0),
    ("ECA2AM331", "330", 12.5, 25.0, 700, 0.10, 0.6, 5.0),
    ("ECA2AM471", "470", 16.0, 25.0, 900, 0.10, 0.8, 7.5),
    ("ECA2AM102", "1000", 18.0, 35.5, 1300, 0.10, 0.8, 7.5),
    ("ECA2CM2R2", "2.2", 6.3, 11.2, 53, 0.16, 0.5, 2.5),
    ("ECA2CM3R3", "3.3", 6.3, 11.2, 66, 0.16, 0.5, 2.5),
    ("ECA2CM4R7", "4.7", 6.3, 11.2, 78, 0.16, 0.5, 2.5),
    ("ECA2CM100", "10", 10.0, 12.5, 105, 0.16, 0.6, 5.0),
    ("ECA2CM220", "22", 10.0, 16.0, 175, 0.16, 0.6, 5.0),
    ("ECA2CM330", "33", 10.0, 20.0, 235, 0.16, 0.6, 5.0),
    ("ECA2CM470", "47", 12.5, 20.0, 320, 0.16, 0.6, 5.0),
    ("ECA2CM101", "100", 12.5, 25.0, 515, 0.16, 0.6, 5.0),
    ("ECA2CM221", "220", 16.0, 31.5, 830, 0.16, 0.8, 7.5),
    ("ECA2DM2R2", "2.2", 6.3, 11.2, 50, 0.18, 0.5, 2.5),
    ("ECA2DM3R3", "3.3", 6.3, 11.2, 62, 0.18, 0.5, 2.5),
    ("ECA2DM4R7", "4.7", 8.0, 11.5, 86, 0.18, 0.6, 3.5),
    ("ECA2DM100", "10", 10.0, 12.5, 100, 0.18, 0.6, 5.0),
    ("ECA2DM220", "22", 10.0, 20.0, 180, 0.18, 0.6, 5.0),
    ("ECA2DM330", "33", 10.0, 20.0, 220, 0.18, 0.6, 5.0),
    ("ECA2DM470", "47", 12.5, 20.0, 300, 0.18, 0.6, 5.0),
    ("ECA2DM101", "100", 16.0, 25.0, 475, 0.18, 0.8, 7.5),
    ("ECA2EM2R2", "2.2", 6.3, 11.2, 50, 0.18, 0.5, 2.5),
    ("ECA2EM3R3", "3.3", 8.0, 11.5, 72, 0.18, 0.6, 3.5),
    ("ECA2EM4R7", "4.7", 8.0, 11.5, 86, 0.18, 0.6, 3.5),
    ("ECA2EM100", "10", 10.0, 16.0, 110, 0.18, 0.6, 5.0),
    ("ECA2EM220", "22", 10.0, 20.0, 180, 0.18, 0.6, 5.0),
    ("ECA2EM330", "33", 12.5, 20.0, 250, 0.18, 0.6, 5.0),
    ("ECA2EM470", "47", 12.5, 25.0, 330, 0.18, 0.6, 5.0),
    ("ECA2EM101", "100", 16.0, 31.5, 530, 0.18, 0.8, 7.5),
    ("ECA2VM2R2", "2.2", 8.0, 11.5, 55, 0.20, 0.6, 3.5),
    ("ECA2VM3R3", "3.3", 8.0, 11.5, 60, 0.20, 0.6, 3.5),
    ("ECA2VM4R7", "4.7", 10.0, 12.5, 65, 0.20, 0.6, 5.0),
    ("ECA2VM100", "10", 10.0, 20.0, 115, 0.20, 0.6, 5.0),
    ("ECA2VM220", "22", 12.5, 20.0, 195, 0.20, 0.6, 5.0),
    ("ECA2VM330", "33", 16.0, 25.0, 300, 0.20, 0.8, 7.5),
    ("ECA2VM470", "47", 16.0, 25.0, 325, 0.20, 0.8, 7.5),
    ("ECA2GM2R2", "2.2", 8.0, 11.5, 50, 0.20, 0.6, 3.5),
    ("ECA2GM3R3", "3.3", 10.0, 12.5, 54, 0.20, 0.6, 5.0),
    ("ECA2GM4R7", "4.7", 10.0, 16.0, 72, 0.20, 0.6, 5.0),
    ("ECA2GM100", "10", 10.0, 20.0, 115, 0.20, 0.6, 5.0),
    ("ECA2GM220", "22", 12.5, 25.0, 215, 0.20, 0.6, 5.0),
    ("ECA2GM330", "33", 16.0, 25.0, 275, 0.20, 0.8, 7.5),
    ("ECA2GM470", "47", 16.0, 31.5, 350, 0.20, 0.8, 7.5),
    ("ECA2WM2R2", "2.2", 10.0, 12.5, 44, 0.20, 0.6, 5.0),
    ("ECA2WM3R3", "3.3", 10.0, 16.0, 60, 0.20, 0.6, 5.0),
    ("ECA2WM4R7", "4.7", 10.0, 20.0, 79, 0.20, 0.6, 5.0),
    ("ECA2WM100", "10", 12.5, 20.0, 130, 0.20, 0.6, 5.0),
    ("ECA2WM220", "22", 16.0, 25.0, 210, 0.20, 0.8, 7.5),
    ("ECA2WM330", "33", 16.0, 31.5, 285, 0.20, 0.8, 7.5),
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "sim_params",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "capacitance", "tolerance", "voltage_rating", "ripple_current_ma",
    "diameter_mm", "length_mm", "lead_spacing_mm", "endurance_hours",
    "low_esr", "polarized",
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def check(pn, cap):
    """The part number encodes the capacitance: two digits and a multiplier, or R."""
    code = pn[-3:]
    val = float(code.replace("R", ".")) if "R" in code else int(code[:2]) * 10 ** int(code[2])
    if abs(val - float(cap)) > 1e-9 or pn[5] != "M" or pn[3:5] not in VOLTS:
        raise SystemExit(f"{pn}: part number does not match {cap} uF")


def row(pn, cap, dia, length, ripple, tan, lead_dia, pitch):
    check(pn, cap)
    v = VOLTS[pn[3:5]]
    vs = f"{v:g}V"
    mpn = f"ECA-{pn[3:]}"
    low_temp = -40.0 if v <= 100 else -25.0
    rec = {
        "unique_id": f"Panasonic-{mpn}",
        "part_locator": f"cap-elec-{cap}uf-{v:g}v-radial-d{dia:g}",
        "mpn": mpn, "manufacturer": MANUFACTURER, "package": "Radial",
        "value": unit_value(f"{cap}u", "F"), "sim_params": sim_params("C", f"{cap}u"),
        "description": (f"Panasonic M-A {cap}\u00b5F {vs} \u00b120% general-purpose aluminum "
                        f"electrolytic, 85\u00b0C 2000h, radial THT, {dia:g}\u00d7{length:g}mm, "
                        f"{pitch:g}mm lead space, tan\u03b4 {tan:g}"),
        "datasheet": DATASHEET,
        "manufacturer_link": f"https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/{pn}",
        "kicad_symbol": SYMBOL,
        "kicad_footprint": f"Capacitor_THT:CP_Radial_D{dia:.1f}mm_P{pitch:.2f}mm",
        "lifecycle_status": "Active", "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
        "keywords": (f"capacitor,electrolytic,aluminum,radial,general purpose,85C,panasonic,"
                     f"M-A,ECA,{mpn},{pn}"),
        "pin_count": "2",
        "temp_operating_min": low_temp, "temp_operating_max": 85.0,
        "capacitance": f"{cap}\u00b5F", "tolerance": "20%", "voltage_rating": vs,
        "ripple_current_ma": f"{ripple}mA",
        "diameter_mm": dia, "length_mm": length, "lead_spacing_mm": pitch,
        "endurance_hours": "2000h@85\u00b0C", "low_esr": "no", "polarized": "yes",
    }
    vals = ", ".join(sql(rec[c]) for c in COLS)
    return f"INSERT INTO capacitors_electrolytic_th ({', '.join(COLS)}) VALUES ({vals});"


def main():
    if not (Path(__file__).resolve().parents[3] / DATASHEET.replace("${TERRA_EDA_LIB}/", "")).exists():
        raise SystemExit(f"datasheet missing: {DATASHEET}")
    pns = [p[0] for p in FAMILY]
    dupes = sorted({p for p in pns if pns.count(p) > 1} | (set(pns) & EOL))
    if dupes:
        raise SystemExit(f"duplicate or EOL part numbers: {dupes}")
    lines = [
        "-- Terra EDA Library - Panasonic M-A (ECA) general-purpose radial aluminum electrolytics",
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
