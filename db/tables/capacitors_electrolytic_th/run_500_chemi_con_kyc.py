#!/usr/bin/env python3
"""Nippon Chemi-Con KYC-series aluminum electrolytic capacitor family generator.

Datasheet-driven (CAT. No. E1001A, parked at datasheets/chemi-con/kyc-series.pdf):
the full KYC STANDARD RATINGS table -- low-ESR 105C radial-leaded (through-hole)
aluminum electrolytics, 16-120V x 68-12000uF. Voltage is decoded from the part
number; case size / ESR / ripple come straight from the ratings row.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("capacitors_electrolytic_th_generated_500_chemi_con_kyc.sql")
CREATED_BY = Path(__file__).name

MANUFACTURER = "Nippon Chemi-Con"
DATASHEET = "${TERRA_EDA_LIB}/datasheets/chemi-con/kyc-series.pdf"
SYMBOL = "Device:CP"

# Parts with a curated terra symbol (correct body/lead geometry) override the
# generic Device:CP, keyed by full MPN.
SYMBOL_OVERRIDES = {
    "EKYC250ELL392MK30S": "terra-capacitors-electrolytic-th:CAP_TH chemicon EKYC250ELL392MK30S 3900 uF 25V",
}

# Parts with a curated terra footprint carrying the true-height 3D model (the
# generic KiCad CP_Radial model uses a short representative body), keyed by MPN.
FOOTPRINT_OVERRIDES = {
    "EKYC250ELL392MK30S": "terra-capacitors-electrolytic-th:CP_Radial_D13.0mm_P5.00mm",
}

# case diameter (mm) -> (lead spacing mm, KiCad radial CP footprint)
CASE = {
    10.0: (5.0, "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"),
    12.5: (5.0, "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm"),
    16.0: (7.5, "Capacitor_THT:CP_Radial_D16.0mm_P7.50mm"),
    18.0: (7.5, "Capacitor_THT:CP_Radial_D18.0mm_P7.50mm"),
}

# (part_no_template (with the lead/taping placeholder), cap_uF, case "DxL", esr_ohm, ripple_mA)
# Transcribed from the KYC STANDARD RATINGS table. The placeholder is the
# lead-forming/taping code; "LL" (straight leads) is the catalog default.
FAMILY = [
    ("EKYC160E□□911MJC5S", "910", "10×12.5", "0.14", "1120"),
    ("EKYC800E□□101MJC5S", "100", "10×12.5", "0.14", "1120"),
    ("EKYC160E□□132MJ16S", "1300", "10×16", "0.10", "1570"),
    ("EKYC800E□□151MJ16S", "150", "10×16", "0.10", "1570"),
    ("EKYC160E□□202MJ20S", "2000", "10×20", "0.065", "1940"),
    ("EKYC800E□□221MJ20S", "220", "10×20", "0.065", "1940"),
    ("EKYC160E□□332MK20S", "3300", "12.5×20", "0.050", "2150"),
    ("EKYC800E□□331MK20S", "330", "12.5×20", "0.050", "2150"),
    ("EKYC160E□□472MK25S", "4700", "12.5×25", "0.037", "2820"),
    ("EKYC800E□□471MK25S", "470", "12.5×25", "0.037", "2820"),
    ("EKYC160E□□562MK30S", "5600", "12.5×30", "0.029", "3120"),
    ("EKYC800E□□621ML20S", "620", "16×20", "0.038", "2530"),
    ("EKYC160E□□562ML20S", "5600", "16×20", "0.038", "2530"),
    ("EKYC800E□□681MK30S", "680", "12.5×30", "0.029", "3120"),
    ("EKYC160E□□682MM20S", "6800", "18×20", "0.037", "2700"),
    ("EKYC800E□□681MK35S", "680", "12.5×35", "0.025", "3300"),
    ("EKYC160E□□752ML25S", "7500", "16×25", "0.031", "3240"),
    ("EKYC800E□□821MM20S", "820", "18×20", "0.037", "2700"),
    ("EKYC160E□□912ML30S", "9100", "16×30", "0.025", "3580"),
    ("EKYC800E□□911ML25S", "910", "16×25", "0.031", "3240"),
    ("EKYC160E□□103MM25S", "10000", "18×25", "0.030", "3350"),
    ("EKYC800E□□102MK40S", "1000", "12.5×40", "0.021", "3600"),
    ("EKYC160E□□123MM30S", "12000", "18×30", "0.024", "3710"),
    ("EKYC800E□□122ML30S", "1200", "16×30", "0.025", "3580"),
    ("EKYC250E□□561MJC5S", "560", "10×12.5", "0.14", "1120"),
    ("EKYC800E□□122MM25S", "1200", "18×25", "0.030", "3350"),
    ("EKYC250E□□821MJ16S", "820", "10×16", "0.10", "1570"),
    ("EKYC800E□□132ML35S", "1300", "16×35", "0.022", "3800"),
    ("EKYC250E□□132MJ20S", "1300", "10×20", "0.065", "1940"),
    ("EKYC800E□□152MM30S", "1500", "18×30", "0.024", "3700"),
    ("EKYC250E□□202MK20S", "2000", "12.5×20", "0.050", "2150"),
    ("EKYC800E□□182ML40S", "1800", "16×40", "0.018", "4100"),
    ("EKYC250E□□302MK25S", "3000", "12.5×25", "0.037", "2820"),
    ("EKYC800E□□182MM35S", "1800", "18×35", "0.021", "4000"),
    ("EKYC250E□□362ML20S", "3600", "16×20", "0.038", "2530"),
    ("EKYC800E□□242MM40S", "2400", "18×40", "0.017", "4300"),
    ("EKYC250E□□392MK30S", "3900", "12.5×30", "0.029", "3120"),
    ("EKYC101E□□680MJC5S", "68", "10×12.5", "0.14", "1120"),
    ("EKYC250E□□472MM20S", "4700", "18×20", "0.037", "2700"),
    ("EKYC101E□□101MJ16S", "100", "10×16", "0.10", "1570"),
    ("EKYC250E□□512ML25S", "5100", "16×25", "0.031", "3240"),
    ("EKYC101E□□151MJ20S", "150", "10×20", "0.065", "1940"),
    ("EKYC250E□□622ML30S", "6200", "16×30", "0.025", "3580"),
    ("EKYC101E□□221MK20S", "220", "12.5×20", "0.050", "2150"),
    ("EKYC250E□□622MM25S", "6200", "18×25", "0.030", "3350"),
    ("EKYC101E□□331MK25S", "330", "12.5×25", "0.037", "2820"),
    ("EKYC250E□□822MM30S", "8200", "18×30", "0.024", "3710"),
    ("EKYC101E□□391MK30S", "390", "12.5×30", "0.029", "3120"),
    ("EKYC350E□□391MJC5S", "390", "10×12.5", "0.14", "1120"),
    ("EKYC101E□□391ML20S", "390", "16×20", "0.038", "2530"),
    ("EKYC350E□□561MJ16S", "560", "10×16", "0.10", "1570"),
    ("EKYC101E□□471MK35S", "470", "12.5×35", "0.025", "3300"),
    ("EKYC350E□□821MJ20S", "820", "10×20", "0.065", "1940"),
    ("EKYC101E□□561MK40S", "560", "12.5×40", "0.021", "3600"),
    ("EKYC350E□□132MK20S", "1300", "12.5×20", "0.050", "2150"),
    ("EKYC101E□□561ML25S", "560", "16×25", "0.031", "3240"),
    ("EKYC350E□□182MK25S", "1800", "12.5×25", "0.037", "2820"),
    ("EKYC101E□□561MM20S", "560", "18×20", "0.037", "2700"),
    ("EKYC350E□□222ML20S", "2200", "16×20", "0.038", "2530"),
    ("EKYC101E□□681ML30S", "680", "16×30", "0.025", "3580"),
    ("EKYC350E□□242MK30S", "2400", "12.5×30", "0.029", "3120"),
    ("EKYC101E□□821ML35S", "820", "16×35", "0.022", "3800"),
    ("EKYC350E□□302MM20S", "3000", "18×20", "0.037", "2700"),
    ("EKYC101E□□821MM25S", "820", "18×25", "0.030", "3350"),
    ("EKYC350E□□332ML25S", "3300", "16×25", "0.031", "3240"),
    ("EKYC101E□□102MM30S", "1000", "18×30", "0.024", "3700"),
    ("EKYC350E□□392ML30S", "3900", "16×30", "0.025", "3580"),
    ("EKYC101E□□122ML40S", "1200", "16×40", "0.018", "4100"),
    ("EKYC350E□□432MM25S", "4300", "18×25", "0.030", "3350"),
    ("EKYC101E□□122MM35S", "1200", "18×35", "0.021", "4000"),
    ("EKYC350E□□512MM30S", "5100", "18×30", "0.024", "3710"),
    ("EKYC101E□□152MM40S", "1500", "18×40", "0.017", "4300"),
    ("EKYC500E□□181MJC5S", "180", "10×12.5", "0.14", "1120"),
    ("EKYC121E□□820MJ20S", "82", "10×20", "0.53", "1590"),
    ("EKYC500E□□301MJ16S", "300", "10×16", "0.10", "1570"),
    ("EKYC121E□□121MK20S", "120", "12.5×20", "0.29", "2090"),
    ("EKYC500E□□431MJ20S", "430", "10×20", "0.065", "1940"),
    ("EKYC121E□□181MK25S", "180", "12.5×25", "0.21", "2590"),
    ("EKYC500E□□681MK20S", "680", "12.5×20", "0.050", "2150"),
    ("EKYC121E□□221MK30S", "220", "12.5×30", "0.16", "3030"),
    ("EKYC500E□□911MK25S", "910", "12.5×25", "0.037", "2820"),
    ("EKYC121E□□221ML20S", "220", "16×20", "0.19", "2150"),
    ("EKYC500E□□122ML20S", "1200", "16×20", "0.038", "2530"),
    ("EKYC121E□□271MK35S", "270", "12.5×35", "0.15", "3330"),
    ("EKYC500E□□132MK30S", "1300", "12.5×30", "0.029", "3120"),
    ("EKYC121E□□271MM20S", "270", "18×20", "0.15", "2530"),
    ("EKYC500E□□152MM20S", "1500", "18×20", "0.037", "2700"),
    ("EKYC121E□□331MK40S", "330", "12.5×40", "0.12", "3840"),
    ("EKYC500E□□162ML25S", "1600", "16×25", "0.031", "3240"),
    ("EKYC121E□□331ML25S", "330", "16×25", "0.14", "2730"),
    ("EKYC500E□□202ML30S", "2000", "16×30", "0.025", "3580"),
    ("EKYC121E□□391ML30S", "390", "16×30", "0.11", "3200"),
    ("EKYC500E□□222MM25S", "2200", "18×25", "0.030", "3350"),
    ("EKYC121E□□391MM25S", "390", "18×25", "0.11", "3120"),
    ("EKYC500E□□272MM30S", "2700", "18×30", "0.024", "3710"),
    ("EKYC121E□□471ML35S", "470", "16×35", "0.10", "3470"),
    ("EKYC630E□□151MJC5S", "150", "10×12.5", "0.14", "1120"),
    ("EKYC121E□□511MM30S", "510", "18×30", "0.090", "3620"),
    ("EKYC630E□□221MJ16S", "220", "10×16", "0.10", "1570"),
    ("EKYC121E□□561ML40S", "560", "16×40", "0.080", "3930"),
    ("EKYC630E□□331MJ20S", "330", "10×20", "0.065", "1940"),
    ("EKYC121E□□621MM35S", "620", "18×35", "0.080", "3940"),
    ("EKYC630E□□471MK20S", "470", "12.5×20", "0.050", "2150"),
    ("EKYC121E□□821MM40S", "820", "18×40", "0.060", "4520"),
    ("EKYC630E□□681MK25S", "680", "12.5×25", "0.037", "2820"),
    ("EKYC630E□□821ML20S", "820", "16×20", "0.038", "2530"),
    ("EKYC630E□□911MK30S", "910", "12.5×30", "0.029", "3120"),
    ("EKYC630E□□102MK35S", "1000", "12.5×35", "0.025", "3300"),
    ("EKYC630E□□122ML25S", "1200", "16×25", "0.031", "3240"),
    ("EKYC630E□□122MM20S", "1200", "18×20", "0.037", "2700"),
    ("EKYC630E□□132MK40S", "1300", "12.5×40", "0.021", "3600"),
    ("EKYC630E□□152ML30S", "1500", "16×30", "0.025", "3580"),
    ("EKYC630E□□162MM25S", "1600", "18×25", "0.030", "3350"),
    ("EKYC630E□□182ML35S", "1800", "16×35", "0.022", "3800"),
    ("EKYC630E□□202MM30S", "2000", "18×30", "0.024", "3700"),
    ("EKYC630E□□242ML40S", "2400", "16×40", "0.018", "4100"),
    ("EKYC630E□□242MM35S", "2400", "18×35", "0.021", "4000"),
    ("EKYC630E□□332MM40S", "3300", "18×40", "0.017", "4300"),
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
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


def voltage(pn):
    c = pn[4:7]               # EKYC[XYZ]E... -> XY * 10^Z volts
    return int(c[:2]) * (10 ** int(c[2]))


def row(pn_t, cap, case, esr, ripple):
    mpn = pn_t.replace("\u25a1\u25a1", "LL")
    v = voltage(pn_t)
    dia, length = (float(x) for x in case.split("\u00d7"))
    lead, footprint = CASE[dia]
    rec = {
        "unique_id": f"Nippon_Chemi-Con-{mpn}",
        "part_locator": f"cap-elec-{cap}uf-{v}v-radial-d{dia:g}",
        "mpn": mpn, "manufacturer": MANUFACTURER, "package": "Radial",
        "value": f"{cap}\u00b5F",  # voltage shown via the separate (visible) Voltage Rating field
        "description": (f"Nippon Chemi-Con KYC {cap}\u00b5F {v}V \u00b120% low-ESR "
                        f"aluminum electrolytic, radial THT, {dia:g}\u00d7{length:g}mm"),
        "datasheet": DATASHEET, "manufacturer_link": "https://www.chemi-con.com",
        "kicad_symbol": SYMBOL_OVERRIDES.get(mpn, SYMBOL),
        "kicad_footprint": FOOTPRINT_OVERRIDES.get(mpn, footprint),
        "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
        "keywords": "capacitor,electrolytic,low-esr", "pin_count": "2",
        "temp_operating_min": -40.0, "temp_operating_max": 105.0,
        "capacitance": f"{cap}\u00b5F", "tolerance": "20%", "voltage_rating": f"{v}V",
        "esr_ohm": f"{esr}\u03a9", "ripple_current_ma": f"{ripple}mA",
        "diameter_mm": dia, "length_mm": length, "lead_spacing_mm": lead,
        "endurance_hours": "3000-5000h@105\u00b0C", "low_esr": "yes", "polarized": "yes",
    }
    vals = ", ".join(sql(rec[c]) for c in COLS)
    return f"INSERT INTO capacitors_electrolytic_th ({', '.join(COLS)}) VALUES ({vals});"


def main():
    lines = [
        "-- Terra EDA Library - Nippon Chemi-Con KYC aluminum electrolytic family",
        f"-- Datasheet-driven (CAT. E1001A). Generated by {CREATED_BY}.",
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
