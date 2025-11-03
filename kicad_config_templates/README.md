# KiCad Configuration Templates

This directory contains template configuration files for setting up Terra EDA Library in KiCad.

## Files

- **`sym-lib-table`** - Symbol library table entry
- **`fp-lib-table`** - Footprint library table entries
- **`terra.kicad_dbl`** - Database library configuration (in parent directory)

## Usage

### Symbol Library

Add the contents of `sym-lib-table` to your global or project-specific symbol library table:

**Global location:**
- **macOS:** `~/Library/Preferences/kicad/8.0/sym-lib-table`
- **Linux:** `~/.config/kicad/8.0/sym-lib-table`
- **Windows:** `%APPDATA%\kicad\8.0\sym-lib-table`

**OR** use KiCad GUI:
1. **Preferences → Manage Symbol Libraries...**
2. **Global Libraries** tab
3. **Add** → browse to `${TERRA_EDA_LIB}/terra_sym.kicad_sym`

### Footprint Libraries

Add the contents of `fp-lib-table` to your global or project-specific footprint library table:

**Global location:**
- **macOS:** `~/Library/Preferences/kicad/8.0/fp-lib-table`
- **Linux:** `~/.config/kicad/8.0/fp-lib-table`
- **Windows:** `%APPDATA%\kicad\8.0\fp-lib-table`

**OR** use KiCad GUI:
1. **Preferences → Manage Footprint Libraries...**
2. **Global Libraries** tab
3. **Add** → browse to footprint directories

### Database Library

Copy `../terra.kicad_dbl` to:

**User-wide:**
- **macOS:** `~/Library/Preferences/kicad/8.0/library/terra.kicad_dbl`
- **Linux:** `~/.config/kicad/8.0/library/terra.kicad_dbl`
- **Windows:** `%APPDATA%\kicad\8.0\library\terra.kicad_dbl`

**Per-project:**
Copy to your project directory alongside the `.kicad_pro` file.

## Prerequisites

1. **Environment Variable:** Set `TERRA_EDA_LIB` to the full path of this library
   - In KiCad: **Preferences → Configure Paths...**
   - Add: `TERRA_EDA_LIB` = `/full/path/to/terra-eda-library`

2. **ODBC Driver:** Install SQLite ODBC driver for database library support
   - **macOS:** `brew install sqliteodbc`
   - **Linux:** `sudo apt-get install libsqliteodbc`
   - **Windows:** Download from http://www.ch-werner.de/sqliteodbc/

## Verification

After adding libraries:

1. Open KiCad symbol chooser (press 'A' in schematic editor)
2. Look for **terra_eda_lib** in library list (symbol library)
3. Look for **Terra EDA Components** in library list (database library)
4. Open footprint chooser
5. Look for **Terra_Custom** and **Terra_Standard** libraries

## Troubleshooting

See [../KICAD_SETUP.md](../KICAD_SETUP.md) for detailed setup instructions and troubleshooting.
