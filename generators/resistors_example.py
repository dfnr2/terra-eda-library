#!/usr/bin/env python3
"""
Example resistor generator script for Terra EDA Library.

This script demonstrates how to generate SQL for a series of resistors
programmatically. You can adapt this template for your own components.

Usage:
    # Generate INSERT statements only (for merging into existing library)
    python3 generators/resistors_example.py > temp/resistors_batch.sql

    # Generate full library (for creating new library)
    python3 generators/resistors_example.py --full-library > db/terra_resistors.sql
"""

import argparse
import sys

# E-series standard values (E12 series - 10% tolerance)
E12_VALUES = ["10", "12", "15", "18", "22", "27", "33", "39", "47", "56", "68", "82"]

# Resistor specifications
RESISTOR_SPECS = {
    "0402": {
        "footprint": "Resistor_SMD:R_0402_1005Metric",
        "power": "0.063W",
        "manufacturer": "Yageo",
        "mpn_template": "RC0402FR-07{value}L"
    },
    "0603": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "power": "0.1W",
        "manufacturer": "Yageo",
        "mpn_template": "RC0603FR-07{value}L"
    },
    "0805": {
        "footprint": "Resistor_SMD:R_0805_2012Metric",
        "power": "0.125W",
        "manufacturer": "Yageo",
        "mpn_template": "RC0805FR-07{value}L"
    }
}


def format_value_for_mpn(value_str):
    """Convert value like '10K' to MPN format like '10KL'."""
    # This is a simplified example - real MPN formatting varies by manufacturer
    return value_str.replace(".", "R")


def generate_resistor_values(multipliers=["1", "10", "100", "1K", "10K", "100K", "1M"]):
    """Generate standard resistor values with multipliers."""
    values = []
    for mult_str in multipliers:
        # Parse multiplier
        if mult_str.endswith("M"):
            mult = 1_000_000
            suffix = "M"
        elif mult_str.endswith("K"):
            mult = 1_000
            suffix = "K"
        else:
            mult = int(mult_str)
            suffix = ""

        for base in E12_VALUES:
            base_val = float(base)
            ohms = base_val * mult

            # Format value string
            if ohms >= 1_000_000:
                value_str = f"{base}M"
            elif ohms >= 1_000:
                if base_val == int(base_val):
                    value_str = f"{int(base_val)}K"
                else:
                    value_str = f"{base}K"
            else:
                value_str = f"{int(ohms)}"

            values.append(value_str)

    return values


def sql_escape(s):
    """Escape single quotes in SQL strings."""
    if s is None:
        return "NULL"
    return s.replace("'", "''")


def generate_resistor_sql(value, tolerance, package, specs):
    """Generate SQL INSERT statement for a resistor."""
    symbol_name = f"RES {value} {tolerance} {specs['power']} {package}"
    mpn = specs['mpn_template'].format(value=format_value_for_mpn(value))

    # Determine SPICE simulation values (auto-populated for resistors)
    sim_device = "R"
    sim_pins = "1=+ 2=-"
    sim_type = ""  # Empty for built-in model
    sim_library = ""  # Empty for built-in model

    # Generate INSERT statement
    sql = f"""INSERT INTO symbols (
    "Symbol_Name", "Reference", "Value",
    "KiCad_Symbol", "KiCad_Footprint", "Altium_Symbol", "Altium_Footprint",
    "Description", "Manufacturer", "MPN", "Package",
    "Component_Type", "Tolerance", "Power_Rating",
    "Sim_Device", "Sim_Pins", "Sim_Type", "Sim_Library",
    "Class"
) VALUES (
    '{sql_escape(symbol_name)}',
    'R',
    '{sql_escape(value)}',
    'terra_eda_lib:{sql_escape(symbol_name)}',
    '{sql_escape(specs["footprint"])}',
    NULL,
    NULL,
    '{sql_escape(f"{value} ohm {tolerance} resistor {specs['power']} {package}")}',
    '{sql_escape(specs["manufacturer"])}',
    '{sql_escape(mpn)}',
    '{sql_escape(package)}',
    'Resistor',
    '{sql_escape(tolerance)}',
    '{sql_escape(specs["power"])}',
    '{sql_escape(sim_device)}',
    '{sql_escape(sim_pins)}',
    '{sql_escape(sim_type)}',
    '{sql_escape(sim_library)}',
    'Resistor'
);"""

    return sql


def generate_schema():
    """Generate CREATE TABLE statement (same schema as terra_eda_lib)."""
    return """-- Terra EDA Library - Resistors
-- Auto-generated resistor library

DROP TABLE IF EXISTS symbols;

CREATE TABLE IF NOT EXISTS symbols (
  "Symbol_Name" TEXT,
  "Allow_Substitution" TEXT,
  "Altium_Footprint" TEXT,
  "Altium_Symbol" TEXT,
  "BOM_Comment" TEXT,
  "Class" TEXT,
  "Component_Type" TEXT,
  "Component_Value" TEXT,
  "Current_Rating" TEXT,
  "Datasheet" TEXT,
  "Description" TEXT,
  "Fitted" TEXT,
  "KiCad_Footprint" TEXT,
  "Manufacturer" TEXT,
  "Manufacturer_Link" TEXT,
  "MPN" TEXT,
  "Material" TEXT,
  "Number_of_Pins" TEXT,
  "Package" TEXT,
  "Part_ID" TEXT,
  "Power_Rating" TEXT,
  "Reference" TEXT,
  "RoHS" TEXT,
  "RoHS_Document_Link" TEXT,
  "Sim_Device" TEXT,
  "Sim_Library" TEXT,
  "Sim_Pins" TEXT,
  "Sim_Type" TEXT,
  "Standards_Version" TEXT,
  "KiCad_Symbol" TEXT,
  "Temp_Operating" TEXT,
  "Temp_Soldering" TEXT,
  "Temp_Storage" TEXT,
  "Temp_Coeff" TEXT,
  "Tolerance" TEXT,
  "Tracking" TEXT,
  "Value" TEXT,
  "Voltage_Rating" TEXT
);
"""


def main():
    parser = argparse.ArgumentParser(description="Generate resistor SQL for Terra EDA Library")
    parser.add_argument("--full-library", action="store_true",
                       help="Generate complete library with CREATE TABLE (for new library)")
    parser.add_argument("--package", default="0603",
                       choices=RESISTOR_SPECS.keys(),
                       help="Resistor package (default: 0603)")
    parser.add_argument("--tolerance", default="1%",
                       help="Tolerance (default: 1%%)")

    args = parser.parse_args()

    # Generate resistor values
    values = generate_resistor_values()
    specs = RESISTOR_SPECS[args.package]

    # Output header
    if args.full_library:
        print(generate_schema())
        print("\n-- Insert resistors")
        print("BEGIN TRANSACTION;\n")
    else:
        print("-- Terra EDA Library - Resistor Batch")
        print(f"-- Package: {args.package}, Tolerance: {args.tolerance}")
        print(f"-- Generated {len(values)} resistors\n")

    # Generate SQL for each resistor
    for value in values:
        sql = generate_resistor_sql(value, args.tolerance, args.package, specs)
        print(sql)
        print()  # Blank line between statements

    if args.full_library:
        print("\nCOMMIT;")
        print(f"\n-- Total: {len(values)} resistors")


if __name__ == "__main__":
    main()
