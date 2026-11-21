#!/usr/bin/env python3
"""Bourns 3362: 1/4" square single-turn cermet trimpots, top-adjust P, H and U styles.

Datasheet datasheets/bourns/3362-trimpot.pdf:
  - 10 ohm to 2 Mohm (standard resistance table), +/-10 %, 0.5 W at 70 C (300 V
    max), +/-100 ppm/C, -55 to 125 C, single turn (240 deg electrical, 270 deg
    mechanical), cermet.
  - key "3362<style>-1-<code><pkg>LF": -1 = standard product, <code> from the
    standard resistance table, blank packaging = tube, LF = 100 % tin (RoHS).
  - pin styles: top adjust F, H, P, R, U; side adjust M, S, W, X, Z. This seeds
    P (triangle: 1 and 3 on 5.08 mm, 2 offset 2.54 mm), H (90 deg: 2 at the
    vertex, 1 and 3 at 2.54 mm on the diagonals) and U (in line, 2.54 mm).

Codes: every standard-table value in each style, tube, LF. All are listed Active
at Mouser (checked 2026-11-21); some were on order rather than in stock that day.

KiCad ships no 3362 footprints, so this script writes them to
kicad_footprints/terra_footprints_potentiometers_th.pretty from the datasheet
pin-style drawings (pin 1 at the origin, body 6.60 x 6.99 mm, pads 1.44 mm on
0.8 mm drills as KiCad's Bourns 3296 footprints). The drawings are read as top
views; P, H and U are mirror-symmetric, so a mirrored reading would only swap
pins 1 and 3 (the direction of clockwise travel).

Symbol Device:R_Potentiometer_Trim (1 and 3 the ends, 2 the wiper, as Bourns:
1 CCW, 2 wiper, 3 CW).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _pot import BOURNS_CODES, row, write  # noqa: E402

OUTPUT_FILE = Path(__file__).with_name("potentiometers_th_generated_310_bourns_3362.sql")
CREATED_BY = Path(__file__).name
ROOT = Path(__file__).resolve().parents[3]
FP_LIB = "terra_footprints_potentiometers_th"
FP_DIR = ROOT / "kicad_footprints" / f"{FP_LIB}.pretty"

BODY_W, BODY_D = 6.60, 6.99
D = 2.54 * 2 ** -0.5  # H style: 2.54 mm along a 45 deg diagonal
# style -> (pin positions with pin 1 at the origin (x right, y toward the front),
#           distance from the body's back edge to pin 1, description)
STYLES = {
    "P": ([(0, 0), (2.54, 2.54), (5.08, 0)], 3.53,
          "pins 1 and 3 on 5.08 mm, pin 2 2.54 mm forward"),
    "H": ([(0, 0), (D, D), (2 * D, 0)], 4.06 - D,
          "pins on a 90 deg angle, 2.54 mm from pin 2 at the vertex"),
    "U": ([(0, 0), (2.54, 0), (5.08, 0)], 3.53, "pins in line on 2.54 mm"),
}

# style -> standard-table codes generated (all listed Active at Mouser, 2026-11-21).
STOCKED = {s: list(BOURNS_CODES) for s in STYLES}


def fp_name(style):
    return f"Potentiometer_Bourns_3362{style}_Vertical"


def footprint_text(style):
    pins, back, what = STYLES[style]
    name = fp_name(style)
    cx = (min(x for x, _ in pins) + max(x for x, _ in pins)) / 2
    x0, x1 = cx - BODY_W / 2, cx + BODY_W / 2
    y0, y1 = -back, -back + BODY_D

    def rect(ax, ay, bx, by, layer, w):
        pts = [(ax, ay), (bx, ay), (bx, by), (ax, by), (ax, ay)]
        return "".join(
            f'  (fp_line (start {p[0]:.3f} {p[1]:.3f}) (end {q[0]:.3f} {q[1]:.3f}) '
            f'(layer "{layer}") (width {w}))\n' for p, q in zip(pts, pts[1:]))

    pads = "".join(
        f'  (pad "{i}" thru_hole circle (at {x:.3f} {y:.3f}) (size 1.44 1.44) '
        f'(drill 0.8) (layers *.Cu *.Mask))\n' for i, (x, y) in enumerate(pins, 1))
    return (
        f'(footprint "{name}" (version 20211014) (generator terra)\n'
        f'  (layer "F.Cu")\n'
        f'  (descr "Potentiometer, vertical (top adjust), Bourns 3362{style}, 1/4in '
        f'square single-turn trimpot, {what}, '
        f'https://www.bourns.com/docs/Product-Datasheets/3362.pdf")\n'
        f'  (tags "potentiometer trimpot vertical Bourns 3362{style}")\n'
        f'  (attr through_hole)\n'
        f'  (fp_text reference "REF**" (at {cx:.3f} {y0 - 1.2:.3f}) (layer "F.SilkS")\n'
        f'    (effects (font (size 1 1) (thickness 0.15)))\n  )\n'
        f'  (fp_text value "{name}" (at {cx:.3f} {y1 + 1.2:.3f}) (layer "F.Fab")\n'
        f'    (effects (font (size 1 1) (thickness 0.15)))\n  )\n'
        + rect(x0, y0, x1, y1, "F.Fab", 0.1)
        + rect(x0 - 0.12, y0 - 0.12, x1 + 0.12, y1 + 0.12, "F.SilkS", 0.12)
        + rect(x0 - 0.5, y0 - 0.5, x1 + 0.5, y1 + 0.5, "F.CrtYd", 0.05)
        + pads + ")\n")


def records():
    for style, codes in STOCKED.items():
        for code in codes:
            yield row(
                created_by=CREATED_BY, manufacturer="Bourns", series="3362",
                style=f"3362{style}", mpn=f"3362{style}-1-{code}LF",
                ohms=BOURNS_CODES[code], tolerance="±10%", power="1/2W",
                temp_coeff="±100ppm/°C", composition="Cermet", turns=1,
                adjustment="top", temp=(-55, 125),
                package=f"Trimpot 1/4in square 3362{style}",
                footprint=f"{FP_LIB}:{fp_name(style)}",
                datasheet="bourns/3362-trimpot.pdf")


def main():
    FP_DIR.mkdir(parents=True, exist_ok=True)
    for style in STYLES:
        (FP_DIR / f"{fp_name(style)}.kicad_mod").write_text(footprint_text(style))
    write(OUTPUT_FILE, "Bourns 3362", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
