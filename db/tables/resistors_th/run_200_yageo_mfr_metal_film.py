#!/usr/bin/env python3
"""Yageo MFR Series Metal Film (axial through-hole) Resistor Generator.

Through-hole counterpart of resistors_smt/run_200_yageo_rc_thick_film.py, adapted
for the Yageo MFR general-purpose metal film axial series. Same data-driven shape:
specs at the top, generic generation below. Cross-products the axial power-variants
x enabled tolerances x E-series values.

Differences from the SMT RC generator:
  - Axial bodies instead of chip packages: each power variant maps to a KiCad DIN
    axial footprint and carries body_style (DIN code) + lead_spacing_mm (pitch).
  - MPN follows the MFR scheme: MFR<power><tol><packing><tcr><forming><value>
    e.g. MFR-25FTF52-10K (1/4W, 1%, box, 100ppm, 52mm forming, 10k).
  - Datasheet is the local PDF in the central store (not a URL).

Datasheet: datasheets/yageo/yageo_mfr.pdf (Metal Film Resistors, MFR Series, V.4).
Generated output (dump_priority=0) is not dumped back to static SQL.
"""

import math
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

OUTPUT_FILE = "resistors_th_generated_200_yageo_mfr_metal_film.sql"

# ======================== CONFIGURATION ========================
E_SERIES_ENABLE = {"E12": "no", "E24": "yes", "E48": "no", "E96": "yes", "E192": "no"}

# Tolerance code -> label; "enable" selects which to generate.
TOLERANCES = [
    {"code": "F", "label": "±1%", "enable": "yes"},
    {"code": "J", "label": "±5%", "enable": "no"},
    {"code": "D", "label": "±0.5%", "enable": "no"},
    {"code": "G", "label": "±2%", "enable": "no"},
]

# Fixed MPN slots (datasheet fields 4-5): packing T=Box, tcr F=±100ppm/°C.
PACKING = "T"
TCR_CODE = "F"
TCR_LABEL = "±100ppm/°C"

# ======================== VENDOR / METADATA ========================
MANUFACTURER = "Yageo"
SERIES = "MFR"
COMPOSITION = "Metal Film"
LIFECYCLE_STATUS = "Active"
ROHS_COMPLIANT = "Yes"
ALLOW_SUBSTITUTION = "Yes"
TRACKING = "No"
SOURCE = None          # NULL for generated data (not dumped)
DUMP_PRIORITY = 0
TIER = 2

DATASHEET = "${TERRA_EDA_LIB}/datasheets/yageo/yageo_mfr.pdf"
MANUFACTURER_LINK = "https://www.yageo.com/en/Product/Index/leadednetworks/metal_film_mfr"
SYMBOL = "Device:R_US"

# Whole-series resistance range (datasheet: 1Ω ~ 4M7Ω for E24 & E96).
MIN_OHM = 1.0
MAX_OHM = 4.7e6

# ======================== POWER / BODY VARIANTS ========================
# One entry per "Normal" axial power rating. power_code is the MFR MPN slot;
# forming is the lead-pitch slot; footprint/body_style/lead pitch are KiCad DIN
# axial bodies sized to the datasheet dimension table.
POWER_SPECS = [
    {"power_code": "-12", "power": "1/6W", "body_style": "DIN0204", "lead_spacing_mm": 5.08,
     "forming": "26-", "working_voltage": "200V", "max_voltage": "400V", "dimensions": "3.4mm x 1.9mm",
     "footprint": "Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal"},
    {"power_code": "-25", "power": "1/4W", "body_style": "DIN0207", "lead_spacing_mm": 10.16,
     "forming": "52-", "working_voltage": "250V", "max_voltage": "500V", "dimensions": "6.3mm x 2.4mm",
     "footprint": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"},
    {"power_code": "-50", "power": "1/2W", "body_style": "DIN0309", "lead_spacing_mm": 12.70,
     "forming": "52-", "working_voltage": "350V", "max_voltage": "700V", "dimensions": "9.0mm x 3.3mm",
     "footprint": "Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"},
    {"power_code": "100", "power": "1W", "body_style": "DIN0414", "lead_spacing_mm": 15.24,
     "forming": "73-", "working_voltage": "500V", "max_voltage": "1000V", "dimensions": "11.5mm x 4.5mm",
     "footprint": "Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal"},
    {"power_code": "200", "power": "2W", "body_style": "DIN0516", "lead_spacing_mm": 20.32,
     "forming": "73-", "working_voltage": "500V", "max_voltage": "1000V", "dimensions": "15.5mm x 5.0mm",
     "footprint": "Resistor_THT:R_Axial_DIN0516_L15.5mm_D5.0mm_P20.32mm_Horizontal"},
]

TEMP_OPERATING = "-55°C to +155°C"
TEMP_STORAGE = "-55°C to +155°C"
TEMP_SOLDERING = "260°C (10s max)"

IEC_UNITS = [("R", 0), ("k", 3), ("M", 6)]
SPICE_UNITS = [("", 0), ("k", 3), ("M", 6)]

INSERT = ("INSERT INTO resistors_th (unique_id, part_locator, mpn, manufacturer, "
          "variant, package, value, description, datasheet, manufacturer_link, "
          "kicad_symbol, kicad_footprint, source, dump_priority, tier, keywords, "
          "tolerance, power_rating, temp_coeff, voltage_rating, composition, "
          "lead_spacing_mm, body_style, temp_operating_min, temp_operating_max, "
          "temp_storage_min, temp_storage_max, temp_soldering, sim_device, sim_pins, "
          "lifecycle_status, rohs, rohs_document_link, allow_substitution, tracking, "
          "created_at, updated_at, created_by)\nVALUES ({vals});")


# ======================== HELPERS ========================
def parse_temp_range(s):
    nums = re.findall(r"[+-]?\d+", str(s))
    return (str(int(nums[0])), str(int(nums[1]))) if len(nums) >= 2 else ("NULL", "NULL")


def parse_temp_single(s):
    m = re.search(r"[+-]?\d+", str(s))
    return str(int(m.group())) if m else "NULL"


def encode_resistance(value_ohm: float, style: str = "iec") -> str:
    units = IEC_UNITS if style == "iec" else SPICE_UNITS
    target = 3 * math.floor(math.log10(value_ohm) / 3.0)
    marker, exp = min(units, key=lambda ue: abs(ue[1] - target))
    scaled = value_ohm / 10 ** exp
    s = format(scaled, ".3f")
    if style == "iec":
        return s.replace(".", marker).rstrip("0")   # 4.700 -> 4R700 -> 4R7; 40.000 -> 40R000 -> 40R
    s = s.rstrip("0").rstrip(".")
    return s + marker if marker else s


E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]


def e_series_values(series: int) -> List[float]:
    """E-series values across [MIN_OHM, MAX_OHM] for E24 (table) or E48/96/192 (formula)."""
    out = set()
    if series in (12, 24):
        stride = 24 // series
        decade = int(math.floor(math.log10(MIN_OHM)))
        while True:
            base = 10 ** decade
            if base > MAX_OHM:
                break
            for i in range(0, 24, stride):
                v = float(f"{E24[i] * base:.3g}")
                if MIN_OHM <= v <= MAX_OHM:
                    out.add(v)
            decade += 1
    else:
        prec = {48: ".3g", 96: ".3g", 192: ".4g"}[series]
        n = int((math.log10(MAX_OHM) - math.log10(MIN_OHM)) * series) + 1
        for i in range(n + 1):
            v = float(f"{10 ** (math.log10(MIN_OHM) + i / series):{prec}}")
            if MIN_OHM <= v <= MAX_OHM:
                out.add(v)
    return sorted(out)


def sqls(v):
    return "NULL" if v is None else ("'" + str(v).replace("'", "''") + "'")


def build() -> str:
    series_map = {"E12": 12, "E24": 24, "E48": 48, "E96": 96, "E192": 192}
    enabled_series = [series_map[k] for k, e in E_SERIES_ENABLE.items() if e.lower() == "yes"]
    # One orderable part per distinct manufacturer value code: distinct E24/E96
    # floats can share an IEC code (e.g. E24 1.1 and E96 1.10), and the MPN is
    # keyed on that code, so dedupe by code rather than by float.
    code_to_ohm = {}
    for v in sorted({v for s in enabled_series for v in e_series_values(s)}):
        code_to_ohm.setdefault(encode_resistance(v, "iec"), v)
    tols = [t for t in TOLERANCES if t["enable"].lower() == "yes"]

    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script = Path(__file__).name
    series_str = "+".join(k for k, e in E_SERIES_ENABLE.items() if e.lower() == "yes")

    lines = [
        f"-- {MANUFACTURER} {SERIES} Series {COMPOSITION} axial through-hole resistors",
        f"-- E-series: {series_str}; tolerances: {', '.join(t['label'] for t in tols)}; TCR {TCR_LABEL}",
        f"-- Datasheet: {DATASHEET}",
        f"-- Generated by {script}. dump_priority=0: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]

    to_min, to_max = parse_temp_range(TEMP_OPERATING)
    ts_min, ts_max = parse_temp_range(TEMP_STORAGE)
    t_sold = parse_temp_single(TEMP_SOLDERING)
    total = 0

    for spec in POWER_SPECS:
        lines.append(f"-- {SERIES}{spec['power_code']} ({spec['power']}, {spec['body_style']} "
                     f"{spec['dimensions']}, {spec['working_voltage']} working)")
        for tol in tols:
            for value_iec, ohm in code_to_ohm.items():
                value_spice = encode_resistance(ohm, "spice")
                mpn = f"{SERIES}{spec['power_code']}{tol['code']}{PACKING}{TCR_CODE}{spec['forming']}{value_iec}"
                unique_id = f"{MANUFACTURER}-{mpn}"
                part_locator = (f"res-metal-film-{value_spice.lower()}-{tol['label'].strip('±').lower()}"
                                f"-{spec['power'].replace('/', '_').lower()}-{spec['body_style'].lower()}")
                desc = (f"{MANUFACTURER} metal film resistor {value_spice} ohm {tol['label']} "
                        f"{spec['power']} {TCR_LABEL} axial {spec['body_style']}")
                row = [
                    unique_id, part_locator, mpn, MANUFACTURER, None,
                    f"Axial {spec['body_style']}", f"{value_spice}Ω", desc, DATASHEET,
                    MANUFACTURER_LINK, SYMBOL, spec["footprint"], SOURCE, DUMP_PRIORITY,
                    TIER, "passive", tol["label"], spec["power"], TCR_LABEL,
                    spec["working_voltage"], COMPOSITION, spec["lead_spacing_mm"],
                    spec["body_style"],
                ]
                vals = ", ".join(sqls(x) for x in row)
                vals += (f", {to_min}, {to_max}, {ts_min}, {ts_max}, {t_sold}, "
                         f"'R', '1=+ 2=-', '{LIFECYCLE_STATUS}', '{ROHS_COMPLIANT}', NULL, "
                         f"'{ALLOW_SUBSTITUTION}', '{TRACKING}', '{created}', '{created}', '{script}'")
                lines.append(INSERT.format(vals=vals))
                lines.append(f"INSERT INTO tags (unique_id, tag) VALUES ('{unique_id}', 'passive');")
                total += 1
        lines.append("")

    lines.append("COMMIT;")
    lines.append(f"\n-- Generated {total} resistor parts")
    return "\n".join(lines)


def main():
    Path(OUTPUT_FILE).write_text(build())
    parts = Path(OUTPUT_FILE).read_text().count("INSERT INTO resistors_th")
    print(f"Generated {OUTPUT_FILE}: {parts} parts "
          f"({len(POWER_SPECS)} power variants x {sum(1 for t in TOLERANCES if t['enable']=='yes')} tol)")


if __name__ == "__main__":
    main()
