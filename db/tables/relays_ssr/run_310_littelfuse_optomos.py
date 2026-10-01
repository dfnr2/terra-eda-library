#!/usr/bin/env python3
"""Littelfuse (formerly IXYS) OptoMOS relays from KiCad's Relay_SolidState
library: CPC10xx 1 Form A, CPC11xx 1 Form B, CPC20xx/CPC2125 dual, and the
LAA110 / LBB110 / LCC110 DIP-8 relays.

Data: littelfuse_a_catalog.json (CPC10xx) and littelfuse_b_catalog.json (the
rest), harvested from the datasheets in datasheets/littelfuse/. Generated output
(dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import re
from _ssr import emit


def value_of(p):
    # LAA110S / LAA110P are package variants of LAA110.
    m = re.match(r"^(L[ABC][ABC]\d+)[SP]$", p["mpn"])
    return m.group(1) if m else p["mpn"]


if __name__ == "__main__":
    emit(__file__, ["littelfuse_a_catalog.json", "littelfuse_b_catalog.json"],
         "OptoMOS relay", value_of, "Littelfuse OptoMOS relays (CPC, LAA/LBB/LCC)")
