#!/bin/bash
# Build Terra EDA Library databases from SQL
# Alternative to 'make' for systems without make installed

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Building Terra EDA Library databases..."
echo "======================================="
echo ""

# Create db directory if needed
mkdir -p db

# Build all databases from SQL files
for sql_file in db/*.sql; do
    if [ -f "$sql_file" ]; then
        db_file="${sql_file%.sql}.db"
        echo "Building: $db_file"
        rm -f "$db_file"
        sqlite3 "$db_file" < "$sql_file"
        echo "  ✓ Done"
    fi
done

echo ""
echo "Build complete!"
echo ""
echo "Database files:"
for db_file in db/*.db; do
    if [ -f "$db_file" ]; then
        count=$(sqlite3 "$db_file" "SELECT COUNT(*) FROM symbols" 2>/dev/null || echo 0)
        size=$(du -h "$db_file" | cut -f1)
        echo "  $db_file ($count components, $size)"
    fi
done
