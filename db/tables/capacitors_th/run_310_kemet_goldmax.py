#!/usr/bin/env python3
"""KEMET Goldmax 300-series conformally coated radial MLCC generator (capacitors_th).

Datasheets (parked in datasheets/kemet/):
  KEM_C1049_GOLDMAX_C0G.pdf  C0G, 25-250 V, commercial grade (2025-08-05)
  KEM_C1093_GOLDMAX_X8L.pdf  X8L, 25-50 V, commercial + automotive grade (2026-01-29)

goldmax_catalog.json holds the capacitance-range waterfalls (availability per size group:
capacitance x voltage, plus the shoulder-bend flag for C330/C331/C340); regenerate it
with _goldmax_transcribe.py. The waterfall does not assign a style to a row: every style
in a group is orderable at every capacitance/voltage in it, so this script expands
style x capacitance x voltage x tolerance x grade x packaging.

MPN: C <style> C <cap code> <tol> <volt code> <diel code> 5 T A [9170] [C-spec]
  e.g. C315C101J3G5TA (100 pF C0G 25 V +/-5%, bulk) and the automotive tape-and-reel
  C320C475K3N5TA91707301 (4.7 uF X8L 25 V +/-10%).
Only the standard 100% matte-Sn lead finish (T) is listed; the SnPb (H) finish is leaded.

Footprints: one custom footprint per (lead spacing, body length, body thickness), written
to kicad_footprints/terra_footprints_capacitors_th.pretty by this script (pads at the
exact datasheet lead spacing; body outline from L and T). There is no 3D model.

Plan: plans/capacitors-th-kemet-goldmax.md. Generated output (dump_priority=0,
source=NULL) is not dumped to static SQL.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "capacitors_th_generated_310_kemet_goldmax.sql"
CATALOG_FILE = HERE / "goldmax_catalog.json"
FOOTPRINT_DIR = ROOT / "kicad_footprints" / "terra_footprints_capacitors_th.pretty"
FP_LIB = "terra_footprints_capacitors_th:"
CREATED_BY = Path(__file__).name

MANUFACTURER = "KEMET"
MANUFACTURER_LINK = "https://www.kemet.com"
SYMBOL = "Device:C"

# ---------------------------------------------------------------- user config
# Tolerances to emit. C0G: D (+/-0.5 pF) exists only below 10 pF; F/G/J/K only from 10 pF
# up (datasheet tolerance column). X8L: J/K/M at every value.
TOLERANCES = {
    "C0G": {"D": "yes", "F": "no", "G": "no", "J": "yes", "K": "no"},
    "X8L": {"J": "no", "K": "yes", "M": "no"},
}
# Grades: "automotive" adds the 9170 C-spec (AEC-Q200). Only the X8L sheet lists it.
GRADES = {"C0G": ["commercial"], "X8L": ["commercial", "automotive"]}
# Packaging C-specs per dielectric. "" = bulk bag. 7301 = 12" tape & reel (16 mm leads),
# 7303 = 12" T&R (18 mm leads), 7305/7317 = ammo pack (16/18 mm leads). Styles C321 and
# C331 are bulk only.
PACKAGING = {"C0G": [""], "X8L": ["", "7301"]}
BULK_ONLY_STYLES = {"321", "331"}

DIELECTRIC = {  # name: (MPN code, operating min C, operating max C)
    "C0G": ("G", -55, 125),
    "X8L": ("N", -55, 150),
}
DATASHEETS = {
    "C0G": "${TERRA_EDA_LIB}/datasheets/kemet/KEM_C1049_GOLDMAX_C0G.pdf",
    "X8L": "${TERRA_EDA_LIB}/datasheets/kemet/KEM_C1093_GOLDMAX_X8L.pdf",
}
TEMP_SOLDERING = 260.0   # wave-solder peak, datasheet soldering profile

TOL_TEXT = {"D": "±0.5pF", "F": "±1%", "G": "±2%", "J": "±5%", "K": "±10%", "M": "±20%"}
PACKAGING_TEXT = {"": "bulk", "7301": "12in tape and reel (16mm leads)",
                  "7303": "12in tape and reel (18mm leads)",
                  "7305": "ammo pack (16mm leads)", "7317": "ammo pack (18mm leads)"}
VOLT_CODE = {25: "3", 50: "5", 100: "1", 200: "2", 250: "A"}

# Style -> (lead spacing S, length L, height H, thickness T, lead dia F, lead form), mm,
# from the dimensions table (identical in both datasheets). Lead form is how the style is
# bent; C330/C331/C340 are shoulder-bend or straight per the waterfall's "*" marks.
STYLE_GEOM = {
    "315": (2.54, 3.81, 3.14, 2.54, 0.51, "straight"),
    "316": (2.54, 3.81, 5.84, 2.54, 0.51, "outside kink"),
    "324": (2.54, 5.08, 5.84, 3.18, 0.51, "snap-in type 2"),
    "320": (2.54, 5.08, 5.84, 3.18, 0.51, "straight"),
    "326": (2.54, 5.08, 7.62, 3.18, 0.51, "outside kink"),
    "317": (5.08, 3.81, 5.08, 2.54, 0.51, "shoulder bend (short)"),
    "318": (5.08, 3.81, 5.97, 2.54, 0.51, "shoulder bend (tall)"),
    "321": (6.35, 5.08, 6.60, 3.18, 0.51, "shoulder bend (short)"),
    "322": (5.08, 5.08, 6.60, 3.18, 0.51, "shoulder bend (short)"),
    "323": (5.08, 5.08, 7.62, 3.18, 0.51, "shoulder bend (tall)"),
    "325": (5.08, 5.08, 7.62, 3.18, 0.51, "snap-in type 1"),
    "328": (5.08, 5.08, 7.62, 3.18, 0.51, "shoulder bend (tall)"),
    "327": (5.08, 5.08, 8.13, 3.18, 0.51, "outside kink"),
    "330": (6.35, 7.11, 9.14, 4.07, 0.51, "shoulder bend (short) or straight"),
    "331": (6.35, 7.62, 9.14, 4.07, 0.51, "shoulder bend (short) or straight"),
    "333": (5.08, 7.11, 10.16, 4.07, 0.51, "inside kink"),
    "335": (5.08, 7.11, 10.16, 4.07, 0.51, "snap-in type 1"),
    "336": (5.08, 7.11, 10.16, 4.07, 0.51, "outside kink"),
    "340": (5.08, 7.36, 10.16, 4.07, 0.51, "shoulder bend (short) or straight"),
    "346": (5.08, 7.36, 10.16, 4.07, 0.51, "outside kink"),
    "350": (10.16, 8.38, 10.16, 5.08, 0.64, "shoulder bend (short)"),
    "356": (10.16, 8.38, 10.16, 5.08, 0.64, "outside kink"),
}
# Thickness maximum is 4.07 mm (not 3.18) for C32X values of 4.7 uF and up.
THICK_32X_BIG = 4.07
BIG_PF = 4.7e6

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "rohs", "allow_substitution", "tracking", "source", "dump_priority", "tier",
    "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max",
    "temp_soldering", "voltage_rating_v", "tolerance", "cap_type", "dielectric_class",
    "polarized", "aec_q_rating", "height_max_mm",
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def _fmt(v):
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def spice(pf):
    if pf < 1000:
        return f"{_fmt(pf)}p"
    if pf < 1e6:
        return f"{_fmt(pf / 1e3)}n"
    return f"{_fmt(pf / 1e6)}u"


def readable(pf):
    if pf < 1000:
        return f"{_fmt(pf)}pF"
    if pf < 1e6:
        return f"{_fmt(pf / 1e3)}nF"
    return f"{_fmt(pf / 1e6)}µF"


def tol_slug(t):
    return t.replace("±", "").replace("%", "pct").replace("pF", "pf").replace(".", "p").lower()


def body_thickness(style, pf):
    t = STYLE_GEOM[style][3]
    if style.startswith("32") and pf >= BIG_PF:
        return THICK_32X_BIG
    return t


def footprint_name(spacing, length, thick):
    return f"Kemet_Goldmax_L{length:g}mm_W{thick:g}mm_P{spacing:g}mm"


def footprint_text(name, spacing, length, thick, lead_d):
    """Two-pad radial footprint: pad 1 at the origin, pad 2 at +spacing; body L x T centred."""
    drill = round(lead_d + 0.3, 2)            # lead + 0.3 mm
    pad = round(drill + 0.8, 2)
    x0, x1 = spacing / 2 - length / 2, spacing / 2 + length / 2
    y = thick / 2
    sk = 0.12
    cy = max(y, pad / 2) + 0.25
    cx0, cx1 = min(x0, -pad / 2) - 0.25, max(x1, spacing + pad / 2) + 0.25

    def line(a, b, c, d, layer, w):
        return f'  (fp_line (start {a:g} {b:g}) (end {c:g} {d:g}) (layer "{layer}") (width {w})) \n'.rstrip(" \n") + "\n"

    def rect(ax, ay, bx, by, layer, w):
        return (line(ax, ay, bx, ay, layer, w) + line(bx, ay, bx, by, layer, w)
                + line(bx, by, ax, by, layer, w) + line(ax, by, ax, ay, layer, w))

    out = [f'(footprint "{name}" (version 20211014) (generator terra)\n',
           '  (layer "F.Cu")\n',
           f'  (descr "KEMET Goldmax 300 series radial MLCC, lead spacing {spacing:g} mm, '
           f'body {length:g} x {thick:g} mm (L x T max), lead dia {lead_d:g} mm")\n',
           '  (tags "capacitor radial MLCC KEMET Goldmax")\n',
           '  (attr through_hole)\n',
           f'  (fp_text reference "REF**" (at {spacing / 2:g} {-(cy + 0.9):g}) (layer "F.SilkS")\n'
           '    (effects (font (size 1 1) (thickness 0.15)))\n  )\n',
           f'  (fp_text value "{name}" (at {spacing / 2:g} {cy + 0.9:g}) (layer "F.Fab")\n'
           '    (effects (font (size 1 1) (thickness 0.15)))\n  )\n']
    out.append(rect(x0, -y, x1, y, "F.Fab", 0.1))
    # silkscreen: top/bottom edges always; end edges only where they clear the pads
    out.append(line(x0 - sk, -y - sk, x1 + sk, -y - sk, "F.SilkS", 0.12))
    out.append(line(x0 - sk, y + sk, x1 + sk, y + sk, "F.SilkS", 0.12))
    keep = pad / 2 + 0.2
    for ex in (x0 - sk, x1 + sk):
        if min(abs(ex), abs(ex - spacing)) > keep:
            out.append(line(ex, -y - sk, ex, y + sk, "F.SilkS", 0.12))
    out.append(rect(cx0, -cy, cx1, cy, "F.CrtYd", 0.05))
    out.append(f'  (pad "1" thru_hole rect (at 0 0) (size {pad:g} {pad:g}) (drill {drill:g}) (layers *.Cu *.Mask))\n')
    out.append(f'  (pad "2" thru_hole circle (at {spacing:g} 0) (size {pad:g} {pad:g}) (drill {drill:g}) (layers *.Cu *.Mask))\n')
    out.append(")\n")
    return "".join(out)


def expand(catalog):
    """Yield one dict per orderable part."""
    for grp in catalog:
        diel = grp["dielectric"]
        code_d, tmin, tmax = DIELECTRIC[diel]
        tols = [t for t, on in TOLERANCES[diel].items() if on.lower() == "yes"]
        for cap in grp["caps"]:
            pf = cap["pf"]
            if diel == "C0G":
                ctol = [t for t in tols if (t == "D") == (pf < 10)]
            else:
                ctol = tols
            for volt, star in cap["v"].items():
                volt = int(volt)
                for style in grp["styles"]:
                    if style not in STYLE_GEOM:
                        continue
                    for tol in ctol:
                        for grade in GRADES[diel]:
                            for pack in PACKAGING[diel]:
                                if pack and style in BULK_ONLY_STYLES:
                                    continue
                                cspec = ("9170" if grade == "automotive" else "") + pack
                                mpn = (f"C{style}C{cap['code']}{tol}{VOLT_CODE[volt]}{code_d}5TA{cspec}")
                                yield {
                                    "style": style, "diel": diel, "pf": pf, "volt": volt,
                                    "tol": tol, "grade": grade, "pack": pack, "mpn": mpn,
                                    "star": star, "tmin": tmin, "tmax": tmax,
                                    "cap_code": cap["code"],
                                }


def row(p, footprints):
    style, diel = p["style"], p["diel"]
    spacing, length, height, _, lead_d, form = STYLE_GEOM[style]
    thick = body_thickness(style, p["pf"])
    fp_name = footprint_name(spacing, length, thick)
    footprints[fp_name] = (spacing, length, thick, lead_d)
    if style in ("330", "331", "340"):
        form = "shoulder bend (short)" if p["star"] else "straight"
    sp, rd, tol_t, v = spice(p["pf"]), readable(p["pf"]), TOL_TEXT[p["tol"]], p["volt"]
    auto = p["grade"] == "automotive"
    note = f", {PACKAGING_TEXT[p['pack']]}" if p["pack"] else ""
    desc = (f"MLCC KEMET Goldmax C{style} {diel} {rd} {tol_t} {v}V radial {spacing:g}mm, "
            f"{form} leads, conformal coated{', automotive grade (AEC-Q200)' if auto else ''}{note}")
    rec = {
        "unique_id": f"{MANUFACTURER}-{p['mpn']}",
        "part_locator": f"cap-mlcc-{diel.lower()}-{sp}-{tol_slug(tol_t)}-{v}v-th-p{spacing:g}",
        "mpn": p["mpn"], "manufacturer": MANUFACTURER, "package": f"C{style}",
        "value": sp, "description": desc,
        "datasheet": DATASHEETS[diel], "manufacturer_link": MANUFACTURER_LINK,
        "kicad_symbol": SYMBOL, "kicad_footprint": FP_LIB + fp_name,
        "rohs": "Yes", "allow_substitution": "Yes", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
        "keywords": (f"capacitor,mlcc,ceramic,through-hole,radial,{diel.lower()},kemet,goldmax,"
                     f"c{style}" + (",automotive,aec-q200" if auto else "")),
        "pin_count": "2",
        "temp_operating_min": float(p["tmin"]), "temp_operating_max": float(p["tmax"]),
        "temp_storage_min": float(p["tmin"]), "temp_storage_max": float(p["tmax"]),
        "temp_soldering": TEMP_SOLDERING,
        "voltage_rating_v": float(v), "tolerance": tol_t, "cap_type": "MLCC",
        "dielectric_class": diel, "polarized": "No",
        "aec_q_rating": "AEC-Q200" if auto else None, "height_max_mm": float(height),
    }
    vals = ", ".join(sql(rec[c]) for c in COLS)
    return rec["unique_id"], f"INSERT INTO capacitors_th ({', '.join(COLS)}) VALUES ({vals});"


def decode_check(p):
    """Validate the MPN against the row it came from (capacitance code, tolerance, voltage)."""
    m = re.fullmatch(r"C(\d{3})C(\d{3})([DFGJKM])([3512A])([GN])5TA(9170)?(\d{4})?", p["mpn"])
    assert m, p["mpn"]
    sig, exp = int(m.group(2)[:2]), int(m.group(2)[2])
    assert abs((sig * 0.1 if exp == 9 else sig * 10 ** exp) - p["pf"]) < 1e-6, p["mpn"]
    assert m.group(3) == p["tol"] and m.group(1) == p["style"], p["mpn"]


def main():
    catalog = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
    footprints, rows, ids = {}, [], set()
    for p in expand(catalog):
        decode_check(p)
        uid, line = row(p, footprints)
        if uid in ids:
            raise SystemExit(f"duplicate unique_id: {uid}")
        ids.add(uid)
        rows.append(line)

    FOOTPRINT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (s, l, t, d) in sorted(footprints.items()):
        (FOOTPRINT_DIR / f"{name}.kicad_mod").write_text(footprint_text(name, s, l, t, d))

    lines = [
        "-- Terra EDA Library - KEMET Goldmax 300-series radial MLCC (capacitors_th)",
        f"-- Datasheet-driven from goldmax_catalog.json. Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "", "BEGIN TRANSACTION;", "", *rows, "", "COMMIT;", "",
    ]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} parts, {len(footprints)} footprints")
    for d in DATASHEETS.values():
        if not (ROOT / d.replace("${TERRA_EDA_LIB}/", "")).exists():
            print(f"WARNING: datasheet missing: {d}")


if __name__ == "__main__":
    main()
