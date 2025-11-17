#!/usr/bin/env python3
"""
Yageo RC Series Resistor Generator
Generates comprehensive E-series resistors for Terra EDA Library

Datasheet Reference:
https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf
"""

import math
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Standard E-series values for resistors (defined as sets)
E12 = {1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2}

E24 = {1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1}

E48 = {1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54,
       1.62, 1.69, 1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49,
       2.61, 2.74, 2.87, 3.01, 3.16, 3.32, 3.48, 3.65, 3.83, 4.02,
       4.22, 4.42, 4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49,
       6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53}

E96 = {1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,
       1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58,
       1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
       2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55,
       2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24,
       3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
       4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23,
       5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
       6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
       8.66, 8.87, 9.09, 9.31, 9.53, 9.76}

E192 = {1.00, 1.01, 1.02, 1.04, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11,
        1.13, 1.14, 1.15, 1.17, 1.18, 1.20, 1.21, 1.23, 1.24, 1.26,
        1.27, 1.29, 1.30, 1.32, 1.33, 1.35, 1.37, 1.38, 1.40, 1.42,
        1.43, 1.45, 1.47, 1.49, 1.50, 1.52, 1.54, 1.56, 1.58, 1.60,
        1.62, 1.64, 1.65, 1.67, 1.69, 1.72, 1.74, 1.76, 1.78, 1.80,
        1.82, 1.84, 1.87, 1.89, 1.91, 1.93, 1.96, 1.98, 2.00, 2.03,
        2.05, 2.08, 2.10, 2.13, 2.15, 2.18, 2.21, 2.23, 2.26, 2.29,
        2.32, 2.34, 2.37, 2.40, 2.43, 2.46, 2.49, 2.52, 2.55, 2.58,
        2.61, 2.64, 2.67, 2.71, 2.74, 2.77, 2.80, 2.84, 2.87, 2.91,
        2.94, 2.98, 3.01, 3.05, 3.09, 3.12, 3.16, 3.20, 3.24, 3.28,
        3.32, 3.36, 3.40, 3.44, 3.48, 3.52, 3.57, 3.61, 3.65, 3.70,
        3.74, 3.79, 3.83, 3.88, 3.92, 3.97, 4.02, 4.07, 4.12, 4.17,
        4.22, 4.27, 4.32, 4.37, 4.42, 4.48, 4.53, 4.59, 4.64, 4.70,
        4.75, 4.81, 4.87, 4.93, 4.99, 5.05, 5.11, 5.17, 5.23, 5.30,
        5.36, 5.42, 5.49, 5.56, 5.62, 5.69, 5.76, 5.83, 5.90, 5.97,
        6.04, 6.12, 6.19, 6.26, 6.34, 6.42, 6.49, 6.57, 6.65, 6.73,
        6.81, 6.90, 6.98, 7.06, 7.15, 7.23, 7.32, 7.41, 7.50, 7.59,
        7.68, 7.77, 7.87, 7.96, 8.06, 8.16, 8.25, 8.35, 8.45, 8.56,
        8.66, 8.76, 8.87, 8.98, 9.09, 9.20, 9.31, 9.42, 9.53, 9.65,
        9.76, 9.88}

# ======================== CONFIGURATION ========================
# Modify these settings to generate different resistor sets
#
# Usage:
#   1. Edit the configuration below
#   2. Run: python3 gen_resistors_yageo_rc.py
#   3. Import generated SQL file into database
# ================================================================

OUTPUT_FILE = "resistors_generated_200_yageo_rc.sql"

# Database metadata for dump system
# source: NULL for generated data (not dumped), or string identifier for static data
# dump_priority: 0 for generated data (ignored during dump)
SOURCE = None  # Generated data - will not be dumped
DUMP_PRIORITY = 0  # Generated data priority

# Datasheet and documentation URLs
DATASHEET_URL = "https://www.yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L"

# Component specifications
MANUFACTURER = 'Yageo'
COMPOSITION = 'Thick Film'
LIFECYCLE_STATUS = 'Active'
ROHS_COMPLIANT = 'yes'
ALLOW_SUBSTITUTION = 'yes'
TRACKING = 'No'

# SPICE simulation parameters
SIM_DEVICE = 'R'
SIM_PINS = '1=+ 2=-'

# Metadata for created_at, updated_at, created_by fields
def get_script_name():
    """Get the script filename without path."""
    return Path(__file__).name

def get_last_commit_date():
    """Get the last git commit date for this script file."""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ci', __file__],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse git date format: "2025-01-16 12:34:56 -0800"
            date_str = result.stdout.strip().split()[0] + ' ' + result.stdout.strip().split()[1]
            return date_str
    except Exception:
        pass
    # Fallback to current date if git fails
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_build_date():
    """Get the current build date."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Symbol style: 'R' (European) or 'R_US' (American)
SYMBOL_STYLE = 'R_US'

# E-series values to generate (specify set directly or union of sets)
# Yageo RC supports union of E24 and E96 at 1% tolerance
# Examples:
#   SERIES_VALUES = E96          # Just E96
#   SERIES_VALUES = E24 | E96    # Union of E24 and E96 (no duplicates)
#   SERIES_VALUES = E192         # Just E192
SERIES_VALUES = E24 | E96
SERIES_STR = "E24+E96"  # Description for display and SQL comments

# Tolerance percentage: 0.1, 0.5, 1.0, or 5.0
TOLERANCE_PERCENT = 1.0

# Package sizes to include (comment out any you don't want)
PACKAGE_SIZES = [
    '0201',  # 0.6mm × 0.3mm
    '0402',  # 1.0mm × 0.5mm
    '0603',  # 1.6mm × 0.8mm
    '0805',  # 2.0mm × 1.25mm
    '1206',  # 3.2mm × 1.6mm
    '2512',  # 6.3mm × 3.2mm
]

# 0R jumper resistors are always included as a special case

# ====================== END CONFIGURATION ======================

# Units for IEC resistance encoding (symbol, exponent in base-10)
IEC_UNITS = (
    ("m", -3),  # milli-ohm
    ("R",  0),  # ohm
    ("K",  3),  # kilo-ohm
    ("M",  6),  # mega-ohm
    ("G",  9),  # giga-ohm
)

# Units for SPICE resistance encoding (symbol, exponent in base-10)
# Note: empty string for base ohms since SPICE doesn't use a suffix for ohms
SPICE_UNITS = (
    ("m", -3),  # milli-ohm
    ("",  0),   # ohm (no suffix)
    ("K",  3),  # kilo-ohm
    ("M",  6),  # mega-ohm
    ("G",  9),  # giga-ohm
)

# Tolerance codes for Yageo
TOLERANCE_CODES = {
    0.1: "B",
    0.5: "D",
    1.0: "F",
    5.0: "J",
}

# Package specifications: size -> (power, tempco, working_voltage, max_voltage, kicad_footprint, min_ohm, max_ohm)
# From Yageo RC datasheet and yageo_RC_params.org
# Temperature coefficient depends on resistance range:
#   - RC0201: only 200ppm available
#   - RC0402-RC2512: 100ppm for 10Ω-10MΩ, 200ppm for 1Ω-10Ω
PACKAGES = {
    # RC0201 - only 200ppm variant available
    '0201_200ppm': ('1/20W', '200ppm', '25V', '50V', 'Resistor_SMD:R_0201_0603Metric', 1.0, 10e6),

    # RC0402 variants
    '0402_100ppm': ('1/16W', '100ppm', '50V', '100V', 'Resistor_SMD:R_0402_1005Metric', 10.0, 10e6),
    '0402_200ppm': ('1/16W', '200ppm', '50V', '100V', 'Resistor_SMD:R_0402_1005Metric', 1.0, 9.99),

    # RC0603 variants
    '0603_100ppm': ('1/10W', '100ppm', '75V', '150V', 'Resistor_SMD:R_0603_1608Metric', 10.0, 10e6),
    '0603_200ppm': ('1/10W', '200ppm', '75V', '150V', 'Resistor_SMD:R_0603_1608Metric', 1.0, 9.99),

    # RC0805 variants
    '0805_100ppm': ('1/8W', '100ppm', '150V', '300V', 'Resistor_SMD:R_0805_2012Metric', 10.0, 10e6),
    '0805_200ppm': ('1/8W', '200ppm', '150V', '300V', 'Resistor_SMD:R_0805_2012Metric', 1.0, 9.99),

    # RC1206 variants
    '1206_100ppm': ('1/4W', '100ppm', '200V', '400V', 'Resistor_SMD:R_1206_3216Metric', 10.0, 10e6),
    '1206_200ppm': ('1/4W', '200ppm', '200V', '400V', 'Resistor_SMD:R_1206_3216Metric', 1.0, 9.99),

    # RC2512 variants
    '2512_100ppm': ('1W', '100ppm', '200V', '500V', 'Resistor_SMD:R_2512_6332Metric', 10.0, 10e6),
    '2512_200ppm': ('1W', '200ppm', '200V', '500V', 'Resistor_SMD:R_2512_6332Metric', 1.0, 9.99),
}

# Resistance decades to generate (7 decades: 1 ohm to 10 Megohm, full E96 coverage)
DECADES = [
    (1, 'R'),       # 1 to 9.76
    (10, 'R'),      # 10 to 97.6
    (100, 'R'),     # 100 to 976
    (1000, 'K'),    # 1K to 9.76K
    (10000, 'K'),   # 10K to 97.6K
    (100000, 'K'),  # 100K to 976K
    (1000000, 'M'), # 1M to 9.76M
    (10000000, 'M'), # 10M to 97.6M
    (100000000, 'M'), # 100M to 976M
]

def generate_resistance_values(base_values=None, decades=None):
    """
    Generate standard resistance values based on E-series.

    This is a manufacturer-independent function that can be reused
    for different resistor manufacturers.

    Parameters
    ----------
    base_values : set, optional
        E-series values (e.g., E96, E24|E96). If None, uses E96
    decades : list of tuples, optional
        List of (multiplier, unit_suffix) tuples. If None, uses DECADES

    Returns
    -------
    list of float
        Resistance values in ohms, sorted

    Examples
    --------
    >>> values = generate_resistance_values(E24, [(1, 'R'), (10, 'R')])
    >>> # Returns E24 values from 1R to 91R

    >>> values = generate_resistance_values(E24 | E96)
    >>> # Returns union of E24 and E96 series
    """
    if base_values is None:
        base_values = E96

    if decades is None:
        decades = DECADES

    resistance_values = []

    # Generate all values
    for decade_mult, _ in decades:
        for base_value in base_values:
            resistance_values.append(base_value * decade_mult)

    return sorted(set(resistance_values))  # Remove duplicates and sort


def encode_resistance(value_ohm: float, style: str = 'iec') -> str:
    """
    Encode a resistance value in IEC or SPICE format.

    Parameters
    ----------
    value_ohm : float
        Resistance value in ohms
    style : str
        'iec' for IEC 60062 format (4R7, 4K7) or 'spice' for SPICE format (4.7, 4.7K)

    Returns
    -------
    str
        Formatted resistance string

    Examples
    --------
    IEC format:
      0        -> '0R'   (jumper)
      0.47     -> '470m'
      4.7      -> '4R7'
      4700     -> '4K7'
      4.7e6    -> '4M7'
      4.7e9    -> '4G7'

    SPICE format:
      0        -> '0'   (jumper)
      0.47     -> '470m'
      4.7      -> '4.7'
      4700     -> '4.7K'
      4.7e6    -> '4.7M'
      4.7e9    -> '4.7G'
    """
    # Handle zero ohm jumpers
    if value_ohm == 0:
        return "0R" if style == 'iec' else "0"

    if value_ohm < 0:
        raise ValueError("Resistance must be non-negative")

    # Select appropriate unit list based on style
    units = IEC_UNITS if style == 'iec' else SPICE_UNITS

    exp10  = math.log10(value_ohm)
    target = 3 * math.floor(exp10 / 3.0)   # nearest 10^(3n) decade

    # Pick the unit whose exponent is closest to that decade
    marker, exp = min(units, key=lambda ue: abs(ue[1] - target))

    scale  = 10 ** exp
    scaled = value_ohm / scale              # we want 1 <= scaled < 1000

    if not (1.0 <= scaled < 1000.0):
        raise ValueError(
            f"value {value_ohm} Ω not representable with units in [1,1000)"
        )

    # Format with 3 decimal places
    s = format(scaled, ".3f")               # '4.700', '47.000', '470.000'

    if style == 'iec':
        # IEC: replace decimal point with marker, then strip trailing zeros
        s = s.replace(".", marker).rstrip('0')  # '4R700' → '4R7', '47R000' → '47R', '470R000' → '470R'
    else:
        # SPICE: strip trailing zeros and decimal, then append marker
        s = s.rstrip('0').rstrip('.')           # '4.7', '47', '470'
        s = s + marker if marker else s

    return s


def resistor_code(value_ohm: float, size: str, tol_percent: float) -> str:
    """
    Generate Yageo RC series MPN using encode_resistance.

    Parameters
    ----------
    value_ohm : float
        Resistance value in ohms
    size : str
        Package size - either base (0402) or with tempco suffix (0402_100ppm)
    tol_percent : float
        Tolerance percentage (0.1, 0.5, 1.0, or 5.0)

    Returns
    -------
    str
        Complete MPN (e.g., 'RC0603FR-074K7L')

    References
    ----------
    .. [1] Yageo RC Group Datasheet
       https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf
    """
    # Extract base package size (remove _100ppm or _200ppm suffix)
    base_size = size.split('_')[0]

    tol_code   = TOLERANCE_CODES[tol_percent]
    value_code = encode_resistance(value_ohm, style='iec')  # Yageo uses IEC format

    series_size = f"RC{base_size}"   # e.g. 'RC0402'
    packaging   = "R"                 # reel/tape placeholder
    tcr_code    = "07"                # slot for 100 ppm band
    rohs        = "L"                 # lead-free

    return f"{series_size}{tol_code}{packaging}-{tcr_code}{value_code}{rohs}"

def generate_manufacturer_link(mpn):
    """Generate manufacturer product page link"""
    return f"https://www.yageogroup.com/products/Resistors/part/{mpn}"

def generate_part_id(value_str, tolerance, power, tempco, package):
    """Generate standardized part ID"""
    return f"RES-{value_str}-{tolerance}-{power}-{tempco}-{package}"

def generate_resistors(symbol_style='R', packages=None, series_values=None, series_str='E96', tolerance_percent=1.0):
    """
    Generate resistor SQL statements for Yageo RC series.

    Parameters
    ----------
    symbol_style : str, optional
        KiCad symbol style: 'R' (European) or 'R_US' (American)
    packages : list, optional
        List of base package sizes to generate. Will be expanded to tempco variants.
    series_values : set, optional
        E-series values to use (e.g., E96, E24|E96). If None, uses E96
    series_str : str, optional
        Description of series for display (default='E96')
    tolerance_percent : float, optional
        Tolerance percentage: 0.1, 0.5, 1.0, or 5.0 (default=1.0)

    Returns
    -------
    str
        Complete SQL content with INSERT statements
    """
    if packages is None:
        packages = PACKAGE_SIZES

    if series_values is None:
        series_values = E96

    # Format tolerance for display
    tolerance_str = f"{tolerance_percent}%"

    symbol_ref = f"Device:{symbol_style}"

    # Get metadata for created_at, updated_at, created_by
    script_name = get_script_name()
    created_date = get_last_commit_date()
    build_date = get_build_date()

    # Generate resistance values (E-series values only, not including 0)
    resistance_values = generate_resistance_values(series_values, DECADES)

    # Add 0 ohm jumper as a special case
    resistance_values_with_zero = [0.0] + resistance_values

    sql_lines = [
        "-- Yageo RC Series SMT Resistors",
        f"-- Series: {series_str}, Tolerance: {tolerance_str}",
        f"-- Datasheet: {DATASHEET_URL}",
        f"-- Symbol: {symbol_ref}",
        "-- ",
        "-- Temperature coefficients by package and range:",
        "-- - RC0201: 200ppm only (all values)",
        "-- - RC0402-RC2512: 100ppm (10Ω-10MΩ), 200ppm (1Ω-10Ω)",
        "-- ",
        "-- Value Formats:",
        "-- - MPN uses Yageo format with encode_resistance",
        "-- - Database value uses simulation format for SPICE compatibility",
        "-- - Booleans stored as 'yes'/'no' for KiCad compatibility",
        "",
        "BEGIN TRANSACTION;",
        ""
    ]

    total_parts = 0

    # Expand base packages to their tempco variants
    package_variants = []
    for base_package in packages:
        if base_package == '0201':
            # RC0201 only has 200ppm variant
            if '0201_200ppm' in PACKAGES:
                package_variants.append('0201_200ppm')
        else:
            # Other packages have both 100ppm and 200ppm variants
            for suffix in ['_100ppm', '_200ppm']:
                variant = base_package + suffix
                if variant in PACKAGES:
                    package_variants.append(variant)

    for package_variant in sorted(package_variants):
        if package_variant not in PACKAGES:
            continue

        power, tempco, working_voltage, max_voltage, footprint, min_ohm, max_ohm = PACKAGES[package_variant]
        base_package = package_variant.split('_')[0]

        # Get temperature specs based on package
        if base_package == '0201':
            temp_operating = '-55°C to +125°C'
        else:
            temp_operating = '-55°C to +155°C'

        # Standard soldering and storage temps for all packages
        temp_soldering = '260°C (10s max)'  # Lead-free solder reflow
        temp_storage = '-55°C to +125°C'

        sql_lines.append(f"-- {base_package} Package ({power}, {tempco}, {working_voltage} working/{max_voltage} max)")

        for resistance_ohms in resistance_values_with_zero:
            # 0 ohm jumpers are only in 200ppm variants
            if resistance_ohms == 0:
                if '100ppm' in package_variant:
                    continue
            # Non-zero values must be in the package's resistance range
            elif resistance_ohms < min_ohm or resistance_ohms > max_ohm:
                continue

            # Generate MPN using the package variant
            mpn = resistor_code(resistance_ohms, package_variant, tolerance_percent)

            # Format values for display and simulation
            value_display = encode_resistance(resistance_ohms, style='iec')    # IEC format for MPN (2k74)
            value_readable = encode_resistance(resistance_ohms, style='spice')  # Decimal format for humans (2.74k)
            value_simulation = value_readable  # SPICE uses same format

            # Generate links and IDs
            manufacturer_link = generate_manufacturer_link(mpn)
            rohs_link = f"https://www.yageogroup.com/component-documentation/download/rohs/{mpn}.pdf"
            part_id = generate_part_id(value_readable, tolerance_str, power.replace('/', '_'),
                                      tempco, base_package)

            # Generate description
            if resistance_ohms == 0:
                description = f"Jumper, 0 ohm resistor, {base_package} package"
            else:
                description = f"Resistor {value_readable} {tolerance_str} {power} {tempco} {base_package} thick film"

            # Format source for SQL (None → NULL, string → 'string')
            source_sql = 'NULL' if SOURCE is None else f"'{SOURCE}'"

            sql_line = f"""INSERT INTO resistors (part_id, mpn, manufacturer, package, value, description, datasheet, manufacturer_link, kicad_symbol, kicad_footprint, source, dump_priority, tolerance, power_rating, temp_coeff, voltage_rating, composition, temp_operating, temp_soldering, temp_storage, sim_device, sim_pins, lifecycle_status, rohs, rohs_document_link, allow_substitution, tracking, created_at, updated_at, created_by)
VALUES ('{part_id}', '{mpn}', '{MANUFACTURER}', '{base_package}', '{value_simulation}', '{description}', '{DATASHEET_URL}', '{manufacturer_link}', '{symbol_ref}', '{footprint}', {source_sql}, {DUMP_PRIORITY}, '{tolerance_str}', '{power}', '{tempco}', '{working_voltage}', '{COMPOSITION}', '{temp_operating}', '{temp_soldering}', '{temp_storage}', '{SIM_DEVICE}', '{SIM_PINS}', '{LIFECYCLE_STATUS}', '{ROHS_COMPLIANT}', '{rohs_link}', '{ALLOW_SUBSTITUTION}', '{TRACKING}', '{created_date}', '{build_date}', '{script_name}');"""

            sql_lines.append(sql_line)
            total_parts += 1

        sql_lines.append("")  # Blank line between packages

    sql_lines.extend([
        "COMMIT;",
        "",
        f"-- Generated {total_parts} resistor parts"
    ])

    return '\n'.join(sql_lines)

def main():
    """Generate resistor SQL based on configuration at top of file."""

    # Validate configuration
    if TOLERANCE_PERCENT not in TOLERANCE_CODES:
        print(f"Error: Invalid tolerance {TOLERANCE_PERCENT}%. Must be one of: {list(TOLERANCE_CODES.keys())}")
        sys.exit(1)

    # Validate that base packages can be expanded to variants
    for package in PACKAGE_SIZES:
        # Check if any variant exists for this base package
        has_variant = False
        if package == '0201':
            has_variant = '0201_200ppm' in PACKAGES
        else:
            has_variant = any(f"{package}_{suffix}" in PACKAGES for suffix in ['100ppm', '200ppm'])

        if not has_variant:
            print(f"Error: No variants found for package {package}")
            sys.exit(1)

    # Generate SQL content
    sql_content = generate_resistors(
        symbol_style=SYMBOL_STYLE,
        packages=PACKAGE_SIZES,
        series_values=SERIES_VALUES,
        series_str=SERIES_STR,
        tolerance_percent=TOLERANCE_PERCENT
    )

    # Write to file
    import os
    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir:  # Only create dir if there's a directory component
        os.makedirs(output_dir, exist_ok=True)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(sql_content)

    # Display summary
    print(f"Generated {OUTPUT_FILE}")
    print(f"Configuration:")
    print(f"  Symbol style: Device:{SYMBOL_STYLE}")
    print(f"  Series: {SERIES_STR}")
    print(f"  Tolerance: {TOLERANCE_PERCENT}%")
    print(f"  Base packages: {', '.join(PACKAGE_SIZES)}")

    # Count actual parts generated (from SQL content)
    total_parts = sql_content.count("INSERT INTO")
    print(f"Total parts generated: {total_parts}")

if __name__ == '__main__':
    main()
