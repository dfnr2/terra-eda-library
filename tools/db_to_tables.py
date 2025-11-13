#!/usr/bin/env python3
"""
Database to Table Structure Dumper

This script dumps a multi-table SQLite database to the Terra EDA Library
table structure: db/tables/{table_name}/{table_name}.sql

Features:
- Discovers all tables in database automatically
- Creates directory structure: db/tables/{table_name}/
- Deterministic output (sorted by primary key)
- Suitable for git tracking and diffing
- Preserves all fields including SPICE simulation fields
- Supports dump_priority-based file numbering

Usage:
    python db_to_tables.py <input.db> <output_dir>

Example:
    python db_to_tables.py db/terra.db db/tables/

The output SQL files can be:
1. Committed to git for version control
2. Modified manually or via database tools
3. Used to rebuild database: cat db/tables/*/*.sql | sqlite3 terra.db
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def sql_escape(value) -> str:
    """Escape a value for SQL, handling NULL values and different types."""
    if value is None or value == '':
        return 'NULL'
    # Handle integers and floats directly (no quotes)
    if isinstance(value, (int, float)):
        return str(value)
    # Handle strings - escape single quotes by doubling them
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def get_all_tables(conn: sqlite3.Connection) -> List[str]:
    """Get list of all user tables in database (excluding sqlite_* tables).

    Args:
        conn: Database connection

    Returns:
        List of table names, sorted alphabetically
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]


def get_primary_key(conn: sqlite3.Connection, table_name: str) -> Optional[str]:
    """Get the primary key column name for a table.

    Args:
        conn: Database connection
        table_name: Name of table

    Returns:
        Primary key column name, or None if no primary key
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    for row in cursor.fetchall():
        # row format: (cid, name, type, notnull, dflt_value, pk)
        if row[5] > 0:  # pk column is non-zero for primary key
            return row[1]
    return None


def get_table_schema(conn: sqlite3.Connection, table_name: str) -> Tuple[str, List[str]]:
    """Get the CREATE TABLE statement and column names for a table.

    Args:
        conn: Database connection
        table_name: Name of table to get schema for

    Returns:
        Tuple of (create_table_sql, list_of_column_names)
    """
    cursor = conn.cursor()

    # Get the CREATE TABLE statement
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"Table '{table_name}' not found in database")

    create_table_sql = result[0]

    # Get column names in order
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]

    return create_table_sql, columns


def get_table_dump_info(conn: sqlite3.Connection, table_name: str) -> Tuple[List[Tuple[int, str]], int]:
    """Get dump priority and source info from a table.
    
    Args:
        conn: Database connection
        table_name: Name of table to query
        
    Returns:
        Tuple of (list of (dump_priority, source) pairs, max_priority) for non-zero priorities only
    """
    cursor = conn.cursor()
    
    # Check if table has 'dump_priority' and 'source' columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    has_dump_priority = 'dump_priority' in columns
    has_source = 'source' in columns
    
    if not has_dump_priority or not has_source:
        # Fallback for tables without priority/source columns
        return [(1, 'static')], 1
    
    # Get distinct (dump_priority, source) pairs for dump_priority > 0
    cursor.execute(f"""
        SELECT DISTINCT dump_priority, source 
        FROM {table_name} 
        WHERE dump_priority > 0 
          AND source IS NOT NULL 
          AND source != ''
        ORDER BY dump_priority, source
    """)
    
    results = cursor.fetchall()
    
    if not results:
        return [(1, 'static')], 1
    
    # Find max priority for padding calculation
    max_priority = max(row[0] for row in results)
    
    return results, max_priority


def dump_table_data_by_priority_source(conn: sqlite3.Connection, table_name: str, dump_priority: int, source: str, sort_column: Optional[str] = None) -> List[str]:
    """Dump table data filtered by dump_priority and source as INSERT statements.
    
    Args:
        conn: Database connection
        table_name: Name of table to dump
        dump_priority: Priority value to filter by
        source: Source value to filter by
        sort_column: Column to sort by
        
    Returns:
        List of INSERT SQL statements
    """
    cursor = conn.cursor()

    # Get table schema
    _, columns = get_table_schema(conn, table_name)

    # Check if table has dump_priority and source columns
    has_dump_priority = 'dump_priority' in columns
    has_source = 'source' in columns

    # Determine sort column
    if sort_column is None:
        sort_column = get_primary_key(conn, table_name)
        if sort_column is None:
            sort_column = columns[0]

    # Build SELECT query with WHERE clause for priority and source filtering
    columns_str = ', '.join([f'"{col}"' for col in columns])

    if has_dump_priority and has_source:
        # Filter by both dump_priority and source
        query = f'SELECT {columns_str} FROM {table_name} WHERE dump_priority = ? AND source = ? ORDER BY "{sort_column}"'
        cursor.execute(query, (dump_priority, source))
    elif has_source:
        # Filter by source only (legacy tables)
        query = f'SELECT {columns_str} FROM {table_name} WHERE source = ? ORDER BY "{sort_column}"'
        cursor.execute(query, (source,))
    else:
        # No filtering columns, dump all data
        query = f'SELECT {columns_str} FROM {table_name} ORDER BY "{sort_column}"'
        cursor.execute(query)

    # Generate INSERT statements
    insert_statements = []
    columns_list = ', '.join([f'"{col}"' for col in columns])

    for row in cursor.fetchall():
        # Escape values
        escaped_values = [sql_escape(value) for value in row]
        values_str = ', '.join(escaped_values)

        insert_sql = f"INSERT INTO {table_name} ({columns_list}) VALUES ({values_str});"
        insert_statements.append(insert_sql)

    return insert_statements


def dump_table_to_file(conn: sqlite3.Connection, table_name: str, output_dir: Path):
    """Dump a single table to its directory structure using priority-based splitting.

    Args:
        conn: Database connection
        table_name: Name of table to dump
        output_dir: Base output directory (e.g., db/tables/)
    """
    # Create table directory
    table_dir = output_dir / table_name
    table_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Processing table '{table_name}'...")

    # Get schema
    create_table_sql, columns = get_table_schema(conn, table_name)

    # Count total rows
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]

    # Determine sort column
    sort_column = get_primary_key(conn, table_name)
    if sort_column:
        print(f"    {total_rows} rows, {len(columns)} columns, sorted by primary key '{sort_column}'")
    else:
        sort_column = columns[0]
        print(f"    {total_rows} rows, {len(columns)} columns, sorted by '{sort_column}'")

    # Get dump priorities and sources (excluding dump_priority = 0)
    dump_info, max_priority = get_table_dump_info(conn, table_name)
    
    # Calculate padding width based on max priority
    padding_width = len(str(max_priority))
    
    # Write schema file with proper padding
    schema_file = table_dir / f"{table_name}_{'0' * padding_width}_schema.sql"
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(f"-- Terra EDA Library - {table_name} Table Schema\n")
        f.write(f"-- This file contains only the table definition\n")
        f.write(f"-- Data is split by dump_priority and source into separate files\n")
        f.write(f"--\n")
        f.write(f"-- This file is auto-generated and suitable for git tracking.\n")
        f.write(f"--\n\n")
        f.write(f"{create_table_sql};\n")
    
    print(f"    ✓ Wrote to {schema_file}")

    # Dump data by priority and source
    if total_rows > 0:
        if not dump_info:
            print(f"    ✓ No data to write (all generated or empty table)")
            return
        
        for dump_priority, source in dump_info:
            insert_statements = dump_table_data_by_priority_source(conn, table_name, dump_priority, source, sort_column)
            
            if not insert_statements:
                continue  # Skip empty priority/source combinations
            
            # Generate filename based on priority and source
            priority_str = f"{dump_priority:0{padding_width}d}"
            if source == 'static':
                data_file = table_dir / f"{table_name}_{priority_str}_data.sql"
            else:
                data_file = table_dir / f"{table_name}_{priority_str}_{source}.sql"
            
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write(f"-- Terra EDA Library - {table_name} Table Data (priority {dump_priority}, source {source})\n")
                f.write(f"-- Number of components: {len(insert_statements)}\n")
                f.write(f"-- Dump priority: {dump_priority}\n")
                f.write(f"-- Source: {source}\n")
                f.write(f"-- Sorted by: {sort_column}\n")
                f.write("--\n")
                f.write("-- This file is auto-generated and suitable for git tracking.\n")
                f.write("-- Rows are sorted deterministically to ensure consistent diffs.\n")
                f.write(f"-- Table schema is in {table_name}_{'0' * padding_width}_schema.sql\n")
                f.write("--\n\n")

                f.write("BEGIN TRANSACTION;\n\n")
                for insert_sql in insert_statements:
                    f.write(insert_sql)
                    f.write("\n")
                f.write("\nCOMMIT;\n")
            
            print(f"    ✓ Wrote {len(insert_statements)} rows to {data_file}")
    else:
        print(f"    ✓ No data to write (empty table)")


def dump_database_to_tables(db_path: Path, output_dir: Path):
    """Dump entire database to table structure.

    Args:
        db_path: Path to SQLite database
        output_dir: Base output directory (e.g., db/tables/)
    """
    print(f"Reading database: {db_path}")
    conn = sqlite3.connect(str(db_path))

    try:
        # Get all tables
        tables = get_all_tables(conn)

        if not tables:
            print("No tables found in database", file=sys.stderr)
            return

        print(f"Found {len(tables)} tables: {', '.join(tables)}\n")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Dump each table
        for table_name in tables:
            dump_table_to_file(conn, table_name, output_dir)

        print(f"\n✓ Successfully dumped {len(tables)} tables to {output_dir}/")

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Dump multi-table database to Terra EDA Library table structure'
    )
    parser.add_argument('input', help='Input SQLite database file (.db)')
    parser.add_argument('output', help='Output directory (e.g., db/tables/)')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    # Validate input file
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix in ['.db', '.sqlite', '.sqlite3']:
        print(f"Warning: Input file does not have a database extension", file=sys.stderr)

    try:
        dump_database_to_tables(input_path, output_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()