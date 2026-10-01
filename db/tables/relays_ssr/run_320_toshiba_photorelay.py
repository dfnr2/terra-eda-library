#!/usr/bin/env python3
"""Toshiba MOSFET photorelays from KiCad's Relay_SolidState library (TLP175A,
TLP222A, TLP222A-2, TLP3123, TLP3542-TLP3546).

Data: toshiba_catalog.json, harvested from the datasheets in datasheets/toshiba/.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import re
from _ssr import emit


def value_of(p):
    # Lead-form options are package variants of one device: TLP222A(LF1) -> TLP222A.
    return re.sub(r"\(.*\)$", "", p["mpn"])


if __name__ == "__main__":
    emit(__file__, "toshiba_catalog.json", "photorelay", value_of,
         "Toshiba MOSFET photorelays")
