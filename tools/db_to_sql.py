#!/usr/bin/env python3
"""
KiCad Database to SQL Script Dumper

This script dumps a KiCad symbol database to a SQL script in a consistent,
predictable order that is suitable for git tracking and diffing.

Features:
- Deterministic output (same database always produces same SQL)
- Sorted by Symbol_Name for consistent ordering
- Formatted for easy diffing
- Preserves all SPICE simulation fields
- Can be used to track database changes in git

Usage:
    python db_to_sql.py <input.db> <output.sql>

The output SQL can be:
1. Committed to git for version control
2. Modified manually or via database tools
3. Used to recreate the database: sqlite3 new.db < output.sql
"""

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def sql_escape(value: Optional[str]) -> str:
    """Escape a string value for SQL, handling NULL values."""
    if value is None or value == '':
        return 'NULL'
    # Escape single quotes by doubling them
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def get_table_schema(conn: sqlite3.Connection, table_name: str = 'symbols') -> Tuple[str, List[str]]:
    """Get the CREATE TABLE statement and column names for a table.

    Args:
        conn: Database connection
        table_name: Name of table to get schema for

    Returns:
        Tuple of (create_table_sql, list_of_column_names)
    """
    cursor = conn.cursor()

    # Get the CREATE TABLE statement
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = cursor.fetchone()

    if not result:
        raise ValueError(f"Table '{table_name}' not found in database")

    create_table_sql = result[0]

    # Get column names in order
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]

    return create_table_sql, columns


def dump_table_data(conn: sqlite3.Connection, table_name: str = 'symbols',
                   sort_column: str = 'Symbol_Name') -> List[str]:
    """Dump table data as INSERT statements in sorted order.

    Args:
        conn: Database connection
        table_name: Name of table to dump
        sort_column: Column to sort by for deterministic output

    Returns:
        List of INSERT SQL statements
    """
    cursor = conn.cursor()

    # Get table schema
    _, columns = get_table_schema(conn, table_name)

    # Build SELECT query with ORDER BY for deterministic output
    columns_str = ', '.join([f'"{col}"' for col in columns])

    # Check if sort column exists
    if sort_column not in columns:
        print(f"Warning: Sort column '{sort_column}' not found, using first column", file=sys.stderr)
        sort_column = columns[0]

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


def dump_database_to_sql(db_path: Path, output_path: Path, table_name: str = 'symbols',
                         sort_column: str = 'Symbol_Name'):
    """Dump entire database to SQL script.

    Args:
        db_path: Path to SQLite database
        output_path: Path to output SQL script
        table_name: Name of table to dump
        sort_column: Column to sort by for deterministic output
    """
    # Open database
    print(f"Reading database: {db_path}")
    conn = sqlite3.connect(str(db_path))

    try:
        # Get schema
        print(f"Extracting schema for table '{table_name}'...")
        create_table_sql, columns = get_table_schema(conn, table_name)

        # Count rows
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"Found {row_count} rows in table '{table_name}'")
        print(f"Found {len(columns)} columns")

        # Dump data
        print(f"Generating INSERT statements (sorted by '{sort_column}')...")
        insert_statements = dump_table_data(conn, table_name, sort_column)

        # Write SQL file
        print(f"Writing SQL script to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write("-- KiCad Symbol Library Database Dump\n")
            f.write(f"-- Source database: {db_path.name}\n")
            f.write(f"-- Number of symbols: {row_count}\n")
            f.write(f"-- Sorted by: {sort_column}\n")
            f.write("--\n")
            f.write("-- This file is generated automatically and is suitable for git tracking.\n")
            f.write("-- Rows are sorted deterministically to ensure consistent diffs.\n")
            f.write("--\n")
            f.write("-- To recreate the database, run:\n")
            f.write(f"--   sqlite3 output.db < {output_path.name}\n")
            f.write("--\n\n")

            # Write DROP TABLE (for clean rebuild)
            f.write(f"-- Drop existing table if it exists\n")
            f.write(f"DROP TABLE IF EXISTS {table_name};\n\n")

            # Write CREATE TABLE
            f.write(f"-- Create {table_name} table\n")
            f.write(create_table_sql)
            f.write(";\n\n")

            # Write INSERT statements
            f.write(f"-- Insert {row_count} symbols\n")
            f.write("BEGIN TRANSACTION;\n\n")
            for insert_sql in insert_statements:
                f.write(insert_sql)
                f.write("\n")
            f.write("\nCOMMIT;\n")

        print(f"Successfully dumped {row_count} rows to {output_path}")

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Dump KiCad symbol database to SQL script in diffable format'
    )
    parser.add_argument('input', help='Input SQLite database file (.db)')
    parser.add_argument('output', help='Output SQL script file (.sql)')
    parser.add_argument('--table', '-t', default='symbols',
                       help='Table name to dump (default: symbols)')
    parser.add_argument('--sort-by', '-s', default='Symbol_Name',
                       help='Column to sort by for consistent output (default: Symbol_Name)')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # Validate input file
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix in ['.db', '.sqlite', '.sqlite3']:
        print(f"Warning: Input file does not have a database extension", file=sys.stderr)

    try:
        dump_database_to_sql(input_path, output_path, args.table, args.sort_by)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
