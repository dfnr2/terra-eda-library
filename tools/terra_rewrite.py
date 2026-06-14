#!/usr/bin/env python3
"""Stage 4b -- project schematic rewrite (terra_rewrite).

CONTRACT / INVARIANT: electrical connectivity must not change. For every net, the
set of (reference, pin-number) members is identical before and after the rewrite.
Component value/footprint/MPN change by design (that is the conversion) and are NOT
part of the invariant. The mechanism below produces a candidate rewrite; the proof
is a netlist connectivity diff (via kicad-cli) that must be empty, else revert.

This module currently implements the SAFE CORE only -- symbol pin geometry and the
pin-preserving transform search. It mutates nothing. The apply + netlist gold-check
stages are added in a later increment and gated on explicit approval per board.

Pin-preservation model
----------------------
A placed symbol has an instance placement (origin x,y; rotation; optional mirror).
Its connection points are the symbol pins' (at x y) coords transformed by that
placement. To swap the legacy symbol for the terra part's symbol without moving any
net, we find a (rotation, mirror) for the terra symbol and a translation such that
each terra pin lands on the SAME board coordinate as the legacy pin of the SAME
number. Requiring same-number coincidence (not just any coincidence) is what keeps
the (reference, pin-number) -> net membership identical -- i.e. the invariant.
"""
from __future__ import annotations

import math
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SYMBOL_DIRS = ["/usr/share/kicad/symbols", str(_ROOT / "kicad_symbols")]


@dataclass(frozen=True)
class Pin:
    """A symbol pin reduced to its connection point (the (at) coord) and number."""
    number: str
    name: str
    x: float
    y: float


@dataclass(frozen=True)
class Placement:
    """An instance placement: origin (x, y), rotation degrees, optional mirror axis."""
    x: float
    y: float
    rot: int = 0
    mirror: str | None = None  # None | 'x' | 'y'


@dataclass(frozen=True)
class Transform:
    """The terra-symbol placement that preserves the legacy pins, plus the proof."""
    rot: int
    mirror: str | None
    x: float
    y: float


_PIN_RE = re.compile(
    r'\(pin\b[^()]*?\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+-?[\d.]+\)'  # connection point
    r'.*?\(name\s+"((?:[^"\\]|\\.)*)"'
    r'.*?\(number\s+"((?:[^"\\]|\\.)*)"',
    re.S,
)


def parse_pins(symbol_text: str) -> list[Pin]:
    """Extract pins (connection point + number) from one symbol's s-expression text.

    The pin's ``(at x y angle)`` is its electrical connection point; angle/length
    are drawing-only and ignored here.
    """
    pins: list[Pin] = []
    for x, y, name, number in _PIN_RE.findall(symbol_text):
        pins.append(Pin(number=number, name=name, x=round(float(x), 4), y=round(float(y), 4)))
    return pins


def _rot(x: float, y: float, deg: int) -> tuple[float, float]:
    r = math.radians(deg)
    c, s = round(math.cos(r)), round(math.sin(r))  # exact for 0/90/180/270
    return (x * c - y * s, x * s + y * c)


def _place(x: float, y: float, p: Placement) -> tuple[float, float]:
    """Map a symbol-local point to absolute coords under a placement.

    One self-consistent convention (mirror, then rotate, then translate). Absolute
    correctness vs KiCad's own axis is irrelevant to the *search* -- legacy and terra
    pins go through the same function, so a found same-number coincidence is real --
    and the applied result is proven by the netlist gold-check regardless.
    """
    if p.mirror == "x":
        y = -y
    elif p.mirror == "y":
        x = -x
    rx, ry = _rot(x, y, p.rot)
    return (round(p.x + rx, 4), round(p.y + ry, 4))


def find_transform(legacy_pins: list[Pin], legacy_at: Placement,
                   terra_pins: list[Pin]) -> Transform | None:
    """Find a terra placement whose pins land on the legacy pins of the same number.

    Returns the ``Transform`` (rotation, mirror, solved origin) or ``None`` when no
    rotation x mirror makes every same-numbered pin coincide (different pin set, span,
    or unresolvable geometry) -- those symbols go to manual review, untouched.
    """
    if {p.number for p in legacy_pins} != {p.number for p in terra_pins}:
        return None
    legacy_abs = {p.number: _place(p.x, p.y, legacy_at) for p in legacy_pins}
    terra_by_num = {p.number: p for p in terra_pins}
    for rot in (0, 90, 180, 270):
        for mirror in (None, "x", "y"):
            # terra pins under (rot, mirror) about a zero origin, then solve the
            # single translation that maps every pin onto its legacy twin.
            offsets = set()
            for num, lp in legacy_abs.items():
                tx, ty = _place(terra_by_num[num].x, terra_by_num[num].y,
                                Placement(0, 0, rot, mirror))
                offsets.add((round(lp[0] - tx, 3), round(lp[1] - ty, 3)))
            if len(offsets) == 1:  # one consistent translation -> all pins coincide
                ox, oy = offsets.pop()
                return Transform(rot=rot, mirror=mirror, x=ox, y=oy)
    return None


# --------------------------------------------------------------------------- #
# Dry-run analysis: does a pin-preserving transform exist for each convertible
# part on a board? (Read-only; the precursor to the write + netlist gold-check.)
# --------------------------------------------------------------------------- #

def _balanced_symbol_block(text: str, name: str) -> str | None:
    """Return the balanced ``(symbol "name" ... )`` block (incl. unit sub-symbols)."""
    anchor = f'(symbol "{name}"'
    i = text.find(anchor)
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def resolve_symbol_pins(kicad_symbol: str, _depth: int = 0) -> list[Pin] | None:
    """Pins for a ``Lib:Name`` symbol from the standard or terra symbol libraries.

    Follows ``(extends "base")`` for derived symbols (e.g. ``OPA365xxDBV`` extends
    ``MCP6L91T-EOT``, ``MMBT3906`` extends ``Q_PNP_BEC``), which inherit the base's
    pin geometry.
    """
    if ":" not in kicad_symbol or _depth > 8:
        return None
    lib, name = kicad_symbol.split(":", 1)
    for d in _SYMBOL_DIRS:
        f = Path(d) / f"{lib}.kicad_sym"
        if f.is_file():
            block = _balanced_symbol_block(f.read_text(), name)
            if block is None:
                continue
            pins = parse_pins(block)
            if pins:
                return pins
            m = re.search(r'\(extends "((?:[^"\\]|\\.)*)"', block)
            if m:
                return resolve_symbol_pins(f"{lib}:{m.group(1)}", _depth + 1)
            return pins
    return None


def _all_sheet_text(root: Path) -> str:
    """Concatenated text of the root schematic and every sub-sheet (for lib_symbols)."""
    seen: set[Path] = set()
    stack = [root]
    out = []
    while stack:
        f = stack.pop()
        try:
            f = f.resolve()
        except OSError:
            continue
        if f in seen or not f.is_file():
            continue
        seen.add(f)
        t = f.read_text(encoding="utf-8")
        out.append(t)
        for m in re.finditer(r'\(property "Sheetfile" "((?:[^"\\]|\\.)*)"', t):
            stack.append(f.parent / m.group(1))
    return "\n".join(out)


def _terra_symbol_for(conn, table: str, uid: str) -> str | None:
    row = conn.execute(f'SELECT kicad_symbol FROM "{table}" WHERE unique_id=?', (uid,)).fetchone()
    return row[0] if row else None


def dry_run(board: Path, db: Path):
    """Classify each convertible instance: pin-preserving transform OK, or manual."""
    import terra_convert as tc
    parts = tc.parse_schematic(board)
    idx = tc.load_terra(db)
    records = tc.build_records(parts, idx)
    libtext = _all_sheet_text(board)
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)

    ok, manual, skipped = [], [], {"C": 0, "REVIEW": 0}
    for rec in records:
        tier = rec["tier"]
        if tier in ("C", "REVIEW"):
            skipped[tier] = skipped.get(tier, 0) + 1
            continue
        ref, lib_id, target = rec["ref"], rec["lib_id"], rec.get("target") or ""
        # resolve the terra part's kicad_symbol
        terra_sym = None
        if tier == "A" and ":" in target:
            table, uid = target.split(":", 1)
            terra_sym = _terra_symbol_for(conn, table, uid)
        elif tier == "B":
            hit = idx.by_mpn.get(tc.norm_mpn(target))
            if hit:
                terra_sym = _terra_symbol_for(conn, hit["table"], hit["uid"])
        legacy = _balanced_symbol_block(libtext, lib_id)
        legacy_pins = parse_pins(legacy) if legacy else []
        terra_pins = resolve_symbol_pins(terra_sym) if terra_sym else None
        if not legacy_pins or not terra_pins:
            manual.append((ref, tier, f"pins unresolved (legacy={len(legacy_pins)}, terra_sym={terra_sym})"))
            continue
        t = find_transform(legacy_pins, Placement(0, 0, 0), terra_pins)
        if t is None:
            manual.append((ref, tier, f"no transform: legacy {len(legacy_pins)}-pin vs {terra_sym}"))
        else:
            ok.append((ref, tier, terra_sym, t))
    conn.close()
    return ok, manual, skipped


if __name__ == "__main__":
    board = Path(sys.argv[1])
    db = Path(sys.argv[2]) if len(sys.argv) > 2 else _ROOT / "db/terra.db"
    ok, manual, skipped = dry_run(board, db)
    print(f"convertible & pin-preserving (OK): {len(ok)}")
    print(f"manual review:                     {len(manual)}")
    print(f"left alone (C/REVIEW):             {skipped}")
    from collections import Counter
    print("OK by rot/mirror:", dict(Counter((t.rot, t.mirror) for _, _, _, t in ok)))
    print("\n-- manual --")
    for ref, tier, why in sorted(manual)[:40]:
        print(f"  {ref:6} {tier}  {why}")
