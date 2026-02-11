#!/usr/bin/env python3
"""
Yageo RT Series Thin Film Resistor Generator
Generates comprehensive E-series resistors for Terra EDA Library

This refactored version separates all specifications from generation logic.
Configuration and templates are at the top, generic generation below.

Datasheet Reference:
https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RT_L_11.pdf

RT Series Part Number Format:
RT [SIZE4] [TOL] [PACK] [TCR] [TAPE] [RV_CODE] L

Example: RT0603DRE0756RL
- RT = series
- 0603 = size
- D = ±0.5%
- R = paper tape
- E = 50 ppm
- 07 = 7" reel
- 56R = 56 Ω
- L = default suffix
"""

import math
import sys
import os
import csv
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

# ============================================================================
# ======================== USER CONFIGURATION ================================
# ============================================================================
# Modify these sections to control what gets generated

# ======================== OUTPUT CONFIGURATION ========================
OUTPUT_FILE = "resistors_smt_generated_210_yageo_rt_thin_film.sql"
OUTPUT_CSV = "resistors_smt_generated_210_yageo_rt_thin_film.csv"
GENERATE_CSV = False  # Set to True to also generate CSV for inspection

# ======================== TOLERANCE CONFIGURATION ========================
# Set to "yes" to include, anything else to exclude (case-insensitive)
TOLERANCE_ENABLE = {
    "0.1%": "yes",  # B - precision tolerance
    "0.5%": "yes",  # D - standard precision
    "1.0%": "yes",  # F - standard tolerance
}

# ======================== PACKAGE / TEMPCO CONFIGURATION ========================
# Set to "yes" to include, anything else to exclude
# Format: "PACKAGE/TEMPCO": "yes/no"
# RT series: 50ppm tempco for all packages
# Note: 2512HP is the high-power 1W variant of 2512
PACKAGE_TEMPCO_ENABLE = {
    # 0402 - 50ppm (4.7Ω to 500kΩ)
    "0402/50ppm": "yes",
    # 0603 - 50ppm (1Ω to 2MΩ)
    "0603/50ppm": "yes",
    # 0805 - 50ppm (1Ω to 3MΩ)
    "0805/50ppm": "yes",
    # 1206 - 50ppm (1Ω to 3MΩ)
    "1206/50ppm": "yes",
    # 1210 - 50ppm (4.7Ω to 1MΩ)
    "1210/50ppm": "yes",
    # 2010 - 50ppm (4.7Ω to 1MΩ)
    "2010/50ppm": "yes",
    # 2512 Standard - 50ppm, 3/4W (4.7Ω to 1MΩ)
    "2512/50ppm": "yes",
    # 2512 High-Power - 50ppm, 1W (10Ω to 1MΩ) - uses KE7W packing
    "2512HP/50ppm": "yes",
}

# ======================== E-SERIES CONFIGURATION ========================
# Which E-series to generate (values will be unioned)
E_SERIES_ENABLE = {
    "E12": "no",
    "E24": "yes",
    "E48": "no",
    "E96": "yes",
    "E192": "no",
}

# ============================================================================
# ======================== VENDOR SPECIFICATIONS =============================
# ============================================================================
# These should not need modification unless datasheet changes

# ======================== DATABASE METADATA ========================
# For dump system - generated data should have priority 0
SOURCE = None  # NULL for generated data (not dumped)
DUMP_PRIORITY = 0  # Generated data priority

# ======================== MANUFACTURER SPECIFICATION ========================
MANUFACTURER = "Yageo"
SERIES = "RT"  # Thin Film series
COMPOSITION = "Thin Film"
LIFECYCLE_STATUS = "Active"
ROHS_COMPLIANT = "Yes"
ALLOW_SUBSTITUTION = "Yes"
TRACKING = "No"

# ======================== URL TEMPLATES ========================
URL_TEMPLATES = {
    "datasheet": "https://www.yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L",
    "manufacturer_link": "https://www.yageogroup.com/products/Resistors/part/{mpn}",
    "rohs_document": "https://www.yageogroup.com/component-documentation/download/rohs/{mpn}.pdf",
}

# ======================== STRING TEMPLATES ========================
STRING_TEMPLATES = {
    # MPN template with available parameters
    # RT series: RT [SIZE] [TOL] [PACK] [TCR] [TAPE] [RV_CODE] L
    # Pack: R=paper tape, K=embossed tape
    # TCR: E=50ppm
    # Tape: 07=7" reel
    "mpn": "{series}{size}{tol}RE07{value_iec}L",
    # Description templates
    "description_jumper": "{manufacturer} {composition} jumper, 0 ohm resistor, {package} package",
    "description_resistor": "{manufacturer} {composition} resistor {value_readable} {tolerance} {power} {tempco} {package}",
    # Part locator template
    "part_locator": "res-{composition_slug}-{value_lower}-{tolerance_lower}-{power_slug}-{tempco_lower}-{package_lower}",
    # Unique ID template
    "unique_id": "{manufacturer}-{mpn}",
    "unique_id_variant": "{manufacturer}-{mpn}-{variant}",
    # Temperature spec templates
    "temp_operating_standard": "-55°C to +155°C",
    "temp_soldering": "260°C (10s max)",  # Lead-free solder reflow
    "temp_storage": "-55°C to +125°C",
}

# ======================== SQL TEMPLATES ========================
SQL_TEMPLATES = {
    "file_header": """-- {manufacturer} {series} Series {composition} Resistors
-- Series: {series_str}, Tolerance: {tolerance}
-- Datasheet: {datasheet_url}
-- Symbol: {symbol_ref}
--
-- Temperature coefficients by package and range:
{tempco_notes}
--
-- Value Formats:
-- - MPN uses manufacturer format with IEC encoding
-- - Database value uses SPICE format for simulation compatibility
-- - Booleans stored as 'yes'/'no' for KiCad compatibility

BEGIN TRANSACTION;
""",
    "package_header": "-- {package} Package ({power}, {tempco}, {working_voltage} working/{max_voltage} max)",
    "insert": """INSERT INTO resistors_smt (unique_id, part_locator, mpn, manufacturer, variant, package, value, description, datasheet, manufacturer_link, kicad_symbol, kicad_footprint, source, dump_priority, tolerance, power_rating, temp_coeff, voltage_rating, composition, temp_operating, temp_soldering, temp_storage, sim_device, sim_pins, lifecycle_status, rohs, rohs_document_link, allow_substitution, tracking, created_at, updated_at, created_by)
VALUES ('{unique_id}', '{part_locator}', '{mpn}', '{manufacturer}', {variant}, '{package}', '{value_sim}', '{description}', '{datasheet}', '{manufacturer_link}', '{kicad_symbol}', '{kicad_footprint}', {source}, {dump_priority}, '{tolerance}', '{power_rating}', '{temp_coeff}', '{voltage_rating}', '{composition}', '{temp_operating}', '{temp_soldering}', '{temp_storage}', '{sim_device}', '{sim_pins}', '{lifecycle_status}', '{rohs}', '{rohs_link}', '{allow_substitution}', '{tracking}', '{created_at}', '{updated_at}', '{created_by}');""",
    "file_footer": """COMMIT;

-- Generated {total_parts} resistor parts""",
}

# ======================== SIMULATION PARAMETERS ========================
SIMULATION = {
    "device": "R",
    "pins": "1=+ 2=-",
}

# ======================== KICAD CONFIGURATION ========================
# Symbol: Same for all resistors in this generator
# Footprint: Built from package using prefix + package + metric + suffix
KICAD_CONFIG = {
    "symbol": "Device:R_US",  # 'Device:R' (European) or 'Device:R_US' (American)
    "footprint_prefix": "Resistor_SMD:R_",
    "footprint_suffix": "Metric",
}

# Package to metric footprint mapping (EIA to metric)
PACKAGE_METRIC = {
    "0201": "0603",
    "0402": "1005",
    "0603": "1608",
    "0805": "2012",
    "1206": "3216",
    "1210": "3225",
    "1812": "4532",
    "2010": "5025",
    "2512": "6332",
}


# ======================== PRODUCT SPECIFICATIONS (SLUGS) ========================
# Each slug is a complete, self-contained specification for a specific
# combination of package/tempco/tolerance/value-range from the datasheet.
# This eliminates all conditionals from the generation loop.
#
# Slug format: {package}-{tempco}-{tolerance}-{min_value}-{max_value}
# All product knowledge is in this data structure, not in code logic.
#
# THIN FILM (RT) CHARACTERISTICS:
# - Only 50ppm TCR covered here (from yageo_RT_params.org)
# - Tolerances: 0.1%, 0.5%, 1% (all have same resistance ranges per size)
# - MPN includes TCR code (E=50ppm) unlike RC series
# - No 0Ω jumpers in thin film series

# Tolerance codes for RT series
# L = ±0.01%, P = ±0.02%, W = ±0.05%, B = ±0.1%, C = ±0.25%, D = ±0.5%, F = ±1%
TOLERANCE_CODES = {
    "0.1%": "B",
    "0.5%": "D",
    "1.0%": "F",
}

# Packing codes combine: pack type (K=embossed, R=paper) + TCR code + tape reel
# Format: {pack}{tcr}{tape}
# Examples: KE07 = embossed + 50ppm + 7" reel, KE7W = embossed + 50ppm + 7" high-power
PACKING_CODES = {
    "KE07": "Embossed tape, 50ppm TCR, 7-inch reel",
    "KE7W": "Embossed tape, 50ppm TCR, 7-inch reel high-power",
    "RE07": "Paper tape, 50ppm TCR, 7-inch reel",
    "RE7W": "Paper tape, 50ppm TCR, 7-inch reel high-power",
}

PRODUCT_SPECS = [
    # 0402 Package - 50ppm, all tolerances (4.7Ω – 500kΩ)
    {
        "slug": "0402-KE07-0.1%-4.7-500k",
        "package": "0402",
        "dimensions": "1.0mm × 0.5mm",
        "power": "1/16W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 500e3,
        "working_voltage": "50V",
        "max_voltage": "100V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "0402-KE07-0.5%-4.7-500k",
        "package": "0402",
        "dimensions": "1.0mm × 0.5mm",
        "power": "1/16W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 500e3,
        "working_voltage": "50V",
        "max_voltage": "100V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "0402-KE07-1%-4.7-500k",
        "package": "0402",
        "dimensions": "1.0mm × 0.5mm",
        "power": "1/16W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 500e3,
        "working_voltage": "50V",
        "max_voltage": "100V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 0603 Package - 50ppm, all tolerances (1Ω – 2MΩ)
    {
        "slug": "0603-KE07-0.1%-1-2M",
        "package": "0603",
        "dimensions": "1.6mm × 0.8mm",
        "power": "1/10W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 2e6,
        "working_voltage": "75V",
        "max_voltage": "150V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "0603-KE07-0.5%-1-2M",
        "package": "0603",
        "dimensions": "1.6mm × 0.8mm",
        "power": "1/10W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 2e6,
        "working_voltage": "75V",
        "max_voltage": "150V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "0603-KE07-1%-1-2M",
        "package": "0603",
        "dimensions": "1.6mm × 0.8mm",
        "power": "1/10W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 2e6,
        "working_voltage": "75V",
        "max_voltage": "150V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 0805 Package - 50ppm, all tolerances (1Ω – 3MΩ)
    {
        "slug": "0805-KE07-0.1%-1-3M",
        "package": "0805",
        "dimensions": "2.0mm × 1.25mm",
        "power": "1/8W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 3e6,
        "working_voltage": "150V",
        "max_voltage": "300V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "0805-KE07-0.5%-1-3M",
        "package": "0805",
        "dimensions": "2.0mm × 1.25mm",
        "power": "1/8W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 3e6,
        "working_voltage": "150V",
        "max_voltage": "300V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "0805-KE07-1%-1-3M",
        "package": "0805",
        "dimensions": "2.0mm × 1.25mm",
        "power": "1/8W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 3e6,
        "working_voltage": "150V",
        "max_voltage": "300V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 1206 Package - 50ppm, all tolerances (1Ω – 3MΩ)
    {
        "slug": "1206-KE07-0.1%-1-3M",
        "package": "1206",
        "dimensions": "3.2mm × 1.6mm",
        "power": "1/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 3e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "1206-KE07-0.5%-1-3M",
        "package": "1206",
        "dimensions": "3.2mm × 1.6mm",
        "power": "1/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 3e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "1206-KE07-1%-1-3M",
        "package": "1206",
        "dimensions": "3.2mm × 1.6mm",
        "power": "1/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE07",
        "min_ohm": 1.0,
        "max_ohm": 3e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 1210 Package - 50ppm, all tolerances (4.7Ω – 1MΩ)
    {
        "slug": "1210-KE07-0.1%-4.7-1M",
        "package": "1210",
        "dimensions": "3.2mm × 2.5mm",
        "power": "1/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "1210-KE07-0.5%-4.7-1M",
        "package": "1210",
        "dimensions": "3.2mm × 2.5mm",
        "power": "1/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "1210-KE07-1%-4.7-1M",
        "package": "1210",
        "dimensions": "3.2mm × 2.5mm",
        "power": "1/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 2010 Package - 50ppm, all tolerances (4.7Ω – 1MΩ)
    {
        "slug": "2010-KE07-0.1%-4.7-1M",
        "package": "2010",
        "dimensions": "5.0mm × 2.5mm",
        "power": "1/2W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "2010-KE07-0.5%-4.7-1M",
        "package": "2010",
        "dimensions": "5.0mm × 2.5mm",
        "power": "1/2W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "2010-KE07-1%-4.7-1M",
        "package": "2010",
        "dimensions": "5.0mm × 2.5mm",
        "power": "1/2W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 2512 Package Standard (3/4W) - 50ppm, all tolerances (4.7Ω – 1MΩ)
    {
        "slug": "2512-KE07-0.1%-4.7-1M",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "3/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "2512-KE07-0.5%-4.7-1M",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "3/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "2512-KE07-1%-4.7-1M",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "3/4W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE07",
        "min_ohm": 4.7,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 2512 Package High-Power (1W) - 50ppm, all tolerances (10Ω – 1MΩ)
    # Uses 7W tape code instead of 07 for high-power version
    {
        "slug": "2512HP-KE7W-0.1%-10-1M",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "1W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.1%",
        "tol_code": "B",
        "packing": "KE7W",
        "min_ohm": 10.0,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "2512HP-KE7W-0.5%-10-1M",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "1W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "0.5%",
        "tol_code": "D",
        "packing": "KE7W",
        "min_ohm": 10.0,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    {
        "slug": "2512HP-KE7W-1%-10-1M",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "1W",
        "tempco": "50ppm",
        "tempco_code": "E",
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "KE7W",
        "min_ohm": 10.0,
        "max_ohm": 1e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
]

# ============================================================================
# ======================== HELPER FUNCTIONS ==================================
# ============================================================================


def get_enabled_tolerances() -> List[str]:
    """
    Parse tolerance configuration and return enabled tolerances.

    Returns list of enabled tolerance strings (e.g., ["0.1%", "0.5%", "1.0%"]).
    """
    return [t for t, enabled in TOLERANCE_ENABLE.items() if enabled.lower() == "yes"]


def get_enabled_package_tempcos() -> List[Tuple[str, str]]:
    """
    Parse package/tempco configuration and return enabled combinations.

    Returns list of (package_key, tempco) tuples.
    Note: package_key may be "2512HP" for high-power variant.
    """
    enabled = []
    for key, value in PACKAGE_TEMPCO_ENABLE.items():
        if value.lower() == "yes":
            parts = key.split("/")
            package_key = parts[0]  # May be "2512" or "2512HP"
            tempco = parts[1]
            enabled.append((package_key, tempco))
    return enabled


def get_enabled_e_series() -> List[int]:
    """
    Parse E-series configuration and return enabled series numbers.

    Returns list of E-series numbers (e.g., [24, 96]).
    """
    series_map = {"E12": 12, "E24": 24, "E48": 48, "E96": 96, "E192": 192}
    return [
        series_map[key]
        for key, enabled in E_SERIES_ENABLE.items()
        if enabled.lower() == "yes"
    ]


def get_e_series_display_str() -> str:
    """Get display string for enabled E-series (e.g., 'E24+E96')."""
    enabled = [key for key, val in E_SERIES_ENABLE.items() if val.lower() == "yes"]
    return "+".join(sorted(enabled, key=lambda x: int(x[1:])))


def get_slug_key(spec: Dict) -> Tuple[str, str]:
    """
    Get the package/tempco key for a spec.

    Handles special case of 2512HP high-power variant.
    """
    slug = spec["slug"]
    # Check if this is a 2512HP variant (slug starts with "2512HP")
    if slug.startswith("2512HP"):
        return ("2512HP", spec["tempco"])
    else:
        return (spec["package"], spec["tempco"])


def get_enabled_specs() -> List[Dict]:
    """
    Filter PRODUCT_SPECS based on enabled package/tempco combinations.

    Returns list of spec dictionaries that match enabled configurations.
    """
    enabled_combos = get_enabled_package_tempcos()

    # Build lookup set for fast matching
    enabled_set = set(enabled_combos)

    # Filter specs - use slug key to handle 2512HP variant
    return [spec for spec in PRODUCT_SPECS if get_slug_key(spec) in enabled_set]


def get_kicad_footprint(package: str) -> str:
    """
    Get the KiCad footprint reference for a package size.

    Parameters
    ----------
    package : str
        EIA package size (e.g., "0603", "0805")

    Returns
    -------
    str
        Full KiCad footprint reference (e.g., "Resistor_SMD:R_0603_1608Metric")
    """
    metric = PACKAGE_METRIC.get(package, package)
    return f"{KICAD_CONFIG['footprint_prefix']}{package}_{metric}{KICAD_CONFIG['footprint_suffix']}"

# ======================== VALUE RANGES ========================
# Global resistance range for value generation
# This range covers all product specs; each spec filters to its own min/max
GLOBAL_MIN_OHM = 1.0  # 1Ω
GLOBAL_MAX_OHM = 10e9  # 10GΩ

# ======================== ENCODING UNITS ========================
# Units for IEC resistance encoding (symbol, exponent)
IEC_UNITS = [
    ("m", -3),  # milli-ohm
    ("R", 0),  # ohm
    ("K", 3),  # kilo-ohm
    ("M", 6),  # mega-ohm
    ("G", 9),  # giga-ohm
]

# Units for SPICE resistance encoding
SPICE_UNITS = [
    ("m", -3),  # milli-ohm
    ("", 0),  # ohm (no suffix)
    ("K", 3),  # kilo-ohm
    ("M", 6),  # mega-ohm
    ("G", 9),  # giga-ohm
]

# ============================================================================
# ==================== GENERIC GENERATION FUNCTIONS =========================
# ============================================================================


def get_script_name() -> str:
    """Get the script filename without path."""
    return Path(__file__).name


def get_last_commit_date() -> str:
    """Get the last git commit date for this script file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", __file__],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = (
                result.stdout.strip().split()[0]
                + " "
                + result.stdout.strip().split()[1]
            )
            return date_str
    except Exception:
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_build_date() -> str:
    """Get the current build date."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def encode_resistance(value_ohm: float, style: str = "iec") -> str:
    """
    Encode a resistance value in IEC, SPICE, or 4-digit format.

    Parameters
    ----------
    value_ohm : float
        Resistance value in ohms
    style : str
        'iec' for IEC 60062 format (4R7, 4K7)
        'spice' for SPICE format (4.7, 4.7K)
        '4digit' for 4-digit code (TODO: implement)

    Returns
    -------
    str
        Formatted resistance string
    """
    # Handle zero ohm jumpers
    if value_ohm == 0:
        return "0R" if style == "iec" else "0"

    if value_ohm < 0:
        raise ValueError("Resistance must be non-negative")

    # TODO: Implement 4digit encoding
    if style == "4digit":
        style = "iec"

    # Select appropriate unit list based on style
    units = IEC_UNITS if style == "iec" else SPICE_UNITS

    exp10 = math.log10(value_ohm)
    target = 3 * math.floor(exp10 / 3.0)  # nearest 10^(3n) decade

    # Pick the unit whose exponent is closest to that decade
    marker, exp = min(units, key=lambda ue: abs(ue[1] - target))

    scale = 10**exp
    scaled = value_ohm / scale  # we want 1 <= scaled < 1000

    if not (1.0 <= scaled < 1000.0):
        raise ValueError(
            f"value {value_ohm} Ω not representable with units in [1,1000)"
        )

    # Format with 3 decimal places
    s = format(scaled, ".3f")  # '4.700', '47.000', '470.000'

    if style == "iec":
        # IEC: replace decimal point with marker, then strip trailing zeros
        s = s.replace(".", marker).rstrip("0")  # '4R700' → '4R7'
    else:
        # SPICE: strip trailing zeros and decimal, then append marker
        s = s.rstrip("0").rstrip(".")  # '4.7', '47', '470'
        s = s + marker if marker else s

    return s


def generate_resistance_values_in_range(
    min_ohm: float, max_ohm: float, series: int
) -> List[float]:
    """
    Generate E-series resistance values directly in a specified range.

    E6/E12/E24: Uses lookup table (IEC 60063 standard values)
    E48/E96/E192: Uses formula with appropriate precision

    Parameters
    ----------
    min_ohm : float
        Minimum resistance value in ohms
    max_ohm : float
        Maximum resistance value in ohms
    series : int
        E-series number (6, 12, 24, 48, 96, or 192)

    Returns
    -------
    list of float
        Resistance values in ohms with standard E-series rounding
    """
    if min_ohm <= 0 or max_ohm <= 0:
        raise ValueError("Resistance values must be positive")
    if min_ohm >= max_ohm:
        raise ValueError("min_ohm must be less than max_ohm")

    # E24 lookup table (IEC 60063 standard)
    E24_TABLE = [
        1.0,
        1.1,
        1.2,
        1.3,
        1.5,
        1.6,
        1.8,
        2.0,
        2.2,
        2.4,
        2.7,
        3.0,
        3.3,
        3.6,
        3.9,
        4.3,
        4.7,
        5.1,
        5.6,
        6.2,
        6.8,
        7.5,
        8.2,
        9.1,
    ]

    # Calculate range in log space
    log_min = math.log10(min_ohm)
    log_max = math.log10(max_ohm)
    num_steps = int((log_max - log_min) * series)

    # E6/E12/E24: Use lookup table with stride
    if series in (6, 12, 24):
        stride = 24 // series
        start_decade_exp = int(math.floor(log_min))

        # Find starting table index: first E24 value in starting decade >= min_ohm
        normalized_min = min_ohm / (10**start_decade_exp)
        start_table_idx = 0
        for idx in range(0, 24, stride):
            if E24_TABLE[idx] >= normalized_min:
                start_table_idx = idx
                break

        # Adjust starting i to begin at start_table_idx
        start_i = start_table_idx // stride

        values = map(
            lambda i: float(
                f"{E24_TABLE[int((i * stride) % 24)] * (10 ** (start_decade_exp + (i * stride) // 24)):.3g}"
            ),
            range(start_i, start_i + num_steps),
        )
        return sorted(set(values))

    # E48/E96/E192: Use formula with precision
    precision = {48: ".3g", 96: ".3g", 192: ".4g"}
    if series not in precision:
        raise ValueError(f"Unsupported E-series: {series}")

    values = map(
        lambda i: float(f"{10 ** (log_min + i / series):{precision[series]}}"),
        range(num_steps),
    )

    return sorted(set(values))


def format_mpn(value_ohm: float, spec: Dict) -> str:
    """
    Generate manufacturer part number using spec template.

    Parameters
    ----------
    value_ohm : float
        Resistance value in ohms
    spec : dict
        Product specification containing all necessary fields

    Returns
    -------
    str
        Complete MPN
    """
    # Calculate value encoding
    value_iec = encode_resistance(value_ohm, style="iec")

    # Apply MPN template from spec
    mpn = spec["mpn_template"].format(
        series=SERIES,
        size=spec["package"],
        tol=spec["tol_code"],
        packing=spec["packing"],
        value_iec=value_iec,
    )

    return mpn


def format_part_locator(value_str: str, spec: Dict) -> str:
    """Generate standardized part locator from spec."""
    return STRING_TEMPLATES["part_locator"].format(
        composition_slug=COMPOSITION.lower().replace(" ", "-"),
        value_lower=value_str.lower(),
        tolerance_lower=spec["tolerance"].lower(),
        power_slug=spec["power"].replace("/", "_").lower(),
        tempco_lower=spec["tempco"].lower(),
        package_lower=spec["package"].lower(),
    )


def format_unique_id(mpn: str, variant: Optional[str] = None) -> str:
    """Generate unique ID from MPN and optional variant."""
    if variant:
        return STRING_TEMPLATES["unique_id_variant"].format(
            manufacturer=MANUFACTURER,
            mpn=mpn,
            variant=variant,
        )
    return STRING_TEMPLATES["unique_id"].format(
        manufacturer=MANUFACTURER,
        mpn=mpn,
    )


def format_description(value_ohm: float, value_readable: str, spec: Dict) -> str:
    """Generate component description from spec."""
    if value_ohm == 0:
        return STRING_TEMPLATES["description_jumper"].format(
            manufacturer=MANUFACTURER,
            composition=COMPOSITION.lower(),
            package=spec["package"],
        )
    else:
        return STRING_TEMPLATES["description_resistor"].format(
            manufacturer=MANUFACTURER,
            composition=COMPOSITION.lower(),
            value_readable=value_readable,
            tolerance=spec["tolerance"],
            power=spec["power"],
            tempco=spec["tempco"],
            package=spec["package"],
        )


def generate_spec_summary() -> str:
    """Generate product specification summary for SQL header."""
    # Group specs by package for summary
    by_package = {}
    for spec in PRODUCT_SPECS:
        pkg = spec["package"]
        # Include power for 2512 variants
        key = f"{pkg} ({spec['power']})" if pkg == "2512" else pkg
        if key not in by_package:
            by_package[key] = []
        min_str = (
            encode_resistance(spec["min_ohm"], "spice") if spec["min_ohm"] > 0 else "0"
        )
        max_str = encode_resistance(spec["max_ohm"], "spice")
        desc = f"{spec['tempco']} {spec['tolerance']} ({min_str}-{max_str})"
        by_package[key].append(desc)

    notes = []
    for pkg in sorted(by_package.keys()):
        # Deduplicate and join
        unique_descs = list(dict.fromkeys(by_package[pkg]))
        notes.append(f"-- - {pkg}: {', '.join(unique_descs)}")
    return "\n".join(notes)


def generate_resistors() -> str:
    """
    Generate resistor SQL statements based on configuration.

    Data-driven generation: all product knowledge is in PRODUCT_SPECS,
    generation loop has NO conditionals.

    Returns
    -------
    str
        Complete SQL content with INSERT statements
    """
    # Get enabled configurations
    enabled_series = get_enabled_e_series()
    series_str = get_e_series_display_str()
    specs_to_generate = get_enabled_specs()

    if not enabled_series:
        print("Warning: No E-series enabled!")
        return ""

    if not specs_to_generate:
        print("Warning: No package/tempco combinations enabled!")
        return ""

    # Generate resistance values by unioning requested E-series across global range
    resistance_values = set()
    for series_num in enabled_series:
        values = generate_resistance_values_in_range(
            GLOBAL_MIN_OHM, GLOBAL_MAX_OHM, series_num
        )
        resistance_values |= set(values)

    resistance_values = sorted(resistance_values)

    # KiCad symbol reference (same for all resistors)
    symbol_ref = KICAD_CONFIG["symbol"]

    # Get metadata
    script_name = get_script_name()
    created_date = get_last_commit_date()
    build_date = get_build_date()

    # Collect unique tolerances from specs
    tolerances = sorted(set(spec["tolerance"] for spec in PRODUCT_SPECS))
    tolerance_str = ", ".join(tolerances)

    # Build SQL header
    sql_lines = [
        SQL_TEMPLATES["file_header"].format(
            manufacturer=MANUFACTURER,
            series=SERIES,
            composition=COMPOSITION,
            series_str=series_str,
            tolerance=tolerance_str,
            datasheet_url=URL_TEMPLATES["datasheet"],
            symbol_ref=symbol_ref,
            tempco_notes=generate_spec_summary(),
        )
    ]

    total_parts = 0

    # ==== DATA-DRIVEN GENERATION LOOP (NO CONDITIONALS) ====
    # Iterate over product specs - each spec is a complete specification
    for spec in specs_to_generate:
        # Add spec header comment
        sql_lines.append(
            SQL_TEMPLATES["package_header"].format(
                package=spec["package"],
                power=spec["power"],
                tempco=spec["tempco"],
                working_voltage=spec["working_voltage"],
                max_voltage=spec["max_voltage"],
            )
        )

        # Determine which values to generate for this spec
        values_to_generate = resistance_values.copy()
        if spec["include_zero_ohm"]:
            values_to_generate = [0.0] + values_to_generate

        # Generate parts for each resistance value in range
        for resistance_ohms in values_to_generate:
            # Filter by resistance range (only conditional needed)
            if resistance_ohms == 0:
                pass  # 0Ω is allowed if include_zero_ohm is True
            elif resistance_ohms < spec["min_ohm"] or resistance_ohms > spec["max_ohm"]:
                continue  # Skip values outside range

            # ==== ALL INFORMATION FROM SPEC - NO LOGIC NEEDED ====

            # Generate MPN using spec
            mpn = format_mpn(resistance_ohms, spec)

            # Format values
            value_readable = encode_resistance(resistance_ohms, style="spice")
            value_sim = value_readable  # SPICE format

            # Generate identifiers using spec
            part_locator = format_part_locator(value_readable, spec)
            unique_id = format_unique_id(mpn)

            # Generate description using spec
            description = format_description(resistance_ohms, value_readable, spec)

            # Generate links
            manufacturer_link = URL_TEMPLATES["manufacturer_link"].format(mpn=mpn)
            rohs_link = URL_TEMPLATES["rohs_document"].format(mpn=mpn)

            # Format SQL values
            source_sql = "NULL" if SOURCE is None else f"'{SOURCE}'"
            variant_sql = "NULL"

            # Generate INSERT statement - all fields from spec
            sql_line = SQL_TEMPLATES["insert"].format(
                unique_id=unique_id,
                part_locator=part_locator,
                mpn=mpn,
                manufacturer=MANUFACTURER,
                variant=variant_sql,
                package=spec["package"],
                value_sim=value_sim,
                description=description,
                datasheet=URL_TEMPLATES["datasheet"],
                manufacturer_link=manufacturer_link,
                kicad_symbol=symbol_ref,
                kicad_footprint=get_kicad_footprint(spec["package"]),
                source=source_sql,
                dump_priority=DUMP_PRIORITY,
                tolerance=spec["tolerance"],
                power_rating=spec["power"],
                temp_coeff=spec["tempco"],
                voltage_rating=spec["working_voltage"],
                composition=COMPOSITION,
                temp_operating=spec["temp_operating"],
                temp_soldering=STRING_TEMPLATES["temp_soldering"],
                temp_storage=STRING_TEMPLATES["temp_storage"],
                sim_device=SIMULATION["device"],
                sim_pins=SIMULATION["pins"],
                lifecycle_status=LIFECYCLE_STATUS,
                rohs=ROHS_COMPLIANT,
                rohs_link=rohs_link,
                allow_substitution=ALLOW_SUBSTITUTION,
                tracking=TRACKING,
                created_at=created_date,
                updated_at=build_date,
                created_by=script_name,
            )

            sql_lines.append(sql_line)
            total_parts += 1

        sql_lines.append("")  # Blank line between specs

    # Add footer
    sql_lines.append(SQL_TEMPLATES["file_footer"].format(total_parts=total_parts))

    return "\n".join(sql_lines)


def generate_csv_data() -> List[Dict[str, str]]:
    """
    Generate CSV data for inspection and validation.

    Returns list of dictionaries with key fields for each resistor.
    """
    # Get enabled configurations
    enabled_series = get_enabled_e_series()
    specs_to_generate = get_enabled_specs()

    # Generate resistance values by unioning requested E-series across global range
    resistance_values = set()
    for series_num in enabled_series:
        values = generate_resistance_values_in_range(
            GLOBAL_MIN_OHM, GLOBAL_MAX_OHM, series_num
        )
        resistance_values |= set(values)

    resistance_values = sorted(resistance_values)

    rows = []

    # Generate CSV rows (same logic as SQL generation)
    for spec in specs_to_generate:
        values_to_generate = resistance_values.copy()
        if spec["include_zero_ohm"]:
            values_to_generate = [0.0] + values_to_generate

        for resistance_ohms in values_to_generate:
            # Filter by resistance range
            if resistance_ohms == 0:
                pass
            elif resistance_ohms < spec["min_ohm"] or resistance_ohms > spec["max_ohm"]:
                continue

            # Generate part data
            mpn = format_mpn(resistance_ohms, spec)
            value_readable = encode_resistance(resistance_ohms, style="spice")
            unique_id = format_unique_id(mpn)

            # Create CSV row
            row = {
                "slug": spec["slug"],
                "unique_id": unique_id,
                "mpn": mpn,
                "package": spec["package"],
                "tempco": spec["tempco"],
                "tolerance": spec["tolerance"],
                "power": spec["power"],
                "value_ohms": resistance_ohms,
                "value_display": value_readable,
                "min_range": spec["min_ohm"],
                "max_range": spec["max_ohm"],
                "voltage": spec["working_voltage"],
                "composition": COMPOSITION,
            }
            rows.append(row)

    return rows


def main():
    """Generate resistor SQL based on configuration."""

    # Get enabled configurations for display
    enabled_series = get_enabled_e_series()
    series_str = get_e_series_display_str()
    enabled_package_tempcos = get_enabled_package_tempcos()
    specs_to_generate = get_enabled_specs()

    # Display configuration summary
    print(f"{MANUFACTURER} {SERIES} Series {COMPOSITION} Resistor Generator")
    print("=" * 50)
    print(f"\nConfiguration:")
    print(f"  Manufacturer: {MANUFACTURER}")
    print(f"  Composition: {COMPOSITION}")
    print(f"  E-series: {series_str or '(none)'}")
    print(f"\nEnabled package/tempco combinations: {len(enabled_package_tempcos)}")
    for pkg, tempco in sorted(enabled_package_tempcos)[:10]:
        print(f"  - {pkg} / {tempco}")
    if len(enabled_package_tempcos) > 10:
        print(f"  ... and {len(enabled_package_tempcos) - 10} more")

    # Generate SQL content
    sql_content = generate_resistors()

    if not sql_content:
        print("\nNo parts generated. Check configuration.")
        sys.exit(1)

    # Write SQL file
    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        f.write(sql_content)

    print(f"\nGenerated: {OUTPUT_FILE}")

    # Generate and write CSV file if enabled
    if GENERATE_CSV:
        csv_data = generate_csv_data()
        with open(OUTPUT_CSV, "w", newline="") as f:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        print(f"Generated: {OUTPUT_CSV}")

    # Count parts
    total_parts = sql_content.count("INSERT INTO")
    print(f"\nTotal parts generated: {total_parts}")


if __name__ == "__main__":
    main()
