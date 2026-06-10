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
    "DC-DC Converters": "cern-dc-dc-converters",
    "Power Supplies": "cern-power-supplies",
    "Optocouplers": "cern-optocouplers",
    "Crystals & Oscillators": "cern-crystals-oscillators",
    "Connectors": "cern-connectors",   # shared symbol lib for all connector vendors
    "Sockets": "cern-sockets",
    "LEDs & Displays": "cern-leds-displays",
    "Relays": "cern-relays",
    "Fuses": "cern-fuses",
    "Sensors": "cern-sensors",
    "Switches": "cern-switches",
    "Inductors & Transformers": "cern-inductors-transformers",
    "Resistors": "cern-resistors",   # shared symbol lib (thermistors/varistors/TCO)
}

FOOTPRINT_LIB_NICK = {
    "ICs And Semiconductors SMD": "cern-ics-and-semiconductors-smd",
    "ICs And Semiconductors THD": "cern-ics-and-semiconductors-thd",
    "ICs And Semiconductors BONDING": "cern-ics-and-semiconductors-bonding",
    "ICs And Semiconductors SMD_BGA": "cern-ics-and-semiconductors-smd-bga",
    "MOLEX SMD": "cern-molex-smd",
    "MOLEX THD": "cern-molex-thd",
    # connector vendors (share the "Connectors" symbol lib; per-vendor footprints)
    "SAMTEC SMD": "cern-samtec-smd", "SAMTEC THD": "cern-samtec-thd",
    "TYCO SMD": "cern-tyco-smd", "TYCO THD": "cern-tyco-thd",
    "3M SMD": "cern-3m-smd", "3M THD": "cern-3m-thd",
    "PHOENIX SMD": "cern-phoenix-smd", "PHOENIX THD": "cern-phoenix-thd",
    "HARTING SMD": "cern-harting-smd", "HARTING THD": "cern-harting-thd",
    "AMPHENOL SMD": "cern-amphenol-smd", "AMPHENOL THD": "cern-amphenol-thd",
    "HARWIN SMD": "cern-harwin-smd", "HARWIN THD": "cern-harwin-thd",
    "SOURIAU THD": "cern-souriau-thd", "LEMO THD": "cern-lemo-thd",
    "FCI SMD": "cern-fci-smd", "FCI THD": "cern-fci-thd",
    "ERNI SMD": "cern-erni-smd", "ERNI THD": "cern-erni-thd",
    "WEIDMULLER THD": "cern-weidmuller-thd", "COMATEL THD": "cern-comatel-thd",
    "MENTOR THD": "cern-mentor-thd",
    "Sockets": "cern-sockets",
    "Relays": "cern-relays",
    "Fuses": "cern-fuses",
    "Switches": "cern-switches",
    "Transformers": "cern-transformers",
    "Thermistors And Varistors": "cern-thermistors-and-varistors",
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
    "ERNI_214012": "ERNI_214012 - duplicate",        # Altium export suffix
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
