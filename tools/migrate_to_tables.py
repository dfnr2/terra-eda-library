#!/usr/bin/env python3
"""
Migrate Single-Table Database to Multi-Table Structure

This script migrates the legacy single-table 'symbols' database to the new
multi-table architecture with one table per component type.

Features:
- Reads from old 'symbols' table
- Categorizes components by Reference field
- Maps old field names to new standardized names
- Converts YES/NO strings to BOOLEAN
- Creates new database with 15 component type tables
- Can optionally dump to db/tables/ SQL structure

Usage:
    python migrate_to_tables.py <input.db> <output.db> [--dump-sql <output_dir>]

Example:
    python migrate_to_tables.py db/terra.db db/terra_new.db
    python migrate_to_tables.py db/terra.db db/terra_new.db --dump-sql db/tables/
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


# Component type mapping based on Reference field
REFERENCE_TO_TABLE = {
    'R': 'resistors',
    'C': 'capacitors',
    'L': 'inductors',
    'FB': 'ferrites',
    'Q': 'transistors',
    'D': 'diodes',
    'J': 'connectors',
    'LED': 'leds',
    'SW': 'switches',
    # ICs need further categorization
    'U': 'ic_analog',  # Default, will be refined
    'IC': 'ic_analog',  # Default, will be refined
}


def normalize_boolean(value: Optional[str]) -> Optional[int]:
    """Convert YES/NO strings to SQLite BOOLEAN (1/0)."""
    if value is None or value == '':
        return None
    value_upper = str(value).upper()
    if value_upper in ['YES', 'Y', 'TRUE', '1']:
        return 1
    if value_upper in ['NO', 'N', 'FALSE', '0']:
        return 0
    return None


def generate_part_id(table_name: str, sequence: int) -> str:
    """Generate a part_id for components missing one."""
    prefix_map = {
        'resistors': 'RES',
        'capacitors': 'CAP',
        'inductors': 'IND',
        'ferrites': 'FER',
        'transistors': 'TRN',
        'diodes': 'DIO',
        'connectors': 'CON',
        'ic_drivers': 'DRV',
        'ic_microcontrollers': 'MCU',
        'ic_logic': 'LOG',
        'ic_memory': 'MEM',
        'ic_opamp': 'OPA',
        'ic_analog': 'ANA',
        'leds': 'LED',
        'switches': 'SW',
    }
    prefix = prefix_map.get(table_name, 'PART')
    return f"{prefix}-{sequence:04d}"


def categorize_ic(row: Dict[str, Any]) -> str:
    """Categorize ICs into specific tables based on description or component type."""
    desc = (row.get('Description') or '').lower()
    comp_type = (row.get('Component_Type') or '').lower()

    # Op-amps
    if any(x in desc for x in ['op-amp', 'opamp', 'operational amplifier', 'instrumentation amp']):
        return 'ic_opamp'
    if any(x in comp_type for x in ['opamp', 'op-amp']):
        return 'ic_opamp'

    # Microcontrollers
    if any(x in desc for x in ['microcontroller', 'mcu', 'stm32', 'pic', 'avr', 'esp32', 'rp2040']):
        return 'ic_microcontrollers'
    if any(x in comp_type for x in ['microcontroller', 'mcu']):
        return 'ic_microcontrollers'

    # Logic
    if any(x in desc for x in ['logic', 'gate', 'buffer', 'latch', 'flip-flop', 'decoder', 'mux']):
        return 'ic_logic'
    if comp_type.startswith('74'):  # 74 series logic
        return 'ic_logic'

    # Memory
    if any(x in desc for x in ['memory', 'sram', 'dram', 'flash', 'eeprom', 'fram']):
        return 'ic_memory'
    if any(x in comp_type for x in ['memory', 'sram', 'eeprom']):
        return 'ic_memory'

    # Drivers
    if any(x in desc for x in ['driver', 'gate driver', 'led driver', 'motor driver']):
        return 'ic_drivers'
    if any(x in comp_type for x in ['driver']):
        return 'ic_drivers'

    # Default to analog
    return 'ic_analog'


def get_target_table(row: Dict[str, Any]) -> str:
    """Determine which table a component should go into."""
    reference = row.get('Reference', '')

    # Direct mapping for non-ICs
    if reference in REFERENCE_TO_TABLE:
        table = REFERENCE_TO_TABLE[reference]
        # Further categorize ICs
        if table == 'ic_analog':
            return categorize_ic(row)
        return table

    # Default to connectors for unknown reference (many are connectors)
    print(f"  Warning: Unknown reference '{reference}' for {row.get('Symbol_Name')}, categorizing as connector", file=sys.stderr)
    return 'connectors'


def map_core_fields(old_row: Dict[str, Any], table_name: str, part_counter: Dict[str, int]) -> Dict[str, Any]:
    """Map old field names to new core field names."""

    # Generate or use existing part_id
    part_id = old_row.get('Part_ID') or old_row.get('Symbol_Name')
    if not part_id:
        part_counter[table_name] += 1
        part_id = generate_part_id(table_name, part_counter[table_name])

    new_row = {
        # Identity Fields
        'part_id': part_id,
        'mpn': old_row.get('MPN') or 'UNKNOWN',
        'manufacturer': old_row.get('Manufacturer') or 'Generic',

        # Physical/Display Fields
        'package': old_row.get('Package'),
        'value': old_row.get('Value'),

        # Documentation Fields
        'description': old_row.get('Description'),
        'datasheet': old_row.get('Datasheet'),
        'manufacturer_link': old_row.get('Manufacturer_Link'),

        # CAD Integration Fields
        'kicad_symbol': old_row.get('KiCad_Symbol'),
        'kicad_footprint': old_row.get('KiCad_Footprint'),
        'altium_symbol': old_row.get('Altium_Symbol'),
        'altium_footprint': old_row.get('Altium_Footprint'),

        # Supply Chain Fields
        'lifecycle_status': 'Active',  # Default
        'rohs': normalize_boolean(old_row.get('RoHS')),
        'rohs_document_link': old_row.get('RoHS_Document_Link'),

        # Process Control Fields
        'allow_substitution': normalize_boolean(old_row.get('Allow_Substitution')),
        'tracking': normalize_boolean(old_row.get('Tracking')),
        'standards_version': old_row.get('Standards_Version') or 'v1.0',
        'bom_comment': old_row.get('BOM_Comment'),

        # Metadata Fields
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'created_by': 'migration_script',

        # SPICE Fields
        'sim_model_type': 'primitive' if old_row.get('Sim_Device') else None,
        'sim_device': old_row.get('Sim_Device'),
        'sim_pins': old_row.get('Sim_Pins'),
        'sim_model_file': old_row.get('Sim_Library'),
        'sim_params': None,  # Old schema didn't have this
    }

    return new_row


def map_type_specific_fields(old_row: Dict[str, Any], table_name: str, new_row: Dict[str, Any]):
    """Add type-specific fields based on table."""

    if table_name == 'resistors':
        new_row.update({
            'tolerance': old_row.get('Tolerance'),
            'power_rating': old_row.get('Power_Rating'),
            'temp_coeff': old_row.get('Temp_Coeff'),
            'voltage_rating': old_row.get('Voltage_Rating'),
            'composition': old_row.get('Material'),
            'temp_operating': old_row.get('Temp_Operating'),
            'temp_storage': old_row.get('Temp_Storage'),
        })

    elif table_name == 'capacitors':
        new_row.update({
            'tolerance': old_row.get('Tolerance'),
            'voltage_rating': old_row.get('Voltage_Rating'),
            'dielectric': old_row.get('Material'),
            'capacitor_type': old_row.get('Component_Type'),
            'esr': None,
            'ripple_current': None,
            'temp_operating': old_row.get('Temp_Operating'),
            'temp_storage': old_row.get('Temp_Storage'),
            'temp_coeff': old_row.get('Temp_Coeff'),
        })

    elif table_name == 'inductors':
        new_row.update({
            'inductance': None,
            'tolerance': old_row.get('Tolerance'),
            'current_rating': old_row.get('Current_Rating'),
            'saturation_current': None,
            'dc_resistance': None,
            'self_resonant_freq': None,
            'inductor_type': old_row.get('Component_Type'),
            'core_material': old_row.get('Material'),
            'shielded': None,
            'temp_operating': old_row.get('Temp_Operating'),
            'temp_storage': old_row.get('Temp_Storage'),
        })

    elif table_name == 'ferrites':
        new_row.update({
            'impedance_at_freq': old_row.get('Value'),
            'test_frequency': None,
            'dc_resistance': None,
            'current_rating': old_row.get('Current_Rating'),
            'tolerance': old_row.get('Tolerance'),
            'ferrite_type': old_row.get('Component_Type'),
            'temp_operating': old_row.get('Temp_Operating'),
            'temp_storage': old_row.get('Temp_Storage'),
        })

    elif table_name == 'connectors':
        # Try to parse pin count from Number_of_Pins or description
        pin_count_str = old_row.get('Number_of_Pins')
        pin_count = None
        if pin_count_str and pin_count_str.isdigit():
            pin_count = int(pin_count_str)

        new_row.update({
            'connector_type': old_row.get('Component_Type'),
            'pin_count': pin_count,
            'rows': None,
            'pitch': None,
            'mounting_type': None,
            'orientation': None,
            'current_rating': old_row.get('Current_Rating'),
            'voltage_rating': old_row.get('Voltage_Rating'),
            'gender': None,
            'mating_cycles': None,
            'temp_operating': old_row.get('Temp_Operating'),
            'temp_storage': old_row.get('Temp_Storage'),
        })

    elif table_name == 'leds':
        new_row.update({
            'color': None,  # Would need to parse from description
            'wavelength': None,
            'forward_voltage': old_row.get('Voltage_Rating'),
            'forward_current': old_row.get('Current_Rating'),
            'luminous_intensity': None,
            'viewing_angle': None,
            'led_type': old_row.get('Component_Type'),
            'lens_type': None,
            'temp_operating': old_row.get('Temp_Operating'),
            'temp_storage': old_row.get('Temp_Storage'),
        })

    # All other component types - basic temp mapping
    else:
        new_row.update({
            'temp_operating': old_row.get('Temp_Operating'),
            'temp_storage': old_row.get('Temp_Storage'),
            # temp_junction_max left as NULL for semiconductors (not in legacy data)
        })


def create_table_schemas(conn: sqlite3.Connection):
    """Create all component type table schemas."""

    cursor = conn.cursor()

    # Core fields SQL (reusable)
    core_fields = """
        part_id TEXT PRIMARY KEY,
        mpn TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        package TEXT,
        value TEXT,
        description TEXT,
        datasheet TEXT,
        manufacturer_link TEXT,
        kicad_symbol TEXT,
        kicad_footprint TEXT,
        altium_symbol TEXT,
        altium_footprint TEXT,
        lifecycle_status TEXT DEFAULT 'Active',
        rohs BOOLEAN DEFAULT TRUE,
        rohs_document_link TEXT,
        allow_substitution BOOLEAN DEFAULT TRUE,
        tracking BOOLEAN DEFAULT FALSE,
        standards_version TEXT DEFAULT 'v1.0',
        bom_comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        sim_model_type TEXT,
        sim_device TEXT,
        sim_pins TEXT,
        sim_model_file TEXT,
        sim_params TEXT
    """

    # Resistors
    cursor.execute(f"""
        CREATE TABLE resistors (
            {core_fields},
            tolerance TEXT,
            power_rating TEXT,
            temp_coeff TEXT,
            voltage_rating TEXT,
            composition TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    # Capacitors
    cursor.execute(f"""
        CREATE TABLE capacitors (
            {core_fields},
            tolerance TEXT,
            voltage_rating TEXT,
            dielectric TEXT,
            capacitor_type TEXT,
            esr TEXT,
            ripple_current TEXT,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_coeff TEXT
        )
    """)

    # Inductors
    cursor.execute(f"""
        CREATE TABLE inductors (
            {core_fields},
            tolerance TEXT,
            current_rating TEXT,
            saturation_current TEXT,
            dc_resistance TEXT,
            self_resonant_freq TEXT,
            inductor_type TEXT,
            core_material TEXT,
            shielded BOOLEAN,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    # Ferrites
    cursor.execute(f"""
        CREATE TABLE ferrites (
            {core_fields},
            impedance_at_freq TEXT,
            test_frequency TEXT,
            dc_resistance TEXT,
            current_rating TEXT,
            tolerance TEXT,
            ferrite_type TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    # Transistors
    cursor.execute(f"""
        CREATE TABLE transistors (
            {core_fields},
            transistor_type TEXT,
            polarity TEXT,
            vce_vds_max TEXT,
            ic_id_max TEXT,
            vgs_vbe_threshold TEXT,
            rds_on TEXT,
            hfe_gain TEXT,
            power_dissipation TEXT,
            transition_freq TEXT,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        )
    """)

    # Diodes
    cursor.execute(f"""
        CREATE TABLE diodes (
            {core_fields},
            diode_type TEXT,
            forward_voltage TEXT,
            forward_current TEXT,
            reverse_voltage TEXT,
            reverse_current TEXT,
            power_dissipation TEXT,
            recovery_time TEXT,
            capacitance TEXT,
            zener_voltage TEXT,
            clamping_voltage TEXT,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        )
    """)

    # Connectors
    cursor.execute(f"""
        CREATE TABLE connectors (
            {core_fields},
            connector_type TEXT,
            pin_count INTEGER,
            rows INTEGER,
            pitch TEXT,
            mounting_type TEXT,
            orientation TEXT,
            current_rating TEXT,
            voltage_rating TEXT,
            gender TEXT,
            mating_cycles INTEGER,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    # IC Drivers
    cursor.execute(f"""
        CREATE TABLE ic_drivers (
            {core_fields},
            driver_type TEXT,
            channels INTEGER,
            output_current TEXT,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            logic_voltage TEXT,
            output_type TEXT,
            switching_freq TEXT,
            control_interface TEXT,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        )
    """)

    # IC Microcontrollers
    cursor.execute(f"""
        CREATE TABLE ic_microcontrollers (
            {core_fields},
            mcu_family TEXT,
            core_architecture TEXT,
            clock_speed TEXT,
            flash_size TEXT,
            ram_size TEXT,
            eeprom_size TEXT,
            gpio_count INTEGER,
            adc_channels INTEGER,
            dac_channels INTEGER,
            timers INTEGER,
            uart_count INTEGER,
            spi_count INTEGER,
            i2c_count INTEGER,
            usb_support BOOLEAN,
            can_support BOOLEAN,
            ethernet_support BOOLEAN,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        )
    """)

    # IC Logic
    cursor.execute(f"""
        CREATE TABLE ic_logic (
            {core_fields},
            logic_family TEXT,
            gate_type TEXT,
            gates_per_package INTEGER,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            propagation_delay TEXT,
            output_current TEXT,
            input_type TEXT,
            output_type TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    # IC Memory
    cursor.execute(f"""
        CREATE TABLE ic_memory (
            {core_fields},
            memory_type TEXT,
            capacity TEXT,
            organization TEXT,
            interface TEXT,
            access_time TEXT,
            clock_speed TEXT,
            supply_voltage TEXT,
            write_cycles TEXT,
            data_retention TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    # IC Op-Amp
    cursor.execute(f"""
        CREATE TABLE ic_opamp (
            {core_fields},
            opamp_type TEXT,
            channels INTEGER,
            gbw_product TEXT,
            slew_rate TEXT,
            input_offset_voltage TEXT,
            input_bias_current TEXT,
            input_impedance TEXT,
            cmrr TEXT,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            supply_current TEXT,
            output_current TEXT,
            noise_voltage TEXT,
            rail_to_rail BOOLEAN,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        )
    """)

    # IC Analog
    cursor.execute(f"""
        CREATE TABLE ic_analog (
            {core_fields},
            function_type TEXT,
            resolution TEXT,
            channels INTEGER,
            sample_rate TEXT,
            interface TEXT,
            output_voltage TEXT,
            output_current TEXT,
            dropout_voltage TEXT,
            efficiency TEXT,
            propagation_delay TEXT,
            input_offset_voltage TEXT,
            reference_voltage TEXT,
            temp_coeff TEXT,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            supply_current TEXT,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        )
    """)

    # LEDs
    cursor.execute(f"""
        CREATE TABLE leds (
            {core_fields},
            color TEXT,
            wavelength TEXT,
            forward_voltage TEXT,
            forward_current TEXT,
            luminous_intensity TEXT,
            viewing_angle TEXT,
            led_type TEXT,
            lens_type TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    # Switches
    cursor.execute(f"""
        CREATE TABLE switches (
            {core_fields},
            switch_type TEXT,
            poles INTEGER,
            throw INTEGER,
            circuit_config TEXT,
            actuation_force TEXT,
            travel_distance TEXT,
            mounting_type TEXT,
            orientation TEXT,
            current_rating TEXT,
            voltage_rating TEXT,
            mechanical_life INTEGER,
            temp_operating TEXT,
            temp_storage TEXT
        )
    """)

    conn.commit()


def migrate_data(input_db: Path, output_db: Path):
    """Migrate data from old single-table to new multi-table structure."""

    print(f"Reading source database: {input_db}")
    source_conn = sqlite3.connect(str(input_db))
    source_conn.row_factory = sqlite3.Row

    print(f"Creating target database: {output_db}")
    target_conn = sqlite3.connect(str(output_db))

    try:
        # Create new table schemas
        print("Creating table schemas...")
        create_table_schemas(target_conn)

        # Read all components from old database
        cursor = source_conn.cursor()
        cursor.execute("SELECT * FROM symbols ORDER BY Symbol_Name")
        rows = cursor.fetchall()

        print(f"Found {len(rows)} components to migrate\n")

        # Track counts and part IDs
        table_counts = {}
        part_counter = {table: 0 for table in [
            'resistors', 'capacitors', 'inductors', 'ferrites', 'transistors',
            'diodes', 'connectors', 'ic_drivers', 'ic_microcontrollers',
            'ic_logic', 'ic_memory', 'ic_opamp', 'ic_analog', 'leds', 'switches'
        ]}

        # Categorize and migrate each component
        for row in rows:
            old_row = dict(row)

            # Determine target table
            table_name = get_target_table(old_row)
            table_counts[table_name] = table_counts.get(table_name, 0) + 1

            # Map fields
            new_row = map_core_fields(old_row, table_name, part_counter)
            map_type_specific_fields(old_row, table_name, new_row)

            # Insert into target table
            columns = ', '.join(new_row.keys())
            placeholders = ', '.join(['?' for _ in new_row])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            target_conn.execute(query, list(new_row.values()))

        target_conn.commit()

        # Print summary
        print("\nMigration Summary:")
        print("=" * 50)
        for table_name, count in sorted(table_counts.items()):
            print(f"  {table_name:30s} {count:4d} components")
        print("=" * 50)
        print(f"  Total:                         {len(rows):4d} components\n")

        print(f"✓ Successfully migrated to {output_db}")

    finally:
        source_conn.close()
        target_conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Migrate single-table database to multi-table structure'
    )
    parser.add_argument('input', help='Input database file with symbols table')
    parser.add_argument('output', help='Output database file (will be created)')
    parser.add_argument('--dump-sql', metavar='DIR',
                       help='Also dump to SQL files in specified directory')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # Validate input
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Warn if output exists
    if output_path.exists():
        print(f"Warning: Output file '{output_path}' already exists and will be overwritten")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted")
            sys.exit(0)
        output_path.unlink()

    try:
        # Migrate
        migrate_data(input_path, output_path)

        # Optionally dump to SQL
        if args.dump_sql:
            print(f"\nDumping to SQL structure in {args.dump_sql}...")
            import subprocess
            result = subprocess.run([
                sys.executable,
                'tools/db_to_tables.py',
                str(output_path),
                args.dump_sql
            ])
            if result.returncode != 0:
                print("Warning: SQL dump failed", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
