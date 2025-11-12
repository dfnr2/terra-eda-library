#!/bin/bash
# Setup script for Terra EDA Library
# Generates terra.kicad_dbl with absolute path for local KiCad use

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Terra EDA Library Setup"
echo "======================"
echo ""
echo "Library path: $SCRIPT_DIR"
echo ""

# Function to find SQLite ODBC driver
find_odbc_driver() {
    # Common paths where SQLite ODBC drivers are installed
    local paths=(
        "/usr/local/lib/libsqlite3odbc.dylib"      # Homebrew (Intel Mac)
        "/opt/homebrew/lib/libsqlite3odbc.dylib"   # Homebrew (Apple Silicon)
        "/opt/local/lib/libsqlite3odbc.dylib"      # MacPorts
        "/usr/lib/x86_64-linux-gnu/odbc/libsqlite3odbc.so"  # Ubuntu/Debian
        "/usr/lib/odbc/libsqlite3odbc.so"          # Other Linux
        "/usr/local/lib/libsqlite3odbc.so"         # Manual install Linux
    )
    
    for path in "${paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Generate terra.kicad_dbl from template
if [ -f "$SCRIPT_DIR/terra.kicad_dbl.template" ]; then
    echo "Generating terra.kicad_dbl with absolute path..."
    
    # Find ODBC driver
    ODBC_DRIVER=$(find_odbc_driver)
    if [ $? -eq 0 ]; then
        echo "Found SQLite ODBC driver: $ODBC_DRIVER"
    else
        echo "ERROR: SQLite ODBC driver not found!"
        echo "  Please install SQLite ODBC driver:"
        echo "    macOS (Homebrew): brew install sqliteodbc"
        echo "    macOS (MacPorts): See KICAD_SETUP.md for build instructions"
        echo "    Linux: sudo apt-get install libsqliteodbc"
        exit 1
    fi
    
    # Perform substitutions
    sed -e "s|__TERRA_PATH__|$SCRIPT_DIR|g" \
        -e "s|__ODBC_DRIVER_PATH__|$ODBC_DRIVER|g" \
        "$SCRIPT_DIR/terra.kicad_dbl.template" > "$SCRIPT_DIR/terra.kicad_dbl"
    
    echo "Created terra.kicad_dbl"
else
    echo "ERROR: Template file not found: terra.kicad_dbl.template"
    exit 1
fi

# Build database if needed
if [ ! -f "$SCRIPT_DIR/db/terra.db" ]; then
    echo ""
    echo "Building database..."

    # Check if make is available
    if command -v make >/dev/null 2>&1; then
        make -C "$SCRIPT_DIR" all
    else
        # Use build.sh instead
        "$SCRIPT_DIR/build.sh"
    fi

    echo "✓ Database built"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To use this library in KiCad:"
echo "1. Set environment variable in KiCad:"
echo "   Preferences → Configure Paths"
echo "   Name: TERRA_EDA_LIB"
echo "   Path: $SCRIPT_DIR"
echo ""
echo "2. Add symbol library:"
echo "   Preferences → Manage Symbol Libraries"
echo "   Path: \${TERRA_EDA_LIB}/terra_sym.kicad_sym"
echo "   Nickname: terra"
echo ""
echo "3. Add database library:"
echo "   In your project, browse to:"
echo "   $SCRIPT_DIR/terra.kicad_dbl"
echo ""