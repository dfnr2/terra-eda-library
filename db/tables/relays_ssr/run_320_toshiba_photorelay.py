#!/usr/bin/env python3
"""Toshiba MOSFET photorelays from KiCad's Relay_SolidState library (TLP175A,
TLP222A, TLP222A-2, TLP3123, TLP3542-TLP3546) and Toshiba's named replacements
for the discontinued ones (TLP3122A, TLP3543A, TLP3545A, TLP3546A, TLP176AM),
which reuse the stock symbol of a part with the identical pinout.

Data: toshiba_catalog.json (KiCad parts) and toshiba_b_catalog.json
(replacements), harvested from the datasheets in datasheets/toshiba/.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import re
from _ssr import emit


def value_of(p):
    # Lead-form options are package variants of one device: TLP222A(LF1) -> TLP222A.
    return re.sub(r"\(.*\)$", "", p["mpn"])


if __name__ == "__main__":
    emit(__file__, ["toshiba_catalog.json", "toshiba_b_catalog.json"], "photorelay", value_of,
         "Toshiba MOSFET photorelays")
