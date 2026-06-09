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

# LED colour from the symbol name (longer phrases first), used only to fill the
# gaps where CERN's dedicated Color column is blank.
_COLOR = re.compile(
    r"(Red-Green|Red/Green|Bi-?Colou?r|Tri-?Colou?r|RGB|Warm White|Cool White|"
    r"Red|Green|Blue|Yellow|Amber|White|Orange|Infra-?red|\bIR\b|\bUV\b|Violet|Pink)",
    re.I)
# Peak wavelength stated in the description, e.g. "590nm" -> "590".
_NM = re.compile(r"(\d{3,4})\s*nm", re.I)

# Tail columns. color + wavelength_nm come from CERN; the electrical/optical
# parameters below are NOT in the CERN database — they are datasheet values, left
# blank here and populated by the datasheet sweep.
EXTRA_COLS = ["color", "wavelength_nm", "luminous_intensity",
              "forward_voltage_v", "current_max_ma"]


def color_from_symbol(libsymbol: str) -> str:
    name = libsymbol.split(":", 1)[1] if ":" in libsymbol else libsymbol
    m = _COLOR.search(name)
    return m.group(1) if m else ""


def tail(row: dict) -> dict:
    clean = cern_import.clean
    color = clean(row.get("Color")) or color_from_symbol(clean(row.get("LibSymbol")))
    nm = _NM.search(clean(row.get("Part Description")))
    return {
        "color": color,
        "wavelength_nm": nm.group(1) if nm else "",
        "luminous_intensity": "",   # datasheet parameter
        "forward_voltage_v": "",    # datasheet parameter
        "current_max_ma": "",       # datasheet parameter
    }


def main() -> None:
    cern_import.generate(CERN_TABLE, OUT_TABLE, OUTPUT_FILE, "led",
                         extra_cols=EXTRA_COLS, extra=tail)


if __name__ == "__main__":
    main()
