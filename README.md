# Terra EDA Library

A multi-EDA database-driven component library supporting both KiCad and Altium Designer.

## Overview

Terra EDA Library uses a SQLite database backend to manage electronic components (resistors, capacitors, ICs, etc.) with their associated symbols, footprints, and 3D models. The library is designed with:

- **Multi-EDA Support**: Separate columns for KiCad and Altium references
- **SQL-First Workflow**: SQL files are the source of truth, databases are generated
- **SPICE Integration**: Built-in SPICE simulation fields for KiCad
- **Git-Friendly**: Deterministic SQL output for clean diffs
- **Scalable**: Easy to add new component libraries

## Simple Setup

### Prerequisites
- **KiCad 7.0 or later** (9.0+ recommended)
- **SQLite** (Required for datbase functionality) - [installation instructions](#installing-sqlite)
- **SQLite ODBC driver** (required for database functionality) - [installation instructions](#installing-odbc-driver)
- **Make** (for building the database) - [installation instructions](#installing-python-and-make)
- **Python3**: Needed if you plan to modify or regenerate the library from symbol files - [installation instructions](#installing-python-and-make)

Follow these steps to get Terra EDA Library working in KiCad:

### Clone and Build

```bash
# Clone to a permanent location
cd ~/kicad-libraries  # or your preferred location
git clone https://github.com/dfnr2/terra-eda-library.git
cd terra-eda-library

# Build the database
make

# OR if make is not installed:
# ./build.sh           # macOS/Linux
# .\build.ps1          # Windows PowerShell

# OR use the automated setup script:
# ./setup.sh           # macOS/Linux - generates .kicad_dbl and builds database
# .\setup.ps1          # Windows PowerShell - generates .kicad_dbl and builds database
```

### Configure KiCad Environment Variable

In KiCad:
1. Open **Preferences → Configure Paths...**
2. Click the **+** button to add a new path
3. Set **Name:** `TERRA_EDA_LIB`
4. Set **Path:** to the full path where you cloned (e.g., `/Users/yourname/kicad-libraries/terra-eda-library`)
5. Click **OK**
6. **Restart KiCad**

### Add Symbol Library

In KiCad:
1. Open **Preferences → Manage Symbol Libraries...**
2. Select the **Global Libraries** tab
3. Click the **Add** button (folder with +)
4. For the **Library Path**, type: `${TERRA_EDA_LIB}/terra_sym.kicad_sym`
5. Set **Nickname:** `terra_sym`
6. Click **OK**

### Add Database Library

In KiCad:
1. Open **Preferences → Manage Symbol Libraries...**
2. Select the **Global Libraries** tab (or **Project Specific** if you prefer)
3. Click the **Add** button
4. **Note:** The file may appear grayed out in the browser - just type the path directly:
   - Type: `${TERRA_EDA_LIB}/terra.kicad_dbl`
5. Set **Nickname:** `terra`
6. Click **OK**
7. **Restart KiCad**

### Verify Setup

1. Open a schematic in KiCad
2. Press **A** to add a symbol
3. Look for **terra** in the library list (this is the database library)
4. Select a component and verify it shows only **Reference** and **Value** when placed

**Done!** You can now use the Terra EDA Library components in your designs.

---

## Prerequisites

If the setup above didn't work, you may be missing required dependencies:

### For Using the Library

1. **KiCad 7.0 or later** (8.0+ recommended for best database library support)
2. **SQLite** (usually included with your system or KiCad)
3. **SQLite ODBC Driver** (for database library functionality)
4. **Make** (for building the database from SQL)

### For Modifying the Library

5. **Python 3** (for conversion tools and scripts - only needed if editing/regenerating)

### Installing SQLite

SQLite is usually pre-installed on most systems. Check if you have it:

```bash
sqlite3 --version
```

If not installed:

**macOS (Homebrew):**
```bash
brew install sqlite
```

**macOS (MacPorts):**
```bash
sudo port install sqlite3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install sqlite3
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install sqlite
```

**Windows:**
1. Download from: https://www.sqlite.org/download.html
2. Extract to a folder (e.g., `C:\sqlite`)
3. Add the folder to your PATH environment variable

### Installing ODBC Driver

The SQLite ODBC driver is required for KiCad to connect to the database.

**macOS (Homebrew):**
```bash
brew install sqliteodbc

# Verify installation
ls /usr/local/lib/libsqlite3odbc.dylib
```

**macOS (MacPorts):**
```bash
# KiCad 9 is compiled to use unixodbc
sudo port install unixodbc
sudo port install sqliteodbc

# Configure ODBC driver (if needed)
# Edit /opt/local/etc/odbcinst.ini to register the driver

# Verify installation
ls /opt/local/lib/libsqlite3odbc.dylib
```

**Linux (Ubuntu/Debian):**
```bash
# Install SQLite ODBC driver
sudo apt-get update
sudo apt-get install libsqliteodbc

# Verify installation
ls /usr/lib/*/odbc/libsqlite3odbc.so
```

**Linux (Fedora/RHEL):**
```bash
# Install SQLite ODBC driver
sudo dnf install sqliteodbc

# Verify installation
ls /usr/lib*/libsqlite3odbc.so
```

**Windows:**
1. Download SQLite ODBC driver from: http://www.ch-werner.de/sqliteodbc/
2. Run the installer (choose 64-bit version for modern systems)
3. The driver will be registered automatically

### Installing Python and Make

**macOS:**
```bash
# Python 3 (usually pre-installed on modern macOS)
python3 --version

# Install make via Xcode Command Line Tools if needed
xcode-select --install
```

**Linux:**
```bash
# Python 3 and make (usually pre-installed)
python3 --version
make --version

# If missing, install via package manager:
sudo apt-get install python3 make  # Debian/Ubuntu
sudo dnf install python3 make      # Fedora/RHEL
```

**Windows:**
```powershell
# Install Python from python.org or via winget
winget install Python.Python.3

# Install make via chocolatey
choco install make

# Or use Git Bash / WSL which includes make
```

### Verifying Prerequisites

After installation, verify everything is ready:

```bash
# Check KiCad version
kicad-cli version  # Should be 7.0 or later

# Check SQLite (usually already present)
sqlite3 --version

# Check make
make --version

# Check SQLite ODBC driver (macOS/Linux)
ls /usr/local/lib/libsqlite3odbc.dylib  # macOS
ls /usr/lib/*/odbc/libsqlite3odbc.so    # Linux

# Check Python (only needed for modifying library)
python3 --version  # Should be 3.7 or later
```

If all prerequisites are installed, return to the [Simple Setup](#simple-setup) section above.

---

For detailed information, troubleshooting, and advanced configuration, see the **[Complete KiCad Setup Guide](KICAD_SETUP.md)**.

### Build Database from SQL

```bash
# Build all databases
make

# OR if make is not installed:
./build.sh           # macOS/Linux
.\build.ps1          # Windows PowerShell

# Check status (make only)
make status

# Verify round-trip consistency (make only)
make verify
```

### Edit Components

```bash
# Edit database directly
sqlite3 db/terra.db

# Dump changes back to SQL for git tracking
make dump

# Review changes
git diff db/terra.sql

# Commit
git add db/terra.sql
git commit -m "Update component specifications"
```

### Add New Components

**Option 1: Via SQL**
```bash
# Edit SQL file directly
vim db/terra.sql

# Rebuild
make

# Test
make verify
```

**Option 2: Via KiCad**
1. Create symbols in KiCad (temp library)
2. Convert to SQL: `python3 tools/kicad_sym_to_db.py temp.kicad_sym temp.sql --config tools/field_mappings.yaml`
3. Merge: `grep "^INSERT" temp.sql >> db/terra.sql`
4. Build: `make`

## Database Schema

The library uses a flat table with dual-EDA support:

```sql
CREATE TABLE symbols (
  Symbol_Name TEXT,          -- Unique identifier
  Reference TEXT,            -- R, C, U, etc.
  Value TEXT,                -- Component value

  -- Multi-EDA Support
  KiCad_Symbol TEXT,         -- library:symbol
  KiCad_Footprint TEXT,      -- footprint reference
  Altium_Symbol TEXT,        -- (future)
  Altium_Footprint TEXT,     -- (future)

  -- Metadata
  Description TEXT,
  Datasheet TEXT,
  Manufacturer TEXT,
  MPN TEXT,
  Package TEXT,

  -- Electrical specs, temperature, SPICE fields, etc.
  ...
);
```

## KiCad Integration

The library uses the `${TERRA_EDA_LIB}` environment variable for portability across projects and machines.

### Setup Required

1. **Set environment variable** in KiCad: `TERRA_EDA_LIB` = `/path/to/terra-eda-library`
2. **Add symbol library:** `terra_sym.kicad_sym`
3. **Add database library:** Copy `terra.kicad_dbl` to KiCad config directory
4. **Add footprint libraries** (optional): For custom footprints

**See [KICAD_SETUP.md](KICAD_SETUP.md) for complete setup instructions.**

### Database Configuration

The `terra.kicad_dbl` file uses `${TERRA_EDA_LIB}` to locate the database:

```json
{
  "source": {
    "type": "odbc",
    "connection_string": "DRIVER=/usr/local/lib/libsqlite3odbc.dylib;Database=${TERRA_EDA_LIB}/db/terra.db"
  },
  "libraries": [{
    "table": "symbols",
    "key": "Symbol_Name",
    "symbols": "KiCad_Symbol",
    "footprints": "KiCad_Footprint"
  }]
}
```

This allows the same library to be used across multiple projects and shared among team members.

## Workflows

See [CLAUDE.md](CLAUDE.md) for detailed workflows:

### 1. KiCad New Part → Merge to Terra
Create parts in KiCad symbol editor, convert to SQL, merge into existing library.

### 2. Edit Existing Part
Direct database editing via SQL, then dump back to SQL file.

### 3. Script-Generated Parts → Existing Library
Generate parts from scripts (e.g., resistor series), append to SQL file.

### 4. Script-Generated Parts → New Library
Create entirely new component libraries with their own database files.

## Makefile Targets

- `make` or `make all` - Build all databases from SQL
- `make dump` - Dump databases to SQL (after editing)
- `make verify` - Verify round-trip consistency
- `make status` - Show file status
- `make clean` - Remove generated .db files
- `make distclean` - Remove all generated files including SQL
- `make help` - Show help

## Directory Structure

```
terra-eda-library/
├── Makefile                  # Build automation
├── terra_sym.kicad_sym   # Symbol library
├── terra.kicad_dbl   # KiCad database config
├── db/
│   ├── terra.sql     # Source of truth (git tracked)
│   └── terra.db      # Generated database
├── tools/
│   ├── kicad_sym_to_db.py    # Convert .kicad_sym → SQL
│   ├── db_to_sql.py          # Convert database → SQL
│   └── field_mappings.yaml   # Field normalization
├── assets/
│   ├── symbols/              # Custom symbol files
│   ├── footprints/           # Custom footprint files
│   └── 3dmodels/             # Custom 3D models
└── generators/               # (future) Part generation scripts
```

## Adding Multiple Libraries

To support multiple component libraries:

1. **Create new .kicad_sym file** (or generate SQL directly)
2. **Add to Makefile**:
   ```makefile
   KICAD_LIBS := terra_sym.kicad_sym terra_resistors.kicad_sym
   ```
3. **Create corresponding .kicad_dbl file** for KiCad integration
4. **Run make** to build `db/terra_resistors.db`

## SPICE Simulation Support

The database includes SPICE fields for KiCad's integrated simulator:

- Auto-populated for resistors, capacitors, and inductors
- Uses KiCad's built-in SPICE models for passives
- Supports external model links for complex components

Example:
```sql
-- Resistor (auto-populated)
Sim_Device='R', Sim_Pins='1=+ 2=-', Sim_Type='', Sim_Library=''

-- IC (ready for external model)
Sim_Device='SUBCKT', Sim_Pins='1=IN 2=OUT 3=GND',
Sim_Type='LM358', Sim_Library='models/opamps.lib'
```

## Best Practices

1. **SQL is source of truth** - Always commit `.sql` files, not `.db` files
2. **Consistent naming** - Follow pattern: `"TYPE MANU SPEC VALUE TOLERANCE PACKAGE"`
3. **Complete metadata** - Include MPN, Manufacturer, Datasheet
4. **Use relative paths** - `${TERRA_EDA_LIB}` or `${KIPRJMOD}` for portability
5. **Test changes** - Run `make verify` after modifications
6. **Review diffs** - Use `git diff` to check SQL changes before committing

## Tools

### kicad_sym_to_db.py

Convert KiCad symbol libraries to SQL:

```bash
python3 tools/kicad_sym_to_db.py input.kicad_sym output.sql --config tools/field_mappings.yaml
```

Features:
- Full S-expression parser for KiCad format
- YAML-based field name normalization
- Dual-EDA column mapping
- Auto-populates SPICE fields for passives

### db_to_sql.py

Dump database to git-friendly SQL:

```bash
python3 tools/db_to_sql.py input.db output.sql
```

Features:
- Deterministic, sorted output
- Safe for git tracking
- Preserves all fields

### field_mappings.yaml

Configuration for field normalization:

```yaml
field_mappings:
  "Symbol": "KiCad_Symbol"      # Rename for dual-EDA
  "Footprint": "KiCad_Footprint"

column_edits:
  "Altium_Symbol": add           # Add new column
  "^ki_.*": remove               # Remove internal fields
```

## Future Tools

Planned tools to improve workflows:

- `extract_symbol.py` - Extract single symbol from DB to .kicad_sym
- `sql_to_kicad_sym.py` - Convert SQL back to .kicad_sym format
- `merge_symbols.py` - Safely merge SQL files with duplicate handling
- `validate_symbols.py` - Validate symbol references and required fields

## Contributing

When adding new components:

1. Follow naming conventions
2. Include complete metadata (MPN, Manufacturer, Datasheet)
3. Use appropriate symbols and footprints
4. Test with `make verify`
5. Write clear commit messages

## License

[Add your license information here]

## Support

For issues or questions:
- See [CLAUDE.md](CLAUDE.md) for detailed documentation
- Check [terra-eda-lib-spec.md](terra-eda-lib-spec.md) for architecture details
