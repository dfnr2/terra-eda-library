#!/usr/bin/env python3
"""Littelfuse (formerly IXYS) OptoMOS relays from KiCad's Relay_SolidState
library: CPC10xx 1 Form A, CPC11xx 1 Form B, CPC20xx/CPC2125 dual, and the
LAA110 / LBB110 / LCC110 DIP-8 relays, plus the current-limited LAA110L (on
the stock LAA110 symbol; identical pinout).

Data: littelfuse_a_catalog.json (CPC10xx), littelfuse_b_catalog.json (CPC11xx,
CPC2xxx, LAA/LBB/LCC110) and littelfuse_c_catalog.json (LAA110L), harvested
from the datasheets in datasheets/littelfuse/. Generated output (dump_priority=0,
source=NULL) is not dumped to static SQL.
"""
import re
from _ssr import emit


def value_of(p):
    # S (surface mount) and P (flatpack) are package variants: LAA110S -> LAA110,
    # LAA110PL / LAA110LS -> LAA110L (L = current-limited).
    m = re.match(r"^(L[ABC][ABC]\d+)P?(L?)S?$", p["mpn"])
    return m.group(1) + m.group(2) if m else p["mpn"]


if __name__ == "__main__":
    emit(__file__, ["littelfuse_a_catalog.json", "littelfuse_b_catalog.json",
          "littelfuse_c_catalog.json"],
         "OptoMOS relay", value_of, "Littelfuse OptoMOS relays (CPC, LAA/LBB/LCC)")
