#!/usr/bin/env python3
"""
Samsung CL Series SMD MLCC Capacitor Generator
Generates capacitor parts for Terra EDA Library from Samsung CSV catalog.

This script reads the Samsung MLCC component list CSV and generates SQL INSERT
statements for the capacitors_smt table. Unlike the KEMET generator which
constructs MPNs from E-series values, this script uses real MPNs from Samsung's
published catalog.

Source CSV: SEM_ComponentLibrary_MLCC_List.csv (2,961 parts)
Dielectrics: C0G, X7R, X5R, Y5V, X7R(S)

Samsung CL Series Part Number Format:
CL [SIZE] [DIELECTRIC] [CAP_CODE] [TOL] [VOLTAGE] [SUFFIX]

Example: CL10A104KA8NNNC
- CL = Samsung MLCC prefix
- 10 = Size code (0603)
- A = X5R dielectric
- 104 = Capacitance code (100nF)
- K = ±10% Tolerance
- A = 10V
- 8 = Thickness code
- NNN = Packaging/suffix
- C = General
"""

import csv
import re
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================================
# ======================== USER CONFIGURATION ================================
# ============================================================================
# Modify these sections to control what gets generated

# ======================== DIELECTRIC CONFIGURATION ========================
# Set to "yes" to include, anything else to exclude
DIELECTRIC_ENABLE = {
    "C0G": "yes",
    "X7R": "yes",
    "X5R": "yes",
    "Y5V": "yes",
    "X7R(S)": "no",
}

# ======================== CASE SIZE CONFIGURATION ========================
CASE_SIZE_ENABLE = {
    "0201": "no",
    "0402": "yes",
    "0603": "yes",
    "0805": "yes",
    "1206": "yes",
    "1210": "yes",
    "1812": "yes",
}

# ======================== VOLTAGE CONFIGURATION ========================
VOLTAGE_ENABLE = {
    "2.5V": "yes",
    "4V": "yes",
    "6.3V": "yes",
    "10V": "yes",
    "16V": "yes",
    "25V": "yes",
    "35V": "yes",
    "50V": "yes",
    "63V": "yes",
    "100V": "yes",
    "200V": "yes",
    "250V": "yes",
    "350V": "yes",
    "500V": "yes",
    "630V": "yes",
    "1000V": "yes",
    "1250V": "yes",
    "2000V": "yes",
}

# ======================== TOLERANCE CONFIGURATION ========================
TOLERANCE_ENABLE = {
    "0.1pF": "yes",
    "0.25pF": "yes",
    "0.5pF": "yes",
    "1%": "yes",
    "2%": "yes",
    "5%": "yes",
    "10%": "yes",
    "20%": "yes",
    "-20/+80%": "yes",
}

# ======================== OUTPUT CONFIGURATION ========================
OUTPUT_FILE = "capacitors_smt_generated_400_samsung_cl_mlcc.sql"
CSV_FILE = "SEM_ComponentLibrary_MLCC_List.csv"

# ============================================================================
# ======================== VENDOR SPECIFICATIONS =============================
# ============================================================================

# ======================== DATABASE METADATA ========================
SOURCE = None  # NULL for generated data (not dumped separately)
DUMP_PRIORITY = 0  # Generated data priority

# ======================== MANUFACTURER SPECIFICATION ========================
MANUFACTURER = "Samsung Electro-Mechanics"
CAP_TYPE = "MLCC"
LIFECYCLE_STATUS = "Active"
ROHS_COMPLIANT = "Yes"
ALLOW_SUBSTITUTION = "Yes"
TRACKING = "No"
POLARIZED = "No"

# ======================== URL TEMPLATES ========================
URL_TEMPLATES = {
    "datasheet": "https://weblib.samsungsem.com/mlcc/{mpn}.pdf",
    "manufacturer_link": "https://product.samsungsem.com/mlcc/{mpn}.do",
}

# ======================== STRING TEMPLATES ========================
STRING_TEMPLATES = {
    "description": "{manufacturer} {cap_type} capacitor {value_readable} {tolerance} {voltage} {dielectric} {package}",
    "part_locator": "cap-{cap_type_slug}-{dielectric_slug}-{value_lower}-{tolerance_lower}-{voltage}v-{package_lower}",
    "unique_id": "{manufacturer}-{mpn}",
    "temp_operating": "-55°C to +125°C",
    "temp_soldering": "260°C (10s max)",
    "temp_storage": "-55°C to +125°C",
}

# ======================== SQL TEMPLATES ========================
SQL_TEMPLATES = {
    "file_header": """-- {manufacturer} CL Series {cap_type} Capacitors
-- Dielectrics: {dielectrics}
-- Source CSV: {csv_file}
--
-- Generated from Samsung MLCC catalog ({total_csv_rows} rows in CSV)
-- Filtered to {total_parts} parts
--
-- Value Formats:
-- - Database value uses SPICE notation (p, n, u suffixes)
-- - Booleans stored as 'Yes'/'No' for KiCad compatibility

BEGIN TRANSACTION;
""",
    "section_header": "-- {dielectric} {package} {voltage}",
    "insert": """INSERT INTO capacitors_smt (unique_id, part_locator, mpn, manufacturer, package, value, description, datasheet, manufacturer_link, kicad_symbol, kicad_footprint, source, dump_priority, voltage_rating_v, tolerance, cap_type, dielectric_class, polarized, temp_operating, temp_soldering, temp_storage, lifecycle_status, rohs, allow_substitution, tracking, created_at, updated_at, created_by, height_max_mm)
VALUES ('{unique_id}', '{part_locator}', '{mpn}', '{manufacturer}', '{package}', '{value_spice}', '{description}', '{datasheet}', '{manufacturer_link}', '{kicad_symbol}', '{kicad_footprint}', {source}, {dump_priority}, {voltage_rating}, '{tolerance}', '{cap_type}', '{dielectric_class}', '{polarized}', '{temp_operating}', '{temp_soldering}', '{temp_storage}', '{lifecycle_status}', '{rohs}', '{allow_substitution}', '{tracking}', '{created_at}', '{updated_at}', '{created_by}', {height_max_mm});""",
    "file_footer": """COMMIT;

-- Generated {total_parts} capacitor parts""",
}

# ======================== KICAD CONFIGURATION ========================
KICAD_CONFIG = {
    "symbol": "Device:C",
    "footprint_prefix": "Capacitor_SMD:C_",
    "footprint_suffix": "Metric",
}

# Case size to metric footprint mapping
CASE_SIZE_METRIC = {
    "0201": "0603",
    "0402": "1005",
    "0603": "1608",
    "0805": "2012",
    "1206": "3216",
    "1210": "3225",
    "1812": "4532",
}


# ============================================================================
# ======================== HELPER FUNCTIONS ==================================
# ============================================================================


def get_script_name() -> str:
    """Get the script filename without path."""
    return Path(__file__).name


def get_build_date() -> str:
    """Get the current build date."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_capacitance_pf(s: str) -> float:
    """
    Parse capacitance string to picofarads.

    Parameters
    ----------
    s : str
        Capacitance string from CSV (e.g., "220uF", "100nF", "4.7pF")

    Returns
    -------
    float
        Capacitance in picofarads
    """
    s = s.strip()
    m = re.match(r"^([\d.]+)\s*(pF|nF|uF)$", s, re.IGNORECASE)
    if not m:
        raise ValueError(f"Cannot parse capacitance: {s!r}")
    value = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "pf":
        return value
    elif unit == "nf":
        return value * 1000
    elif unit == "uf":
        return value * 1000000
    raise ValueError(f"Unknown unit in capacitance: {s!r}")


def parse_voltage(s: str) -> float:
    """
    Parse voltage string to numeric value.

    Parameters
    ----------
    s : str
        Voltage string from CSV (e.g., "6.3Vdc", "100Vdc")

    Returns
    -------
    float
        Voltage as a number
    """
    s = s.strip()
    m = re.match(r"^([\d.]+)\s*Vdc$", s, re.IGNORECASE)
    if not m:
        raise ValueError(f"Cannot parse voltage: {s!r}")
    return float(m.group(1))


def parse_tolerance(s: str) -> str:
    """
    Parse tolerance string to normalized form.

    Parameters
    ----------
    s : str
        Tolerance from CSV (e.g., "+/-10%", "+/-0.5pF", "-20/+80%")

    Returns
    -------
    str
        Normalized tolerance (e.g., "10%", "0.5pF", "-20/+80%")
    """
    s = s.strip()
    if s.startswith("+/-"):
        return s[3:]
    return s


def parse_size(s: str) -> Tuple[str, str]:
    """
    Parse size string to (imperial, metric) tuple.

    Parameters
    ----------
    s : str
        Size from CSV (e.g., "1210/3225", "0603/1608")

    Returns
    -------
    tuple of (str, str)
        (imperial_code, metric_code) e.g. ("1210", "3225")
    """
    s = s.strip()
    parts = s.split("/")
    if len(parts) != 2:
        raise ValueError(f"Cannot parse size: {s!r}")
    return parts[0], parts[1]


def parse_height_mm(s: str) -> Optional[float]:
    """
    Parse height/thickness string to mm.

    Parameters
    ----------
    s : str
        Height string from CSV (e.g., "2.8mm", "1mm")

    Returns
    -------
    float or None
        Height in mm, or None if unparseable
    """
    s = s.strip()
    m = re.match(r"^([\d.]+)\s*mm$", s, re.IGNORECASE)
    if not m:
        return None
    return float(m.group(1))


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
        if value_pf == int(value_pf):
            return f"{int(value_pf)}p"
        else:
            formatted = f"{value_pf:.2f}".rstrip("0").rstrip(".")
            return f"{formatted}p"
    elif value_pf < 1000000:
        value_nf = value_pf / 1000
        if value_nf == int(value_nf):
            return f"{int(value_nf)}n"
        else:
            formatted = f"{value_nf:.3f}".rstrip("0").rstrip(".")
            return f"{formatted}n"
    else:
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


def format_voltage_key(voltage: float) -> str:
    """Format voltage as a lookup key for VOLTAGE_ENABLE (e.g., 6.3 -> '6.3V')."""
    if voltage == int(voltage):
        return f"{int(voltage)}V"
    return f"{voltage}V"


def format_tolerance_key(tolerance: str) -> str:
    """Format tolerance as a lookup key for TOLERANCE_ENABLE (e.g., '10%' -> '10%')."""
    return tolerance


def is_enabled(row: Dict[str, str]) -> bool:
    """
    Check whether a CSV row passes all enable filters.

    Parameters
    ----------
    row : dict
        A row from the Samsung CSV

    Returns
    -------
    bool
        True if the row passes all filters
    """
    # Dielectric filter
    dielectric = row["TCC"].strip()
    if DIELECTRIC_ENABLE.get(dielectric, "no").lower() != "yes":
        return False

    # Case size filter
    case_size, _ = parse_size(row["Size(inch/mm)"])
    if CASE_SIZE_ENABLE.get(case_size, "no").lower() != "yes":
        return False

    # Voltage filter
    voltage = parse_voltage(row["Rated Vdc"])
    voltage_key = format_voltage_key(voltage)
    if VOLTAGE_ENABLE.get(voltage_key, "no").lower() != "yes":
        return False

    # Tolerance filter
    tolerance = parse_tolerance(row["Tolerance"])
    tolerance_key = format_tolerance_key(tolerance)
    if TOLERANCE_ENABLE.get(tolerance_key, "no").lower() != "yes":
        return False

    return True


def read_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    Read and return all rows from the Samsung CSV.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file

    Returns
    -------
    list of dict
        All rows from the CSV
    """
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def sort_key(row: Dict[str, str]) -> Tuple:
    """
    Generate a sort key for consistent SQL output ordering.

    Sort order: dielectric → case size → voltage → capacitance (pF) → tolerance → MPN
    """
    dielectric = row["TCC"].strip()
    case_size, _ = parse_size(row["Size(inch/mm)"])
    voltage = parse_voltage(row["Rated Vdc"])
    cap_pf = parse_capacitance_pf(row["Capacitance"])
    tolerance = parse_tolerance(row["Tolerance"])
    mpn = row["Part Number"].strip()
    return (dielectric, case_size, voltage, cap_pf, tolerance, mpn)


def sql_escape(s: str) -> str:
    """Escape single quotes for SQL strings."""
    return s.replace("'", "''")


# ============================================================================
# ======================== MAIN GENERATION FUNCTION ==========================
# ============================================================================


def generate_capacitors(csv_rows: List[Dict[str, str]]) -> str:
    """
    Generate capacitor SQL statements from filtered CSV rows.

    Parameters
    ----------
    csv_rows : list of dict
        All rows from the Samsung CSV

    Returns
    -------
    str
        Complete SQL content with INSERT statements
    """
    # Filter rows
    filtered = [r for r in csv_rows if is_enabled(r)]

    if not filtered:
        print("Warning: No rows passed filters!")
        return ""

    # Sort for consistent output
    filtered.sort(key=sort_key)

    # Get metadata
    script_name = get_script_name()
    build_date = get_build_date()

    # Collect enabled dielectrics for header
    enabled_dielectrics = sorted(set(
        r["TCC"].strip() for r in filtered
    ))

    # Build SQL header
    sql_lines = [
        SQL_TEMPLATES["file_header"].format(
            manufacturer=MANUFACTURER,
            cap_type=CAP_TYPE,
            dielectrics=", ".join(enabled_dielectrics),
            csv_file=CSV_FILE,
            total_csv_rows=len(csv_rows),
            total_parts=len(filtered),
        )
    ]

    total_parts = 0
    last_section = None

    for row in filtered:
        mpn = row["Part Number"].strip()
        dielectric = row["TCC"].strip()
        case_size, metric_size = parse_size(row["Size(inch/mm)"])
        voltage = parse_voltage(row["Rated Vdc"])
        cap_pf = parse_capacitance_pf(row["Capacitance"])
        tolerance = parse_tolerance(row["Tolerance"])
        height_mm = parse_height_mm(row["T Size Max"])

        # Section header when dielectric/size/voltage changes
        section = (dielectric, case_size, voltage)
        if section != last_section:
            if last_section is not None:
                sql_lines.append("")
            sql_lines.append(
                SQL_TEMPLATES["section_header"].format(
                    dielectric=dielectric,
                    package=case_size,
                    voltage=format_voltage_key(voltage),
                )
            )
            last_section = section

        # Encode values
        value_spice = encode_capacitance_spice(cap_pf)
        value_readable = encode_capacitance_readable(cap_pf)
        kicad_footprint = get_kicad_footprint(case_size)

        # Build unique_id
        unique_id = STRING_TEMPLATES["unique_id"].format(
            manufacturer="Samsung", mpn=mpn
        )

        # Build part_locator
        tol_lower = tolerance.lower().replace("%", "pct").replace("pf", "pf")
        dielectric_slug = dielectric.lower().replace("(", "").replace(")", "")
        part_locator = STRING_TEMPLATES["part_locator"].format(
            cap_type_slug=CAP_TYPE.lower(),
            dielectric_slug=dielectric_slug,
            value_lower=value_spice.lower(),
            tolerance_lower=tol_lower,
            voltage=format_voltage_key(voltage).lower().replace("v", ""),
            package_lower=case_size.lower(),
        )

        # Build description
        description = STRING_TEMPLATES["description"].format(
            manufacturer=MANUFACTURER,
            cap_type=CAP_TYPE,
            value_readable=value_readable,
            tolerance=tolerance,
            voltage=format_voltage_key(voltage),
            dielectric=dielectric,
            package=case_size,
        )

        # URLs
        datasheet = URL_TEMPLATES["datasheet"].format(mpn=mpn)
        manufacturer_link = URL_TEMPLATES["manufacturer_link"].format(mpn=mpn)

        source_sql = "NULL" if SOURCE is None else f"'{SOURCE}'"
        height_sql = str(height_mm) if height_mm is not None else "NULL"

        sql_line = SQL_TEMPLATES["insert"].format(
            unique_id=sql_escape(unique_id),
            part_locator=sql_escape(part_locator),
            mpn=sql_escape(mpn),
            manufacturer=sql_escape(MANUFACTURER),
            package=case_size,
            value_spice=sql_escape(value_spice),
            description=sql_escape(description),
            datasheet=sql_escape(datasheet),
            manufacturer_link=sql_escape(manufacturer_link),
            kicad_symbol=KICAD_CONFIG["symbol"],
            kicad_footprint=kicad_footprint,
            source=source_sql,
            dump_priority=DUMP_PRIORITY,
            voltage_rating=voltage,
            tolerance=sql_escape(tolerance),
            cap_type=CAP_TYPE,
            dielectric_class=dielectric,
            polarized=POLARIZED,
            temp_operating=STRING_TEMPLATES["temp_operating"],
            temp_soldering=STRING_TEMPLATES["temp_soldering"],
            temp_storage=STRING_TEMPLATES["temp_storage"],
            lifecycle_status=LIFECYCLE_STATUS,
            rohs=ROHS_COMPLIANT,
            allow_substitution=ALLOW_SUBSTITUTION,
            tracking=TRACKING,
            created_at=build_date,
            updated_at=build_date,
            created_by=script_name,
            height_max_mm=height_sql,
        )

        sql_lines.append(sql_line)
        total_parts += 1

    # Add footer
    sql_lines.append(
        SQL_TEMPLATES["file_footer"].format(total_parts=total_parts)
    )

    return "\n".join(sql_lines)


def main():
    """Generate Samsung MLCC capacitor SQL from CSV catalog."""
    # Resolve CSV path relative to script directory
    script_dir = Path(__file__).parent
    csv_path = script_dir / CSV_FILE

    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    # Read CSV
    csv_rows = read_csv(str(csv_path))

    # Display configuration summary
    enabled_dielectrics = [k for k, v in DIELECTRIC_ENABLE.items() if v.lower() == "yes"]
    enabled_sizes = [k for k, v in CASE_SIZE_ENABLE.items() if v.lower() == "yes"]
    enabled_voltages = [k for k, v in VOLTAGE_ENABLE.items() if v.lower() == "yes"]
    enabled_tolerances = [k for k, v in TOLERANCE_ENABLE.items() if v.lower() == "yes"]

    print(f"Samsung CL Series {CAP_TYPE} Capacitor Generator")
    print("=" * 50)
    print(f"\nCSV source: {csv_path.name} ({len(csv_rows)} rows)")
    print(f"\nConfiguration:")
    print(f"  Manufacturer: {MANUFACTURER}")
    print(f"  Dielectrics: {', '.join(enabled_dielectrics)}")
    print(f"  Case sizes: {', '.join(enabled_sizes)}")
    print(f"  Voltages: {', '.join(enabled_voltages)}")
    print(f"  Tolerances: {', '.join(enabled_tolerances)}")

    # Count how many pass filter before generating
    filtered_count = sum(1 for r in csv_rows if is_enabled(r))
    print(f"\n  Rows passing filters: {filtered_count} / {len(csv_rows)}")

    # Generate SQL content
    sql_content = generate_capacitors(csv_rows)

    if not sql_content:
        print("\nNo parts generated. Check configuration.")
        sys.exit(1)

    # Write SQL file (relative to script directory)
    output_path = script_dir / OUTPUT_FILE
    with open(output_path, "w") as f:
        f.write(sql_content)

    total_parts = sql_content.count("INSERT INTO")
    print(f"\nGenerated: {output_path.name}")
    print(f"Total parts generated: {total_parts}")

    # Summary by dielectric
    print("\nParts by dielectric:")
    for dielectric in sorted(set(r["TCC"].strip() for r in csv_rows if is_enabled(r))):
        count = sum(1 for r in csv_rows if is_enabled(r) and r["TCC"].strip() == dielectric)
        print(f"  {dielectric}: {count}")


if __name__ == "__main__":
    main()
