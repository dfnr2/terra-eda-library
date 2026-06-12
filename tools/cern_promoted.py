"""MPNs promoted out of CERN into curated terra-native tables — skipped on CERN import.

When a part is reclassified into a terra-native table (e.g. an LED driver moved to
`led_drivers`), its MPN is listed here so re-running the CERN import does not re-add it
to its old cern_* table.
"""
from __future__ import annotations

PROMOTED = {
    "STCS05DR": "led_drivers",
    "TLC5925IDW": "led_drivers",
    "TLC5971RGE": "led_drivers",
    "TLC5920DL": "led_drivers",
    "MAX3967AETG": "led_drivers",
    "NSI45015W": "led_drivers",
    "NSI50010Y": "led_drivers",
}


def is_promoted(mpn) -> bool:
    return (str(mpn).strip() if mpn is not None else "") in PROMOTED
