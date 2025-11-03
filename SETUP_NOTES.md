# Terra EDA Library Setup Notes

## Adding Database Library to KiCad

**Note:** The `terra.kicad_dbl` file may appear grayed out in the file browser due to ODBC validation issues.

**Workaround:**
1. In Symbol Library Manager, click Add
2. Instead of browsing, type the path directly:
   - `${TERRA_EDA_LIB}/terra.kicad_dbl` (if TERRA_EDA_LIB is set)
   - Or use the full absolute path
3. Set Nickname to: `terra`
4. Click OK

The library will load correctly even though the file browser shows it as grayed out.

## Library Naming Convention

The Terra EDA Library appears in KiCad as two separate libraries:

1. **Symbol Library** (terra_sym)
   - File: `terra_sym.kicad_sym`
   - Nickname in KiCad: `terra_sym`
   - Provides: Actual symbol graphics (backing library)
   - Setup: Preferences → Manage Symbol Libraries

2. **Database Library** (terra)
   - File: `terra.kicad_dbl`
   - Appears as: `terra` in symbol chooser
   - Provides: Component database with metadata
   - Setup: Browse to terra.kicad_dbl file
   - This is what users select from when placing components

## Why This Naming?

- Users interact with database libraries when placing components
- Database libraries get the cleaner names (terra, terra_resistors, etc.)
- Symbol libraries are backing libraries with _sym suffix
- The database references symbols as `terra_sym:SYMBOL_NAME`

## Future Libraries

When adding specialized libraries:

**Resistor Library Example:**
- Symbol library: `terra_resistors_sym.kicad_sym` → nickname: `terra_resistors_sym`
- Database library: `db/terra_resistors.db` → appears as: `terra_resistors`
- Symbol references in DB: `terra_resistors_sym:R_0603_1%`

This pattern keeps database libraries with clean names for user interaction.

## Symbol References

- Standard KiCad symbols: `Device:R`, `Package_SO:SOIC-8`, etc.
- Terra symbols: `terra_sym:CustomIC`, `terra_sym:NEMA_17_Motor`, etc.
- Future specialized: `terra_resistors_sym:R_0603_1%`, etc.

## Footprint References

- Standard KiCad footprints: Direct references like `Package_SO:MSOP-8`
- Terra custom footprints: `terra:CustomFootprint` or `${TERRA_EDA_LIB}/assets/footprints/Custom.pretty/name`