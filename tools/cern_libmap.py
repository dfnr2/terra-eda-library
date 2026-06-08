"""Canonical CERN -> terra library nickname mapping (diodes pilot scope).

CERN libs are copied into terra's kicad_symbols/ and kicad_footprints/ hierarchy
under normalized names (lowercase, non-alphanumerics -> '-', 'cern-' prefix); the
nickname equals the copied lib's filename stem.
"""
from __future__ import annotations

SYMBOL_LIB_NICK = {
    "Diodes": "cern-diodes",
    "Transistors": "cern-transistors",
    "Regulators": "cern-regulators",
}

FOOTPRINT_LIB_NICK = {
    "ICs And Semiconductors SMD": "cern-ics-and-semiconductors-smd",
    "ICs And Semiconductors THD": "cern-ics-and-semiconductors-thd",
    "ICs And Semiconductors BONDING": "cern-ics-and-semiconductors-bonding",
    "ICs And Semiconductors SMD_BGA": "cern-ics-and-semiconductors-smd-bga",
}


# CERN data-entry errors: a few rows reference a footprint item whose name does
# not match any real .kicad_mod in the PcbLib (typo / spurious or dropped
# suffix). Map the bad item name -> the actual file stem. Deterministic, exact;
# symbol names never collide with these keys, so it is safe to apply globally.
FOOTPRINT_ITEM_FIXUP = {
    "BGA144C127P12X12_1600X1600X521": "BGA144C127P12X12_1600X1600X521R",
    "TEXAS_RGY (S-PVQFN-N14)+THERMAL": "TEXAS_RGY (S-PVQFN-N14)",
    "SOT95P2d80X100-6N": "SOT95P280X100-6N",
}


def rewrite_ref(ref: str, nickmap: dict) -> str:
    """Rewrite the library nickname of a 'Lib:Item' ref and fix known item typos."""
    if not ref or ":" not in ref:
        return ref
    nick, name = ref.split(":", 1)
    name = FOOTPRINT_ITEM_FIXUP.get(name, name)
    return f"{nickmap.get(nick, nick)}:{name}"
