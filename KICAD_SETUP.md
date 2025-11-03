# KiCad Setup Guide for Terra EDA Library

This guide explains how to configure KiCad to use the Terra EDA Library across all your projects.

## Overview

The Terra EDA Library uses the `${TERRA_EDA_LIB}` environment variable to reference library assets. This allows:
- **Single library location** - One copy of the library for all projects
- **Portability** - Projects reference the library, not hardcoded paths
- **Easy updates** - Update library once, all projects benefit
- **Team sharing** - Each team member sets their own `TERRA_EDA_LIB` path

## Step 1: Clone the Terra EDA Library

Choose a permanent location for the library:

```bash
# Example locations:
cd ~/kicad-libraries/
# OR
cd /opt/kicad-libraries/
# OR
cd /Volumes/User/shared/kicad-libraries/

# Clone the library
git clone <repository-url> terra-eda-library
cd terra-eda-library

# Build the database
make
```

**Important:** Choose a location that won't change. Moving it later requires updating the environment variable in KiCad.

## Step 2: Configure KiCad Environment Variable

### Method 1: KiCad Preferences (Recommended)

1. Open KiCad
2. Go to **Preferences → Configure Paths...**
3. Click **Add** (the + button)
4. Enter:
   - **Name:** `TERRA_EDA_LIB`
   - **Path:** `/full/path/to/terra-eda-library` (use your actual path)
5. Click **OK**

**Example:**
```
Name: TERRA_EDA_LIB
Path: /Users/dave/kicad-libraries/terra-eda-library
```

### Method 2: Environment File (Advanced)

Create/edit KiCad's environment file:

**Location:**
- **macOS:** `~/Library/Preferences/kicad/8.0/kicad_common.json`
- **Linux:** `~/.config/kicad/8.0/kicad_common.json`
- **Windows:** `%APPDATA%\kicad\8.0\kicad_common.json`

Add to the `environment.vars` section:
```json
{
  "environment": {
    "vars": {
      "TERRA_EDA_LIB": "/full/path/to/terra-eda-library"
    }
  }
}
```

### Verify Environment Variable

In KiCad, go to **Preferences → Configure Paths...**

You should see `TERRA_EDA_LIB` listed with your path. The resolved path should show the full directory.

## Step 3: Add Symbol Library

### Method 1: Global Symbol Library (Recommended)

1. Go to **Preferences → Manage Symbol Libraries...**
2. Select the **Global Libraries** tab
3. Click **Add** (folder icon with +)
4. Browse to **or type**: `${TERRA_EDA_LIB}/terra_sym.kicad_sym`
5. Set **Nickname:** `terra_eda_lib`
6. Click **OK**

The library table entry will look like:
```
Nickname: terra
Library Path: ${TERRA_EDA_LIB}/terra_sym.kicad_sym
Plugin Type: KiCad
Options: (empty)
Description: Terra EDA Component Library
```

### Method 2: Manual sym-lib-table Edit

Edit your global `sym-lib-table`:

**Location:**
- **macOS:** `~/Library/Preferences/kicad/8.0/sym-lib-table`
- **Linux:** `~/.config/kicad/8.0/sym-lib-table`
- **Windows:** `%APPDATA%\kicad\8.0\sym-lib-table`

Add this line:
```lisp
(lib (name "terra_eda_lib")(type "KiCad")(uri "${TERRA_EDA_LIB}/terra_sym.kicad_sym")(options "")(descr "Terra EDA Component Library"))
```

## Step 4: Add Footprint Library (for Custom Footprints)

If you're using custom footprints in `assets/footprints/Custom.pretty/`:

1. Go to **Preferences → Manage Footprint Libraries...**
2. Select the **Global Libraries** tab
3. Click **Add** (folder icon with +)
4. Browse to **or type**: `${TERRA_EDA_LIB}/assets/footprints/Custom.pretty`
5. Set **Nickname:** `Terra_Custom`
6. Click **OK**

**Manual fp-lib-table entry:**
```lisp
(lib (name "Terra_Custom")(type "KiCad")(uri "${TERRA_EDA_LIB}/assets/footprints/Custom.pretty")(options "")(descr "Terra custom footprints"))
```

## Step 5: Add Database Library

### Copy .kicad_dbl to KiCad Configuration

The database library file needs to be in a location where KiCad can find it.

**Option A: User Configuration Directory (Recommended)**

```bash
# macOS
cp terra.kicad_dbl ~/Library/Preferences/kicad/8.0/library/

# Linux
cp terra.kicad_dbl ~/.config/kicad/8.0/library/

# Windows
copy terra.kicad_dbl %APPDATA%\kicad\8.0\library\
```

**Option B: Project-Specific**

For per-project use, copy `terra.kicad_dbl` to your project directory.

### Verify Database Library

1. Open the **Symbol Chooser** in Eeschema (Place → Add Symbol, or press 'A')
2. You should see **Terra EDA Components** in the library list
3. Select it and browse components
4. Components should show metadata (MPN, Manufacturer, etc.)

## Step 6: Verify Setup

### Test Symbol Placement

1. Create a new schematic or open existing project
2. Press **A** (Add Symbol)
3. Search for a component (e.g., type "RES 10K")
4. Select a component from **Terra EDA Components**
5. Place it
6. Verify the footprint is correct

### Test Database Connection

1. Right-click a placed Terra EDA component
2. Select **Properties**
3. Check that fields are populated (MPN, Manufacturer, Datasheet, etc.)
4. The Symbol Library should show: `terra_eda_lib`
5. If using database, fields should auto-populate from database

## Troubleshooting

### "Library not found" Error

**Problem:** KiCad can't find `terra_sym.kicad_sym`

**Solution:**
1. Verify `TERRA_EDA_LIB` is set: **Preferences → Configure Paths**
2. Check the path resolves correctly (expand the variable)
3. Verify the file exists: `${TERRA_EDA_LIB}/terra_sym.kicad_sym`
4. Try using absolute path temporarily to test

### Database Library Not Showing

**Problem:** "Terra EDA Components" doesn't appear in symbol chooser

**Solution:**
1. Verify ODBC driver is installed: `/usr/local/lib/libsqlite3odbc.dylib` (macOS)
2. Check `.kicad_dbl` file is in correct location
3. Verify database exists: `${TERRA_EDA_LIB}/db/terra.db`
4. Check KiCad version (database libraries require KiCad 7.0+)
5. Look at KiCad logs for database connection errors

### ODBC Driver Installation

**macOS:**
```bash
brew install sqliteodbc
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libsqliteodbc
```

**Windows:**
Download from: http://www.ch-werner.de/sqliteodbc/

### Custom Footprints Not Found

**Problem:** Footprints with `terra_eda_lib:` prefix not found

**Solution:**
1. Check if footprint is really custom (should be in `assets/footprints/Custom.pretty/`)
2. For standard KiCad footprints, they shouldn't have `terra_eda_lib:` prefix
3. Add Terra_Custom footprint library (see Step 4)
4. Update database to use correct footprint references

### Variables Not Resolving

**Problem:** Paths show `${TERRA_EDA_LIB}` literally instead of resolving

**Solution:**
1. Restart KiCad after setting environment variable
2. Check spelling of variable name (case-sensitive)
3. Verify variable is set in **Configure Paths**
4. Try using KiCad 8.0+ (better variable support)

## Path Reference Conventions

### Symbols

- **Standard KiCad:** `Device:R`, `Device:C`, etc.
- **Terra Library:** `terra_eda_lib:COMPONENT_NAME`
- **Custom in Terra:** `${TERRA_EDA_LIB}/assets/symbols/Custom/my_symbol.kicad_sym:SYMBOL_NAME`

### Footprints

- **Standard KiCad:** `Resistor_SMD:R_0603_1608Metric`, `Package_SO:SOIC-8`
- **Terra Custom:** `Terra_Custom:my_footprint` (after adding footprint library)
- **OR:** `${TERRA_EDA_LIB}/assets/footprints/Custom.pretty/my_footprint.kicad_mod`

### 3D Models

Referenced from footprint files using:
```
${TERRA_EDA_LIB}/assets/3dmodels/Custom.3dshapes/my_model.step
```

## Team Setup

For teams, each member should:

1. Clone the library to their preferred location
2. Set `TERRA_EDA_LIB` to their local path
3. Copy `.kicad_dbl` to their KiCad config
4. Add symbol and footprint libraries as global libraries

Projects will be portable because they reference `${TERRA_EDA_LIB}`, not absolute paths.

## Updating the Library

To update to the latest library version:

```bash
cd /path/to/terra-eda-library
git pull
make clean
make
make verify
```

All projects using the library will automatically see the updates.

## Multiple Library Versions

If you need different library versions for different projects:

1. Clone library to version-specific locations:
   ```
   ~/kicad-libraries/terra-eda-library-v1/
   ~/kicad-libraries/terra-eda-library-v2/
   ```

2. Use project-specific environment variables (KiCad 8.0+):
   - Add `.kicad_vars` to project directory
   - Define `TERRA_EDA_LIB` per-project

3. OR use project-specific library tables instead of global

## Next Steps

- Read [README.md](README.md) for library usage
- See [CLAUDE.md](CLAUDE.md) for component editing workflows
- Check [generators/](generators/) for part generation scripts

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify KiCad version (8.0+ recommended)
3. Check KiCad logs for errors
4. Review library paths in **Configure Paths**
