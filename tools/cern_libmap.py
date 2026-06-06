"""Canonical CERN -> terra library nickname mapping (diodes pilot scope)."""
from __future__ import annotations

SYMBOL_LIB_NICK = {
    "Diodes": "cern_Diodes",
}

FOOTPRINT_LIB_NICK = {
    "ICs And Semiconductors SMD": "cern_ICs_SMD",
    "ICs And Semiconductors THD": "cern_ICs_THD",
    "ICs And Semiconductors BONDING": "cern_ICs_BONDING",
}


def rewrite_ref(ref: str, nickmap: dict) -> str:
    """Rewrite the library-nickname portion of a 'Lib:Item' reference."""
    if not ref or ":" not in ref:
        return ref
    nick, name = ref.split(":", 1)
    return f"{nickmap.get(nick, nick)}:{name}"
