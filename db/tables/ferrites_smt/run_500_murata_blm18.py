#!/usr/bin/env python3
"""Murata BLM18...N1 chip ferrite bead family generator (datasheet-driven).

Generates the full BLM18[xx][nnn]SN1D / TN1D family (0603 / 1608Metric) from
Murata reference spec JENF243A_0003AN-01 (parked alongside this script as
murata_blm18xxxxxxN1x_datasheet.pdf). This supersedes the hand-migrated,
cut/paste-rotted BLM18 rows: the schematic's "BLM18EG121SN1D" was a typo for
BLM18PG121SN1D (120 ohm / 2 A; no "EG" series exists), and the previously
missing BLM18BD121SN1D (120 ohm / 300 mA) is now present.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ferrites_smt_generated_500_murata_blm18.sql")
CREATED_BY = Path(__file__).name

MANUFACTURER = "Murata"
PACKAGE = "0603"
SYMBOL = "Device:FerriteBead_Small"
FOOTPRINT = "Inductor_SMD:L_0603_1608Metric"
DATASHEET = "${TERRA_EDA_LIB}/datasheets/murata/blm18-n1.pdf"

# Series characteristics code -> Murata application classification.
APPLICATION = {
    "RK": "digital interface", "AG": "general use",
    "BA": "high-speed signal line", "BB": "high-speed signal line",
    "BD": "high-speed signal line",
    "PG": "DC power line", "SP": "DC power line", "KG": "DC power line",
    "SD": "DC power line", "SG": "DC power line", "SN": "DC power line",
}

# (mpn, impedance_spec, typ_ohm@100MHz, rated_mA@85C|None, rated_mA@125C, dcr_max_ohm)
# Transcribed from Murata reference spec JENF243A_0003AN-01.
FAMILY = [
    ("BLM18RK121SN1D", "120±25%", 120, None, 200, 0.35),
    ("BLM18RK221SN1D", "220±25%", 220, None, 200, 0.40),
    ("BLM18RK471SN1D", "470±25%", 470, None, 200, 0.60),
    ("BLM18RK601SN1D", "600±25%", 600, None, 200, 0.70),
    ("BLM18RK102SN1D", "1000±25%", 1000, None, 200, 0.90),
    ("BLM18PG300SN1D", "20 min.", 30, None, 1000, 0.10),
    ("BLM18PG330SN1D", "33±25%", 33, 3000, 1000, 0.050),
    ("BLM18PG600SN1D", "40 min.", 60, None, 1000, 0.20),
    ("BLM18PG121SN1D", "120±25%", 120, 2000, 1000, 0.10),
    ("BLM18PG181SN1D", "180±25%", 180, 1500, 1000, 0.18),
    ("BLM18PG221SN1D", "220±25%", 220, 1400, 1000, 0.14),
    ("BLM18PG331SN1D", "330±25%", 330, 1200, 1000, 0.20),
    ("BLM18PG471SN1D", "470±25%", 470, None, 1000, 0.26),
    ("BLM18SP300SN1D", "30±10", 30, 6000, 4000, 0.010),
    ("BLM18SP101SN1D", "100±25%", 100, 3700, 2500, 0.026),
    ("BLM18SP221SN1D", "220±25%", 220, 2800, 1900, 0.048),
    ("BLM18SP601SN1D", "600±25%", 600, 1500, 1000, 0.168),
    ("BLM18SP102SN1D", "1000±25%", 1000, 1200, 800, 0.222),
    ("BLM18KG221SN1D", "220±25%", 220, 2200, 1500, 0.060),
    ("BLM18KG331SN1D", "330±25%", 330, 1700, 1200, 0.095),
    ("BLM18KG471SN1D", "470±25%", 470, 1500, 1000, 0.145),
    ("BLM18KG601SN1D", "600±25%", 600, 1300, 1000, 0.165),
    ("BLM18KG102SN1D", "1000±25%", 1000, 1000, 800, 0.230),
    ("BLM18SD220SN1D", "22±25%", 22, 6000, 3500, 0.013),
    ("BLM18SG330SN1D", "33±25%", 33, 6000, 3500, 0.013),
    ("BLM18AG121SN1D", "120±25%", 120, None, 800, 0.28),
    ("BLM18AG151SN1D", "150±25%", 150, None, 700, 0.35),
    ("BLM18AG221SN1D", "220±25%", 220, None, 700, 0.35),
    ("BLM18AG331SN1D", "330±25%", 330, None, 600, 0.40),
    ("BLM18AG471SN1D", "470±25%", 470, None, 550, 0.45),
    ("BLM18AG601SN1D", "600±25%", 600, None, 500, 0.48),
    ("BLM18AG102SN1D", "1000±25%", 1000, None, 450, 0.60),
    ("BLM18BB050SN1D", "5±25%", 5, None, 800, 0.10),
    ("BLM18BA050SN1D", "5±25%", 5, None, 500, 0.3),
    ("BLM18BB100SN1D", "10±25%", 10, None, 700, 0.20),
    ("BLM18BA100SN1D", "10±25%", 10, None, 500, 0.35),
    ("BLM18BB220SN1D", "22±25%", 22, None, 700, 0.30),
    ("BLM18BA220SN1D", "22±25%", 22, None, 500, 0.45),
    ("BLM18BB470SN1D", "47±25%", 47, None, 600, 0.35),
    ("BLM18BD470SN1D", "47±25%", 47, None, 500, 0.4),
    ("BLM18BA470SN1D", "47±25%", 47, None, 300, 0.65),
    ("BLM18BB600SN1D", "60±25%", 60, None, 600, 0.35),
    ("BLM18BA750SN1D", "75±25%", 75, None, 300, 0.80),
    ("BLM18BB750SN1D", "75±25%", 75, None, 600, 0.40),
    ("BLM18BB121SN1D", "120±25%", 120, None, 550, 0.40),
    ("BLM18BD121SN1D", "120±25%", 120, None, 300, 0.5),
    ("BLM18BA121SN1D", "120±25%", 120, None, 200, 1.0),
    ("BLM18BB141SN1D", "140±25%", 140, None, 500, 0.45),
    ("BLM18BB151SN1D", "150±25%", 150, None, 450, 0.47),
    ("BLM18BD151SN1D", "150±25%", 150, None, 300, 0.5),
    ("BLM18BB221SN1D", "220±25%", 220, None, 450, 0.55),
    ("BLM18BD221SN1D", "220±25%", 220, None, 250, 0.55),
    ("BLM18BB331SN1D", "330±25%", 330, None, 400, 0.68),
    ("BLM18BD331SN1D", "330±25%", 330, None, 250, 0.6),
    ("BLM18BD421SN1D", "420±25%", 420, None, 250, 0.65),
    ("BLM18BB471SN1D", "470±25%", 470, None, 300, 0.95),
    ("BLM18BD471SN1D", "470±25%", 470, None, 250, 0.65),
    ("BLM18BD601SN1D", "600±25%", 600, None, 200, 0.75),
    ("BLM18BD102SN1D", "1000±25%", 1000, None, 200, 0.95),
    ("BLM18BD152SN1D", "1500±25%", 1500, None, 150, 1.3),
    ("BLM18BD182SN1D", "1800±25%", 1800, None, 150, 1.6),
    ("BLM18BD222SN1D", "2200±25%", 2200, None, 150, 1.6),
    ("BLM18BD252SN1D", "2500±25%", 2500, None, 150, 1.6),
    ("BLM18SG260TN1D", "26±25%", 26, 6000, 1000, 0.012),
    ("BLM18SG700TN1D", "70±25%", 70, 4000, 1000, 0.030),
    ("BLM18SG121TN1D", "120±25%", 120, 3000, 1000, 0.035),
    ("BLM18SG221TN1D", "220±25%", 220, 2500, 1000, 0.055),
    ("BLM18SG331TN1D", "330±25%", 330, 1500, 1000, 0.085),
    ("BLM18SN220TN1D", "22±7", 22, 8000, 5000, 0.005),
    ("BLM18KG260TN1D", "26±25%", 26, 6000, 4000, 0.012),
    ("BLM18KG300TN1D", "30±25%", 30, 5000, 3300, 0.015),
    ("BLM18KG700TN1D", "70±25%", 70, 3500, 2200, 0.032),
    ("BLM18KG101TN1D", "100±25%", 100, 3000, 1900, 0.040),
    ("BLM18KG121TN1D", "120±25%", 120, 3000, 1900, 0.040),
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "tags", "pin_count",
    "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max",
    "impedance_at_freq", "dc_resistance", "current_rating", "tolerance",
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def tolerance_of(imp):
    if "min." in imp:
        return "min"
    if "%" in imp:
        return imp.split("\u00b1")[1]
    if "\u00b1" in imp:
        return "\u00b1" + imp.split("\u00b1")[1] + "\u03a9"
    return None


def row(mpn, imp, typ, r85, r125, dcr):
    series = mpn[5:7]
    # Headline current = the 85 C rating where the datasheet quotes one (power-line
    # series), else the 125 C rating (signal series list 125 C only). This matches
    # how the parts are commonly identified (e.g. BLM18PG121 = "2 A").
    rated = r85 if r85 is not None else r125
    imax = (f"Imax={r85}mA(85\u00b0C)/{r125}mA(125\u00b0C)"
            if r85 is not None else f"Imax={r125}mA(125\u00b0C)")
    tol = tolerance_of(imp)
    app = APPLICATION.get(series, "")
    rec = {
        "unique_id": f"{MANUFACTURER}-{mpn}",
        "part_locator": f"ferrite-bead-{typ}r-{rated}ma-0603",
        "mpn": mpn, "manufacturer": MANUFACTURER, "package": PACKAGE,
        "value": f"{typ}\u03a9 {rated}mA",
        "description": (f"Murata {mpn} chip ferrite bead, {typ}\u03a9@100MHz {tol}, "
                        f"{imax}, DCRmax={dcr}\u03a9, {app}, 0603"),
        "datasheet": DATASHEET,
        "manufacturer_link": f"https://www.murata.com/en-us/products/productdetail?partno={mpn[:-1]}%23",
        "kicad_symbol": SYMBOL, "kicad_footprint": FOOTPRINT,
        "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
        "tags": "ferrite,bead", "pin_count": "2",
        "temp_operating_min": -55.0, "temp_operating_max": 125.0,
        "temp_storage_min": -55.0, "temp_storage_max": 125.0,
        "impedance_at_freq": f"{typ}\u03a9@100MHz",
        "dc_resistance": f"{dcr}\u03a9", "current_rating": f"{rated}mA",
        "tolerance": tol,
    }
    vals = ", ".join(sql(rec[c]) for c in COLS)
    return f"INSERT INTO ferrites_smt ({', '.join(COLS)}) VALUES ({vals});"


def main():
    lines = [
        "-- Terra EDA Library - Murata BLM18...N1 chip ferrite bead family",
        f"-- Datasheet-driven (JENF243A_0003AN-01). Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
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
