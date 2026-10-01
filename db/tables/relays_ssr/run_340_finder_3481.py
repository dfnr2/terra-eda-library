#!/usr/bin/env python3
"""Finder 34.81 ultra-slim solid-state relays with DC output (KiCad
Relay_SolidState 34.81-7048 / 34.81-9024). Voltage-driven modules: the input
range is in control_voltage and the LED columns stay empty.

Data: finder_catalog.json, harvested from the datasheet in datasheets/finder/.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from _ssr import emit


def value_of(p):
    return p["mpn"]


if __name__ == "__main__":
    emit(__file__, "finder_catalog.json", "SSR module", value_of,
         "Finder 34.81 DC-output solid-state relays")
