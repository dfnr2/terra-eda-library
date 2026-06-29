#!/usr/bin/env python3
"""TDK FG-series dipped radial-lead MLCC generator (capacitors_th).

Datasheet-driven (parked at datasheets/tdk/fg-series-leaded-mlcc.pdf, Nov 2024):
the FG catalog transcribed from the catalog tables into fg_catalog.json -- only the
C0G and X7R dielectrics and only parts NOT marked "not recommended for new designs".
Each part's exact orderable MPN, capacitance, tolerance and rated voltage come
straight from that table; this script formats them into rows and attaches the
type's geometry + footprint.

Footprints: the FG dipped-MLCC bodies have no exact stock KiCad match, so each FG
type maps to the nearest stock Capacitor_THT:C_Disc footprint at the correct lead
pitch (holes + 2.5/5.0mm pitch exact; body silhouette approximate). FG16/FG11
(5.5mm wide at 2.5mm pitch) have no stock disc that wide -> nearest is undersized;
these two especially want a custom terra footprint later (see TECH_DEBT/plan).

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import json
import re
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("capacitors_th_generated_300_tdk_fg.sql")
CATALOG_FILE = Path(__file__).with_name("fg_catalog.json")
CREATED_BY = Path(__file__).name

MANUFACTURER = "TDK"
DATASHEET = "${TERRA_EDA_LIB}/datasheets/tdk/fg-series-leaded-mlcc.pdf"
MANUFACTURER_LINK = "https://product.tdk.com/en/search/capacitor/ceramic/mlcc/list?series_name=FG%20Series"
SYMBOL = "Device:C"

# ---------------------------------------------------------------- user config
# Enable/disable dielectrics (the catalog only carries C0G + X7R this round).
DIELECTRICS = {"C0G": "yes", "X7R": "yes", "X5R": "no", "X7S": "no", "X7T": "no"}
# Also emit the taping variant (MPN ...6) alongside the bulk part (MPN ...0)?
INCLUDE_TAPING = "no"

# -------------------------------------------------- per-type geometry + footprint
# type: (body_w_mm, body_h_mm, body_t_mm, lead_pitch_mm, kicad_footprint)
# Footprint = nearest stock C_Disc at the correct pitch (see module docstring).
TYPE_GEOM = {
    "FG28": (4.0, 5.5, 2.5, 5.0, "Capacitor_THT:C_Disc_D4.7mm_W2.5mm_P5.00mm"),
    "FG24": (4.5, 5.5, 3.0, 5.0, "Capacitor_THT:C_Disc_D5.1mm_W3.2mm_P5.00mm"),
    "FG26": (5.5, 6.0, 3.5, 5.0, "Capacitor_THT:C_Disc_D6.0mm_W4.4mm_P5.00mm"),
    "FG20": (5.5, 7.0, 4.0, 5.0, "Capacitor_THT:C_Disc_D6.0mm_W4.4mm_P5.00mm"),
    "FG22": (7.5, 8.5, 4.5, 5.0, "Capacitor_THT:C_Disc_D7.5mm_W4.4mm_P5.00mm"),
    "FG23": (8.5, 11.0, 5.5, 5.0, "Capacitor_THT:C_Disc_D9.0mm_W5.0mm_P5.00mm"),
    "FG18": (4.0, 5.5, 2.5, 2.5, "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"),
    "FG14": (4.5, 5.5, 3.0, 2.5, "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"),
    "FG16": (5.5, 6.0, 3.5, 2.5, "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"),  # undersized
    "FG11": (5.5, 7.0, 4.0, 2.5, "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"),  # undersized
}

# operating/storage temperature range by dielectric (deg C)
TEMP = {"C0G": (-55, 125), "X7R": (-55, 125), "X7S": (-55, 125),
        "X7T": (-55, 125), "X5R": (-55, 85)}
TEMP_SOLDERING = 260.0  # FG flow-soldering peak

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "rohs", "allow_substitution", "tracking", "source", "dump_priority", "tier",
    "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max",
    "temp_soldering", "voltage_rating_v", "tolerance", "cap_type", "dielectric_class",
    "polarized", "height_max_mm",
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def cap_to_pf(s):
    s = s.strip().replace("µ", "u").replace("μ", "u")
    m = re.match(r"([\d.]+)\s*(pf|nf|uf|f)\b", s, re.I)
    if not m:
        raise ValueError(f"unparseable capacitance: {s!r}")
    num, unit = float(m.group(1)), m.group(2).lower()
    return num * {"pf": 1, "nf": 1e3, "uf": 1e6, "f": 1e12}[unit]


def _fmt(v):
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def spice(s):
    """Capacitance string -> SPICE notation (100p, 2.2n, 1u)."""
    pf = cap_to_pf(s)
    if pf < 1000:
        return f"{_fmt(pf)}p"
    if pf < 1e6:
        return f"{_fmt(pf / 1e3)}n"
    return f"{_fmt(pf / 1e6)}u"


def readable(s):
    """Capacitance string -> human form (100pF, 2.2nF, 1µF)."""
    pf = cap_to_pf(s)
    if pf < 1000:
        return f"{_fmt(pf)}pF"
    if pf < 1e6:
        return f"{_fmt(pf / 1e3)}nF"
    return f"{_fmt(pf / 1e6)}µF"


def tol_slug(t):
    return (t.replace("±", "").replace("%", "pct").replace("pF", "pf")
             .replace(".", "p").strip().lower())


def row(p, mpn, pkg_note):
    diel = p["dielectric"]
    bw, bh, bt, pitch, footprint = TYPE_GEOM[p["type"]]
    v = int(p["voltage_v"])
    sp, rd, tol = spice(p["capacitance"]), readable(p["capacitance"]), p["tolerance"]
    tmin, tmax = TEMP[diel]
    rec = {
        "unique_id": f"{MANUFACTURER}-{mpn}",
        "part_locator": f"cap-mlcc-{diel.lower()}-{sp}-{tol_slug(tol)}-{v}v-th-p{pitch:g}",
        "mpn": mpn, "manufacturer": MANUFACTURER, "package": p["type"],
        "value": sp,
        "description": (f"MLCC TDK FG {diel} {rd} {tol} {v}V radial {pitch:g}mm{pkg_note}"),
        "datasheet": DATASHEET, "manufacturer_link": MANUFACTURER_LINK,
        "kicad_symbol": SYMBOL, "kicad_footprint": footprint,
        "rohs": "Yes", "allow_substitution": "Yes", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
        "keywords": f"capacitor,mlcc,ceramic,through-hole,radial,{diel.lower()}",
        "pin_count": "2",
        "temp_operating_min": float(tmin), "temp_operating_max": float(tmax),
        "temp_storage_min": float(tmin), "temp_storage_max": float(tmax),
        "temp_soldering": TEMP_SOLDERING,
        "voltage_rating_v": float(v), "tolerance": tol, "cap_type": "MLCC",
        "dielectric_class": diel, "polarized": "No", "height_max_mm": float(bh),
    }
    vals = ", ".join(sql(rec[c]) for c in COLS)
    return f"INSERT INTO capacitors_th ({', '.join(COLS)}) VALUES ({vals});"


def main():
    catalog = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    rows = []
    for p in catalog:
        if DIELECTRICS.get(p["dielectric"]) != "yes":
            continue
        if p["type"] not in TYPE_GEOM:
            continue
        rows.append(row(p, p["mpn"], ""))
        if INCLUDE_TAPING == "yes" and p["mpn"].endswith("0"):
            rows.append(row(p, p["mpn"][:-1] + "6", " (taping)"))

    lines = [
        "-- Terra EDA Library - TDK FG-series dipped radial-lead MLCC (capacitors_th)",
        f"-- Datasheet-driven from fg_catalog.json. Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    lines += rows
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} parts "
          f"(dielectrics: {[d for d, e in DIELECTRICS.items() if e == 'yes']})")


if __name__ == "__main__":
    main()
