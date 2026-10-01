#!/usr/bin/env python3
"""Broadcom ASSR-1218 photo-MOSFET solid-state relay (KiCad Relay_SolidState).

Data: broadcom_catalog.json, harvested from the datasheet in datasheets/broadcom/.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import re
from _ssr import emit


def value_of(p):
    # Option codes (ASSR-1218-003E) are ordering options of one device.
    return re.sub(r"-\d{3}E$", "", p["mpn"])


if __name__ == "__main__":
    emit(__file__, "broadcom_catalog.json", "photo-MOSFET relay", value_of,
         "Broadcom ASSR-1218 photo-MOSFET relay")
