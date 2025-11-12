#!/usr/bin/env python3
"""
Generate .kicad_dbl files for all component type tables.

This script reads the database schema and creates a .kicad_dbl file for each table,
allowing KiCad to access all component types as separate libraries.
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import List, Dict


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """Get all column names for a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def get_all_tables(conn: sqlite3.Connection) -> List[str]:
    """Get all user tables (excluding sqlite_ tables)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]


def get_display_name(table_name: str) -> str:
    """Convert table name to display name."""
    name_map = {
        'bjt': 'BJT Transistors',
        'mosfet': 'MOSFET Transistors',
        'ic_analog': 'Analog ICs',
        'ic_drivers': 'Driver ICs',
        'ic_logic': 'Logic ICs',
        'ic_memory': 'Memory ICs',
        'ic_microcontrollers': 'Microcontrollers',
        'ic_opamp': 'Op-Amps',
    }
    return name_map.get(table_name, table_name.replace('_', ' ').title())


def create_field_config(column: str) -> Dict:
    """Create field configuration for a column."""
    # Skip internal/metadata columns
    skip_cols = {
        'part_id', 'created_at', 'updated_at', 'created_by',
        'lifecycle_status', 'rohs_document_link', 'allow_substitution',
        'tracking', 'standards_version', 'bom_comment',
        'altium_symbol', 'altium_footprint',
        'sim_model_type', 'sim_device', 'sim_pins', 'sim_model_file', 'sim_params'
    }

    if column in skip_cols:
        return None

    # Special handling for specific columns
    visible_in_chooser = column in {
        'value', 'description', 'mpn', 'manufacturer', 'package',
        'kicad_footprint', 'tolerance', 'power_rating', 'voltage_rating',
        'current_rating', 'dielectric', 'color', 'wavelength'
    }

    visible_on_add = column in {'value'}

    # Convert column name to display name
    display_name = column.replace('_', ' ').title()
    if column == 'mpn':
        display_name = 'Manufacturer PN'
    elif column == 'kicad_footprint':
        display_name = 'Footprint'
    elif column == 'kicad_symbol':
        display_name = 'Symbol'

    return {
        'column': column,
        'name': display_name,
        'visible_on_add': visible_on_add,
        'visible_in_chooser': visible_in_chooser
    }


def generate_dbl_file(db_path: Path, output_dir: Path, table_name: str, terra_path: str):
    """Generate a .kicad_dbl file for a specific table."""
    conn = sqlite3.connect(str(db_path))

    # Get all columns
    columns = get_table_columns(conn, table_name)

    # Create field configurations
    fields = []
    for col in columns:
        field = create_field_config(col)
        if field:
            fields.append(field)

    conn.close()

    # Create the .kicad_dbl structure
    dbl_config = {
        'meta': {
            'version': 0,
            'filename': f'terra_{table_name}.kicad_dbl'
        },
        'name': f'Terra EDA Library - {get_display_name(table_name)}',
        'description': f'Multi-table component library - {get_display_name(table_name)}',
        'source': {
            'type': 'odbc',
            'dsn': '',
            'username': '',
            'password': '',
            'timeout_seconds': 2,
            'connection_string': f'DRIVER=/usr/local/lib/libsqlite3odbc.dylib;Database={terra_path}/db/terra.db;Timeout=2000;'
        },
        'libraries': [
            {
                'name': f'terra_{table_name}',
                'table': table_name,
                'key': 'part_id',
                'symbols': 'kicad_symbol',
                'footprints': 'kicad_footprint',
                'fields': fields
            }
        ]
    }

    # Write to file
    output_file = output_dir / f'terra_{table_name}.kicad_dbl'
    with open(output_file, 'w') as f:
        json.dump(dbl_config, f, indent=2)

    print(f'  ✓ Created {output_file.name}')


def main():
    if len(sys.argv) < 2:
        print('Usage: generate_kicad_dbl_files.py <db_path> [terra_path]')
        print('  db_path: Path to terra.db')
        print('  terra_path: Path to terra-eda-library root (default: auto-detect)')
        sys.exit(1)

    db_path = Path(sys.argv[1])

    if len(sys.argv) >= 3:
        terra_path = sys.argv[2]
    else:
        # Auto-detect: assume we're in tools/ and terra-eda-library is parent of db/
        terra_path = str(db_path.parent.parent.absolute())

    output_dir = db_path.parent.parent  # Go up from db/ to repo root

    print(f'Reading database: {db_path}')
    print(f'Terra path: {terra_path}')
    print(f'Output directory: {output_dir}')
    print()

    conn = sqlite3.connect(str(db_path))
    tables = get_all_tables(conn)
    conn.close()

    print(f'Generating .kicad_dbl files for {len(tables)} tables...')
    print()

    for table in tables:
        generate_dbl_file(db_path, output_dir, table, terra_path)

    print()
    print(f'✓ Generated {len(tables)} .kicad_dbl files')
    print()
    print('Add these to KiCad:')
    print('  Preferences → Manage Symbol Libraries → Database Libraries')
    print('  Click + to add each terra_*.kicad_dbl file')


if __name__ == '__main__':
    main()
