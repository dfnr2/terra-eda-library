#!/usr/bin/env python3
"""
Yageo RC Series Thick Film Resistor Generator
Generates comprehensive E-series resistors for Terra EDA Library

This refactored version separates all specifications from generation logic.
Configuration and templates are at the top, generic generation below.

Datasheet Reference:
https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf
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
OUTPUT_FILE = "resistors_smt_generated_200_yageo_rc_thick_film.sql"
OUTPUT_CSV = "resistors_smt_generated_200_yageo_rc_thick_film.csv"
GENERATE_CSV = False  # Set to True to also generate CSV for inspection

# ======================== TOLERANCE CONFIGURATION ========================
# Set to "yes" to include, anything else to exclude (case-insensitive)
TOLERANCE_ENABLE = {
    "1.0%": "yes",  # F - standard tolerance for RC series
    "5.0%": "no",   # J - wider tolerance (if needed)
}

# ======================== PACKAGE / TEMPCO CONFIGURATION ========================
# Set to "yes" to include, anything else to exclude
# Format: "PACKAGE/TEMPCO": "yes/no"
# RC series: 100ppm for 10Ω-10MΩ, 200ppm for 1Ω-9.99Ω (includes 0Ω jumper)
PACKAGE_TEMPCO_ENABLE = {
    # 0201 - Only 200ppm variant available
    "0201/200ppm": "yes",
    # 0402 - Both variants
    "0402/100ppm": "yes",  # 10Ω to 10MΩ
    "0402/200ppm": "yes",  # 1Ω to 9.99Ω + 0Ω jumper
    # 0603 - Both variants
    "0603/100ppm": "yes",  # 10Ω to 10MΩ
    "0603/200ppm": "yes",  # 1Ω to 9.99Ω + 0Ω jumper
    # 0805 - Both variants
    "0805/100ppm": "yes",  # 10Ω to 10MΩ
    "0805/200ppm": "yes",  # 1Ω to 9.99Ω + 0Ω jumper
    # 1206 - Both variants
    "1206/100ppm": "yes",  # 10Ω to 10MΩ
    "1206/200ppm": "yes",  # 1Ω to 9.99Ω + 0Ω jumper
    # 2512 - Both variants
    "2512/100ppm": "yes",  # 10Ω to 10MΩ
    "2512/200ppm": "yes",  # 1Ω to 9.99Ω + 0Ω jumper
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
SERIES = "RC"  # Thick Film series
COMPOSITION = "Thick Film"
LIFECYCLE_STATUS = "Active"
ROHS_COMPLIANT = "Yes"
ALLOW_SUBSTITUTION = "Yes"
TRACKING = "No"

# ======================== URL TEMPLATES ========================
URL_TEMPLATES = {
    "datasheet": "https://www.yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L",
    "manufacturer_link": "https://www.yageogroup.com/products/Resistors/part/{mpn}",
    "rohs_document": "https://www.yageogroup.com/component-documentation/download/rohs/{mpn}.pdf",
}

# ======================== STRING TEMPLATES ========================
STRING_TEMPLATES = {
    # MPN template with available parameters
    # NOTE: RC series does NOT include tempco in MPN (always "07" in tcr_code slot)
    "mpn": "{series}{size}{tol}R-07{value_iec}L",

    # Description templates
    "description_jumper": "{manufacturer} {composition} jumper, 0 ohm resistor, {package} package",
    "description_resistor": "{manufacturer} {composition} resistor {value_readable} {tolerance} {power} {tempco} {package}",

    # Part locator template
    "part_locator": "res-{composition_slug}-{value_lower}-{tolerance_lower}-{power_slug}-{tempco_lower}-{package_lower}",

    # Unique ID template
    "unique_id": "{manufacturer}-{mpn}",
    "unique_id_variant": "{manufacturer}-{mpn}-{variant}",

    # Temperature spec templates
    "temp_operating_0201": "-55°C to +125°C",
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

    "insert": """INSERT INTO resistors_smt (unique_id, part_locator, mpn, manufacturer, variant, package, value, description, datasheet, manufacturer_link, kicad_symbol, kicad_footprint, source, dump_priority, tier, tags, tolerance, power_rating, temp_coeff, voltage_rating, composition, temp_operating, temp_soldering, temp_storage, sim_device, sim_pins, lifecycle_status, rohs, rohs_document_link, allow_substitution, tracking, created_at, updated_at, created_by)
VALUES ('{unique_id}', '{part_locator}', '{mpn}', '{manufacturer}', {variant}, '{package}', '{value_sim}', '{description}', '{datasheet}', '{manufacturer_link}', '{kicad_symbol}', '{kicad_footprint}', {source}, {dump_priority}, {tier}, '{tags}', '{tolerance}', '{power_rating}', '{temp_coeff}', '{voltage_rating}', '{composition}', '{temp_operating}', '{temp_soldering}', '{temp_storage}', '{sim_device}', '{sim_pins}', '{lifecycle_status}', '{rohs}', '{rohs_link}', '{allow_substitution}', '{tracking}', '{created_at}', '{updated_at}', '{created_by}');""",

    "tag_insert": "INSERT INTO tags (unique_id, tag) VALUES ('{unique_id}', '{tag}');",

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
# Slug format: {package}-{tempco}-{min_value}-{max_value}
# All product knowledge is in this data structure, not in code logic.
#
# THICK FILM (RC) DIFFERENCES:
# - Only 100ppm and 200ppm tempco (no 25/50ppm)
# - 0201: Only 200ppm (all values)
# - Other packages: 100ppm (10Ω-10MΩ), 200ppm (1Ω-9.99Ω, includes 0Ω)
# - MPN does NOT include tempco code (always "07" in tcr_code slot)

# Packing codes for RC series: {pack}-{tape}
# Pack: R=paper tape, K=embossed tape
# Tape: 07=7" reel, 10=10" reel, 13=13" reel
# Note: RC series does NOT include TCR code in MPN (unlike RT series)
PACKING_CODES = {
    "R-07": "Paper tape, 7-inch reel",
    "K-07": "Embossed tape, 7-inch reel",
    "R-10": "Paper tape, 10-inch reel",
    "K-10": "Embossed tape, 10-inch reel",
}

PRODUCT_SPECS = [
    # 0201 Package - 200ppm variant only (with 0Ω jumper)
    {
        "slug": "0201-R07-200ppm-1-10M",
        "package": "0201",
        "dimensions": "0.6mm × 0.3mm",
        "power": "1/20W",
        "tempco": "200ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 1.0,
        "max_ohm": 10e6,
        "working_voltage": "25V",
        "max_voltage": "50V",
        "temp_operating": "-55°C to +125°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": True,
    },

    # 0402 Package - 100ppm variant (10Ω to 10MΩ, no 0Ω)
    {
        "slug": "0402-R07-100ppm-10-10M",
        "package": "0402",
        "dimensions": "1.0mm × 0.5mm",
        "power": "1/16W",
        "tempco": "100ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 10,
        "max_ohm": 10e6,
        "working_voltage": "50V",
        "max_voltage": "100V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 0402 Package - 200ppm variant (1Ω to 9.99Ω, with 0Ω)
    {
        "slug": "0402-R07-200ppm-1-10",
        "package": "0402",
        "dimensions": "1.0mm × 0.5mm",
        "power": "1/16W",
        "tempco": "200ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 1.0,
        "max_ohm": 9.99,
        "working_voltage": "50V",
        "max_voltage": "100V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": True,
    },

    # 0603 Package - 100ppm variant (10Ω to 10MΩ, no 0Ω)
    {
        "slug": "0603-R07-100ppm-10-10M",
        "package": "0603",
        "dimensions": "1.6mm × 0.8mm",
        "power": "1/10W",
        "tempco": "100ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 10,
        "max_ohm": 10e6,
        "working_voltage": "75V",
        "max_voltage": "150V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 0603 Package - 200ppm variant (1Ω to 9.99Ω, with 0Ω)
    {
        "slug": "0603-R07-200ppm-1-10",
        "package": "0603",
        "dimensions": "1.6mm × 0.8mm",
        "power": "1/10W",
        "tempco": "200ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 1.0,
        "max_ohm": 9.99,
        "working_voltage": "75V",
        "max_voltage": "150V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": True,
    },

    # 0805 Package - 100ppm variant (10Ω to 10MΩ, no 0Ω)
    {
        "slug": "0805-R07-100ppm-10-10M",
        "package": "0805",
        "dimensions": "2.0mm × 1.25mm",
        "power": "1/8W",
        "tempco": "100ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 10,
        "max_ohm": 10e6,
        "working_voltage": "150V",
        "max_voltage": "300V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 0805 Package - 200ppm variant (1Ω to 9.99Ω, with 0Ω)
    {
        "slug": "0805-R07-200ppm-1-10",
        "package": "0805",
        "dimensions": "2.0mm × 1.25mm",
        "power": "1/8W",
        "tempco": "200ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 1.0,
        "max_ohm": 9.99,
        "working_voltage": "150V",
        "max_voltage": "300V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": True,
    },

    # 1206 Package - 100ppm variant (10Ω to 10MΩ, no 0Ω)
    {
        "slug": "1206-R07-100ppm-10-10M",
        "package": "1206",
        "dimensions": "3.2mm × 1.6mm",
        "power": "1/4W",
        "tempco": "100ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 10,
        "max_ohm": 10e6,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 1206 Package - 200ppm variant (1Ω to 9.99Ω, with 0Ω)
    {
        "slug": "1206-R07-200ppm-1-10",
        "package": "1206",
        "dimensions": "3.2mm × 1.6mm",
        "power": "1/4W",
        "tempco": "200ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 1.0,
        "max_ohm": 9.99,
        "working_voltage": "200V",
        "max_voltage": "400V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": True,
    },

    # 2512 Package - 100ppm variant (10Ω to 10MΩ, no 0Ω)
    {
        "slug": "2512-R07-100ppm-10-10M",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "1W",
        "tempco": "100ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 10,
        "max_ohm": 10e6,
        "working_voltage": "200V",
        "max_voltage": "500V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": False,
    },
    # 2512 Package - 200ppm variant (1Ω to 9.99Ω, with 0Ω)
    {
        "slug": "2512-R07-200ppm-1-10",
        "package": "2512",
        "dimensions": "6.3mm × 3.2mm",
        "power": "1W",
        "tempco": "200ppm",
        "tempco_code": "",  # Not used in RC MPN
        "tolerance": "1.0%",
        "tol_code": "F",
        "packing": "R-07",
        "min_ohm": 1.0,
        "max_ohm": 9.99,
        "working_voltage": "200V",
        "max_voltage": "500V",
        "temp_operating": "-55°C to +155°C",
        "mpn_template": "{series}{size}{tol}{packing}{value_iec}L",
        "include_zero_ohm": True,
    },
]

# ============================================================================
# ======================== HELPER FUNCTIONS ==================================
# ============================================================================


def get_enabled_tolerances() -> List[str]:
    """
    Parse tolerance configuration and return enabled tolerances.

    Returns list of enabled tolerance strings (e.g., ["1.0%"]).
    """
    return [t for t, enabled in TOLERANCE_ENABLE.items() if enabled.lower() == "yes"]


def get_enabled_package_tempcos() -> List[Tuple[str, str]]:
    """
    Parse package/tempco configuration and return enabled combinations.

    Returns list of (package, tempco) tuples.
    """
    enabled = []
    for key, value in PACKAGE_TEMPCO_ENABLE.items():
        if value.lower() == "yes":
            parts = key.split("/")
            package = parts[0]
            tempco = parts[1]
            enabled.append((package, tempco))
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


def get_enabled_specs() -> List[Dict]:
    """
    Filter PRODUCT_SPECS based on enabled package/tempco combinations.

    Returns list of spec dictionaries that match enabled configurations.
    """
    enabled_combos = get_enabled_package_tempcos()

    # Build lookup set for fast matching
    enabled_set = set(enabled_combos)

    # Filter specs
    return [
        spec
        for spec in PRODUCT_SPECS
        if (spec["package"], spec["tempco"]) in enabled_set
    ]


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
GLOBAL_MIN_OHM = 1.0       # 1Ω
GLOBAL_MAX_OHM = 10e9      # 10GΩ

# ======================== ENCODING UNITS ========================
# Units for IEC resistance encoding (symbol, exponent)
IEC_UNITS = [
    ("m", -3),  # milli-ohm
    ("R", 0),   # ohm
    ("K", 3),   # kilo-ohm
    ("M", 6),   # mega-ohm
    ("G", 9),   # giga-ohm
]

# Units for SPICE resistance encoding
SPICE_UNITS = [
    ("m", -3),  # milli-ohm
    ("", 0),    # ohm (no suffix)
    ("K", 3),   # kilo-ohm
    ("M", 6),   # mega-ohm
    ("G", 9),   # giga-ohm
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
            date_str = result.stdout.strip().split()[0] + " " + result.stdout.strip().split()[1]
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
        raise ValueError(f"value {value_ohm} Ω not representable with units in [1,1000)")

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


def generate_resistance_values_in_range(min_ohm: float, max_ohm: float, series: int) -> List[float]:
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
    E24_TABLE = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4,
                 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2,
                 6.8, 7.5, 8.2, 9.1]

    # Calculate range in log space
    log_min = math.log10(min_ohm)
    log_max = math.log10(max_ohm)
    num_steps = int((log_max - log_min) * series)

    # E6/E12/E24: Use lookup table with stride
    if series in (6, 12, 24):
        stride = 24 // series
        start_decade_exp = int(math.floor(log_min))

        # Find starting table index: first E24 value in starting decade >= min_ohm
        normalized_min = min_ohm / (10 ** start_decade_exp)
        start_table_idx = 0
        for idx in range(0, 24, stride):
            if E24_TABLE[idx] >= normalized_min:
                start_table_idx = idx
                break

        # Adjust starting i to begin at start_table_idx
        start_i = start_table_idx // stride

        values = map(
            lambda i: float(f"{E24_TABLE[int((i * stride) % 24)] * (10 ** (start_decade_exp + (i * stride) // 24)):.3g}"),
            range(start_i, start_i + num_steps)
        )
        return sorted(set(values))

    # E48/E96/E192: Use formula with precision
    precision = {48: ".3g", 96: ".3g", 192: ".4g"}
    if series not in precision:
        raise ValueError(f"Unsupported E-series: {series}")

    values = map(
        lambda i: float(f"{10 ** (log_min + i / series):{precision[series]}}"),
        range(num_steps)
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

    # Apply MPN template from spec (RC series doesn't use tempco in MPN)
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
        if pkg not in by_package:
            by_package[pkg] = []
        min_str = encode_resistance(spec["min_ohm"], "spice") if spec["min_ohm"] > 0 else "0"
        max_str = encode_resistance(spec["max_ohm"], "spice")
        desc = f"{spec['tempco']} ({min_str}-{max_str})"
        if spec["include_zero_ohm"]:
            desc += " +0Ω"
        by_package[pkg].append(desc)

    notes = []
    for pkg in sorted(by_package.keys()):
        notes.append(f"-- - {pkg}: {', '.join(by_package[pkg])}")
    return '\n'.join(notes)


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

    # Generate resistance values by unioning all enabled E-series
    resistance_values = set()
    for series_num in enabled_series:
        values = generate_resistance_values_in_range(
            GLOBAL_MIN_OHM, GLOBAL_MAX_OHM, series_num
        )
        resistance_values |= set(values)

    resistance_values = sorted(resistance_values)

    # Tier is determined by package size, not E-series origin
    PACKAGE_TIER = {
        "0603": 0, "0805": 0,
        "0402": 1, "1206": 1,
        "0201": 2, "2512": 2,
    }

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
    sql_lines = [SQL_TEMPLATES["file_header"].format(
        manufacturer=MANUFACTURER,
        series=SERIES,
        composition=COMPOSITION,
        series_str=series_str,
        tolerance=tolerance_str,
        datasheet_url=URL_TEMPLATES["datasheet"],
        symbol_ref=symbol_ref,
        tempco_notes=generate_spec_summary(),
    )]

    total_parts = 0

    # ==== DATA-DRIVEN GENERATION LOOP (NO CONDITIONALS) ====
    # Iterate over product specs - each spec is a complete specification
    for spec in specs_to_generate:
        # Add spec header comment
        sql_lines.append(SQL_TEMPLATES["package_header"].format(
            package=spec["package"],
            power=spec["power"],
            tempco=spec["tempco"],
            working_voltage=spec["working_voltage"],
            max_voltage=spec["max_voltage"],
        ))

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

            # Tier by package size (0Ω jumpers same tier as their package)
            part_tier = PACKAGE_TIER.get(spec["package"], 2)

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
                tier=part_tier,
                tags='passive',
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
            sql_lines.append(SQL_TEMPLATES["tag_insert"].format(
                unique_id=unique_id, tag='passive'))
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
        with open(OUTPUT_CSV, "w", newline='') as f:
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
