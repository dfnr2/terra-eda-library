"""Shared connector conventions: per-pin symbol rows and generated 3D models.

Every terra connector gets two rows with the same MPN and parameters (Dave,
2026-11-22; plan: plans/connectors-conventions.md):

  - the whole-connector row, with a one-body symbol (usually stock
    ``Connector_Generic``);
  - a per-pin row, ``variant = 'pins'`` and ``unique_id = '<Mfr>-<MPN>-pins'`` (the
    pattern of the 74xx ``-IEEE`` rows), whose symbol has one unit per pin so each
    contact can be placed where its signal is drawn.

The per-pin symbols are generic: one per pin-numbering scheme (``Conn_PerPin_12``
for pins 1-12, ``Conn_PerPin_EdgeLetter_2x22`` for 1-22 and A-Z without G/I/O/Q),
written by :func:`write_symbols` into ``terra_symbols_connectors``.

Custom footprints carry a 3D model in ``assets/3dmodels/terra-connectors.3dshapes``
named after the footprint. A generator that writes footprints defines
``model_specs()`` returning ``{footprint_name: [primitive, ...]}``; the models are
built from those primitives by ``tools/make_connector_models.py`` under FreeCAD (the
generators themselves never need FreeCAD). Primitives are in footprint coordinates
(mm, x right, y down, z up from the board's top surface):

  ("box", colour, x0, y0, z0, x1, y1, z1)        axis-aligned block
  ("cyl", colour, x, y, z0, z1, d)               round pin, vertical
  ("pin", colour, x, y, z0, z1, w)               square pin w x w, vertical
  ("hpin", colour, x, y0, y1, z, w)              square pin w x w along y (right angle)
  ("hcyl", colour, x, y0, y1, z, d)              round pin along y (right angle)

Colours are names from ``COLOURS`` below.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SYM_LIB = "terra_symbols_connectors"
SYM_PATH = ROOT / "kicad_symbols" / f"{SYM_LIB}.kicad_sym"
MODEL_LIB = "terra-connectors.3dshapes"
MODEL_DIR = ROOT / "assets" / "3dmodels" / MODEL_LIB
MODEL_REF = "${TERRA_EDA_LIB}/assets/3dmodels/" + MODEL_LIB

COLOURS = {
    "natural": (0.93, 0.91, 0.84),      # unfilled nylon / natural polyester
    "white": (0.96, 0.96, 0.95),
    "grey": (0.75, 0.74, 0.69),         # RAL 7032 pebble grey (DIN 41612)
    "black": (0.12, 0.12, 0.12),
    "green": (0.12, 0.45, 0.25),
    "blue": (0.15, 0.30, 0.65),
    "tin": (0.82, 0.82, 0.84),
    "gold": (0.86, 0.69, 0.27),
}

LETTERS = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in "GIOQ"]


# --- rows ----------------------------------------------------------------------------

def with_pins(rows, symbol_for):
    """Return rows plus, after each, its per-pin twin.

    symbol_for(row) -> the per-pin symbol's lib_id. The twin keeps every field but
    unique_id (suffixed ``-pins``), variant and kicad_symbol.
    """
    out = []
    for r in rows:
        out.append(r)
        out.append({**r, "unique_id": r["unique_id"] + "-pins", "variant": "pins",
                    "kicad_symbol": symbol_for(r)})
    return out


def numeric_pins_name(n):
    return f"Conn_PerPin_{n:02d}"


def numeric_pins_id(n):
    return f"{SYM_LIB}:{numeric_pins_name(n)}"


# --- per-pin symbols ------------------------------------------------------------------

T = "\t"


def _fmt(v):
    v = round(v, 4)
    return f"{0.0 if v == 0 else v:g}"


def _effects(ind, hide=False):
    out = [f"{ind}(effects", f"{ind}\t(font", f"{ind}\t\t(size 1.27 1.27)", f"{ind}\t)"]
    if hide:
        out.append(f"{ind}\t(hide yes)")
    out.append(f"{ind})")
    return out


def _prop(name, value, x, y, hide=False):
    ind = T * 2
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    out = [f'{ind}(property "{name}" "{value}"', f"{ind}\t(at {_fmt(x)} {_fmt(y)} 0)",
           f"{ind}\t(show_name no)", f"{ind}\t(do_not_autoplace no)"]
    if hide:
        out.append(f"{ind}\t(hide yes)")
    out += _effects(ind + T)
    out.append(f"{ind})")
    return out


def per_pin_symbol(name, numbers, description, fp_filters="Connector*:*"):
    """Lines of a symbol with one unit per pin, in the stock Conn_01x01 style.

    numbers: pin numbers in unit order (strings or ints). Unit k carries numbers[k-1]
    and is named "-<number>": KiCad 10 shows a named unit as reference + name, so the
    placed units read J1-12, J1-A (checked with kicad-cli sch export).
    """
    numbers = [str(n) for n in numbers]
    if len(set(numbers)) != len(numbers):
        raise SystemExit(f"{name}: duplicate pin numbers")
    out = [f'{T}(symbol "{name}"', f"{T*2}(pin_names", f"{T*3}(offset 1.016)",
           f"{T*3}(hide yes)", f"{T*2})", f"{T*2}(exclude_from_sim no)",
           f"{T*2}(in_bom yes)", f"{T*2}(on_board yes)", f"{T*2}(in_pos_files yes)",
           f"{T*2}(duplicate_pin_numbers_are_jumpers no)"]
    out += _prop("Reference", "J", 0, 2.54)
    out += _prop("Value", name, 0, -2.54)
    out += _prop("Footprint", "", 0, 0, hide=True)
    out += _prop("Datasheet", "", 0, 0, hide=True)
    out += _prop("Description", description, 0, 0, hide=True)
    out += _prop("ki_keywords", "connector per-pin split", 0, 0, hide=True)
    out += _prop("ki_fp_filters", fp_filters, 0, 0, hide=True)
    for unit, num in enumerate(numbers, start=1):
        out += [f'{T*2}(symbol "{name}_{unit}_1"', f'{T*3}(unit_name "-{num}")',
                f"{T*3}(rectangle", f"{T*4}(start -1.27 1.27)", f"{T*4}(end 1.27 -1.27)",
                f"{T*4}(stroke", f"{T*5}(width 0.254)", f"{T*5}(type default)", f"{T*4})",
                f"{T*4}(fill", f"{T*5}(type background)", f"{T*4})", f"{T*3})",
                f"{T*3}(rectangle", f"{T*4}(start -1.27 0.127)", f"{T*4}(end 0 -0.127)",
                f"{T*4}(stroke", f"{T*5}(width 0.1524)", f"{T*5}(type default)", f"{T*4})",
                f"{T*4}(fill", f"{T*5}(type none)", f"{T*4})", f"{T*3})",
                f"{T*3}(pin passive line", f"{T*4}(at -5.08 0 0)", f"{T*4}(length 3.81)",
                f'{T*4}(name "Pin_{num}"']
        out += _effects(T * 5)
        out += [f"{T*4})", f'{T*4}(number "{num}"']
        out += _effects(T * 5)
        out += [f"{T*4})", f"{T*3})", f"{T*2})"]
    out += [f"{T*2}(embedded_fonts no)", f"{T})"]
    return out


def numeric_pins_symbol(n):
    name = numeric_pins_name(n)
    return name, per_pin_symbol(
        name, range(1, n + 1),
        f"Connector, {n} contacts numbered 1-{n}, one unit per pin (place each contact "
        "with its signal)")


def _rect(x0, y0, x1, y1, width, fill):
    return [f"{T*3}(rectangle", f"{T*4}(start {_fmt(x0)} {_fmt(y0)})",
            f"{T*4}(end {_fmt(x1)} {_fmt(y1)})", f"{T*4}(stroke", f"{T*5}(width {width})",
            f"{T*5}(type default)", f"{T*4})", f"{T*4}(fill", f"{T*5}(type {fill})",
            f"{T*4})", f"{T*3})"]


def _pin(x, y, rot, num):
    out = [f"{T*3}(pin passive line", f"{T*4}(at {_fmt(x)} {_fmt(y)} {rot})",
           f"{T*4}(length 3.81)", f'{T*4}(name "Pin_{num}"']
    out += _effects(T * 5)
    out += [f"{T*4})", f'{T*4}(number "{num}"']
    out += _effects(T * 5)
    out += [f"{T*4})", f"{T*3})"]
    return out


def dual_column_symbol(name, left, right, description, fp_filters="Connector*:*"):
    """Whole-connector symbol in the stock Connector_Generic Conn_02xNN style.

    left / right: pin numbers top to bottom on each side; left[i] sits beside right[i]
    (draw them so that matches the contacts facing each other across the card). None
    leaves a one-row gap; a shorter column is padded at the bottom.
    """
    rows = max(len(left), len(right))
    left = [None if p is None else str(p) for p in left] + [None] * (rows - len(left))
    right = [None if p is None else str(p) for p in right] + [None] * (rows - len(right))
    y_bot = -(rows - 1) * 2.54 - 1.27
    out = [f'{T}(symbol "{name}"', f"{T*2}(pin_names", f"{T*3}(offset 1.016)",
           f"{T*3}(hide yes)", f"{T*2})", f"{T*2}(exclude_from_sim no)",
           f"{T*2}(in_bom yes)", f"{T*2}(on_board yes)", f"{T*2}(in_pos_files yes)",
           f"{T*2}(duplicate_pin_numbers_are_jumpers no)"]
    out += _prop("Reference", "J", 1.27, 2.54)
    out += _prop("Value", name, 1.27, y_bot - 1.27)
    out += _prop("Footprint", "", 0, 0, hide=True)
    out += _prop("Datasheet", "", 0, 0, hide=True)
    out += _prop("Description", description, 0, 0, hide=True)
    out += _prop("ki_keywords", "connector card edge", 0, 0, hide=True)
    out += _prop("ki_fp_filters", fp_filters, 0, 0, hide=True)
    out += [f'{T*2}(symbol "{name}_1_1"']
    out += _rect(-1.27, 1.27, 3.81, y_bot, 0.254, "background")
    for i in range(rows):
        y = -i * 2.54
        if left[i] is not None:
            out += _rect(-1.27, y + 0.127, 0, y - 0.127, 0.1524, "none")
        if right[i] is not None:
            out += _rect(3.81, y + 0.127, 2.54, y - 0.127, 0.1524, "none")
    for i, num in enumerate(left):
        if num is not None:
            out += _pin(-5.08, -i * 2.54, 0, num)
    for i, num in enumerate(right):
        if num is not None:
            out += _pin(7.62, -i * 2.54, 180, num)
    out += [f"{T*2})", f"{T*2}(embedded_fonts no)", f"{T})"]
    return out


def edge_letter_whole_name(n):
    return f"Conn_CardEdge_2x{n:02d}_NumberLetter"


def edge_letter_whole_symbol(n):
    """Card edge 1-n on one side, A.. (no G/I/O/Q) facing them on the other."""
    name = edge_letter_whole_name(n)
    return name, dual_column_symbol(
        name, range(1, n + 1), LETTERS[:n],
        f"Card-edge connector, 2x{n}, contacts 1-{n} facing "
        f"{LETTERS[0]}-{LETTERS[n - 1]} (no G/I/O/Q)")


def edge_letter_pins_name(n):
    return f"Conn_PerPin_EdgeLetter_2x{n:02d}"


def edge_letter_pins_id(n):
    return f"{SYM_LIB}:{edge_letter_pins_name(n)}"


def edge_letter_pins_symbol(n):
    """Card edge numbered 1-n on one side and A, B, ... (no G/I/O/Q) on the other."""
    if n > len(LETTERS):
        raise SystemExit(f"edge-letter numbering runs out of letters at 2x{n}")
    name = edge_letter_pins_name(n)
    return name, per_pin_symbol(
        name, [*range(1, n + 1), *LETTERS[:n]],
        f"Card-edge connector, 2x{n}, contacts 1-{n} on one side and "
        f"{LETTERS[0]}-{LETTERS[n - 1]} (no G/I/O/Q) on the other, one unit per pin")


def _top_level_blocks(text):
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


def write_symbols(symbols):
    """Replace or append each (name, lines) in terra_symbols_connectors.

    Rewrites the file only when something changed, so reruns leave git clean.
    """
    text = old = SYM_PATH.read_text()
    for name, lines in symbols:
        block = "\n".join(lines)
        found = [(s, e) for n, s, e in _top_level_blocks(text) if n == name]
        if found:
            s, e = found[0]
            text = text[:s] + block + text[e:]
        else:
            end = text.rstrip().rfind(")")
            text = text[:end].rstrip("\n") + "\n" + block + "\n" + text[end:]
    if text != old:
        SYM_PATH.write_text(text)


# --- 3D models -------------------------------------------------------------------------

def model_sexpr(fp_name):
    """The (model ...) block for a terra-generated connector footprint."""
    return (f'  (model "{MODEL_REF}/{fp_name}.step"\n'
            "    (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0))\n  )\n")


def pin_row(colour, n, pitch, y, z0, z1, w, round_=False):
    """One vertical pin per position along +x from the origin."""
    kind = "cyl" if round_ else "pin"
    return [(kind, colour, i * pitch, y, z0, z1, w) for i in range(n)]
