#!/usr/bin/env python3
"""Panasonic PhotoMOS relays: the AQY28x parts from KiCad's Relay_SolidState
library plus the GE DIP8 2 Form A family (AQW21xEH), which uses the stock LAA110
symbol (identical pinout, checked against the Panasonic catalog).

Data: panasonic_catalog.json, harvested from the Panasonic catalogs in
datasheets/panasonic/. Generated output (dump_priority=0, source=NULL) is not
dumped to static SQL.
"""
from _ssr import emit


def value_of(p):
    # The surface-mount "A" suffix is not marked on the device (AQW210EHA -> AQW210EH).
    return p["mpn"][:-1] if p["mpn"].endswith("EHA") else p["mpn"]


if __name__ == "__main__":
    emit(__file__, "panasonic_catalog.json", "PhotoMOS relay", value_of,
         "Panasonic PhotoMOS relays (AQY28x, AQW21xEH)")
