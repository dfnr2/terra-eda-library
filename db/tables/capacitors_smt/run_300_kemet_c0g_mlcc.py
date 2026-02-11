#!/usr/bin/env python3
"""
KEMET C0G (NP0) SMD MLCC Capacitor Generator
Generates comprehensive capacitor parts for Terra EDA Library

This script separates all specifications from generation logic.
Configuration and templates are at the top, generic generation below.

Datasheet Reference:
https://www.yageogroup.com/content/datasheet/asset/file/KEM_C1003_C0G_SMD

C0G Series Part Number Format:
C [SIZE] C [CAP_CODE] [TOL] [VOLTAGE] G A C [PACKAGING]

Example: C1206C104J3GACTU
- C = Ceramic
- 1206 = Case Size (EIA)
- C = Standard Series
- 104 = Capacitance Code (pF)
- J = ±5% Tolerance
- 3 = 25V
- G = C0G Dielectric
- A = N/A (Failure Rate/Design)
- C = 100% Matte Sn Termination
- TU = 7" Reel Packaging
"""

import math
import sys
import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

# ============================================================================
# ======================== USER CONFIGURATION ================================
# ============================================================================
# Modify these sections to control what gets generated

# ======================== OUTPUT CONFIGURATION ========================
OUTPUT_FILE = "capacitors_smt_generated_300_kemet_c0g_mlcc.sql"
OUTPUT_CSV = "capacitors_smt_generated_300_kemet_c0g_mlcc.csv"
GENERATE_CSV = False  # Set to True to also generate CSV for inspection

# ======================== PACKAGING CONFIGURATION ========================
# Available options: "" (bulk bag), "TU" (7" reel), "7411" (13" reel ≤0603), "7210" (13" reel ≥0805)
# Default: "TU" (7" reel) - most common for pick-and-place
DEFAULT_PACKAGING = "TU"

# ======================== TOLERANCE CONFIGURATION ========================
# Set to "yes" to include, anything else to exclude (case-insensitive)
# Absolute tolerances (for small pF values):
TOLERANCE_ABSOLUTE_ENABLE = {
    "0.10pF": "no",  # B - very tight, specialty
    "0.25pF": "no",  # C - tight tolerance
    "0.5pF": "yes",  # D - common for RF/precision
}

# Percentage tolerances (for values ≥ 10pF):
TOLERANCE_PERCENT_ENABLE = {
    "1%": "no",  # F - precision
    "2%": "no",  # G - precision
    "5%": "yes",  # J - standard/common
    "10%": "yes",  # K - standard
    "20%": "no",  # M - wide tolerance
}

# ======================== CASE SIZE / VOLTAGE CONFIGURATION ========================
# Set to "yes" to include, anything else to exclude
# Format: "SIZE/VOLTAGE": "yes/no"
# Based on Table 1A, 1B, 1C availability from datasheet

CASE_VOLTAGE_ENABLE = {
    # 0201 - Limited voltage range
    "0201/10V": "no",
    "0201/16V": "no",
    "0201/25V": "no",
    # 0402 - Full voltage range
    "0402/10V": "no",
    "0402/16V": "yes",
    "0402/25V": "yes",
    "0402/50V": "yes",
    "0402/100V": "yes",
    "0402/200V": "no",
    "0402/250V": "no",
    # 0603 - Full voltage range
    "0603/10V": "no",
    "0603/16V": "yes",
    "0603/25V": "yes",
    "0603/50V": "yes",
    "0603/100V": "yes",
    "0603/200V": "no",
    "0603/250V": "no",
    # 0805 - Full voltage range
    "0805/10V": "no",
    "0805/16V": "yes",
    "0805/25V": "yes",
    "0805/50V": "yes",
    "0805/100V": "yes",
    "0805/200V": "no",
    "0805/250V": "no",
    # 1206 - Full voltage range
    "1206/10V": "no",
    "1206/16V": "yes",
    "1206/25V": "yes",
    "1206/50V": "yes",
    "1206/100V": "yes",
    "1206/200V": "no",
    "1206/250V": "no",
    # 1210 - Full voltage range
    "1210/10V": "no",
    "1210/16V": "yes",
    "1210/25V": "yes",
    "1210/50V": "yes",
    "1210/100V": "yes",
    "1210/200V": "no",
    "1210/250V": "no",
    # 1805 - Higher voltages only
    "1805/50V": "no",
    "1805/100V": "no",
    "1805/200V": "no",
    # 1808 - Higher voltages only
    "1808/50V": "no",
    "1808/100V": "no",
    "1808/200V": "no",
    "1808/250V": "no",
    # 1812 - Higher voltages only
    "1812/50V": "no",
    "1812/100V": "no",
    "1812/200V": "no",
    "1812/250V": "no",
    # 1825 - Higher voltages only
    "1825/50V": "no",
    "1825/100V": "no",
    "1825/200V": "no",
    "1825/250V": "no",
    # 2220 - Higher voltages only
    "2220/50V": "no",
    "2220/100V": "no",
    "2220/200V": "no",
    # 2225 - Higher voltages only
    "2225/50V": "no",
    "2225/100V": "no",
    "2225/200V": "no",
    "2225/250V": "no",
}

# ============================================================================
# ======================== VENDOR SPECIFICATIONS =============================
# ============================================================================
# These should not need modification unless datasheet changes

# ======================== DATABASE METADATA ========================
SOURCE = None  # NULL for generated data (not dumped separately)
DUMP_PRIORITY = 0  # Generated data priority

# ======================== MANUFACTURER SPECIFICATION ========================
MANUFACTURER = "KEMET"
SERIES = "C"  # Standard ceramic series
DIELECTRIC = "C0G"
CAP_TYPE = "MLCC"
LIFECYCLE_STATUS = "Active"
ROHS_COMPLIANT = "Yes"
ALLOW_SUBSTITUTION = "Yes"
TRACKING = "No"
POLARIZED = "No"

# ======================== URL TEMPLATES ========================
URL_TEMPLATES = {
    "datasheet": "https://www.yageogroup.com/content/datasheet/asset/file/KEM_C1003_C0G_SMD",
    "manufacturer_link": "https://www.yageogroup.com/products/Capacitors/part/{mpn}",
    "rohs_document": "https://www.yageogroup.com/component-documentation/download/rohs/{mpn}",
}

# ======================== STRING TEMPLATES ========================
STRING_TEMPLATES = {
    # MPN template: C [SIZE] C [CAP_CODE] [TOL] [VOLTAGE] G A C [PACKAGING]
    "mpn": "C{size}C{cap_code}{tol_code}{voltage_code}GAC{packaging}",
    # Description templates
    "description": "{manufacturer} {cap_type} capacitor {value_readable} {tolerance} {voltage}V {dielectric} {package}",
    # Part locator template (for finding equivalent parts)
    "part_locator": "cap-{cap_type_slug}-{dielectric_slug}-{value_lower}-{tolerance_lower}-{voltage}v-{package_lower}",
    # Unique ID template
    "unique_id": "{manufacturer}-{mpn}",
    # Temperature specs from datasheet
    "temp_operating": "-55°C to +125°C",
    "temp_soldering": "260°C (10s max)",
    "temp_storage": "-55°C to +125°C",
}

# ======================== SQL TEMPLATES ========================
SQL_TEMPLATES = {
    "file_header": """-- {manufacturer} {series} Series {dielectric} {cap_type} Capacitors
-- Dielectric: {dielectric}, Tolerances: {tolerances}
-- Datasheet: {datasheet_url}
-- Symbol: {symbol_ref}
--
-- Capacitance ranges by case size:
{cap_range_notes}
--
-- Value Formats:
-- - MPN uses manufacturer capacitance code (pF-based)
-- - Database value uses SPICE notation (p, n, u suffixes)
-- - Booleans stored as 'Yes'/'No' for KiCad compatibility

BEGIN TRANSACTION;
""",
    "spec_header": "-- {package} Package, {voltage}V, {tolerance} ({cap_min} to {cap_max})",
    "insert": """INSERT INTO capacitors_smt (unique_id, part_locator, mpn, manufacturer, package, value, description, datasheet, manufacturer_link, kicad_symbol, kicad_footprint, source, dump_priority, voltage_rating_v, tolerance, cap_type, dielectric_class, polarized, temp_operating, temp_soldering, temp_storage, lifecycle_status, rohs, rohs_document_link, allow_substitution, tracking, created_at, updated_at, created_by, height_max_mm)
VALUES ('{unique_id}', '{part_locator}', '{mpn}', '{manufacturer}', '{package}', '{value_spice}', '{description}', '{datasheet}', '{manufacturer_link}', '{kicad_symbol}', '{kicad_footprint}', {source}, {dump_priority}, {voltage_rating}, '{tolerance}', '{cap_type}', '{dielectric_class}', '{polarized}', '{temp_operating}', '{temp_soldering}', '{temp_storage}', '{lifecycle_status}', '{rohs}', '{rohs_link}', '{allow_substitution}', '{tracking}', '{created_at}', '{updated_at}', '{created_by}', {height_max_mm});""",
    "file_footer": """COMMIT;

-- Generated {total_parts} capacitor parts""",
}

# ======================== SIMULATION PARAMETERS ========================
SIMULATION = {
    "device": "C",
    "pins": "1 2",
}

# ======================== KICAD CONFIGURATION ========================
KICAD_CONFIG = {
    "symbol": "Device:C",
    "footprint_prefix": "Capacitor_SMD:C_",
    "footprint_suffix": "Metric",
}

# ======================== ENCODING TABLES ========================

# Tolerance code mapping
TOLERANCE_CODES = {
    # Absolute tolerances
    "0.10pF": "B",
    "0.25pF": "C",
    "0.5pF": "D",
    # Percentage tolerances
    "1%": "F",
    "2%": "G",
    "5%": "J",
    "10%": "K",
    "20%": "M",
}

# Voltage code mapping
VOLTAGE_CODES = {
    10: "8",
    16: "4",
    25: "3",
    50: "5",
    100: "1",
    200: "2",
    250: "A",
}

# Case size to metric footprint mapping
CASE_SIZE_METRIC = {
    "0201": "0603",
    "0402": "1005",
    "0603": "1608",
    "0805": "2012",
    "1206": "3216",
    "1210": "3225",
    "1805": "4512",
    "1808": "4520",
    "1812": "4532",
    "1825": "4564",
    "2220": "5650",
    "2225": "5664",
}

# ======================== PRODUCT SPECIFICATIONS ========================
# Each spec defines a complete product slug for one combination of:
# case size, voltage, tolerance type, and capacitance range
#
# Capacitance ranges are derived from Tables 1A, 1B, 1C in datasheet
# Note: Absolute tolerances (B, C, D) only apply to values < 10pF
#       Percentage tolerances (F, G, J, K, M) apply to values >= 10pF

# Base specifications per case size / voltage combination
# These define the capacitance ranges available
# Tolerance slugs are generated programmatically from these

CASE_VOLTAGE_SPECS = {
    # 0201 - Very limited range
    ("0201", 10): {"min_pf": 0.5, "max_pf": 100, "has_fractional": True},
    ("0201", 16): {"min_pf": 0.5, "max_pf": 100, "has_fractional": True},
    ("0201", 25): {"min_pf": 0.5, "max_pf": 100, "has_fractional": True},
    # 0402 - Good range
    ("0402", 10): {"min_pf": 0.5, "max_pf": 2200, "has_fractional": True},
    ("0402", 16): {"min_pf": 0.5, "max_pf": 2200, "has_fractional": True},
    ("0402", 25): {"min_pf": 0.5, "max_pf": 2200, "has_fractional": True},
    ("0402", 50): {"min_pf": 0.5, "max_pf": 1000, "has_fractional": True},
    ("0402", 100): {"min_pf": 0.5, "max_pf": 330, "has_fractional": True},
    ("0402", 200): {"min_pf": 0.5, "max_pf": 330, "has_fractional": True},
    ("0402", 250): {"min_pf": 0.5, "max_pf": 330, "has_fractional": True},
    # 0603 - Wide range
    ("0603", 10): {"min_pf": 0.5, "max_pf": 15000, "has_fractional": True},
    ("0603", 16): {"min_pf": 0.5, "max_pf": 15000, "has_fractional": True},
    ("0603", 25): {"min_pf": 0.5, "max_pf": 10000, "has_fractional": True},
    ("0603", 50): {"min_pf": 0.5, "max_pf": 5600, "has_fractional": True},
    ("0603", 100): {"min_pf": 0.5, "max_pf": 2200, "has_fractional": True},
    ("0603", 200): {"min_pf": 0.5, "max_pf": 2200, "has_fractional": True},
    ("0603", 250): {"min_pf": 0.5, "max_pf": 2200, "has_fractional": True},
    # 0805 - Wide range
    ("0805", 10): {"min_pf": 0.5, "max_pf": 47000, "has_fractional": True},
    ("0805", 16): {"min_pf": 0.5, "max_pf": 47000, "has_fractional": True},
    ("0805", 25): {"min_pf": 0.5, "max_pf": 33000, "has_fractional": True},
    ("0805", 50): {"min_pf": 0.5, "max_pf": 15000, "has_fractional": True},
    ("0805", 100): {"min_pf": 0.5, "max_pf": 8200, "has_fractional": True},
    ("0805", 200): {"min_pf": 0.5, "max_pf": 8200, "has_fractional": True},
    ("0805", 250): {"min_pf": 0.5, "max_pf": 8200, "has_fractional": True},
    # 1206 - Wide range
    ("1206", 10): {"min_pf": 1.0, "max_pf": 100000, "has_fractional": True},
    ("1206", 16): {"min_pf": 1.0, "max_pf": 100000, "has_fractional": True},
    ("1206", 25): {"min_pf": 1.0, "max_pf": 82000, "has_fractional": True},
    ("1206", 50): {"min_pf": 1.0, "max_pf": 47000, "has_fractional": True},
    ("1206", 100): {"min_pf": 1.0, "max_pf": 22000, "has_fractional": True},
    ("1206", 200): {"min_pf": 1.0, "max_pf": 22000, "has_fractional": True},
    ("1206", 250): {"min_pf": 1.0, "max_pf": 22000, "has_fractional": True},
    # 1210 - Wide range, higher capacitance
    ("1210", 10): {"min_pf": 1.0, "max_pf": 220000, "has_fractional": True},
    ("1210", 16): {"min_pf": 1.0, "max_pf": 220000, "has_fractional": True},
    ("1210", 25): {"min_pf": 1.0, "max_pf": 150000, "has_fractional": True},
    ("1210", 50): {"min_pf": 1.0, "max_pf": 100000, "has_fractional": True},
    ("1210", 100): {"min_pf": 1.0, "max_pf": 68000, "has_fractional": True},
    ("1210", 200): {"min_pf": 1.0, "max_pf": 33000, "has_fractional": True},
    ("1210", 250): {"min_pf": 1.0, "max_pf": 22000, "has_fractional": True},
    # 1805 - Higher voltage focus
    ("1805", 50): {"min_pf": 220, "max_pf": 2700, "has_fractional": False},
    ("1805", 100): {"min_pf": 220, "max_pf": 2700, "has_fractional": False},
    ("1805", 200): {"min_pf": 220, "max_pf": 2700, "has_fractional": False},
    # 1808 - Higher voltage/capacitance
    ("1808", 50): {"min_pf": 330, "max_pf": 56000, "has_fractional": False},
    ("1808", 100): {"min_pf": 330, "max_pf": 56000, "has_fractional": False},
    ("1808", 200): {"min_pf": 330, "max_pf": 33000, "has_fractional": False},
    ("1808", 250): {"min_pf": 330, "max_pf": 33000, "has_fractional": False},
    # 1812 - Higher voltage/capacitance
    ("1812", 50): {"min_pf": 330, "max_pf": 180000, "has_fractional": False},
    ("1812", 100): {"min_pf": 330, "max_pf": 100000, "has_fractional": False},
    ("1812", 200): {"min_pf": 330, "max_pf": 68000, "has_fractional": False},
    ("1812", 250): {"min_pf": 330, "max_pf": 47000, "has_fractional": False},
    # 1825 - Large case, high capacitance
    ("1825", 50): {"min_pf": 3900, "max_pf": 270000, "has_fractional": False},
    ("1825", 100): {"min_pf": 3900, "max_pf": 270000, "has_fractional": False},
    ("1825", 200): {"min_pf": 5600, "max_pf": 270000, "has_fractional": False},
    ("1825", 250): {"min_pf": 5600, "max_pf": 270000, "has_fractional": False},
    # 2220 - Large case
    ("2220", 50): {"min_pf": 4700, "max_pf": 470000, "has_fractional": False},
    ("2220", 100): {"min_pf": 6800, "max_pf": 330000, "has_fractional": False},
    ("2220", 200): {"min_pf": 6800, "max_pf": 220000, "has_fractional": False},
    # 2225 - Largest case
    ("2225", 50): {"min_pf": 4700, "max_pf": 33000, "has_fractional": False},
    ("2225", 100): {"min_pf": 4700, "max_pf": 33000, "has_fractional": False},
    ("2225", 200): {"min_pf": 4700, "max_pf": 27000, "has_fractional": False},
    ("2225", 250): {"min_pf": 4700, "max_pf": 15000, "has_fractional": False},
}

# E24 capacitance values (standard decade multipliers)
E24_VALUES = [
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

# Fractional pF values (special encoding, values < 10pF)
FRACTIONAL_PF_VALUES = [
    0.5,
    0.75,  # Sub-pF range (use 8 multiplier code)
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
    9.1,  # 1-9.9 pF range (use 9 multiplier code)
]


# ============================================================================
# ======================== HELPER FUNCTIONS ==================================
# ============================================================================


def get_enabled_tolerances() -> Dict[str, List[str]]:
    """
    Parse tolerance configuration and return enabled tolerances.

    Returns dict with 'absolute' and 'percent' keys containing lists of enabled tolerances.
    """
    absolute = [
        t
        for t, enabled in TOLERANCE_ABSOLUTE_ENABLE.items()
        if enabled.lower() == "yes"
    ]
    percent = [
        t for t, enabled in TOLERANCE_PERCENT_ENABLE.items() if enabled.lower() == "yes"
    ]
    return {"absolute": absolute, "percent": percent}


def get_enabled_case_voltages() -> List[Tuple[str, int]]:
    """
    Parse case/voltage configuration and return enabled combinations.

    Returns list of (case_size, voltage) tuples.
    """
    enabled = []
    for key, value in CASE_VOLTAGE_ENABLE.items():
        if value.lower() == "yes":
            parts = key.split("/")
            case_size = parts[0]
            voltage = int(parts[1].replace("V", ""))
            enabled.append((case_size, voltage))
    return enabled


def get_script_name() -> str:
    """Get the script filename without path."""
    return Path(__file__).name


def get_build_date() -> str:
    """Get the current build date."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def encode_capacitance_mpn(value_pf: float) -> str:
    """
    Encode capacitance value into KEMET MPN format (3-character code).

    Rules from datasheet:
    - 0.5-0.99 pF: Use 8 as multiplier (e.g., 0.5pF = 508)
    - 1.0-9.9 pF: Use 9 as multiplier (e.g., 2.2pF = 229)
    - 10+ pF: Standard EIA code (2 digits + zeros count)

    Parameters
    ----------
    value_pf : float
        Capacitance value in picofarads

    Returns
    -------
    str
        3-character capacitance code
    """
    if value_pf < 0.5:
        raise ValueError(f"Capacitance {value_pf}pF is below minimum 0.5pF")

    if value_pf < 1.0:
        # Sub-pF range: 0.5-0.99 pF uses 8 as multiplier
        # Value encoded as first digits: 0.5 -> 5, 0.75 -> 7 (rounded)
        digit = int(round(value_pf * 10))
        return f"{digit}08"

    elif value_pf < 10.0:
        # 1.0-9.9 pF range: uses 9 as multiplier
        # Value encoded as two digits: 2.2 -> 22, 4.7 -> 47
        digits = int(round(value_pf * 10))
        return f"{digits:02d}9"

    else:
        # 10+ pF: Standard EIA code
        # Find the exponent (number of zeros after two significant digits)
        if value_pf >= 1e12:
            raise ValueError(f"Capacitance {value_pf}pF exceeds encoding range")

        exp = int(math.floor(math.log10(value_pf)))
        mantissa = value_pf / (10 ** (exp - 1))  # Get 2 significant digits

        # Round mantissa to 2 digits
        mantissa_int = int(round(mantissa))

        # Handle edge cases where rounding pushes us up
        if mantissa_int >= 100:
            mantissa_int = int(mantissa_int / 10)
            exp += 1

        # Zeros count is (exponent - 1) since we have 2 sig digits
        zeros = exp - 1

        if zeros < 0:
            zeros = 0
            mantissa_int = int(round(value_pf))

        return f"{mantissa_int:02d}{zeros}"


def encode_capacitance_spice(value_pf: float) -> str:
    """
    Encode capacitance value into SPICE notation.

    Parameters
    ----------
    value_pf : float
        Capacitance value in picofarads

    Returns
    -------
    str
        SPICE-format capacitance string (e.g., "100p", "10n", "1u")
    """
    if value_pf < 1000:
        # Picofarads
        if value_pf == int(value_pf):
            return f"{int(value_pf)}p"
        else:
            # Format fractional values nicely
            formatted = f"{value_pf:.2f}".rstrip("0").rstrip(".")
            return f"{formatted}p"
    elif value_pf < 1000000:
        # Nanofarads
        value_nf = value_pf / 1000
        if value_nf == int(value_nf):
            return f"{int(value_nf)}n"
        else:
            formatted = f"{value_nf:.3f}".rstrip("0").rstrip(".")
            return f"{formatted}n"
    else:
        # Microfarads
        value_uf = value_pf / 1000000
        if value_uf == int(value_uf):
            return f"{int(value_uf)}u"
        else:
            formatted = f"{value_uf:.4f}".rstrip("0").rstrip(".")
            return f"{formatted}u"


def encode_capacitance_readable(value_pf: float) -> str:
    """
    Encode capacitance value into human-readable format.

    Parameters
    ----------
    value_pf : float
        Capacitance value in picofarads

    Returns
    -------
    str
        Human-readable capacitance string (e.g., "100pF", "10nF", "1µF")
    """
    if value_pf < 1000:
        if value_pf == int(value_pf):
            return f"{int(value_pf)}pF"
        else:
            formatted = f"{value_pf:.2f}".rstrip("0").rstrip(".")
            return f"{formatted}pF"
    elif value_pf < 1000000:
        value_nf = value_pf / 1000
        if value_nf == int(value_nf):
            return f"{int(value_nf)}nF"
        else:
            formatted = f"{value_nf:.3f}".rstrip("0").rstrip(".")
            return f"{formatted}nF"
    else:
        value_uf = value_pf / 1000000
        if value_uf == int(value_uf):
            return f"{int(value_uf)}µF"
        else:
            formatted = f"{value_uf:.4f}".rstrip("0").rstrip(".")
            return f"{formatted}µF"


def generate_capacitance_values(
    min_pf: float, max_pf: float, include_fractional: bool = True
) -> List[float]:
    """
    Generate E24 capacitance values within a range.

    Parameters
    ----------
    min_pf : float
        Minimum capacitance in picofarads
    max_pf : float
        Maximum capacitance in picofarads
    include_fractional : bool
        Whether to include fractional pF values (< 10pF)

    Returns
    -------
    list of float
        Sorted list of capacitance values in picofarads
    """
    values = set()

    # Add fractional values if enabled and within range
    if include_fractional:
        for val in FRACTIONAL_PF_VALUES:
            if min_pf <= val <= max_pf:
                values.add(val)

    # Generate E24 values across decades
    # Start from appropriate decade
    if min_pf < 10:
        start_decade = 1  # 10^1 = 10 pF
    else:
        start_decade = int(math.floor(math.log10(min_pf)))

    end_decade = int(math.ceil(math.log10(max_pf))) + 1

    for decade in range(start_decade, end_decade):
        multiplier = 10**decade
        for e24_val in E24_VALUES:
            value_pf = e24_val * multiplier
            if min_pf <= value_pf <= max_pf:
                # Round to avoid floating point issues
                value_pf = round(value_pf, 3)
                values.add(value_pf)

    return sorted(values)


def get_kicad_footprint(case_size: str) -> str:
    """
    Get the KiCad footprint reference for a case size.

    Parameters
    ----------
    case_size : str
        EIA case size (e.g., "0603", "0805")

    Returns
    -------
    str
        Full KiCad footprint reference
    """
    metric = CASE_SIZE_METRIC.get(case_size, case_size)
    return f"{KICAD_CONFIG['footprint_prefix']}{case_size}_{metric}{KICAD_CONFIG['footprint_suffix']}"


def format_mpn(
    case_size: str, cap_pf: float, tolerance: str, voltage: int, packaging: str
) -> str:
    """
    Generate complete manufacturer part number.

    Parameters
    ----------
    case_size : str
        EIA case size
    cap_pf : float
        Capacitance in picofarads
    tolerance : str
        Tolerance string (e.g., "5%", "0.5pF")
    voltage : int
        Voltage rating
    packaging : str
        Packaging code (e.g., "TU", "")

    Returns
    -------
    str
        Complete MPN
    """
    cap_code = encode_capacitance_mpn(cap_pf)
    tol_code = TOLERANCE_CODES[tolerance]
    voltage_code = VOLTAGE_CODES[voltage]

    return STRING_TEMPLATES["mpn"].format(
        size=case_size,
        cap_code=cap_code,
        tol_code=tol_code,
        voltage_code=voltage_code,
        packaging=packaging,
    )


def format_unique_id(mpn: str) -> str:
    """Generate unique ID from MPN."""
    return STRING_TEMPLATES["unique_id"].format(
        manufacturer=MANUFACTURER,
        mpn=mpn,
    )


def format_part_locator(
    cap_pf: float, tolerance: str, voltage: int, case_size: str
) -> str:
    """Generate standardized part locator."""
    value_spice = encode_capacitance_spice(cap_pf).lower()
    tol_lower = tolerance.lower().replace("%", "pct").replace("pf", "pf")

    return STRING_TEMPLATES["part_locator"].format(
        cap_type_slug=CAP_TYPE.lower(),
        dielectric_slug=DIELECTRIC.lower(),
        value_lower=value_spice,
        tolerance_lower=tol_lower,
        voltage=voltage,
        package_lower=case_size.lower(),
    )


def format_description(
    cap_pf: float, tolerance: str, voltage: int, case_size: str
) -> str:
    """Generate component description."""
    value_readable = encode_capacitance_readable(cap_pf)

    return STRING_TEMPLATES["description"].format(
        manufacturer=MANUFACTURER,
        cap_type=CAP_TYPE,
        value_readable=value_readable,
        tolerance=tolerance,
        voltage=voltage,
        dielectric=DIELECTRIC,
        package=case_size,
    )


def generate_spec_summary(enabled_case_voltages: List[Tuple[str, int]]) -> str:
    """Generate capacitance range summary for SQL header."""
    notes = []

    # Group by case size
    by_case = {}
    for case_size, voltage in enabled_case_voltages:
        if case_size not in by_case:
            by_case[case_size] = []
        spec = CASE_VOLTAGE_SPECS.get((case_size, voltage))
        if spec:
            min_str = encode_capacitance_readable(spec["min_pf"])
            max_str = encode_capacitance_readable(spec["max_pf"])
            by_case[case_size].append(f"{voltage}V: {min_str}-{max_str}")

    for case_size in sorted(by_case.keys()):
        voltage_ranges = ", ".join(by_case[case_size])
        notes.append(f"-- - {case_size}: {voltage_ranges}")

    return "\n".join(notes)


# ============================================================================
# ======================== MAIN GENERATION FUNCTION ==========================
# ============================================================================


def generate_capacitors() -> str:
    """
    Generate capacitor SQL statements based on configuration.

    Returns
    -------
    str
        Complete SQL content with INSERT statements
    """
    # Parse configuration
    enabled_tolerances = get_enabled_tolerances()
    enabled_case_voltages = get_enabled_case_voltages()

    if not enabled_case_voltages:
        print("Warning: No case/voltage combinations enabled!")
        return ""

    all_tolerances = enabled_tolerances["absolute"] + enabled_tolerances["percent"]
    if not all_tolerances:
        print("Warning: No tolerances enabled!")
        return ""

    # Get metadata
    script_name = get_script_name()
    build_date = get_build_date()

    # Build SQL header
    sql_lines = [
        SQL_TEMPLATES["file_header"].format(
            manufacturer=MANUFACTURER,
            series=SERIES,
            dielectric=DIELECTRIC,
            cap_type=CAP_TYPE,
            tolerances=", ".join(all_tolerances),
            datasheet_url=URL_TEMPLATES["datasheet"],
            symbol_ref=KICAD_CONFIG["symbol"],
            cap_range_notes=generate_spec_summary(enabled_case_voltages),
        )
    ]

    total_parts = 0

    # Generate parts for each enabled case/voltage combination
    for case_size, voltage in sorted(enabled_case_voltages):
        spec = CASE_VOLTAGE_SPECS.get((case_size, voltage))
        if not spec:
            print(f"Warning: No spec found for {case_size}/{voltage}V")
            continue

        min_pf = spec["min_pf"]
        max_pf = spec["max_pf"]
        has_fractional = spec["has_fractional"]

        # Generate capacitance values for this range
        cap_values = generate_capacitance_values(min_pf, max_pf, has_fractional)

        # Determine which tolerances apply
        # Absolute tolerances only for values < 10pF
        # Percentage tolerances for values >= 10pF

        # Process absolute tolerances (< 10pF)
        if enabled_tolerances["absolute"] and has_fractional:
            fractional_caps = [c for c in cap_values if c < 10.0]

            for tolerance in enabled_tolerances["absolute"]:
                if not fractional_caps:
                    continue

                # Add section header
                min_str = encode_capacitance_readable(min(fractional_caps))
                max_str = encode_capacitance_readable(max(fractional_caps))
                sql_lines.append(
                    SQL_TEMPLATES["spec_header"].format(
                        package=case_size,
                        voltage=voltage,
                        tolerance=tolerance,
                        cap_min=min_str,
                        cap_max=max_str,
                    )
                )

                for cap_pf in fractional_caps:
                    mpn = format_mpn(
                        case_size, cap_pf, tolerance, voltage, DEFAULT_PACKAGING
                    )
                    unique_id = format_unique_id(mpn)
                    part_locator = format_part_locator(
                        cap_pf, tolerance, voltage, case_size
                    )
                    description = format_description(
                        cap_pf, tolerance, voltage, case_size
                    )
                    value_spice = encode_capacitance_spice(cap_pf)
                    kicad_footprint = get_kicad_footprint(case_size)
                    manufacturer_link = URL_TEMPLATES["manufacturer_link"].format(
                        mpn=mpn
                    )
                    rohs_link = URL_TEMPLATES["rohs_document"].format(mpn=mpn)

                    source_sql = "NULL" if SOURCE is None else f"'{SOURCE}'"

                    sql_line = SQL_TEMPLATES["insert"].format(
                        unique_id=unique_id,
                        part_locator=part_locator,
                        mpn=mpn,
                        manufacturer=MANUFACTURER,
                        package=case_size,
                        value_spice=value_spice,
                        description=description,
                        datasheet=URL_TEMPLATES["datasheet"],
                        manufacturer_link=manufacturer_link,
                        kicad_symbol=KICAD_CONFIG["symbol"],
                        kicad_footprint=kicad_footprint,
                        source=source_sql,
                        dump_priority=DUMP_PRIORITY,
                        voltage_rating=voltage,
                        tolerance=tolerance,
                        cap_type=CAP_TYPE,
                        dielectric_class=DIELECTRIC,
                        polarized=POLARIZED,
                        temp_operating=STRING_TEMPLATES["temp_operating"],
                        temp_soldering=STRING_TEMPLATES["temp_soldering"],
                        temp_storage=STRING_TEMPLATES["temp_storage"],
                        lifecycle_status=LIFECYCLE_STATUS,
                        rohs=ROHS_COMPLIANT,
                        rohs_link=rohs_link,
                        allow_substitution=ALLOW_SUBSTITUTION,
                        tracking=TRACKING,
                        created_at=build_date,
                        updated_at=build_date,
                        created_by=script_name,
                        height_max_mm="NULL",
                    )

                    sql_lines.append(sql_line)
                    total_parts += 1

                sql_lines.append("")  # Blank line between sections

        # Process percentage tolerances (>= 10pF)
        if enabled_tolerances["percent"]:
            percent_caps = [c for c in cap_values if c >= 10.0]

            for tolerance in enabled_tolerances["percent"]:
                if not percent_caps:
                    continue

                # Add section header
                min_str = encode_capacitance_readable(min(percent_caps))
                max_str = encode_capacitance_readable(max(percent_caps))
                sql_lines.append(
                    SQL_TEMPLATES["spec_header"].format(
                        package=case_size,
                        voltage=voltage,
                        tolerance=tolerance,
                        cap_min=min_str,
                        cap_max=max_str,
                    )
                )

                for cap_pf in percent_caps:
                    mpn = format_mpn(
                        case_size, cap_pf, tolerance, voltage, DEFAULT_PACKAGING
                    )
                    unique_id = format_unique_id(mpn)
                    part_locator = format_part_locator(
                        cap_pf, tolerance, voltage, case_size
                    )
                    description = format_description(
                        cap_pf, tolerance, voltage, case_size
                    )
                    value_spice = encode_capacitance_spice(cap_pf)
                    kicad_footprint = get_kicad_footprint(case_size)
                    manufacturer_link = URL_TEMPLATES["manufacturer_link"].format(
                        mpn=mpn
                    )
                    rohs_link = URL_TEMPLATES["rohs_document"].format(mpn=mpn)

                    source_sql = "NULL" if SOURCE is None else f"'{SOURCE}'"

                    sql_line = SQL_TEMPLATES["insert"].format(
                        unique_id=unique_id,
                        part_locator=part_locator,
                        mpn=mpn,
                        manufacturer=MANUFACTURER,
                        package=case_size,
                        value_spice=value_spice,
                        description=description,
                        datasheet=URL_TEMPLATES["datasheet"],
                        manufacturer_link=manufacturer_link,
                        kicad_symbol=KICAD_CONFIG["symbol"],
                        kicad_footprint=kicad_footprint,
                        source=source_sql,
                        dump_priority=DUMP_PRIORITY,
                        voltage_rating=voltage,
                        tolerance=tolerance,
                        cap_type=CAP_TYPE,
                        dielectric_class=DIELECTRIC,
                        polarized=POLARIZED,
                        temp_operating=STRING_TEMPLATES["temp_operating"],
                        temp_soldering=STRING_TEMPLATES["temp_soldering"],
                        temp_storage=STRING_TEMPLATES["temp_storage"],
                        lifecycle_status=LIFECYCLE_STATUS,
                        rohs=ROHS_COMPLIANT,
                        rohs_link=rohs_link,
                        allow_substitution=ALLOW_SUBSTITUTION,
                        tracking=TRACKING,
                        created_at=build_date,
                        updated_at=build_date,
                        created_by=script_name,
                        height_max_mm="NULL",
                    )

                    sql_lines.append(sql_line)
                    total_parts += 1

                sql_lines.append("")  # Blank line between sections

    # Add footer
    sql_lines.append(SQL_TEMPLATES["file_footer"].format(total_parts=total_parts))

    return "\n".join(sql_lines)


def generate_csv_data() -> List[Dict[str, str]]:
    """
    Generate CSV data for inspection and validation.

    Returns list of dictionaries with key fields for each capacitor.
    """
    # Parse configuration
    enabled_tolerances = get_enabled_tolerances()
    enabled_case_voltages = get_enabled_case_voltages()

    rows = []

    for case_size, voltage in sorted(enabled_case_voltages):
        spec = CASE_VOLTAGE_SPECS.get((case_size, voltage))
        if not spec:
            continue

        min_pf = spec["min_pf"]
        max_pf = spec["max_pf"]
        has_fractional = spec["has_fractional"]

        cap_values = generate_capacitance_values(min_pf, max_pf, has_fractional)

        # Process absolute tolerances
        if enabled_tolerances["absolute"] and has_fractional:
            fractional_caps = [c for c in cap_values if c < 10.0]
            for tolerance in enabled_tolerances["absolute"]:
                for cap_pf in fractional_caps:
                    mpn = format_mpn(
                        case_size, cap_pf, tolerance, voltage, DEFAULT_PACKAGING
                    )
                    rows.append(
                        {
                            "mpn": mpn,
                            "case_size": case_size,
                            "voltage": voltage,
                            "capacitance_pf": cap_pf,
                            "capacitance_display": encode_capacitance_readable(cap_pf),
                            "tolerance": tolerance,
                            "tolerance_type": "absolute",
                            "dielectric": DIELECTRIC,
                        }
                    )

        # Process percentage tolerances
        if enabled_tolerances["percent"]:
            percent_caps = [c for c in cap_values if c >= 10.0]
            for tolerance in enabled_tolerances["percent"]:
                for cap_pf in percent_caps:
                    mpn = format_mpn(
                        case_size, cap_pf, tolerance, voltage, DEFAULT_PACKAGING
                    )
                    rows.append(
                        {
                            "mpn": mpn,
                            "case_size": case_size,
                            "voltage": voltage,
                            "capacitance_pf": cap_pf,
                            "capacitance_display": encode_capacitance_readable(cap_pf),
                            "tolerance": tolerance,
                            "tolerance_type": "percent",
                            "dielectric": DIELECTRIC,
                        }
                    )

    return rows


def main():
    """Generate capacitor SQL based on configuration."""

    # Display configuration summary
    enabled_tolerances = get_enabled_tolerances()
    enabled_case_voltages = get_enabled_case_voltages()

    print(f"KEMET {DIELECTRIC} {CAP_TYPE} Capacitor Generator")
    print("=" * 50)
    print(f"\nConfiguration:")
    print(f"  Manufacturer: {MANUFACTURER}")
    print(f"  Dielectric: {DIELECTRIC}")
    print(f"  Packaging: {DEFAULT_PACKAGING or '(bulk)'}")
    print(f"\nEnabled tolerances:")
    print(f"  Absolute: {enabled_tolerances['absolute'] or '(none)'}")
    print(f"  Percent: {enabled_tolerances['percent'] or '(none)'}")
    print(f"\nEnabled case/voltage combinations: {len(enabled_case_voltages)}")
    for case_size, voltage in sorted(enabled_case_voltages)[:10]:
        print(f"  - {case_size} / {voltage}V")
    if len(enabled_case_voltages) > 10:
        print(f"  ... and {len(enabled_case_voltages) - 10} more")

    # Generate SQL content
    sql_content = generate_capacitors()

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

    # Generate CSV if enabled
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
