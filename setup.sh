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

# Generate terra.kicad_dbl from template
if [ -f "$SCRIPT_DIR/terra.kicad_dbl.template" ]; then
    echo "Generating terra.kicad_dbl with absolute path..."
    sed "s|__TERRA_PATH__|$SCRIPT_DIR|g" "$SCRIPT_DIR/terra.kicad_dbl.template" > "$SCRIPT_DIR/terra.kicad_dbl"
    echo "✓ Created terra.kicad_dbl"
else
    echo "✗ Template file not found: terra.kicad_dbl.template"
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