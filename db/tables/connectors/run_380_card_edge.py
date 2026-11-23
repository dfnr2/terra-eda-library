#!/usr/bin/env python3
"""EDAC card-edge sockets for vintage buses: S-100, Apple II, KIM-1/AIM-65/Apple I, 0.156".

Dual-row, vertical, PC-tail (contact code 520) EDAC sockets. Plan:
plans/connectors-card-edge.md. Drawings are EDAC's ordering guides
(datasheets/edac/edac-*-ordering-guide.pdf):

  - 346 (green diallyl phthalate) / 396 (black thermoplastic), 0.125" (3.175 mm) pitch,
    0.250" (6.35 mm) rows, 0.600" insulator: the **S-100** (IEEE-696) motherboard
    socket. s100computers.com names 346-100-520-202 (Mouser 587-346-100); Herb Johnson
    (retrotechnology.com/herbs_stuff/s100_conn.html) also names 396-100-520-202.
  - 345 (green) / 395 (black), 0.100" (2.54 mm) pitch, 0.200" (5.08 mm) rows, 0.600"
    insulator: the **Apple II** peripheral slot. applefritter.com/node/32398 names
    345-050-520-202 (green with lugs, original) and 395-050-520-201 (black, no lugs, ][+).
  - 305 (green) / 355 (black), 0.156" (3.96 mm) pitch, 0.140" (3.56 mm) rows, 0.470"
    insulator, and 307 / 357, 0.200" (5.08 mm) rows, 0.473": the **KIM-1** application
    and expansion connectors (the wfd3 KIM-1 breakout names EDAC 305-044), the AIM-65
    J1/J3 and Apple I expansion connectors (same 2x22 0.156" edge), and generic 0.156"
    card edges in the sizes the drawings list.

Pad names follow the machine, not the socket's moulded markings:
  - S-100: 1-50 on one row, 51-100 on the other, pin 1 facing 51 (both +8 V).
  - Apple II: 1-25 on one row, 26-50 on the other, pin 1 facing 50 (I/O SELECT / +12 V).
  - 0.156", up to 22 per row: 1-22 facing A-Z without G, I, O, Q (KIM-1, AIM-65 and the
    existing EDAC 307 footprint). Over 22 per row the letters run out, so those sizes are
    numbered 1-N facing N+1-2N.
Row 1 (pins 1..) is at y = 0, the facing row at y = +row pitch; pin 1 at the origin.

Mounting code 202: flush lugs with 0.128" (3.25 mm) holes on the row centreline at
DIM B; 201: no lugs. Footprint drill per the drawings' recommended holes (0.042"
+0.004 for 0.100"/0.125"; 0.050" +0.004 for 0.156"). Generated 3D models: insulator
with its card slot, lugs and tails, coloured green or black by series.

Ratings from each guide's specification table. Each part also gets a `-pins` per-pin
symbol row (_connkit.py). Generated output (dump_priority=0, source=NULL) is not dumped
to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _conn156 import FP_LIB, check_datasheets, line, npth, rect, tht_pad, write, write_footprint  # noqa: E402
from _connkit import (LETTERS, SYM_LIB, dual_column_symbol, edge_letter_pins_id,  # noqa: E402
                      edge_letter_pins_symbol, edge_letter_whole_name, edge_letter_whole_symbol,
                      model_sexpr, numeric_pins_id, numeric_pins_symbol, with_pins, write_symbols)

OUTPUT_FILE = HERE / "connectors_generated_380_card_edge.sql"
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets/edac"
IN = 25.4

# Per-series geometry and ratings, from the ordering guides. a/b/c/d: overall length,
# mounting-hole centres, body length and card-slot length as (per-position mm, constant
# mm) for N positions per row.
_0125 = dict(pitch=0.125 * IN, label="3.175", row=0.250 * IN, depth=9.40, height=15.24, slot=8.38,
             lug_h=6.35, a=(3.175, 20.575), b=(3.175, 13.845), c=(3.175, 7.235),
             d=(3.175, 3.175), drill=1.1, pad=1.8, tail=4.45, tail_w=0.64,
             current=3.0, withstand=1500.0, datasheet=f"{DS}/edac-346-396-card-edge-0125-ordering-guide.pdf")
_0100 = dict(pitch=0.100 * IN, label="2.54", row=0.200 * IN, depth=9.40, height=15.24, slot=8.38,
             lug_h=6.35, a=(2.54, 21.21), b=(2.54, 14.61), c=(2.54, 6.60),
             d=(2.54, 2.54), drill=1.1, pad=1.7, tail=4.45, tail_w=0.6,
             current=3.0, withstand=1200.0, datasheet=f"{DS}/edac-345-395-card-edge-0100-ordering-guide.pdf")
_0156 = dict(pitch=0.156 * IN, label="3.96", depth=8.71, depth_wide=12.70, a=(3.9624, 23.02),
             b=(3.9624, 15.14), c=(3.9624, 7.88), d=(3.9624, 4.17), drill=1.3, pad=2.3,
             tail=5.41, tail_w=0.8, current=5.0, withstand=1800.0)
SERIES = {
    "346": dict(_0125, colour="green", material="diallyl phthalate, green"),
    "396": dict(_0125, colour="black", material="thermoplastic, black"),
    "345": dict(_0100, colour="green", material="thermoplastic polyester, green"),
    "395": dict(_0100, colour="black", material="thermoplastic polyester, black"),
    "305": dict(_0156, row=0.140 * IN, height=11.94, slot=7.50, lug_h=6.60, colour="green",
                material="thermoplastic polyester, green",
                datasheet=f"{DS}/edac-305-315-355-card-edge-0156-ordering-guide.pdf"),
    "355": dict(_0156, row=0.140 * IN, height=11.94, slot=7.50, lug_h=6.60, colour="black",
                material="thermoplastic polyester, black",
                datasheet=f"{DS}/edac-305-315-355-card-edge-0156-ordering-guide.pdf"),
    "307": dict(_0156, row=0.200 * IN, height=12.01, slot=7.62, lug_h=6.86, colour="green",
                material="thermoplastic polyester, green",
                datasheet=f"{DS}/edac-307-357-card-edge-0156-ordering-guide.pdf"),
    "357": dict(_0156, row=0.200 * IN, height=12.01, slot=7.62, lug_h=6.86, colour="black",
                material="thermoplastic polyester, black",
                datasheet=f"{DS}/edac-307-357-card-edge-0156-ordering-guide.pdf"),
}

# (series, positions per row, mounting code, numbering, machines)
S100 = "S-100 (IEEE-696) bus, Altair/IMSAI"
APPLE2 = "Apple II peripheral slot"
KIM = "KIM-1, AIM-65, Apple I expansion"
PARTS = [
    ("346", 50, "202", "s100", S100),
    ("396", 50, "202", "s100", S100),
    ("345", 25, "202", "apple2", APPLE2),
    ("395", 25, "201", "apple2", APPLE2),
    *[("305", n, "202", "edge", KIM if n == 22 else "")
      for n in (6, 10, 12, 15, 18, 22, 24, 25, 28, 30, 36, 43)],
    *[("355", n, "202", "edge", KIM if n == 22 else "")
      for n in (6, 10, 12, 15, 18, 22, 24, 25, 28, 30, 36, 43)],
    *[("307", n, "202", "edge", KIM if n == 22 else "")
      for n in (6, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 36, 43, 44)],
    *[("357", n, "202", "edge", KIM if n == 22 else "")
      for n in (6, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 36, 43, 44)],
]


def mpn_for(series, n, mount):
    return f"{series}-{2 * n:03d}-520-{mount}"


def numbering(scheme, n):
    """(row 1 pad names, facing row pad names), index i facing index i."""
    if scheme == "s100":
        return list(range(1, 51)), list(range(51, 101))
    if scheme == "apple2":
        return list(range(1, 26)), list(range(50, 25, -1))
    if n <= len(LETTERS):
        return list(range(1, n + 1)), LETTERS[:n]
    return list(range(1, n + 1)), list(range(n + 1, 2 * n + 1))


def whole_symbol(scheme, n):
    """(lib_id, (name, lines) to write or None)."""
    if scheme == "apple2":
        return "Connector_Generic:Conn_02x25_Counter_Clockwise", None
    if scheme == "edge" and n <= len(LETTERS):
        return f"{SYM_LIB}:{edge_letter_whole_name(n)}", edge_letter_whole_symbol(n)
    if n <= 40:
        return f"Connector_Generic:Conn_02x{n:02d}_Top_Bottom", None
    name = f"Conn_CardEdge_2x{n:02d}_TopBottom"
    left, right = numbering("s100" if scheme == "s100" else "edge", n)
    return f"{SYM_LIB}:{name}", (name, dual_column_symbol(
        name, left, right, f"Card-edge connector, 2x{n}, contacts 1-{n} facing {n + 1}-{2 * n}"))


def pins_symbol(scheme, n):
    """(lib_id, (name, lines))."""
    if scheme == "edge" and n <= len(LETTERS):
        return edge_letter_pins_id(n), edge_letter_pins_symbol(n)
    return numeric_pins_id(2 * n), numeric_pins_symbol(2 * n)


def fp_name(series, n, mount):
    s = SERIES[series]
    return f"EDAC_{mpn_for(series, n, mount)}_2x{n:02d}_P{s['label']}mm_Vertical"


def _dims(s, n):
    L = lambda k: s[k][0] * n + s[k][1]     # noqa: E731
    depth = s["depth_wide"] if n >= 28 and "depth_wide" in s else s["depth"]
    mid = (n - 1) * s["pitch"] / 2
    return mid, L("a"), L("b"), L("c"), L("d"), depth


def footprint_text(series, n, mount, scheme):
    s = SERIES[series]
    mid, a, b, c, d, depth = _dims(s, n)
    yc = s["row"] / 2
    lugs = mount != "201"
    x0, x1 = mid - (a if lugs else c) / 2, mid + (a if lugs else c) / 2
    y0, y1 = yc - depth / 2, yc + depth / 2
    row1, row2 = numbering(scheme, n)
    pads = "".join(tht_pad(p, i * s["pitch"], 0, s["pad"], s["drill"], first=(i == 0))
                   for i, p in enumerate(row1))
    pads += "".join(tht_pad(p, i * s["pitch"], s["row"], s["pad"], s["drill"])
                    for i, p in enumerate(row2))
    if lugs:
        pads += npth(mid - b / 2, yc, 3.25) + npth(mid + b / 2, yc, 3.25)
    name = fp_name(series, n, mount)
    g = 0.12
    fab = rect(x0, y0, x1, y1, "F.Fab", 0.1)
    if lugs:   # body ends inside the lugs
        fab += line(mid - c / 2, y0, mid - c / 2, y1, "F.Fab", 0.1)
        fab += line(mid + c / 2, y0, mid + c / 2, y1, "F.Fab", 0.1)
    marker = line(-s["pitch"] / 2, y0 - g - 0.5, s["pitch"] / 2, y0 - g - 0.5, "F.SilkS", 0.12)
    return (
        f'(footprint "{name}" (version 20211014) (generator terra)\n'
        f'  (layer "F.Cu")\n'
        f'  (descr "EDAC {series} card-edge socket {mpn_for(series, n, mount)}, 2x{n}, '
        f'{s["label"]}mm pitch, {s["row"]:.2f}mm rows (EDAC {series} ordering guide)")\n'
        f'  (tags "connector card edge EDAC {series} {2 * n} vertical")\n'
        f'  (attr through_hole)\n'
        f'  (fp_text reference "REF**" (at {mid:.3f} {y0 - 1.6:.3f}) (layer "F.SilkS")\n'
        f'    (effects (font (size 1 1) (thickness 0.15)))\n  )\n'
        f'  (fp_text value "{name}" (at {mid:.3f} {y1 + 1.2:.3f}) (layer "F.Fab")\n'
        f'    (effects (font (size 1 1) (thickness 0.15)))\n  )\n'
        f'  (fp_text user "${{REFERENCE}}" (at {mid:.3f} {yc:.3f}) (layer "F.Fab")\n'
        f'    (effects (font (size 1 1) (thickness 0.15)))\n  )\n'
        + fab
        + rect(x0 - g, y0 - g, x1 + g, y1 + g, "F.SilkS", 0.12)
        + marker
        + rect(x0 - 0.5, y0 - 0.5, x1 + 0.5, y1 + 0.5, "F.CrtYd", 0.05)
        + pads + model_sexpr(name) + ")\n")


def model_specs():
    specs = {}
    for series, n, mount, scheme, _ in PARTS:
        s = SERIES[series]
        mid, a, b, c, d, depth = _dims(s, n)
        yc, col, h = s["row"] / 2, s["colour"], s["height"]
        y0, y1 = yc - depth / 2, yc + depth / 2
        slot_w, floor = 2.0, h - s["slot"]
        spec = [
            ("box", col, mid - c / 2, y0, 0, mid + c / 2, y1, floor),               # floor
            ("box", col, mid - c / 2, y0, floor, mid + c / 2, yc - slot_w / 2, h),  # wall
            ("box", col, mid - c / 2, yc + slot_w / 2, floor, mid + c / 2, y1, h),  # wall
            ("box", col, mid - c / 2, yc - slot_w / 2, floor, mid - d / 2, yc + slot_w / 2, h),
            ("box", col, mid + d / 2, yc - slot_w / 2, floor, mid + c / 2, yc + slot_w / 2, h),
        ]
        if mount != "201":
            spec += [("box", col, mid - a / 2, y0, 0, mid - c / 2, y1, s["lug_h"]),
                     ("box", col, mid + c / 2, y0, 0, mid + a / 2, y1, s["lug_h"])]
        for row_y in (0, s["row"]):
            spec += [("pin", "tin", i * s["pitch"], row_y, -s["tail"], 0.5, s["tail_w"])
                     for i in range(n)]
        specs[fp_name(series, n, mount)] = spec
    return specs


FAMILY = {
    "connector_category": "board-to-board", "connector_type": "receptacle",
    "rows": 2, "orientation": "vertical", "termination_type": "Through Hole",
    "gender": "female", "polarized": "no",
    "keying_detail": "none moulded; EDAC in-contact or between-contact polarizing keys",
    "locking_mechanism": "none", "shielding": "unshielded",
    "contact_resistance_mohm": 10.0, "insulation_resistance_mohm": 5000.0,
    "signal_type": "mixed", "flammability_rating": "UL94-V0",
    "temp_operating_min": -40.0, "temp_operating_max": 105.0,
    "lifecycle_status": "Active", "rohs": "Yes",
    "allow_substitution": "No", "tracking": "No",
    "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
}

COLS_EXTRA = ["row_pitch_mm", "contact_resistance_mohm", "insulation_resistance_mohm",
              "dielectric_withstand_vrms"]


def parts():
    for series, n, mount, scheme, machines in PARTS:
        s = SERIES[series]
        mpn = mpn_for(series, n, mount)
        whole_id, _ = whole_symbol(scheme, n)
        lugs = ("flush lugs with 3.25mm holes" if mount == "202" else "no mounting lugs")
        use = f"; {machines}" if machines else ""
        yield {
            **FAMILY,
            "unique_id": f"EDAC-{mpn}",
            "part_locator": (f"conn-card-edge-{2 * n}pos-{s['label']}mm-2row-"
                             f"{s['row']:.2f}mm-th-vertical"),
            "mpn": mpn, "manufacturer": "EDAC", "value": mpn,
            "description": (
                f"EDAC {series} card-edge socket {mpn}, {2 * n} contacts (2x{n}), "
                f"{s['label']}mm pitch, {s['row']:.2f}mm rows, vertical PC tail "
                f"{s['tail']}mm, {s['material']}, gold contact area, {lugs}, for 1.57mm "
                f"cards{use}"),
            "datasheet": s["datasheet"],
            "manufacturer_link": f"https://edac.net/series/{series}",
            "kicad_symbol": whole_id,
            "kicad_footprint": f"{FP_LIB}:{fp_name(series, n, mount)}",
            "keywords": (
                f"connector,card edge,edge connector,socket,edac,{series},{mpn},"
                f"{s['label']}mm,{2 * n}-pin,2x{n},vintage"
                + (f",{machines}" if machines else "")),
            "pin_count": str(2 * n), "positions": 2 * n,
            "connector_family": f"EDAC {series} card edge", "connector_series": series,
            "pitch_mm": round(s["pitch"], 3), "row_pitch_mm": round(s["row"], 3),
            "color": s["colour"], "current_rating": s["current"],
            "dielectric_withstand_vrms": s["withstand"],
            "mating_family": f"1.57mm (0.062in) PCB edge fingers on {s['label']}mm centres",
            "mates_with": f"card with 2x{n} gold fingers, {s['label']}mm pitch",
        }


def main():
    check_datasheets(sorted({s["datasheet"] for s in SERIES.values()}))
    symbols, pins_ids = {}, {}
    for series, n, mount, scheme, _ in PARTS:
        write_footprint(fp_name(series, n, mount), footprint_text(series, n, mount, scheme))
        _, whole = whole_symbol(scheme, n)
        if whole:
            symbols[whole[0]] = whole[1]
        pid, pins = pins_symbol(scheme, n)
        symbols[pins[0]] = pins[1]
        pins_ids[mpn_for(series, n, mount)] = pid
    write_symbols(sorted(symbols.items()))
    rows = with_pins(list(parts()), lambda r: pins_ids[r["mpn"]])
    write(OUTPUT_FILE, "EDAC card-edge sockets", CREATED_BY, rows, extra_cols=COLS_EXTRA)


if __name__ == "__main__":
    main()
