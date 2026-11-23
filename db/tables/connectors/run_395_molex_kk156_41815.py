#!/usr/bin/env python3
"""Molex KK 156 PCB receptacles, series 41815: 3.96 mm (0.156"), 1 row, 2-15 circuits.

The card side of the 0.156" pin buses: OSI's 48-line bus (4 x 12, osiweb's replacement
list names 09-52-3121 right-angle and 09-52-3123 vertical, series 2145, now obsolete;
these are their 41815 successors) and SWTPC SS-50/SS-30 (the Corsham specification
names 09-48-2101). The receptacle takes 0.045" (1.14 mm) square or round pins, so it
mates with the TE MTA-156 round-post headers of run_390 and the KK 396 headers.

Sales drawing SDA-41815 (datasheets/molex/kk-156-41815-pcb-receptacle-sd.pdf, 11
sheets): three entry styles (right angle, top entry, bottom entry), each in several
terminal/plating/ramp builds, plus voided-circuit and hooks-removed variants. Generated
here: every **tin** build (197 = 1.52 um reflowed matte tin over nickel, P909 = 2.54
um tin) with **no voided circuits and hooks intact**, restricted to the codes listed at
Mouser on 2026-11-21 (141 of the 196 such codes; none flagged obsolete). Gold builds
are skipped by request.

Ratings, product specification PS-08-50-001 rev. U
(datasheets/molex/kk-396-product-spec-ps-08-50-001.pdf), which the drawing cites:
600 V (UL; CSA 250 V); current per circuit by style and terminal (top entry and
right angle 4.5 A brass / 5.0 A phosphor bronze, bottom entry 4.0 / 4.5 A);
operating -40 to +80 C with brass terminals, -40 to +105 C with phosphor bronze.
Polyester housing, UL94V-0, natural.

Footprints: KiCad has none for 41815, so this script writes them to
terra_footprints_connectors from the drawing's PCB layouts (component side), pin 1 at
the origin and the row along +x:
  - right angle: 1.52 mm holes on 3.96 mm; board edge 7.87 mm from the hole row on the
    mating side; housing 11.4 mm deep, overhanging the edge by 1.91 mm.
  - top entry: 1.52 mm holes; housing outline scaled from the drawing's dashed top
    view (approximate), mating axis 3.18 mm from the hole row.
  - bottom entry: 1.02 mm tail holes plus a 2.54 mm non-plated hole 3.35 mm away under
    each circuit for the mating pin to pass through the board; housing extent scaled
    from the side view (approximate).
Body width is the drawing's DIM A (n x 3.96 - 0.10 mm).

3D models (generated, tools/make_connector_models.py) are block approximations scaled
from the sheet-1 side views: right angle, housing 6.5 mm high with a skirt 3.3 mm down
past the board edge and the edge hook under the board; top entry, 10.7 mm tall body on
a 1.7 mm base with the hook; bottom entry, 11.5 mm tall on a 2.5 mm base. Tails 0.64
mm square, 3.68 / 3.05 / 3.18 mm below the board. Each part also has a per-pin symbol
row (`-pins`, _connkit.py).

Plan: plans/connectors-0156-bus.md. Generated output (dump_priority=0, source=NULL) is
not dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _conn156 import FP_LIB, PITCH, check_datasheets, footprint, line, write, write_footprint  # noqa: E402
from _connkit import numeric_pins_id, numeric_pins_symbol, pin_row, with_pins, write_symbols  # noqa: E402

OUTPUT_FILE = HERE / "connectors_generated_395_molex_kk156_41815.sql"
CREATED_BY = Path(__file__).name

DS = "${TERRA_EDA_LIB}/datasheets/molex"
DATASHEET = f"{DS}/kk-156-41815-pcb-receptacle-sd.pdf"
SPEC = f"{DS}/kk-396-product-spec-ps-08-50-001.pdf"

# Tin builds from SDA-41815 (no voids, hooks intact), Mouser-listed codes only.
# tail = drawing DIM C (mm); beam = "single" for the lower-insertion-force 4244
# terminal (drawing note 5).
VARIANTS = [
    dict(style="right-angle", ramp=True, terminal="phosphor bronze", plating="197", tail=3.68,  # 2144-BA-A1AA-197B
         mpns={2: "09-48-1024", 3: "09-48-1034", 4: "09-48-1044", 5: "09-48-1054", 6: "09-48-1064", 7: "09-48-1074", 8: "09-48-1084", 9: "09-48-1094", 10: "09-48-1104", 11: "09-48-1114", 12: "09-48-1124", 13: "09-48-1134", 14: "09-48-1144", 15: "09-48-1154"}),
    dict(style="right-angle", ramp=True, terminal="brass", plating="P909", tail=3.68,  # 2144-AA-A1AA-P909B
         mpns={2: "09-48-2021", 3: "09-48-2031", 4: "09-48-2041", 5: "09-48-2051", 6: "09-48-2061", 7: "09-48-2071", 8: "09-48-2081", 9: "09-48-2091", 10: "09-48-2101", 11: "09-48-2111", 12: "09-48-2121", 13: "09-48-2131", 14: "09-48-2141", 15: "09-48-2151"}),
    dict(style="right-angle", ramp=True, terminal="phosphor bronze", plating="P909", tail=3.68,  # 2144-BA-A1AA-P909B
         mpns={2: "09-48-2020", 3: "09-48-2030", 4: "09-48-2040", 5: "09-48-2050", 6: "09-48-2060", 7: "09-48-2070", 8: "09-48-2080", 9: "09-48-2090", 10: "09-48-2100", 11: "09-48-2110", 12: "09-48-2120", 13: "09-48-2130", 14: "09-48-2140", 15: "09-48-2150"}),
    dict(style="right-angle", ramp=True, terminal="phosphor bronze", plating="197", tail=3.68, beam="single",  # 4244-A-197A
         mpns={3: "09-48-1033", 6: "09-48-1063", 8: "09-48-1083", 10: "09-48-1103", 12: "09-48-1123"}),
    dict(style="right-angle", ramp=False, terminal="phosphor bronze", plating="197", tail=3.68,  # 2144-BA-A1AA-197B
         mpns={2: "41815-0630", 8: "41815-0636"}),
    dict(style="top-entry", ramp=True, terminal="phosphor bronze", plating="197", tail=3.05,  # 2144-BA-A1AA-197B
         mpns={2: "09-48-4028", 3: "09-48-4038", 4: "09-48-4048", 5: "09-48-4058", 6: "09-48-4068", 7: "09-48-4078", 8: "09-48-4088", 9: "09-48-4098", 10: "09-48-4108", 11: "09-48-4118", 12: "09-48-4128", 13: "09-48-4138", 14: "09-48-4148", 15: "09-48-4158"}),
    dict(style="top-entry", ramp=True, terminal="brass", plating="P909", tail=3.05,  # 2144-AA-A1AA-P909B
         mpns={2: "09-48-2023", 3: "09-48-2033", 4: "09-48-2043", 5: "09-48-2053", 6: "09-48-2063", 7: "09-48-2073", 8: "09-48-2083", 9: "09-48-2093", 10: "09-48-2103", 11: "09-48-2113", 12: "09-48-2123", 13: "09-48-2133", 14: "09-48-2143", 15: "09-48-2153"}),
    dict(style="top-entry", ramp=True, terminal="phosphor bronze", plating="P909", tail=3.05,  # 2144-BA-A1AA-P909B
         mpns={2: "09-48-2028", 3: "09-48-2038", 4: "09-48-2048", 5: "09-48-2058", 6: "09-48-2068", 7: "09-48-2078", 8: "09-48-2088", 9: "09-48-2098", 10: "09-48-2108", 11: "09-48-2118", 12: "09-48-2128", 13: "09-48-2138", 14: "09-48-2148", 15: "09-48-2158"}),
    dict(style="top-entry", ramp=False, terminal="brass", plating="P909", tail=3.05,  # 2144-AA-A1AA-P909B
         mpns={4: "09-48-2047", 10: "09-48-2107"}),
    dict(style="bottom-entry", ramp=True, terminal="phosphor bronze", plating="197", tail=3.18,  # 6298-1-197
         mpns={2: "09-48-4029", 3: "09-48-4039", 4: "09-48-4049", 5: "09-48-4059", 6: "09-48-4069", 7: "09-48-4079", 8: "09-48-4089", 9: "09-48-4099", 10: "09-48-4109", 11: "09-48-4119", 12: "09-48-4129", 13: "09-48-4139", 14: "09-48-4149", 15: "09-48-4159"}),
    dict(style="bottom-entry", ramp=True, terminal="brass", plating="P909", tail=3.18,  # 2188-1-P909
         mpns={3: "09-48-2032", 4: "09-48-2042", 5: "09-48-2052", 6: "09-48-2062", 7: "09-48-2072", 8: "09-48-2082", 9: "09-48-2092", 10: "09-48-2102", 11: "09-48-2112", 12: "09-48-2122", 13: "09-48-2132", 14: "09-48-2142", 15: "09-48-2152"}),
    dict(style="bottom-entry", ramp=True, terminal="phosphor bronze", plating="P909", tail=3.18,  # 6298-1-P909
         mpns={2: "09-48-2029", 3: "09-48-2039", 4: "09-48-2049", 5: "09-48-2059", 6: "09-48-2069", 7: "09-48-2079", 8: "09-48-2089", 9: "09-48-2099", 10: "09-48-2109", 11: "09-48-2119", 12: "09-48-2129", 13: "09-48-2139", 14: "09-48-2149", 15: "09-48-2159"}),
    dict(style="bottom-entry", ramp=True, terminal="phosphor bronze", plating="197", tail=4.06,  # 6298-197
         mpns={4: "09-48-4041", 6: "09-48-4061", 8: "09-48-4081", 10: "09-48-4101", 12: "09-48-4121"}),
    dict(style="bottom-entry", ramp=False, terminal="phosphor bronze", plating="197", tail=3.18,  # 6298-1-197
         mpns={2: "41815-0564", 3: "41815-0565"}),
]

PLATING = {"197": "1.52um matte tin over nickel", "P909": "2.54um tin"}

# PS-08-50-001 section 4.2b: amps per circuit by style, (brass, phosphor bronze).
CURRENT = {"right-angle": (4.5, 5.0), "top-entry": (4.5, 5.0), "bottom-entry": (4.0, 4.5)}
# PS-08-50-001 section 4.3: operating temperature by terminal material.
TEMP = {"brass": (-40.0, 80.0), "phosphor bronze": (-40.0, 105.0)}

# style -> (KiCad name suffix, footprint builder key)
FP_STYLE = {"right-angle": "Horizontal", "top-entry": "Vertical",
            "bottom-entry": "Vertical_BottomEntry"}

FAMILY = {
    "connector_category": "board-to-board", "connector_family": "Molex KK 396",
    "connector_series": "41815", "connector_type": "receptacle",
    "rows": 1, "pitch_mm": PITCH, "termination_type": "Through Hole", "gender": "female",
    "shielding": "unshielded", "color": "natural", "voltage_rating": 600.0,
    "signal_type": "mixed", "flammability_rating": "UL94-V0",
    "mating_family": ("0.156in (3.96mm) headers with 0.045in square or round pins: "
                      "TE MTA-156 640384 (round post), Molex KK 396 41771/41791"),
    "mates_with": "TE 640384 or Molex 41791/41771 header, same circuit count",
}


def fp_name(style, n):
    return f"Molex_KK-156_41815_1x{n:02d}_P3.96mm_{FP_STYLE[style]}"


def footprint_text(style, n):
    a = n * PITCH - 0.10                      # drawing DIM A
    mid = (n - 1) * PITCH / 2
    x0, x1 = mid - a / 2, mid + a / 2
    descr = (f"Molex KK 156 PCB receptacle 41815, {style}, 1x{n:02d}, 3.96mm pitch "
             f"(Molex SDA-41815)")
    tags = f"connector Molex KK 156 KK 396 41815 receptacle {style} 3.96mm 0.156in"
    if style == "right-angle":
        edge = 7.87
        body = (x0, edge + 1.91 - 11.4, x1, edge + 1.91)
        extra = (line(x0 - 1.0, edge, x1 + 1.0, edge, "F.Fab", 0.1)
                 + f'  (fp_text user "board edge" (at {mid:.3f} {edge - 0.8:.3f}) '
                   f'(layer "F.Fab")\n    (effects (font (size 0.8 0.8) (thickness 0.12)))\n  )\n')
        return footprint(fp_name(style, n), descr, tags, n, pad_size=2.3, drill=1.55,
                         body=body, courtyard=_grow(body), extra=extra)
    if style == "top-entry":
        body = (x0, -6.2, x1, 5.3)
        return footprint(fp_name(style, n), descr, tags, n, pad_size=2.3, drill=1.55,
                         body=body, courtyard=_grow(body))
    body = (x0, -5.9, x1, 6.75)
    return footprint(fp_name(style, n), descr, tags, n, pad_size=1.8, drill=1.05,
                     body=body, courtyard=_grow(body), npth_offset_y=3.35, npth_drill=2.55)


TAIL_W = 0.64
TAIL = {"right-angle": 3.68, "top-entry": 3.05, "bottom-entry": 3.18}


def model_specs():
    """Block models scaled from SDA-41815 sheet 1 (approximate, see docstring)."""
    specs = {}
    styles_n = {(v["style"], n) for v in VARIANTS for n in v["mpns"]}
    for style, n in sorted(styles_n):
        a = n * PITCH - 0.10
        mid = (n - 1) * PITCH / 2
        x0, x1 = mid - a / 2, mid + a / 2
        if style == "right-angle":
            edge = 7.87
            spec = [("box", "natural", x0, -1.62, 0, x1, edge + 1.91, 6.5),
                    ("box", "natural", x0, edge, -3.3, x1, edge + 1.91, 0),
                    ("box", "natural", x0, 5.5, -2.6, x1, edge, -1.6)]
        elif style == "top-entry":
            spec = [("box", "natural", x0, -6.1, 0, x1, 4.6, 1.7),
                    ("box", "natural", x0, -5.1, 0, x1, 0.9, 10.7),
                    ("box", "natural", x0, 0.9, 8.9, x1, 4.6, 10.7)]
        else:
            spec = [("box", "natural", x0, -5.2, 0, x1, 6.6, 2.5),
                    ("box", "natural", x0, -1.2, 0, x1, 5.2, 11.5),
                    ("box", "natural", x0, -5.2, 2.2, x1, -1.2, 4.9)]
        spec += pin_row("tin", n, PITCH, 0, -TAIL[style], 0.5, TAIL_W)
        specs[fp_name(style, n)] = spec
    return specs


def _grow(r, g=0.5):
    return (r[0] - g, r[1] - g, r[2] + g, r[3] + g)


def catalog(mpn):
    """Molex catalog number: 09-48-2121 -> 0009482121, 41815-0564 -> 0418150564."""
    digits = mpn.replace("-", "")
    return digits.rjust(10, "0")


def parts():
    for v in VARIANTS:
        brass = v["terminal"] == "brass"
        current = CURRENT[v["style"]][0 if brass else 1]
        tmin, tmax = TEMP[v["terminal"]]
        ramp_txt = "locking ramp" if v["ramp"] else "no ramp"
        beam = ", single-beam contact" if v.get("beam") == "single" else ""
        for n, mpn in v["mpns"].items():
            cat = catalog(mpn)
            yield {
                **FAMILY,
                "unique_id": f"Molex-{mpn}",
                "part_locator": f"conn-receptacle-{n}pos-3.96mm-1row-th-{v['style']}-tin",
                "mpn": mpn, "manufacturer": "Molex", "value": mpn,
                "description": (
                    f"Molex KK 156 41815 PCB receptacle {mpn}, 3.96mm pitch, 1x{n:02d}, "
                    f"{v['style']}, {ramp_txt}, {v['terminal']}{beam}, "
                    f"tin plating ({PLATING[v['plating']]}), {v['tail']}mm tail, "
                    "for 0.045in square or round pins, through-hole"),
                "datasheet": DATASHEET,
                "manufacturer_link": f"https://www.molex.com/en-us/products/part-detail/{cat}",
                "kicad_symbol": f"Connector_Generic:Conn_01x{n:02d}",
                "kicad_footprint": f"{FP_LIB}:{fp_name(v['style'], n)}",
                "lifecycle_status": "Active", "rohs": "Yes",
                "allow_substitution": "No", "tracking": "No",
                "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
                "keywords": (
                    f"connector,receptacle,socket,molex,kk156,kk 156,kk396,kk 396,41815,"
                    f"{mpn},{cat},3.96mm,0.156in,{v['style']},{n}-pin,round pin,bus,"
                    "card edge socket,SWTPC,SS-50,SS-30,OSI,vintage"),
                "pin_count": str(n), "positions": n, "orientation": v["style"],
                "polarized": "yes" if v["ramp"] else "no",
                "keying_detail": ("locking ramp engages the header's friction lock"
                                  if v["ramp"] else "none"),
                "locking_mechanism": "friction" if v["ramp"] else "none",
                "current_rating": current,
                "temp_operating_min": tmin, "temp_operating_max": tmax,
            }


def main():
    check_datasheets([DATASHEET, SPEC])
    rows = list(parts())
    for style, n in sorted({(r["orientation"], r["positions"]) for r in rows}):
        write_footprint(fp_name(style, n), footprint_text(style, n))
    write_symbols([numeric_pins_symbol(n) for n in sorted({r["positions"] for r in rows})])
    rows = with_pins(rows, lambda r: numeric_pins_id(r["positions"]))
    write(OUTPUT_FILE, "Molex KK 156 41815 PCB receptacles", CREATED_BY, rows)


if __name__ == "__main__":
    main()
