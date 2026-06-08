"""Canonical CERN -> terra library nickname mapping (diodes pilot scope).

CERN libs are copied into terra's kicad_symbols/ and kicad_footprints/ hierarchy
under normalized names (lowercase, non-alphanumerics -> '-', 'cern-' prefix); the
nickname equals the copied lib's filename stem.
"""
from __future__ import annotations

SYMBOL_LIB_NICK = {
    "Diodes": "cern-diodes",
    "Transistors": "cern-transistors",
}

FOOTPRINT_LIB_NICK = {
    "ICs And Semiconductors SMD": "cern-ics-and-semiconductors-smd",
    "ICs And Semiconductors THD": "cern-ics-and-semiconductors-thd",
    "ICs And Semiconductors BONDING": "cern-ics-and-semiconductors-bonding",
    "ICs And Semiconductors SMD_BGA": "cern-ics-and-semiconductors-smd-bga",
}


def rewrite_ref(ref: str, nickmap: dict) -> str:
    """Rewrite the library-nickname portion of a 'Lib:Item' reference."""
    if not ref or ":" not in ref:
        return ref
    nick, name = ref.split(":", 1)
    return f"{nickmap.get(nick, nick)}:{name}"
