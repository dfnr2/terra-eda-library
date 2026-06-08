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
    "Operational Amplifiers": "cern-operational-amplifiers",
    "Analog & Interface": "cern-analog-interface",
    "Standard Logic": "cern-standard-logic",
    "Logic": "cern-logic",
}

FOOTPRINT_LIB_NICK = {
    "ICs And Semiconductors SMD": "cern-ics-and-semiconductors-smd",
    "ICs And Semiconductors THD": "cern-ics-and-semiconductors-thd",
    "ICs And Semiconductors BONDING": "cern-ics-and-semiconductors-bonding",
    "ICs And Semiconductors SMD_BGA": "cern-ics-and-semiconductors-smd-bga",
}


# CERN data-entry errors: a few rows reference a symbol/footprint item whose name
# does not match any real item in the library (typo / spurious or dropped suffix,
# or a never-created variant symbol). Map the bad item name -> the real one.
# Deterministic and exact; applied to both symbol and footprint refs (the keys are
# distinct enough not to collide).
ITEM_FIXUP = {
    # footprints
    "BGA144C127P12X12_1600X1600X521": "BGA144C127P12X12_1600X1600X521R",
    "TEXAS_RGY (S-PVQFN-N14)+THERMAL": "TEXAS_RGY (S-PVQFN-N14)",
    "SOT95P2d80X100-6N": "SOT95P280X100-6N",
    "INFININEON_PG-DSO-14-71": "INFINEON_PG-DSO-14-71",
    "QFP80P900X900X160-32AN": "QFP80P900X900X160-32N",
    "TEXAS_DYY0016A": "TEXAS_DYY0016A - duplicate",  # Altium export suffix
    # symbols
    "TXS0108ERGY": "TXS0108E_a",   # QFN variant; symbol never created, same logic
}


def rewrite_ref(ref: str, nickmap: dict) -> str:
    """Rewrite the library nickname of a 'Lib:Item' ref and fix known item typos."""
    if not ref or ":" not in ref:
        return ref
    nick, name = ref.split(":", 1)
    name = ITEM_FIXUP.get(name, name)
    return f"{nickmap.get(nick, nick)}:{name}"
