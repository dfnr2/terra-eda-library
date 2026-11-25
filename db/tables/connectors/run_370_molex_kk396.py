#!/usr/bin/env python3
"""Molex KK 396 friction-lock headers: 3.96 mm (0.156"), single row, 2-18 circuits.

The SWTPC/S-100-era power and wire-to-board header, still in production.
  - series 41791, vertical: 26-60-40NN0 (engineering 41791-00NN), sales drawing
    SDA-41791-000 (datasheets/molex/kk-396-41791-vertical-header-sd.pdf)
  - series 41792, right-angle: 26-60-50NN0 (41792-00NN), sales drawing
    datasheets/molex/kk-396-41792-right-angle-header-sd.pdf
NN = circuits; the trailing 0 is tin plating (the drawings also list a 3 = second
plating, not generated). Molex's catalog number drops the dashes and adds a leading
00 (0026604020); the printed part number 26-60-4020 is the MPN, as distributors use.

Ratings from product specification PS-08-50-001 rev. U (2021-11-24,
datasheets/molex/kk-396-product-spec-ps-08-50-001.pdf): agency 600 V (UL) / 250 V
(CSA) and 7 A single circuit for both series; operating -40 to 80 C with brass pins
(the headers' pin material). Molex's part pages disagree (41791 page: 5.0 A / 600 V;
41792 page: 7.0 A / 250 V); the specification is used: 7.0 A, 600 V.

Mates with KK 396 crimp housings 2139, 3069, 41695 and 6442 (crimp terminals 2478,
2578, 2878) and the 41815 PCB connector, per the Molex part pages and the spec.

Lifecycle: all 34 codes Active at Molex and listed at Mouser, 2026-11-21.
Symbol Connector_Generic:Conn_01xNN, plus a per-pin symbol row (`-pins`, _connkit.py).

Footprints: KiCad's stock
Connector_Molex:Molex_KK-396_A-4179x-00NN_1xNN_P3.96mm_{Vertical,Horizontal}, but KiCad
ships no 3D models for them (their model paths point at STEPs that exist neither in
KiCad 10's packages3d nor upstream). So they are vendored, under the same names, into
terra_footprints_connectors with only the (model ...) block changed, pointing at a
generated model named after the footprint (model_specs below; built by
tools/make_connector_models.py). Pads, silk, fab and courtyard stay byte-identical to
KiCad's, pin 1 at the origin and the row along +x. The vendored files are committed;
rewrite them from the installed KiCad library with

    python3 run_370_molex_kk396.py --vendor-footprints

Model dimensions, from the sales drawings (mm; "scaled" = measured off the drawing):
  - pins 1.14 (0.045") square. Pin length L = M + 3.30 + P (41791: 18.29) or
    M + Y + bend (41792: 27.94); mating M = 11.43 beyond the housing face.
  - housing base 3.30 thick (drawing "3.30" / "(3.30)", seating face to mating face),
    DIM A = n x 3.96 - 0.15 long, 1.91 from the end pins' centres to the housing ends.
  - 10.01 across, pin centreline 5.11 from the plain face and 4.90 from the back wall's
    outer face; the wall is 11.33 high (from the seating face), ~1.0 thick (scaled;
    KiCad's fab outline gives 3.895 to 4.90) and runs between the end pins' centres
    (front view; KiCad's fab tab). Wall slots between circuits (note 9) are omitted.
  - friction-lock ramp on the wall's inner face, approximated as a box reaching to
    2.41 from the pin centreline (drawing "2.41") over 7.0-9.8 above the seating face
    (scaled: the band where the ramp stands out by more than half its depth).
  - 41791 vertical: seated on the board, pins z = -3.56 (tail P) to 3.30 + 11.43; the
    wall on +y, as KiCad's F.Fab draws it (body -5.11 to 3.895, wall tab to 4.90).
  - 41792 right-angle: the same housing on its side, plain face on the board, so the
    wall lies at z = 9.0-10.0 and the mating pins run along -y at z = 5.11. Tail at the
    pad (y = 0), P = 3.96 below the board top; seating face Y = 5.41 from the tail,
    mating face at y = -(5.41 + 3.30) = -8.71, which is where KiCad's F.Fab outline
    ends. KiCad's fab/courtyard do not include the wall and pins overhanging beyond
    that face (wall to y = -16.74, pin tips to -20.14, both above the board), and
    their back edge (y = +2.4) is clear of the housing; the pin bends are drawn square.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _conn156 import FP_DIR, FP_LIB  # noqa: E402
from _connkit import (MODEL_LIB, numeric_pins_id, numeric_pins_symbol, pin_row,  # noqa: E402
                      with_pins, write_symbols)
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "connectors_generated_370_molex_kk396.sql"
CREATED_BY = Path(__file__).name

CIRCUITS = range(2, 19)
DS = "${TERRA_EDA_LIB}/datasheets/molex"
MATING = ("Molex KK 396 crimp housings 2139, 3069, 41695, 6442 "
          "(crimp terminals 2478, 2578, 2878); KK 396 PCB connector 41815")

SERIES = {
    "41791": dict(prefix="26-60-4", orientation="vertical", fp_style="Vertical",
                  word="Vertical", datasheet=f"{DS}/kk-396-41791-vertical-header-sd.pdf",
                  tail="3.56mm PC tail"),
    "41792": dict(prefix="26-60-5", orientation="right-angle", fp_style="Horizontal",
                  word="Right-Angle", datasheet=f"{DS}/kk-396-41792-right-angle-header-sd.pdf",
                  tail="3.96mm PC tail"),
}

PITCH = 3.96
PIN_W = 1.14          # 0.045in square pin
MATE_LEN = 11.43      # M: pin beyond the housing's mating face
BASE = 3.30           # housing base, seating face to mating face
END = 1.91            # end pin centre to housing end
FRONT = 5.11          # pin centreline to the plain (no-wall) face
WALL_IN, WALL_OUT = 3.895, 4.90   # back wall, from the pin centreline
WALL_H = 11.33        # wall height from the seating face
RAMP_IN = 2.41        # ramp's innermost point from the pin centreline
RAMP_Z = (7.0, 9.8)   # ramp band above the seating face (scaled)
TAIL_V = 3.56         # 41791 PC tail
TAIL_RA = 3.96        # 41792 PC tail
Y_RA = 5.41           # 41792 tail centre to the seating face

FAMILY = {
    "connector_category": "wire-to-board", "connector_family": "Molex KK 396",
    "connector_type": "header", "rows": 1, "pitch_mm": 3.96,
    "termination_type": "Through Hole", "gender": "male", "polarized": "yes",
    "keying_detail": "polarizing back wall, friction-lock ramp",
    "locking_mechanism": "friction", "shielding": "unshielded", "color": "natural",
    "current_rating": 7.0, "voltage_rating": 600.0, "signal_type": "power",
    "flammability_rating": "UL94-V0", "mating_family": MATING,
    "mates_with": "2139/3069/41695/6442 crimp housing, same circuit count",
    "temp_operating_min": -40.0, "temp_operating_max": 80.0,
}

COLS = [
    "unique_id", "variant", "part_locator", "mpn", "manufacturer", "value", "description",
    "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "connector_category", "connector_family", "connector_series", "connector_type",
    "positions", "rows", "pitch_mm", "orientation", "termination_type", "gender",
    "polarized", "keying_detail", "locking_mechanism", "shielding", "color",
    "current_rating", "voltage_rating", "signal_type", "flammability_rating",
    "mating_family", "mates_with",
]


def fp_name(series, n):
    """KiCad's stock footprint name, kept for the vendored copy and its model."""
    return (f"Molex_KK-396_A-{series}-{n:04d}_1x{n:02d}"
            f"_P3.96mm_{SERIES[series]['fp_style']}")


def model_specs():
    specs = {}
    for n in CIRCUITS:
        x0, x1 = -END, (n - 1) * PITCH + END      # housing ends
        w0, w1 = 0.0, (n - 1) * PITCH               # back wall: end pin centre to centre
        # 41791 vertical: seating face on the board, wall on +y
        specs[fp_name("41791", n)] = [
            ("box", "natural", x0, -FRONT, 0, x1, WALL_IN, BASE),
            ("box", "natural", w0, WALL_IN, 0, w1, WALL_OUT, WALL_H),
            ("box", "natural", w0, RAMP_IN, RAMP_Z[0], w1, WALL_IN, RAMP_Z[1]),
            *pin_row("tin", n, PITCH, 0, -TAIL_V, BASE + MATE_LEN, PIN_W),
        ]
        # 41792 right-angle: plain face on the board, mating toward -y; housing depth
        # coordinate d (from the seating face) maps to y = -(Y_RA + d), the vertical
        # part's y (from the pin centreline) to z = FRONT + y
        y_seat, y_mate = -Y_RA, -(Y_RA + BASE)
        hz = FRONT
        ra = [
            ("box", "natural", x0, y_mate, 0, x1, y_seat, hz + WALL_IN),
            ("box", "natural", w0, y_seat - WALL_H, hz + WALL_IN, w1, y_seat, hz + WALL_OUT),
            ("box", "natural", w0, y_seat - RAMP_Z[1], hz + RAMP_IN,
             w1, y_seat - RAMP_Z[0], hz + WALL_IN),
            *pin_row("tin", n, PITCH, 0, -TAIL_RA, hz + PIN_W / 2, PIN_W),
        ]
        ra += [("hpin", "tin", i * PITCH, PIN_W / 2, y_mate - MATE_LEN, hz, PIN_W)
               for i in range(n)]
        specs[fp_name("41792", n)] = ra
    return {name: [tuple(round(v, 3) if isinstance(v, float) else v for v in prim)
                   for prim in spec] for name, spec in specs.items()}


def vendor_footprints():
    """Copy KiCad's stock footprints in, with the model pointed at terra's STEP."""
    sys.path.insert(0, str(ROOT))
    from tools.vendor_footprint import stock_footprint_dir, vendor_footprint
    stock = stock_footprint_dir() / "Connector_Molex.pretty"
    names = [fp_name(series, n) for series in SERIES for n in CIRCUITS]
    missing = [nm for nm in names if not (stock / f"{nm}.kicad_mod").is_file()]
    if missing:
        sys.exit(f"stock footprints missing from {stock}: {missing}")
    for nm in names:
        vendor_footprint("Connector_Molex", nm, FP_LIB, f"{MODEL_LIB}/{nm}.step",
                         (0, 0, 0), (0, 0, 0))
    print(f"Vendored {len(names)} footprints into {FP_LIB}.pretty")


def parts():
    for series, s in SERIES.items():
        for n in CIRCUITS:
            mpn = f"{s['prefix']}{n:02d}0"            # 26-60-4020
            catalog = "00" + mpn.replace("-", "")       # 0026604020
            yield {
                **FAMILY,
                "unique_id": f"Molex-{mpn}",
                "part_locator": f"conn-header-{n}pos-3.96mm-1row-th-{s['orientation']}-tin",
                "mpn": mpn, "manufacturer": "Molex", "value": mpn,
                "description": (
                    f"Molex KK 396 {mpn} header, 3.96mm pitch, 1x{n:02d}, "
                    f"{s['orientation']}, friction lock, through-hole, tin plating, "
                    f"{s['tail']}"),
                "datasheet": s["datasheet"],
                "manufacturer_link": f"https://www.molex.com/en-us/products/part-detail/{catalog[2:]}",
                "kicad_symbol": f"Connector_Generic:Conn_01x{n:02d}",
                "kicad_footprint": f"{FP_LIB}:{fp_name(series, n)}",
                "lifecycle_status": "Active", "rohs": "Yes",
                "allow_substitution": "No", "tracking": "No",
                "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
                "keywords": (
                    f"connector,header,molex,kk396,kk 396,3.96mm,0.156in,friction lock,"
                    f"{s['orientation']},{series},{mpn},{catalog},{series}-{n:04d},"
                    f"power,SWTPC,vintage"),
                "pin_count": str(n), "positions": n, "connector_series": series,
                "orientation": s["orientation"],
            }


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def insert(p):
    vals = ", ".join(sql(p.get(c)) for c in COLS)
    return f"INSERT INTO connectors ({', '.join(COLS)}) VALUES ({vals});"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--vendor-footprints", action="store_true",
                    help="rewrite the vendored footprints from the installed KiCad library")
    if ap.parse_args().vendor_footprints:
        vendor_footprints()
        return
    missing = [nm for nm in (fp_name(s, n) for s in SERIES for n in CIRCUITS)
               if not (FP_DIR / f"{nm}.kicad_mod").is_file()]
    if missing:
        sys.exit(f"vendored footprints missing (run with --vendor-footprints): {missing}")
    write_symbols([numeric_pins_symbol(n) for n in CIRCUITS])
    rows = with_pins(list(parts()), lambda r: numeric_pins_id(r["positions"]))
    ids = [p["unique_id"] for p in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        sys.exit(f"duplicate unique_id: {dupes}")
    for s in SERIES.values():
        if not (ROOT / s["datasheet"].replace("${TERRA_EDA_LIB}/", "")).exists():
            sys.exit(f"datasheet missing: {s['datasheet']}")
    lines = [
        "-- Terra EDA Library - Molex KK 396 friction-lock headers (41791 vertical, 41792 right-angle)",
        f"-- Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
        *(insert(p) for p in rows),
        "",
        "COMMIT;",
        "",
    ]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} parts")


if __name__ == "__main__":
    main()
