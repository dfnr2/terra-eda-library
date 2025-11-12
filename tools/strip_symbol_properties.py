#!/usr/bin/env python3
"""
Strip specific properties from KiCad symbol files.

This removes property definitions from symbol files so that database-driven
libraries can provide all field values from the database instead of having
them baked into the symbol definitions.

Uses S-expression parsing to correctly handle nested structures.
"""

import sys
import re
from pathlib import Path
try:
    import sexpdata
except ImportError:
    print("Error: sexpdata library not found. Install with: pip install sexpdata")
    sys.exit(1)


def is_property_to_remove(sexp, properties_to_remove: set[str]) -> bool:
    """Check if an S-expression is a property block that should be removed."""
    if not isinstance(sexp, list) or len(sexp) < 2:
        return False

    # Check if this is a (property "Name" ...) block
    if isinstance(sexp[0], sexpdata.Symbol) and str(sexp[0]) == 'property':
        if isinstance(sexp[1], str) and sexp[1] in properties_to_remove:
            return True

    return False


def format_sexp(sexp, indent=0, inline_threshold=40) -> str:
    """
    Format an S-expression with proper indentation, similar to KiCad's formatting.

    Args:
        sexp: The S-expression to format
        indent: Current indentation level
        inline_threshold: Max characters for inline formatting

    Returns:
        Formatted string
    """
    if not isinstance(sexp, list):
        # Atom - format based on type
        if isinstance(sexp, sexpdata.Symbol):
            return str(sexp)
        elif isinstance(sexp, str):
            # Escape quotes in strings
            escaped = sexp.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(sexp, (int, float)):
            return str(sexp)
        else:
            return str(sexp)

    if len(sexp) == 0:
        return "()"

    # Try inline format first for short expressions
    inline = "(" + " ".join(format_sexp(item, 0) for item in sexp) + ")"
    if len(inline) <= inline_threshold and '\n' not in inline:
        return inline

    # Multi-line format
    result = "("
    first = True

    for item in sexp:
        if first:
            result += format_sexp(item, indent)
            first = False
        else:
            if isinstance(item, list):
                # Nested list - put on new line with increased indent
                result += "\n" + "\t" * (indent + 1) + format_sexp(item, indent + 1)
            else:
                # Atom - can stay on same line with space
                result += " " + format_sexp(item, indent)

    result += ")"
    return result


def strip_properties(input_file: Path, output_file: Path, properties_to_remove: list[str]):
    """
    Remove property blocks from a KiCad symbol file using S-expression parsing.

    Args:
        input_file: Path to input .kicad_sym file
        output_file: Path to output .kicad_sym file
        properties_to_remove: List of property names to remove
    """
    # Read and parse the file
    with open(input_file, 'r') as f:
        content = f.read()

    # Parse S-expression
    try:
        sexp = sexpdata.loads(content)
    except Exception as e:
        print(f"Error parsing S-expression: {e}")
        raise

    # Convert to set for faster lookup
    properties_set = set(properties_to_remove)

    # Recursively filter properties
    def filter_sexp(obj):
        if not isinstance(obj, list):
            return obj

        # Check if this is a property to remove
        if is_property_to_remove(obj, properties_set):
            return None  # Mark for removal

        # Recursively filter children
        filtered = []
        for item in obj:
            result = filter_sexp(item)
            if result is not None:
                filtered.append(result)

        return filtered

    filtered_sexp = filter_sexp(sexp)

    # Format and write output
    output_text = format_sexp(filtered_sexp)

    with open(output_file, 'w') as f:
        f.write(output_text)
        f.write('\n')  # Final newline

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
