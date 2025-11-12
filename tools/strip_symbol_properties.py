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
        content = f.read()

    # For each property to remove, create a regex pattern that matches the entire property block
    # Pattern matches: (property "Name" "value" ... ) including nested parentheses
    for prop_name in properties_to_remove:
        # Escape the property name for use in regex
        escaped_name = re.escape(prop_name)

        # Pattern to match property block with nested parentheses
        # Matches: (property "Name" ... ) including all nested content
        pattern = rf'\(property "{escaped_name}"[^)]*(?:\([^)]*(?:\([^)]*\)[^)]*)*\)[^)]*)*\)'

        # Keep removing matches until none are left (handles multiple occurrences)
        while True:
            new_content = re.sub(pattern, '', content, count=1)
            if new_content == content:
                break
            content = new_content

    # Clean up any resulting blank lines (more than 2 consecutive newlines)
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Write output
    with open(output_file, 'w') as f:
        f.write(content)

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
