#!/usr/bin/env python3
"""
Strip specific properties from KiCad symbol files.

This removes property definitions from symbol files so that database-driven
libraries can provide all field values from the database instead of having
them baked into the symbol definitions.
"""

import sys
import re
from pathlib import Path


def strip_properties(input_file: Path, output_file: Path, properties_to_remove: list[str]):
    """
    Remove property blocks from a KiCad symbol file.

    Args:
        input_file: Path to input .kicad_sym file
        output_file: Path to output .kicad_sym file
        properties_to_remove: List of property names to remove (e.g., ["Component Value", "Component Type"])
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Parse and filter properties by walking through the file
    output_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line starts a property we want to remove
        prop_match = re.search(r'\(property "([^"]+)"', line)
        if prop_match:
            prop_name = prop_match.group(1)
            if prop_name in properties_to_remove:
                # Skip this entire property block by counting parentheses
                depth = line.count('(') - line.count(')')
                i += 1
                while i < len(lines) and depth > 0:
                    depth += lines[i].count('(') - lines[i].count(')')
                    i += 1
                continue

        output_lines.append(line)
        i += 1

    # Write output
    with open(output_file, 'w') as f:
        f.writelines(output_lines)

    print(f"✓ Stripped properties from {input_file}")
    print(f"  Output: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python strip_symbol_properties.py <symbol_file>")
        print("       python strip_symbol_properties.py <input_file> <output_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        # Default: overwrite input file
        output_file = input_file

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    # KiCad default properties - KEEP THESE
    kicad_defaults = {
        'Reference',
        'Value',
        'Footprint',
        'Datasheet',
        'Description',
        'ki_fp_filters',
        'ki_keywords',
        'ki_locked',
        'ki_description',  # Sometimes used
    }

    # Get all properties in the file
    print(f"Analyzing: {input_file}")
    with open(input_file, 'r') as f:
        content = f.read()

    # Find all unique property names
    all_properties = set(re.findall(r'\(property "([^"]+)"', content))

    # Calculate which properties to remove (anything not in KiCad defaults)
    properties_to_remove = sorted(all_properties - kicad_defaults)

    print(f"\nKiCad default properties (keeping): {sorted(kicad_defaults & all_properties)}")
    print(f"\nCustom properties (removing {len(properties_to_remove)} types):")
    for prop in properties_to_remove:
        count = len(re.findall(rf'\(property "{re.escape(prop)}"', content))
        print(f"  - {prop} ({count} occurrences)")

    strip_properties(input_file, output_file, properties_to_remove)

    print("\n✓ Done - all custom properties removed, KiCad defaults preserved")


if __name__ == '__main__':
    main()
