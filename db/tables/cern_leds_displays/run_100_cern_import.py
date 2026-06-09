#!/usr/bin/env python3
# db/tables/cern_leds_displays/run_100_cern_import.py
"""Import CERN 'LEDs & Displays' -> cern_leds_displays_generated_100_cern_import.sql."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Make repo root importable (for tools.*) when run via Makefile (cwd = table dir)
_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))

from tools import cern_import  # noqa: E402

CERN_TABLE = "LEDs & Displays"
OUT_TABLE = "cern_leds_displays"
OUTPUT_FILE = "cern_leds_displays_generated_100_cern_import.sql"

# LED colour from the symbol name (longer phrases first). Blank for light pipes,
# bargraphs, or device-named symbols with no colour.
_COLOR = re.compile(
    r"(Red-Green|Red/Green|Bi-?Colou?r|Tri-?Colou?r|RGB|Warm White|Cool White|"
    r"Red|Green|Blue|Yellow|Amber|White|Orange|Infra-?red|\bIR\b|\bUV\b|Violet|Pink)",
    re.I)


def color_from_symbol(libsymbol: str) -> str:
    name = libsymbol.split(":", 1)[1] if ":" in libsymbol else libsymbol
    m = _COLOR.search(name)
    return m.group(1) if m else ""


def main() -> None:
    cern_import.generate(
        CERN_TABLE, OUT_TABLE, OUTPUT_FILE, "led",
        extra_cols=["color"],
        extra=lambda row: {"color": color_from_symbol(
            cern_import.clean(row.get("LibSymbol")))},
    )


if __name__ == "__main__":
    main()
