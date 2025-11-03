#!/usr/bin/env python3
"""
KiCad Symbol Library to SQL Script Converter

This script parses a KiCad symbol library (.kicad_sym) file and exports
the symbols and their properties to a SQL script that can be executed
to create a SQLite database.

Features:
- Generates SQL script (instead of directly creating database)
- Includes SPICE simulation fields (Sim.Device, Sim.Pins, Sim.Type, Sim.Library)
- Automatically populates SPICE fields for passive components (R, L, C) using built-in models
- For other components, SPICE fields are left empty for manual external model linking

SPICE Model Handling:
- Resistors (R): Uses built-in model based on Value field
- Inductors (L): Uses built-in model based on Value field
- Capacitors (C): Uses built-in model based on Value field
- Other components: SPICE fields included but empty (can be populated with external model paths)

Usage:
    python kicad_sym_to_db.py <input.kicad_sym> <output.sql> [--config <config.yaml>]

To create the database:
    sqlite3 output.db < output.sql
"""

import argparse
import re
import sqlite3
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class SExpressionParser:
    """Simple S-expression parser for KiCad symbol library format."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def skip_whitespace(self):
        """Skip whitespace and comments."""
        while self.pos < self.length:
            if self.text[self.pos].isspace():
                self.pos += 1
            else:
                break

    def parse_string(self) -> str:
        """Parse a quoted string."""
        if self.text[self.pos] != '"':
            raise ValueError(f"Expected '\"' at position {self.pos}")

        self.pos += 1
        start = self.pos
        result = []

        while self.pos < self.length:
            if self.text[self.pos] == '"':
                self.pos += 1
                return ''.join(result)
            elif self.text[self.pos] == '\\' and self.pos + 1 < self.length:
                # Handle escape sequences
                self.pos += 1
                result.append(self.text[self.pos])
                self.pos += 1
            else:
                result.append(self.text[self.pos])
                self.pos += 1

        raise ValueError("Unterminated string")

    def parse_atom(self) -> str:
        """Parse an unquoted atom."""
        start = self.pos
        while self.pos < self.length and not self.text[self.pos].isspace() and self.text[self.pos] not in '()':
            self.pos += 1
        return self.text[start:self.pos]

    def parse(self):
        """Parse an S-expression."""
        self.skip_whitespace()

        if self.pos >= self.length:
            return None

        if self.text[self.pos] == '(':
            # Parse a list
            self.pos += 1
            result = []

            while True:
                self.skip_whitespace()

                if self.pos >= self.length:
                    raise ValueError("Unterminated list")

                if self.text[self.pos] == ')':
                    self.pos += 1
                    return result

                result.append(self.parse())

        elif self.text[self.pos] == '"':
            # Parse a quoted string
            return self.parse_string()

        else:
            # Parse an atom
            return self.parse_atom()


def extract_symbols_from_sexp(sexp, library_name: str = None) -> List[Dict[str, str]]:
    """Extract symbol information from parsed S-expression.

    Args:
        sexp: Parsed S-expression
        library_name: Name of the library (without .kicad_sym extension) to prepend to symbol references

    Returns:
        List of symbol dictionaries with properties
    """
    symbols = []

    if not isinstance(sexp, list):
        return symbols

    # Look for symbol definitions
    for item in sexp:
        if isinstance(item, list) and len(item) > 0:
            if item[0] == 'symbol' and len(item) > 1:
                # Found a symbol definition
                symbol_name = item[1]

                # Create Symbol reference in library_name:symbol_name format
                if library_name:
                    symbol_ref = f"{library_name}:{symbol_name}"
                else:
                    symbol_ref = symbol_name

                properties = {
                    'Symbol_Name': symbol_name,
                    'Symbol': symbol_ref  # Set Symbol field to reference the symbol in the library
                }

                # Extract properties from the symbol
                for sub_item in item[2:]:
                    if isinstance(sub_item, list) and len(sub_item) > 0:
                        if sub_item[0] == 'property' and len(sub_item) > 2:
                            prop_name = sub_item[1]
                            prop_value = sub_item[2]
                            properties[prop_name] = prop_value

                symbols.append(properties)
            else:
                # Recursively search for symbols
                symbols.extend(extract_symbols_from_sexp(item, library_name))

    return symbols


def load_config(config_path: Optional[Path]) -> Tuple[Dict, Dict, Dict]:
    """Load configuration from YAML config file.

    Args:
        config_path: Path to YAML config file containing field mappings and column edits

    Returns:
        Tuple of (field_mappings dict, field_mapping_patterns list, column_edits dict)
        - field_mappings: {exact_field_name: normalized_name}
        - field_mapping_patterns: [{pattern: regex, replacement: normalized_name}, ...]
        - column_edits: {column_name_or_pattern: 'add' or 'remove'}
    """
    if config_path is None or not config_path.exists():
        return {}, [], {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if config is None:
            return {}, [], {}

        field_mappings = config.get('field_mappings', {})
        field_mapping_patterns_raw = config.get('field_mapping_patterns', [])
        column_edits = config.get('column_edits', {})

        # Normalize field_mapping_patterns to list of dicts format
        # Support both {"pattern": "replacement"} and [{"pattern": "...", "replacement": "..."}]
        field_mapping_patterns = []
        if isinstance(field_mapping_patterns_raw, dict):
            # Convert dict format to list of dicts
            for pattern, replacement in field_mapping_patterns_raw.items():
                field_mapping_patterns.append({'pattern': pattern, 'replacement': replacement})
        elif isinstance(field_mapping_patterns_raw, list):
            # Already in list format
            field_mapping_patterns = field_mapping_patterns_raw
        else:
            field_mapping_patterns = []

        return field_mappings, field_mapping_patterns, column_edits
    except Exception as e:
        print(f"Warning: Error loading config file {config_path}: {e}", file=sys.stderr)
        return {}, [], {}


def collect_all_fields(symbols: List[Dict[str, str]]) -> Set[str]:
    """Collect all unique field names from all symbols.

    Automatically includes required fields for KiCad db-lib and SPICE simulation.
    """
    fields = set()
    for symbol in symbols:
        fields.update(symbol.keys())

    # Always include required db-lib fields
    fields.add('Symbol')
    fields.add('Footprint')

    # Always include SPICE simulation fields
    # See: https://dev-docs.kicad.org/en/addons/database-libraries/#simmodel_fields
    fields.add('Sim.Device')
    fields.add('Sim.Pins')
    fields.add('Sim.Type')
    fields.add('Sim.Library')

    return fields


def apply_column_edits(fields: Set[str], column_edits: Dict[str, str]) -> Set[str]:
    """Apply column add/remove operations from config.

    Supports regex patterns for matching multiple columns.
    For example: '^ki_.*': remove' will remove all fields starting with 'ki_'.

    Args:
        fields: Set of field names from symbols
        column_edits: Dict with {column_name_or_regex_pattern: 'add' or 'remove'}

    Returns:
        Modified set of fields
    """
    fields = fields.copy()

    for col_pattern, action in column_edits.items():
        if action == 'add':
            # Add operation doesn't support patterns - must be exact name
            if col_pattern.startswith('^') or col_pattern.endswith('$') or any(c in col_pattern for c in r'.*+?[]{}()\|'):
                print(f"Warning: Regex patterns not supported for 'add' action: '{col_pattern}'", file=sys.stderr)
            else:
                fields.add(col_pattern)
        elif action == 'remove':
            # Remove operation supports regex patterns
            # Check if it looks like a regex pattern
            if col_pattern.startswith('^') or col_pattern.endswith('$') or any(c in col_pattern for c in r'.*+?[]{}()\|'):
                try:
                    pattern = re.compile(col_pattern)
                    matching_fields = [f for f in fields if pattern.match(f)]
                    for field in matching_fields:
                        fields.discard(field)
                    if matching_fields:
                        print(f"  Removing {len(matching_fields)} fields matching regex '{col_pattern}'")
                except re.error as e:
                    print(f"Warning: Invalid regex pattern '{col_pattern}': {e}", file=sys.stderr)
            else:
                # Exact match
                fields.discard(col_pattern)
        else:
            print(f"Warning: Unknown column edit action '{action}' for column '{col_pattern}'", file=sys.stderr)

    return fields


def create_field_mapping(fields: Set[str], name_mappings: Dict[str, str] = None,
                         mapping_patterns: List[Dict] = None) -> Dict[str, str]:
    """Create mapping from original field names to unique sanitized column names.

    When multiple fields map to the same column (e.g., "Current" -> "Current_Rating"
    and "Current_Rating" exists), they merge into a single column.

    Args:
        fields: Set of all field names found in symbols
        name_mappings: Optional dictionary of exact field name normalizations from config
        mapping_patterns: Optional list of {pattern: regex, replacement: name} for pattern-based mappings

    Returns:
        Dictionary mapping original field names to database column names
    """
    if name_mappings is None:
        name_mappings = {}
    if mapping_patterns is None:
        mapping_patterns = []

    field_list = sorted(fields)

    # Ensure Symbol_Name is first
    if 'Symbol_Name' in field_list:
        field_list.remove('Symbol_Name')
        field_list.insert(0, 'Symbol_Name')

    # Create mapping - allow multiple original fields to map to the same column
    mapping = {}

    for field in field_list:
        normalized_field = None

        # First check exact name mappings
        if field in name_mappings:
            normalized_field = name_mappings[field]
        else:
            # Try pattern-based mappings
            for pattern_def in mapping_patterns:
                pattern = pattern_def.get('pattern')
                replacement = pattern_def.get('replacement')
                if pattern and replacement:
                    try:
                        regex = re.compile(pattern)
                        if regex.search(field):
                            normalized_field = replacement
                            break
                    except re.error as e:
                        print(f"Warning: Invalid regex pattern '{pattern}': {e}", file=sys.stderr)

        # If no mapping found, use the field name as-is
        if normalized_field is None:
            normalized_field = field

        # Sanitize field name for SQL (replace spaces and special chars with underscores)
        safe_field = re.sub(r'[^\w]+', '_', normalized_field).strip('_')

        # Store the mapping - multiple fields can map to the same column
        mapping[field] = safe_field

    return mapping


def get_unique_columns(field_mapping: Dict[str, str]) -> List[str]:
    """Get list of unique column names from field mapping, preserving order.

    Uses case-insensitive comparison to avoid duplicate column names.

    Args:
        field_mapping: Dict mapping original field names to column names

    Returns:
        Ordered list of unique column names
    """
    seen_lower = set()
    unique_cols = []

    for original_field in field_mapping.keys():
        col_name = field_mapping[original_field]
        col_name_lower = col_name.lower()

        if col_name_lower not in seen_lower:
            seen_lower.add(col_name_lower)
            unique_cols.append(col_name)

    return unique_cols


def sql_escape(value: Optional[str]) -> str:
    """Escape a string value for SQL, handling NULL values."""
    if value is None or value == '':
        return 'NULL'
    # Escape single quotes by doubling them
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def generate_create_table_sql(field_mapping: Dict[str, str]) -> str:
    """Generate CREATE TABLE SQL statement for symbols table."""
    # Get unique column names (multiple fields may map to same column)
    unique_columns = get_unique_columns(field_mapping)

    # Create column definitions
    columns = [f'"{col}" TEXT' for col in unique_columns]

    create_table_sql = f"CREATE TABLE IF NOT EXISTS symbols (\n  {',\n  '.join(columns)}\n);"
    return create_table_sql


def create_database(db_path: str, field_mapping: Dict[str, str]) -> sqlite3.Connection:
    """Create SQLite database with table for symbols."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get unique column names (multiple fields may map to same column)
    unique_columns = get_unique_columns(field_mapping)

    # Create column definitions
    columns = [f'"{col}" TEXT' for col in unique_columns]

    create_table_sql = f"CREATE TABLE symbols ({', '.join(columns)})"
    cursor.execute(create_table_sql)

    conn.commit()
    return conn


def get_existing_columns(conn: sqlite3.Connection) -> List[str]:
    """Get list of column names from existing symbols table."""
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(symbols)")
        columns = [row[1] for row in cursor.fetchall()]
        return columns
    except sqlite3.OperationalError:
        return []


def merge_schemas(existing_cols: List[str], new_field_mapping: Dict[str, str]) -> Dict[str, str]:
    """Merge existing database columns with new field mapping.

    Args:
        existing_cols: List of column names from existing database
        new_field_mapping: Field mapping from new symbols

    Returns:
        Combined field mapping that includes all columns
    """
    # Start with existing columns in order
    combined = {col: col for col in existing_cols}

    # Add new columns from field mapping
    for original, safe_name in new_field_mapping.items():
        if safe_name not in combined.values():
            combined[original] = safe_name

    return combined


def add_missing_columns(conn: sqlite3.Connection, existing_cols: List[str], field_mapping: Dict[str, str]):
    """Add new columns to existing database table.

    Args:
        conn: Database connection
        existing_cols: List of existing column names
        field_mapping: Complete field mapping including new fields
    """
    cursor = conn.cursor()

    # Get the lowercase set of existing columns for case-insensitive comparison
    existing_cols_lower = {col.lower() for col in existing_cols}

    for original, safe_name in field_mapping.items():
        if safe_name.lower() not in existing_cols_lower:
            print(f"  Adding new column: {safe_name}")
            cursor.execute(f'ALTER TABLE symbols ADD COLUMN "{safe_name}" TEXT')

    conn.commit()


def populate_spice_fields(symbol: Dict[str, str]) -> Dict[str, str]:
    """Populate SPICE simulation fields for a symbol.

    For passive components (R, L, C), uses built-in SPICE models based on the Value field.
    For other components, leaves SPICE fields empty (can be filled with external model info).

    Args:
        symbol: Symbol dictionary

    Returns:
        Updated symbol dictionary with SPICE fields populated
    """
    # Get the symbol's reference prefix (first character of Reference field)
    reference = symbol.get('Reference', '')
    value = symbol.get('Value', '')

    # Initialize SPICE fields if not already present
    if 'Sim.Device' not in symbol:
        symbol['Sim.Device'] = None
    if 'Sim.Pins' not in symbol:
        symbol['Sim.Pins'] = None
    if 'Sim.Type' not in symbol:
        symbol['Sim.Type'] = None
    if 'Sim.Library' not in symbol:
        symbol['Sim.Library'] = None

    # For resistors, inductors, and capacitors, use built-in models
    if reference.startswith('R') and value:
        symbol['Sim.Device'] = 'R'
        symbol['Sim.Pins'] = '1=+ 2=-'
        symbol['Sim.Type'] = ''  # Empty for built-in model
        symbol['Sim.Library'] = ''  # Empty for built-in model
    elif reference.startswith('L') and value:
        symbol['Sim.Device'] = 'L'
        symbol['Sim.Pins'] = '1=+ 2=-'
        symbol['Sim.Type'] = ''
        symbol['Sim.Library'] = ''
    elif reference.startswith('C') and value:
        symbol['Sim.Device'] = 'C'
        symbol['Sim.Pins'] = '1=+ 2=-'
        symbol['Sim.Type'] = ''
        symbol['Sim.Library'] = ''

    return symbol


def prepare_symbol_values(symbol: Dict[str, str], field_mapping: Dict[str, str]) -> Dict[str, str]:
    """Prepare symbol values for insertion, merging fields that map to the same column.

    When multiple fields map to the same column, uses the first non-None value found.
    Priority is given to fields that are NOT mapped (i.e., the target field name itself).
    Uses case-insensitive comparison for column names.

    Args:
        symbol: Dictionary of symbol field values
        field_mapping: Mapping from original field names to database columns

    Returns:
        Dictionary mapping column names to values
    """
    # Populate SPICE fields first
    symbol = populate_spice_fields(symbol)

    column_values = {}

    # Group original fields by their target column (case-insensitive)
    column_to_fields = {}
    column_canonical = {}  # Maps lowercase -> canonical name

    for original, column in field_mapping.items():
        column_lower = column.lower()

        if column_lower not in column_canonical:
            column_canonical[column_lower] = column

        if column_lower not in column_to_fields:
            column_to_fields[column_lower] = []
        column_to_fields[column_lower].append(original)

    # For each column, find the first non-None value
    # Prioritize unmapped fields (where original == column after sanitization)
    for column_lower, original_fields in column_to_fields.items():
        value = None
        canonical_column = column_canonical[column_lower]

        # Sort fields to prioritize the target column name itself
        sorted_fields = sorted(original_fields, key=lambda f: 0 if re.sub(r'[^\w]+', '_', f).strip('_').lower() == column_lower else 1)

        for original in sorted_fields:
            field_value = symbol.get(original)
            if field_value is not None:
                value = field_value
                break

        column_values[canonical_column] = value

    return column_values


def generate_insert_sql(symbols: List[Dict[str, str]], field_mapping: Dict[str, str]) -> List[str]:
    """Generate INSERT SQL statements for symbols.

    Args:
        symbols: List of symbol dictionaries
        field_mapping: Mapping from original field names to database columns

    Returns:
        List of SQL INSERT statements
    """
    # Get unique columns
    unique_columns = get_unique_columns(field_mapping)
    columns_str = ', '.join([f'"{col}"' for col in unique_columns])

    insert_statements = []

    for symbol in symbols:
        # Prepare values, merging fields that map to the same column
        column_values = prepare_symbol_values(symbol, field_mapping)
        values = [column_values.get(col) for col in unique_columns]

        # Escape values for SQL
        escaped_values = [sql_escape(v) for v in values]
        values_str = ', '.join(escaped_values)

        insert_sql = f"INSERT INTO symbols ({columns_str}) VALUES ({values_str});"
        insert_statements.append(insert_sql)

    return insert_statements


def insert_symbols(conn: sqlite3.Connection, symbols: List[Dict[str, str]], field_mapping: Dict[str, str], merge_mode: bool = False):
    """Insert symbols into the database.

    Args:
        conn: Database connection
        symbols: List of symbol dictionaries
        field_mapping: Mapping from original field names to database columns
        merge_mode: If True, skip duplicate symbols based on Symbol_Name
    """
    cursor = conn.cursor()

    # Get unique columns
    unique_columns = get_unique_columns(field_mapping)

    if merge_mode:
        # Get existing symbol names
        cursor.execute('SELECT Symbol_Name FROM symbols')
        existing_symbols = {row[0] for row in cursor.fetchall()}

        # Remove duplicates from new symbols
        symbols_to_insert = [s for s in symbols if s.get('Symbol_Name') not in existing_symbols]

        if len(symbols_to_insert) < len(symbols):
            print(f"  Skipping {len(symbols) - len(symbols_to_insert)} duplicate symbols")

        symbols = symbols_to_insert

    placeholders = ', '.join(['?' for _ in unique_columns])
    columns_str = ', '.join([f'"{col}"' for col in unique_columns])
    insert_sql = f"INSERT INTO symbols ({columns_str}) VALUES ({placeholders})"

    for symbol in symbols:
        # Prepare values, merging fields that map to the same column
        column_values = prepare_symbol_values(symbol, field_mapping)
        values = [column_values.get(col) for col in unique_columns]
        cursor.execute(insert_sql, values)

    conn.commit()


def main():
    parser = argparse.ArgumentParser(
        description='Convert KiCad symbol library to SQL script'
    )
    parser.add_argument('input', help='Input KiCad symbol library file (.kicad_sym)')
    parser.add_argument('output', help='Output SQL script file (.sql)')
    parser.add_argument('--config', '-c', help='YAML config file for field name mappings and column edits', default=None)

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # Validate input file
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix == '.kicad_sym':
        print(f"Warning: Input file does not have .kicad_sym extension", file=sys.stderr)

    print(f"Reading symbol library: {input_path}")

    # Read and parse the symbol library
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract library name from input filename (without .kicad_sym extension)
    library_name = input_path.stem

    print("Parsing S-expressions...")
    try:
        parser = SExpressionParser(content)
        sexp = parser.parse()
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting symbols from library '{library_name}'...")
    symbols = extract_symbols_from_sexp(sexp, library_name)

    if not symbols:
        print("Warning: No symbols found in the library", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(symbols)} symbols")

    # Load config (field mappings and column edits)
    config_path = Path(args.config) if args.config else None
    name_mappings, mapping_patterns, column_edits = load_config(config_path)
    if name_mappings:
        print(f"Loaded {len(name_mappings)} field name mappings from config")
    if mapping_patterns:
        print(f"Loaded {len(mapping_patterns)} field mapping patterns from config")
    if column_edits:
        print(f"Loaded {len(column_edits)} column edits from config")

    # Collect all fields
    print("Collecting all fields...")
    fields = collect_all_fields(symbols)
    print(f"Found {len(fields)} unique fields: {', '.join(sorted(fields))}")

    # Apply column edits
    if column_edits:
        print("Applying column edits...")
        fields = apply_column_edits(fields, column_edits)

    # Create field mapping to handle duplicate column names
    print("Creating field mapping...")
    field_mapping = create_field_mapping(fields, name_mappings, mapping_patterns)

    # Generate SQL statements
    print("Generating SQL statements...")

    # Generate CREATE TABLE statement
    create_table_sql = generate_create_table_sql(field_mapping)

    # Generate INSERT statements
    insert_statements = generate_insert_sql(symbols, field_mapping)

    print(f"  Generated {len(insert_statements)} INSERT statements")

    # Write SQL to output file
    print(f"Writing SQL script to: {output_path}")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header comment
            f.write(f"-- KiCad Symbol Library SQL Script\n")
            f.write(f"-- Generated from: {input_path.name}\n")
            f.write(f"-- Number of symbols: {len(symbols)}\n")
            f.write(f"--\n")
            f.write(f"-- To create the database, run:\n")
            f.write(f"--   sqlite3 output.db < {output_path.name}\n")
            f.write(f"--\n\n")

            # Write CREATE TABLE
            f.write("-- Create symbols table\n")
            f.write(create_table_sql)
            f.write("\n\n")

            # Write INSERT statements
            f.write("-- Insert symbols\n")
            f.write("BEGIN TRANSACTION;\n\n")
            for insert_sql in insert_statements:
                f.write(insert_sql)
                f.write("\n")
            f.write("\nCOMMIT;\n")

    except Exception as e:
        print(f"Error writing SQL file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully generated SQL script")
    print(f"SQL script saved to: {output_path}")


if __name__ == '__main__':
    main()
