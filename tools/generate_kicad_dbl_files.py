#!/usr/bin/env python3
"""
Generate terra.kicad_dbl file with all component type tables.

This script reads the database schema and creates a single terra.kicad_dbl file
with all tables as separate libraries within it.
"""

import sqlite3
import json
import platform
import sys
from pathlib import Path
from typing import List, Dict


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """Get all column names for a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def get_all_tables(conn: sqlite3.Connection) -> List[str]:
    """Get all part tables (excluding infrastructure and sqlite_ tables)."""
    skip_tables = {
        'tags', 'user_tags', 'terra_tier_config', 'terra_tag_config',
        'terra_meta',
    }
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall() if row[0] not in skip_tables]


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
    # Skip internal/metadata columns and columns handled as library-level properties
    skip_cols = {
        'unique_id',  # Internal primary key (used as key field, not displayed)
        'part_locator',  # Internal database locator
        'altium_symbol', 'altium_footprint',  # Not relevant for KiCad
        'sim_model_type', 'sim_device', 'sim_pins', 'sim_model_file', 'sim_params',  # SPICE internals
        'source', 'dump_priority',  # Internal dump system metadata
        'exclude_from_bom',  # Handled as library-level property
        'tier', 'tags',  # Tier/tag system internals
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

    # Display name mappings
    display_name_map = {
        'mpn': 'Manufacturer PN',
        'kicad_footprint': 'Footprint',
        'kicad_symbol': 'Symbol',
        'rohs': 'RoHS',
        'rohs_document_link': 'RoHS Link',
        'lifecycle_status': 'Lifecycle Status',
        'allow_substitution': 'Allow Substitution',
        'tracking': 'Tracking',
        'standards_version': 'Standards Version',
        'bom_comment': 'BOM Comment',
        'created_at': 'Built On',
        'updated_at': 'Updated On',
        'created_by': 'Created By',
    }

    # Convert column name to display name
    display_name = display_name_map.get(column, column.replace('_', ' ').title())

    return {
        'column': column,
        'name': display_name,
        'visible_on_add': visible_on_add,
        'visible_in_chooser': visible_in_chooser
    }


# KiCad chooser labels for tables whose slug reads poorly as a category name.
# Unlisted tables fall back to the raw table name (the prevailing convention).
CATEGORY_DISPLAY_NAMES = {
    'optoelectronics_led': 'Optoelectronics - LED',
    'optoelectronics_sensor': 'Optoelectronics - Sensor',
}


def create_library_config(conn: sqlite3.Connection, table_name: str) -> Dict:
    """Create library configuration for a specific table."""
    # Get all columns
    columns = get_table_columns(conn, table_name)

    # Determine primary key column
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    pk_col = None
    for row in cursor.fetchall():
        if row[5]:  # pk flag is non-zero
            pk_col = row[1]
            break
    if pk_col is None:
        pk_col = columns[0]  # fallback to first column

    # Create field configurations
    fields = []
    for col in columns:
        field = create_field_config(col)
        if field:
            fields.append(field)

    # Build library-level properties mapping column names for KiCad properties
    properties = {}
    if 'description' in columns:
        properties['description'] = 'description'
    if 'exclude_from_bom' in columns:
        properties['exclude_from_bom'] = 'exclude_from_bom'

    # Use the filtered view (*_v) instead of the raw table
    view_name = f'{table_name}_v'

    config = {
        'name': CATEGORY_DISPLAY_NAMES.get(table_name, table_name),
        'table': view_name,
        'key': pk_col,
        'symbols': 'kicad_symbol',
        'footprints': 'kicad_footprint',
        'fields': fields
    }

    if properties:
        config['properties'] = properties

    return config


def find_sqlite_odbc_driver() -> str:
    """Find the SQLite ODBC driver for the current platform."""
    system = platform.system()

    if system == 'Darwin':
        candidates = [
            Path('/usr/local/lib/libsqlite3odbc.dylib'),   # Homebrew
            Path('/opt/local/lib/libsqlite3odbc.dylib'),    # MacPorts
            Path('/opt/homebrew/lib/libsqlite3odbc.dylib'),  # Homebrew Apple Silicon
        ]
    elif system == 'Linux':
        import struct
        bits = struct.calcsize('P') * 8
        # Debian/Ubuntu multiarch, then generic paths
        candidates = [
            Path(f'/usr/lib/{platform.machine()}-linux-gnu/odbc/libsqlite3odbc.so'),
            Path('/usr/lib/odbc/libsqlite3odbc.so'),
            Path('/usr/lib64/libsqlite3odbc.so'),
            Path('/usr/local/lib/libsqlite3odbc.so'),
        ]
    elif system == 'Windows':
        candidates = [
            Path(r'C:\Windows\System32\sqlite3odbc.dll'),
        ]
    else:
        candidates = []

    for path in candidates:
        if path.exists():
            return str(path)

    searched = '\n  '.join(str(p) for p in candidates)
    print(f'Error: SQLite ODBC driver not found. Searched:\n  {searched}', file=sys.stderr)
    print(f'\nInstall it with:', file=sys.stderr)
    if system == 'Darwin':
        print(f'  brew install sqliteodbc', file=sys.stderr)
    elif system == 'Linux':
        print(f'  sudo apt-get install libsqliteodbc', file=sys.stderr)
    sys.exit(1)


def generate_unified_dbl_file(db_path: Path, output_dir: Path, tables: List[str]):
    """Generate a single terra.kicad_dbl file with all tables."""
    conn = sqlite3.connect(str(db_path))

    # Create library configs for all tables
    libraries = []
    for table in tables:
        libraries.append(create_library_config(conn, table))
        print(f'  + Added library: {table}')

    conn.close()

    # Auto-detect ODBC driver for this platform
    odbc_driver = find_sqlite_odbc_driver()
    print(f'  Using ODBC driver: {odbc_driver}')

    # KiCad does NOT expand path variables inside the ODBC connection string
    # (only in the lib-table file URI) — ${KIPRJMOD} and ${TERRA_EDA_LIB} both
    # produced "[SQLite]connect failed". The connection string is handed to the
    # driver verbatim, so emit an absolute path to the master DB. terra.kicad_dbl
    # is generated/gitignored and rebuilt per machine, so this stays correct.
    db_kicad_path = str(db_path.resolve())

    # Create the unified .kicad_dbl structure
    dbl_config = {
        'meta': {
            'version': 1,
            'filename': 'terra.kicad_dbl'
        },
        'name': 'Terra EDA Library',
        'description': 'Multi-table component library for all component types',
        'source': {
            'type': 'odbc',
            'dsn': '',
            'username': '',
            'password': '',
            'timeout_seconds': 2,
            'connection_string': f'DRIVER={odbc_driver};Database={db_kicad_path};Timeout=2000;'
        },
        'libraries': libraries
    }

    # Write to file
    output_file = output_dir / 'terra.kicad_dbl'
    with open(output_file, 'w') as f:
        json.dump(dbl_config, f, indent=2)

    print(f'\nCreated {output_file.name}')


def main():
    if len(sys.argv) < 2:
        print('Usage: generate_kicad_dbl_files.py <db_path>')
        print('  db_path: Path to terra.db')
        sys.exit(1)

    db_path = Path(sys.argv[1])
    output_dir = db_path.parent.parent  # Go up from db/ to repo root

    print(f'Reading database: {db_path}')
    print(f'Output directory: {output_dir}')
    print()

    conn = sqlite3.connect(str(db_path))
    tables = get_all_tables(conn)
    conn.close()

    print(f'Generating terra.kicad_dbl with {len(tables)} tables (using *_v filtered views)...')
    print()

    generate_unified_dbl_file(db_path, output_dir, tables)

    print()
    print('Add to KiCad:')
    print('  Preferences -> Manage Symbol Libraries -> Database Libraries')
    print('  Click + to add terra.kicad_dbl and terra_sym.kicad_sym')
    print()
    print(f'Libraries included: {", ".join(tables)}')


if __name__ == '__main__':
    main()
