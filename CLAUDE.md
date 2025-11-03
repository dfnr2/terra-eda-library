# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## How to Assist with This Repository

When the user asks for help with component library tasks, you should:

1. **Understand the workflow** - There are 4 main workflows documented below. Ask which workflow they want to use if unclear.
2. **Use the right tools** - Use `tools/kicad_sym_to_db.py` for .kicad_sym → SQL, `tools/db_to_sql.py` for DB → SQL
3. **Work with SQL first** - SQL files in `db/` are the source of truth, databases are generated
4. **Follow naming conventions** - Components follow pattern: "TYPE MANU SPEC VALUE TOLERANCE PACKAGE"
5. **Validate changes** - Always recommend running `make verify` after modifications
6. **Use temp/ for working files** - Never commit generated databases or temp files

### Common User Requests and How to Help

**"Add a resistor/capacitor/IC"** → Guide them through Workflow 1 or 3
- Workflow 1: Create in KiCad, convert to SQL, merge
- Workflow 3: Generate via script, append to SQL

**"Edit/fix a component"** → Recommend Workflow 2
- Direct database edit via SQL UPDATE statements
- Run `make dump` to update SQL file
- Review with `git diff`

**"Generate a series of components"** → Use Workflow 3 or 4
- Show them `generators/resistors_example.py`
- Help them adapt it for their component type
- Validate before merging

**"Create a new library"** → Guide through Workflow 4
- Generate SQL with full schema
- Update Makefile `KICAD_LIBS` variable
- Create corresponding .kicad_dbl file

**"Something is broken"** → Debugging steps
1. Run `make status` to see file status
2. Run `make verify` to check consistency
3. Check SQL syntax in `db/*.sql` files
4. Rebuild from clean: `make clean && make`

## Overview

The Terra EDA Library is a **multi-EDA database-driven component library** that supports both Altium and KiCad. It uses a SQLite database backend to manage electronic components (resistors, capacitors, ICs, etc.) with their associated symbols, footprints, and 3D models.

- For KiCad: Integrates via `.kicad_dbl` database library files
- For Altium: (Integration method TBD)

**Note:** This project was originally called "Ether KiCad Library" in early specifications, but has been renamed to "Terra EDA Library" to reflect its multi-EDA nature. The implementation uses "terra" as the prefix in file names and identifiers.

## Repository Structure

```
terra-eda-library/
├── README.md                 # User documentation
├── CLAUDE.md                 # This file - AI assistant guidance
├── Makefile                  # Build automation
├── terra_sym.kicad_sym   # Main KiCad symbol library file
├── terra.kicad_dbl   # Database library configuration for KiCad
├── terra-eda-lib-spec.md     # Architecture specification document
├── db/
│   ├── terra.sql     # SQL source of truth (tracked in git)
│   └── terra.db      # SQLite database (generated, not tracked)
├── tools/
│   ├── kicad_sym_to_db.py    # Convert .kicad_sym to SQL
│   ├── db_to_sql.py          # Dump database to SQL
│   └── field_mappings.yaml   # Field name normalization config
├── generators/
│   ├── README.md             # Generator script documentation
│   └── resistors_example.py  # Example part generation script
├── temp/                     # Working directory (gitignored)
├── assets/
│   ├── symbols/
│   │   ├── Standard/
│   │   └── Custom/
│   ├── footprints/
│   │   ├── Standard.pretty/
│   │   └── Custom.pretty/
│   └── 3dmodels/
│       ├── Standard.3dshapes/
│       └── Custom.3dshapes/
├── old/                      # Archived old files
└── parts/                    # (future) Per-part YAML definitions
```

## Current Implementation

The repository has a working build system with the following features:

- **Build system**: Makefile with targets for building, dumping, verifying databases
- **Database schema**: Single flat `symbols` table with dual-EDA support
- **Workflow**: SQL files are source of truth (git tracked), databases are generated artifacts
- **Multi-EDA**: Separate columns for KiCad and Altium (KiCad_Symbol, Altium_Symbol, etc.)
- **SPICE support**: Built-in SPICE simulation fields for passive components

**Note:** The spec describes a normalized schema (part, symbol_map, footprint_map tables) which is not currently implemented. The flat schema is simpler and works well for current needs.

## Database Schema (Current Implementation)

The `db/terra.db` contains a single flat table with dual-EDA support:

```sql
CREATE TABLE symbols (
  "Symbol_Name" TEXT,           -- Unique identifier
  "Reference" TEXT,              -- Component reference prefix (R, C, U, etc.)
  "Value" TEXT,                  -- Component value

  -- Multi-EDA Support
  "KiCad_Symbol" TEXT,           -- KiCad symbol reference (library:symbol)
  "KiCad_Footprint" TEXT,        -- KiCad footprint reference
  "Altium_Symbol" TEXT,          -- Altium symbol reference (future)
  "Altium_Footprint" TEXT,       -- Altium footprint reference (future)

  -- Metadata
  "Description" TEXT,
  "Datasheet" TEXT,
  "Manufacturer" TEXT,
  "MPN" TEXT,
  "Package" TEXT,
  "Class" TEXT,

  -- Electrical Characteristics
  "Component_Type" TEXT,
  "Component_Value" TEXT,
  "Tolerance" TEXT,
  "Power_Rating" TEXT,
  "Voltage_Rating" TEXT,
  "Current_Rating" TEXT,
  "Material" TEXT,
  "Number_of_Pins" TEXT,

  -- Temperature
  "Temp_Coeff" TEXT,
  "Temp_Operating" TEXT,
  "Temp_Soldering" TEXT,
  "Temp_Storage" TEXT,

  -- SPICE Simulation (KiCad)
  "Sim_Device" TEXT,             -- SPICE device type (R, L, C, etc.)
  "Sim_Pins" TEXT,               -- Pin mapping for SPICE
  "Sim_Type" TEXT,               -- SPICE model type
  "Sim_Library" TEXT,            -- Path to external SPICE model

  -- BOM and Assembly
  "Part_ID" TEXT,
  "Allow_Substitution" TEXT,
  "BOM_Comment" TEXT,
  "Fitted" TEXT,
  "Standards_Version" TEXT,
  "Tracking" TEXT,
  "RoHS" TEXT,
  "RoHS_Document_Link" TEXT,
  "Manufacturer_Link" TEXT
);
```

**Key Changes from Old Schema:**
- `Symbol` → `KiCad_Symbol` (dual-EDA naming)
- `Footprint` → `KiCad_Footprint` (dual-EDA naming)
- Added `Altium_Symbol` and `Altium_Footprint` columns
- Added SPICE simulation fields (`Sim_*`)

## Build Workflow

The library uses a Makefile-based workflow with SQL as the source of truth:

### Initial Setup (from .kicad_sym)

```bash
# Convert symbol library to SQL (one-time)
make db/terra.sql

# Build database from SQL
make

# Or do both at once
make all
```

### Daily Workflow

**Option A: Edit Database Directly**
```bash
# Edit database using SQLite or KiCad DB editor
sqlite3 db/terra.db

# Dump changes back to SQL for git tracking
make dump

# Review changes
git diff db/terra.sql

# Commit
git add db/terra.sql
git commit -m "Update component specifications"
```

**Option B: Edit SQL Directly**
```bash
# Edit SQL file in your editor
vim db/terra.sql

# Rebuild database
make

# Commit
git add db/terra.sql
git commit -m "Add new components"
```

### Makefile Targets

- `make` or `make all` - Build all databases from SQL files
- `make dump` - Dump databases back to SQL (after editing)
- `make verify` - Verify round-trip consistency (SQL → DB → SQL)
- `make status` - Show status of all files
- `make clean` - Remove generated .db files (keep SQL)
- `make distclean` - Remove all generated files including SQL
- `make help` - Show help

### Adding New Libraries

To add a new symbol library (e.g., resistors):

1. Add the library to `KICAD_LIBS` in Makefile:
   ```makefile
   KICAD_LIBS := terra_sym.kicad_sym resistors.kicad_sym
   ```

2. Run make to generate `db/resistors.sql` and `db/resistors.db`

### Tools

**`tools/kicad_sym_to_db.py`** - Convert .kicad_sym to SQL
- Full S-expression parser for KiCad format
- YAML-based field name normalization (`field_mappings.yaml`)
- Dual-EDA support (KiCad/Altium columns)
- Auto-populates SPICE fields for passives (R, L, C)
- Handles schema evolution (adds missing columns)

**`tools/db_to_sql.py`** - Dump database to SQL
- Deterministic, sorted output (good for git diffs)
- Preserves all fields including SPICE

**`tools/field_mappings.yaml`** - Field normalization config
- Maps field names (e.g., "Symbol" → "KiCad_Symbol")
- Regex pattern matching
- Column add/remove operations

## KiCad Database Library Configuration

The `terra.kicad_dbl` file configures KiCad to use this database:

- **Database path**: Uses `${KIPRJMOD}/db/terra.db` (relative to project)
- **ODBC driver**: `/usr/local/lib/libsqlite3odbc.dylib` (macOS SQLite ODBC driver)
- **Table**: References the `symbols` table
- **Symbol column**: `KiCad_Symbol` (dual-EDA naming)
- **Footprint column**: `KiCad_Footprint` (dual-EDA naming)
- **Fields mapping**: Maps database columns to KiCad component properties

**Note:** The database path uses KiCad's `${KIPRJMOD}` variable which resolves to the project directory, making the library portable across different machines.

## Path References

The spec describes an `@@ASSET_ROOT@@` placeholder system that gets replaced during build, but the current database uses direct references to KiCad standard libraries (e.g., `Package_SO:MSOP-8_3x3mm_P0.65mm`) or relative paths within the assets structure.

## SPICE Simulation Support

The database includes SPICE simulation fields for KiCad's integrated circuit simulator:

- **Sim_Device**: SPICE device type (R, L, C, D, etc.)
- **Sim_Pins**: Pin mapping (e.g., "1=+ 2=-")
- **Sim_Type**: Model type (empty for built-in models)
- **Sim_Library**: Path to external SPICE model file

**Auto-population for passives:**
- **Resistors**: `Sim_Device='R'`, `Sim_Pins='1=+ 2=-'`, uses built-in model
- **Capacitors**: `Sim_Device='C'`, `Sim_Pins='1=+ 2=-'`, uses built-in model
- **Inductors**: `Sim_Device='L'`, `Sim_Pins='1=+ 2=-'`, uses built-in model

For other components (ICs, transistors, etc.), SPICE fields are included but empty, ready for external model configuration.

## Part Editing/Addition Workflows

The Terra EDA Library supports multiple workflows for adding and editing parts, depending on your use case.

### Workflow 1: KiCad New Part Creation → Merge to Terra

**Use Case:** Creating brand new parts from scratch in KiCad's symbol editor

**Steps:**
1. Create temp library in KiCad (e.g., `temp_new_parts.kicad_sym`)
2. Design part with:
   - Symbols: Either KiCad standard (e.g., `Device:R`) or custom (`${TERRA_EDA_LIB}/assets/symbols/Custom/my_symbol`)
   - Footprints: Either KiCad standard or `${TERRA_EDA_LIB}/assets/footprints/Custom.pretty/my_footprint`
3. Save temp library
4. Convert to SQL:
   ```bash
   python3 tools/kicad_sym_to_db.py temp_new_parts.kicad_sym temp_new_parts.sql --config tools/field_mappings.yaml
   ```
5. **Merge to existing library:**
   ```bash
   # Extract INSERT statements (skip CREATE TABLE)
   grep "^INSERT" temp_new_parts.sql >> db/terra.sql
   make  # Rebuild database
   make verify  # Verify integrity
   ```

**Best Practices:**
- Use consistent naming (e.g., `CAP KEMET MLCC 0.1uF X7R 10% 16V 0603`)
- Fill in all metadata (MPN, Manufacturer, Datasheet, etc.)
- Use `${TERRA_EDA_LIB}` for custom asset paths within the library
- Use standard KiCad library references for common components (e.g., `Device:R`, `Resistor_SMD:R_0603_1608Metric`)

**Path Reference Rules:**
- **Standard KiCad symbols:** `Device:R`, `Device:C`, etc. (no path needed)
- **Standard KiCad footprints:** `Resistor_SMD:R_0603_1608Metric`, `Package_SO:SOIC-8`, etc. (no path needed)
- **Terra library symbols:** `terra_eda_lib:COMPONENT_NAME` (requires symbol library setup)
- **Custom footprints:** `Terra_Custom:my_footprint` OR `${TERRA_EDA_LIB}/assets/footprints/Custom.pretty/my_footprint.kicad_mod`
- **3D models:** `${TERRA_EDA_LIB}/assets/3dmodels/Custom.3dshapes/my_model.step` (in footprint files)

### Workflow 2: KiCad Part Modification → Replace Original

**Use Case:** Fixing/updating existing parts

**Steps:**
1. Edit database directly:
   ```bash
   sqlite3 db/terra.db
   ```
2. Make changes via SQL UPDATE statements
3. Dump changes back to SQL:
   ```bash
   make dump
   git diff db/terra.sql  # Review changes
   ```

**Alternative (via KiCad):**
1. Export part to temp library (requires `extract_symbol.py` tool - see Future Tools)
2. Edit in KiCad symbol editor
3. Convert back to SQL
4. Replace in database using SQL DELETE + INSERT
5. Run `make dump` to update SQL file

### Workflow 3: Script-Generated Parts → Merge to Existing Library

**Use Case:** Bulk creation of similar parts (e.g., resistor series from datasheet)

**Steps:**
1. Create generation script:
   ```python
   # generators/resistors.py
   def generate_resistor_sql(value, tolerance, power, package, mpn, manufacturer):
       symbol_name = f"RES {value} {tolerance} {power}W {package}"
       return f"""INSERT INTO symbols (Symbol_Name, Reference, Value, KiCad_Symbol, ...)
       VALUES ('{symbol_name}', 'R', '{value}', 'terra_eda_lib:{symbol_name}', ...);"""

   for value in ["1K", "10K", "100K"]:
       print(generate_resistor_sql(value, "1%", "0.1", "0603", "RC0603FR-071KL", "Yageo"))
   ```
2. Generate SQL:
   ```bash
   python3 generators/resistors.py > resistors_batch.sql
   ```
3. Check for duplicates:
   ```bash
   grep "Symbol_Name" db/terra.sql resistors_batch.sql | sort | uniq -d
   ```
4. Merge into existing library:
   ```bash
   cat resistors_batch.sql >> db/terra.sql
   make  # Rebuild
   make verify
   ```

### Workflow 4: Script-Generated Parts → New Library

**Use Case:** Large sets of related parts that deserve their own library/database

**Steps:**
1. Generate complete SQL with CREATE TABLE:
   ```python
   # generators/resistor_library.py
   print("DROP TABLE IF EXISTS symbols;")
   print("CREATE TABLE IF NOT EXISTS symbols (...);")  # Copy schema
   print("BEGIN TRANSACTION;")
   for resistor in resistor_list:
       print(generate_resistor_sql(resistor))
   print("COMMIT;")
   ```
2. Create new library:
   ```bash
   python3 generators/resistor_library.py > db/terra_resistors.sql
   ```
3. Add to Makefile:
   ```makefile
   KICAD_LIBS := terra_sym.kicad_sym terra_resistors.kicad_sym
   ```
4. Create corresponding `.kicad_dbl` file (copy and modify `terra.kicad_dbl`)
5. Build:
   ```bash
   make  # Builds db/terra_resistors.db
   ```

**Note:** You'll need to create `terra_resistors.kicad_sym` manually or use a reverse tool (future: `sql_to_kicad_sym.py`)

## Best Practices

1. **SQL is Source of Truth** - Always edit/generate SQL, then build database from it
2. **Use temp/ directory** - For work-in-progress (add to .gitignore)
3. **Validate before merging** - Check for duplicates and valid references
4. **Consistent naming** - Follow patterns: `"TYPE MANU SPEC VALUE TOLERANCE RATING PACKAGE"`
5. **Complete metadata** - Always include: MPN, Manufacturer, Datasheet, Description
6. **Use ${TERRA_EDA_LIB} variable** - For library-internal paths (footprints, 3D models, custom symbols)
7. **Use standard KiCad refs** - When possible, use built-in KiCad libraries (`Device:R`, `Resistor_SMD:R_0603`)
8. **Test round-trip** - Run `make verify` after significant changes
9. **Clear commits** - Document what parts were added/modified

## Path and Reference Conventions

The library uses `${TERRA_EDA_LIB}` environment variable for portability. Users configure this once in KiCad (see [KICAD_SETUP.md](KICAD_SETUP.md)).

### Symbol References

```sql
-- Standard KiCad library (always available)
KiCad_Symbol = 'Device:R'

-- Terra library symbol (requires terra_eda_lib in symbol library table)
KiCad_Symbol = 'terra_eda_lib:RES 10K 1% 0.1W 0603'

-- Custom symbol in assets (rare, for unique symbols)
KiCad_Symbol = '${TERRA_EDA_LIB}/assets/symbols/Custom/my_symbol.kicad_sym:SYMBOL_NAME'
```

### Footprint References

```sql
-- Standard KiCad library (always available)
KiCad_Footprint = 'Resistor_SMD:R_0603_1608Metric'
KiCad_Footprint = 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'

-- Terra custom footprint (requires Terra_Custom in footprint library table)
KiCad_Footprint = 'Terra_Custom:my_custom_footprint'

-- OR with full path
KiCad_Footprint = '${TERRA_EDA_LIB}/assets/footprints/Custom.pretty/my_custom_footprint.kicad_mod'
```

### 3D Model References (in .kicad_mod files)

```lisp
(model "${TERRA_EDA_LIB}/assets/3dmodels/Custom.3dshapes/my_model.step"
  (offset (xyz 0 0 0))
  (scale (xyz 1 1 1))
  (rotate (xyz 0 0 0))
)
```

### When to Use Each

| Asset Type | Use Standard KiCad | Use Terra Library | Use ${TERRA_EDA_LIB} Path |
|------------|-------------------|-------------------|---------------------------|
| Common resistor symbol | ✅ `Device:R` | ❌ | ❌ |
| Common resistor footprint | ✅ `Resistor_SMD:...` | ❌ | ❌ |
| Specific component in DB | ❌ | ✅ `terra_eda_lib:PART` | ❌ |
| Custom footprint | ❌ | ✅ `Terra_Custom:name` | OR ✅ `${TERRA_EDA_LIB}/...` |
| Custom 3D model | ❌ | ❌ | ✅ `${TERRA_EDA_LIB}/...` |

## Recommended Directory Structure

```
terra-eda-library/
├── generators/              # Part generation scripts
│   ├── resistors.py
│   ├── capacitors.py
│   └── templates/
│       └── passive.sql.j2
├── temp/                   # Working area (gitignored)
│   └── .gitkeep
```

## Helper Scripts You Can Generate for Users

When users need automation, you can help create Python scripts for:

### Component Generation Scripts

Based on `generators/resistors_example.py`, you can create generators for:
- **Capacitors** - With voltage ratings, dielectric types (X7R, C0G, etc.)
- **Inductors** - With current ratings, saturation specs
- **ICs** - With package variants, pin counts
- **Connectors** - With pin counts, orientations, manufacturers

**Template pattern:**
```python
def generate_component_sql(specs):
    symbol_name = f"{type} {manufacturer} {value} {package}"
    return f"""INSERT INTO symbols (...) VALUES ('{symbol_name}', ...);"""
```

### Data Import Scripts

Help users create scripts to:
- Parse CSV files from distributors (Digi-Key, Mouser)
- Import from manufacturer part tables
- Convert from other EDA library formats
- Batch update metadata (datasheets, links)

### Validation Scripts

Create scripts that:
- Check for duplicate Symbol_Names
- Validate footprint references exist
- Verify MPN format patterns
- Find missing required fields
- Check SPICE field consistency

### Utility Scripts

Quick helper scripts for:
- Finding components by criteria (package, manufacturer, value range)
- Bulk updating fields (e.g., add manufacturer link to all parts)
- Generating .kicad_dbl files for new libraries
- Creating summary reports (components by category, manufacturer, etc.)

## Future Tools (Planned but Not Yet Implemented)

These tools are documented for future development. When users need them, you can help implement:

1. **`tools/extract_symbol.py`** - Extract single symbol from DB to .kicad_sym
   ```bash
   python3 tools/extract_symbol.py db/terra.db "RES 10K 0603" > temp/edit.kicad_sym
   ```

2. **`tools/sql_to_kicad_sym.py`** - Convert SQL back to .kicad_sym format
   ```bash
   python3 tools/sql_to_kicad_sym.py db/terra_resistors.sql terra_resistors.kicad_sym
   ```

3. **`tools/merge_symbols.py`** - Safely merge symbol SQL, handling duplicates
   ```bash
   python3 tools/merge_symbols.py source.sql target.sql --replace-duplicates
   ```

4. **`tools/validate_symbols.py`** - Validate references and required fields
   ```bash
   python3 tools/validate_symbols.py db/terra.sql
   ```

When users request these tools, offer to implement them based on the specifications above.

## Common SQL Patterns for Editing Components

When helping users edit components directly via SQL, use these patterns:

### Query Components
```sql
-- Find by name pattern
SELECT Symbol_Name, MPN, Manufacturer FROM symbols
WHERE Symbol_Name LIKE 'RES%0603%';

-- Find by manufacturer
SELECT Symbol_Name, MPN, Package FROM symbols
WHERE Manufacturer = 'Yageo';

-- Find missing data
SELECT Symbol_Name FROM symbols
WHERE MPN IS NULL OR MPN = '';
```

### Update Components
```sql
-- Update single field
UPDATE symbols
SET Datasheet = 'https://example.com/datasheet.pdf'
WHERE Symbol_Name = 'RES 10K 1% 0.1W 0603';

-- Bulk update pattern
UPDATE symbols
SET Manufacturer_Link = 'https://www.yageo.com'
WHERE Manufacturer = 'Yageo';

-- Update SPICE fields for component
UPDATE symbols
SET Sim_Device = 'C', Sim_Pins = '1=+ 2=-'
WHERE Reference = 'C' AND (Sim_Device IS NULL OR Sim_Device = '');
```

### Add Components
```sql
-- Insert new component (always use all columns for consistency)
INSERT INTO symbols (
    Symbol_Name, Reference, Value,
    KiCad_Symbol, KiCad_Footprint,
    Description, Manufacturer, MPN, Package
) VALUES (
    'RES 10K 1% 0.1W 0603',
    'R',
    '10K',
    'terra_eda_lib:RES 10K 1% 0.1W 0603',
    'Resistor_SMD:R_0603_1608Metric',
    '10k ohm 1% resistor 0.1W',
    'Yageo',
    'RC0603FR-0710KL',
    '0603'
);
```

### Delete Components
```sql
-- Delete component (use with caution!)
DELETE FROM symbols WHERE Symbol_Name = 'OLD_PART_NAME';

-- Delete multiple (verify with SELECT first!)
DELETE FROM symbols WHERE Manufacturer = 'Obsolete Corp';
```

### Important SQL Notes
- Always escape single quotes in strings: `'O''Reilly'` for `O'Reilly`
- Use `IS NULL` not `= NULL` for null checks
- After editing database, always run `make dump` to save to SQL
- Review changes with `git diff db/terra.sql` before committing

## Future Development

See `terra-eda-lib-spec.md` for long-term architecture plans:
- YAML-based part definitions in `parts/<PartID>/part.yml`
- Normalized database schema (part, symbol_map, footprint_map, mpn tables)
- Asset validation tool
- Altium integration
- Category-specific database views
