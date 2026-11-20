#!/usr/bin/env python3
"""Write pin-table-driven DIP symbols into a terra symbol library.

Vintage memories, CPUs and support chips need dozens of plain rectangular DIP
symbols. Drawing them by hand invites pin-number slips, so each family keeps its
pinouts as data in a ``_pinouts.py`` module beside its generators, and this tool
turns them into KiCad symbols in the stock ``Memory_EPROM:27C256`` style:

  - a body 15.24 mm wide (wider if ``width`` is given), pins 2.54 mm long on the
    2.54 mm grid;
  - ``left`` and ``right`` list pin names top to bottom, ``None`` leaving a one-row
    gap (address pins top-left with A0 first, data top-right, controls bottom-left);
  - ``top`` and ``bottom`` list the supply pins, the first one centred (VCC, GND)
    and any extra rails beside it;
  - ``nc`` pins are ``no_connect``, hidden at the body centre as the stock
    Memory_RAM symbols do.

A pinout is a dict::

    {"pins": {1: ("A6", "in"), ..., 18: ("VCC", "pwr")},
     "left": ["A0", ..., "A9", None, "~{CS}", "~{WE}"],
     "right": ["I/O1", ...], "top": ["VCC"], "bottom": ["GND"],
     "footprint": "Package_DIP:DIP-18_W7.62mm",
     "description": "1Kx4 static RAM, common I/O", "keywords": "SRAM 1Kx4"}

Pin types: in, out, tri, bidi, oc, pwr, nc. Every pin number from 1 to the pin
count must be placed exactly once, which the tool checks before writing.

Writing replaces a symbol of the same name in place or appends a new one, so it is
safe to rerun after a pinout fix. Usage::

    python3 tools/make_dip_symbol.py db/tables/ic_memory/_pinouts.py \\
        kicad_symbols/terra_symbols_ic_memory.kicad_sym [NAME ...]

With no names, every pinout in the module's ``PINOUTS`` dict is written.
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

TYPES = {
    "in": "input", "out": "output", "tri": "tri_state", "bidi": "bidirectional",
    "oc": "open_collector", "pwr": "power_in", "nc": "no_connect",
}
GRID = 2.54
PIN_LEN = 2.54
T = "\t"


def fmt(v):
    """Format a coordinate the way KiCad does: no trailing zeros, no -0."""
    v = round(v, 4)
    if v == 0:
        v = 0.0
    return f"{v:g}"


def effects(ind, justify=None, hide=False):
    lines = [f"{ind}(effects", f"{ind}\t(font", f"{ind}\t\t(size 1.27 1.27)", f"{ind}\t)"]
    if justify:
        lines.append(f"{ind}\t(justify {justify})")
    lines.append(f"{ind})")
    return lines


def prop(name, value, x, y, hide=False, justify=None):
    ind = T * 2
    value = value.replace('"', '\\"')
    out = [f'{ind}(property "{name}" "{value}"', f"{ind}\t(at {fmt(x)} {fmt(y)} 0)",
           f"{ind}\t(show_name no)", f"{ind}\t(do_not_autoplace no)"]
    if hide:
        out.append(f"{ind}\t(hide yes)")
    out += effects(ind + T, justify)
    out.append(f"{ind})")
    return out


def pin(etype, x, y, rot, name, number, hide=False):
    ind = T * 3
    out = [f"{ind}(pin {etype} line", f"{ind}\t(at {fmt(x)} {fmt(y)} {rot})",
           f"{ind}\t(length {fmt(PIN_LEN)})"]
    if hide:
        out.append(f"{ind}\t(hide yes)")
    out.append(f'{ind}\t(name "{name}"')
    out += effects(ind + T * 2)
    out.append(f"{ind}\t)")
    out.append(f'{ind}\t(number "{number}"')
    out += effects(ind + T * 2)
    out.append(f"{ind}\t)")
    out.append(f"{ind})")
    return out


def check(name, p):
    """Fail unless every pin number is placed exactly once with a known type."""
    pins = p["pins"]
    n = len(pins)
    if sorted(pins) != list(range(1, n + 1)):
        raise SystemExit(f"{name}: pin numbers are not 1..{n}: {sorted(pins)}")
    by_name = {}
    for num, (pname, ptype) in pins.items():
        if ptype not in TYPES:
            raise SystemExit(f"{name}: pin {num} has unknown type {ptype!r}")
        if ptype == "nc":
            continue
        if pname in by_name:
            raise SystemExit(f"{name}: pin name {pname!r} used by pins {by_name[pname]} and {num}")
        by_name[pname] = num
    placed = [x for side in ("left", "right", "top", "bottom") for x in p.get(side, []) if x]
    dupes = sorted({x for x in placed if placed.count(x) > 1})
    if dupes:
        raise SystemExit(f"{name}: placed more than once: {dupes}")
    unknown = sorted(set(placed) - set(by_name))
    if unknown:
        raise SystemExit(f"{name}: placed names not in the pin table: {unknown}")
    missing = sorted(set(by_name) - set(placed))
    if missing:
        raise SystemExit(f"{name}: pins not placed: {missing}")
    for num, (pname, ptype) in pins.items():
        side = next((s for s in ("top", "bottom") if pname in p.get(s, [])), None)
        if side and ptype != "pwr":
            raise SystemExit(f"{name}: {pname} on the {side} edge is not a power pin")
    return by_name


def symbol(name, p):
    """Return the lines of one top-level (symbol ...) block."""
    by_name = check(name, p)
    pins = p["pins"]
    left, right = p.get("left", []), p.get("right", [])
    top, bottom = p.get("top", []), p.get("bottom", [])
    half_w = p.get("width", 15.24) / 2
    px = half_w + PIN_LEN
    rows = max(len(left), len(right))
    # Leave a clear row under the top/bottom edge when there are extra rails, so
    # their vertical pin names don't run into the first side pin names.
    margin_top = GRID * (2 if len(top) > 1 else 1)
    margin_bot = GRID * (2 if len(bottom) > 1 else 1)
    height = margin_top + GRID * (rows - 1) + margin_bot
    # Centre the body on the origin, snapped to the grid.
    y_top = GRID * round(height / 2 / GRID)
    y_bot = y_top - height
    first_row = y_top - margin_top

    out = [f'{T}(symbol "{name}"',
           f"{T*2}(exclude_from_sim no)", f"{T*2}(in_bom yes)", f"{T*2}(on_board yes)",
           f"{T*2}(in_pos_files yes)", f"{T*2}(duplicate_pin_numbers_are_jumpers no)"]
    out += prop("Reference", "U", -half_w, y_top + 1.27, justify="left")
    # Value sits under the body, right of the rightmost bottom supply pin.
    offsets = [0, GRID * 2, -GRID * 2, GRID * 4, -GRID * 4]
    value_x = max([0] + offsets[:len(bottom)]) + GRID
    out += prop("Value", name, value_x, y_bot - 1.27, justify="left")
    out += prop("Footprint", p.get("footprint", ""), 0, 0, hide=True)
    out += prop("Datasheet", p.get("datasheet", ""), 0, 0, hide=True)
    out += prop("Description", p.get("description", ""), 0, 0, hide=True)
    if p.get("keywords"):
        out += prop("ki_keywords", p["keywords"], 0, 0, hide=True)
    fp = p.get("footprint", "")
    m = re.match(r"Package_DIP:DIP-\d+_(W[\d.]+mm)", fp)
    if m:
        out += prop("ki_fp_filters", f"DIP*{m.group(1)}*", 0, 0, hide=True)

    unit = [f'{T*2}(symbol "{name}_1_1"',
            f"{T*3}(rectangle", f"{T*4}(start {fmt(-half_w)} {fmt(y_top)})",
            f"{T*4}(end {fmt(half_w)} {fmt(y_bot)})",
            f"{T*4}(stroke", f"{T*5}(width 0.254)", f"{T*5}(type default)", f"{T*4})",
            f"{T*4}(fill", f"{T*5}(type background)", f"{T*4})", f"{T*3})"]
    placed = []
    for i, pname in enumerate(left):
        if pname:
            placed.append((by_name[pname], -px, first_row - GRID * i, 0))
    for i, pname in enumerate(right):
        if pname:
            placed.append((by_name[pname], px, first_row - GRID * i, 180))
    # Supplies: first centred, the rest alternating right then left of it.
    for i, pname in enumerate(top):
        placed.append((by_name[pname], offsets[i], y_top + PIN_LEN, 270))
    for i, pname in enumerate(bottom):
        placed.append((by_name[pname], offsets[i], y_bot - PIN_LEN, 90))
    for num, x, y, rot in sorted(placed):
        pname, ptype = pins[num]
        unit += pin(TYPES[ptype], x, y, rot, pname, num)
    for num, (pname, ptype) in sorted(pins.items()):
        if ptype == "nc":
            unit += pin("no_connect", 0, 0, 0, pname, num, hide=True)
    unit.append(f"{T*2})")
    out += unit
    out.append(f"{T*2}(embedded_fonts no)")
    out.append(f"{T})")
    return out


def top_level_blocks(text):
    """Yield (name, start, end) for each top-level (symbol ...) in a library."""
    for m in re.finditer(r'^\t\(symbol "((?:[^"\\]|\\.)*)"', text, re.M):
        depth, i = 0, m.start() + 1
        while True:
            c = text[i]
            if c == '"':
                i += 1
                while text[i] != '"':
                    i += 2 if text[i] == "\\" else 1
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        yield m.group(1), m.start(), i + 1


def write(lib_path, symbols):
    """Replace or append each (name, lines) in the library at lib_path."""
    text = lib_path.read_text()
    for name, lines in symbols:
        block = "\n".join(lines)
        found = [(s, e) for n, s, e in top_level_blocks(text) if n == name]
        if found:
            s, e = found[0]
            text = text[:s] + block + text[e:]
            action = "replaced"
        else:
            end = text.rstrip().rfind(")")
            text = text[:end].rstrip("\n") + "\n" + block + "\n" + text[end:]
            action = "added"
        print(f"{action} {name}")
    lib_path.write_text(text)


def load(module_path):
    spec = importlib.util.spec_from_file_location("_pinouts", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PINOUTS


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pinouts", type=Path, help="module defining PINOUTS")
    ap.add_argument("library", type=Path, help=".kicad_sym library to write into")
    ap.add_argument("names", nargs="*", help="symbols to write (default: all)")
    args = ap.parse_args()
    pinouts = load(args.pinouts)
    names = args.names or list(pinouts)
    unknown = [n for n in names if n not in pinouts]
    if unknown:
        sys.exit(f"not in {args.pinouts}: {unknown}")
    write(args.library, [(n, symbol(n, pinouts[n])) for n in names])


if __name__ == "__main__":
    main()
