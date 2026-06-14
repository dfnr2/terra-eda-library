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
from dataclasses import dataclass


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
