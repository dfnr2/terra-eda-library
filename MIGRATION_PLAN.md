# Migration Plan: Single-Table to Multi-Table Architecture

**Date:** 2025-11-10
**Status:** Planning Phase

## Overview

Migrating Terra EDA Library from a single `symbols` table to a multi-table architecture with one table per component type, all within a single database.

## Architecture Decision

### Structure
```
db/tables/
├── resistors/
│   ├── resistors.sql              # CREATE TABLE + INSERT statements
│   └── kicad/                     # Optional: custom assets
│       ├── resistors.pretty/
│       ├── symbols/
│       └── 3dmodels/
├── capacitors/
│   └── capacitors.sql
└── ... (14 more component types)
```

### Design Principles
1. **Single Database** - All tables in one `db/terra.db` file
2. **Denormalized** - No foreign keys, tables are independent
3. **Core Fields** - All tables share 22 standard fields
4. **Type-Specific Fields** - Each table adds its own specialized columns
5. **Co-located Assets** - Custom symbols/footprints live with their table
6. **SQL Source of Truth** - SQL files tracked in git, DB is generated
7. **Perfect Round-Trip** - `SQL → DB → SQL` must be deterministic

## Core Fields (22 fields in all tables)

```sql
-- Identity (3)
part_id TEXT PRIMARY KEY,
mpn TEXT NOT NULL,
manufacturer TEXT NOT NULL,

-- Physical/Display (2)
package TEXT,
value TEXT,

-- Documentation (3)
description TEXT,
datasheet TEXT,
manufacturer_link TEXT,

-- CAD Integration (4)
kicad_symbol TEXT,
kicad_footprint TEXT,
altium_symbol TEXT,
altium_footprint TEXT,

-- Supply Chain (3)
lifecycle_status TEXT DEFAULT 'Active',
rohs BOOLEAN DEFAULT TRUE,
rohs_document_link TEXT,

-- Process Control (4)
allow_substitution BOOLEAN DEFAULT TRUE,
tracking BOOLEAN DEFAULT FALSE,
standards_version TEXT DEFAULT 'v1.0',
bom_comment TEXT,

-- Metadata (3)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
created_by TEXT
```

## Component Type Tables

### Planned Tables (15 total)

1. **resistors** - resistance, tolerance, power_rating, temp_coeff
2. **capacitors** - capacitance, tolerance, voltage_rating, dielectric
3. **inductors** - inductance, tolerance, current_rating, saturation_current
4. **ferrites** - impedance_at_freq, dc_resistance, current_rating
5. **transistors** - transistor_type, vce_vds, ic_id, hfe_gain
6. **diodes** - diode_type, forward_voltage, forward_current, reverse_voltage
7. **connectors** - pin_count, pitch, mounting_type, current_rating
8. **ic_drivers** - output_current, channels, logic_level, driver_type
9. **ic_microcontrollers** - mcu_family, flash_size, ram_size, gpio_count, peripherals
10. **ic_logic** - logic_family, gate_type, propagation_delay, operating_voltage
11. **ic_memory** - memory_type, capacity, speed, interface
12. **ic_opamp** - gbw_product, slew_rate, input_offset, noise, channels
13. **ic_analog** - function_type, function_specific_fields
14. **leds** - color, wavelength, forward_voltage, luminous_intensity, viewing_angle
15. **switches** - switch_type, poles, throw, actuation_force

## Migration Steps

### Phase 1: Schema Design
- [ ] Define type-specific fields for each of the 15 component types
- [ ] Create template SQL for each table
- [ ] Document field mapping from old `symbols` table to new tables

### Phase 2: Tool Development
- [ ] Create `tools/db_to_tables.py` - Dumps DB to table structure
- [ ] Create `tools/migrate_to_tables.py` - Splits current terra.sql by Reference field
- [ ] Update `tools/field_mappings.yaml` for new field names

### Phase 3: Makefile Updates
- [ ] Update build target to concatenate `db/tables/*/*.sql`
- [ ] Update dump target to call `db_to_tables.py`
- [ ] Update verify target for multi-table round-trip
- [ ] Update status target to show per-table stats

### Phase 4: Migration Execution
- [ ] Backup current `db/terra.sql` and `db/terra.db`
- [ ] Run migration script on current data
- [ ] Verify all components migrated correctly
- [ ] Test round-trip: new SQL → DB → SQL
- [ ] Archive old files to `old/legacy_single_table/`

### Phase 5: Documentation
- [ ] Update README.md with new structure
- [ ] Update CLAUDE.md (already done)
- [ ] Update examples in generators/
- [ ] Create per-table schema documentation

## Field Mapping Strategy

### Old `symbols` table → New tables

**Categorization by Reference field:**
- `Reference = 'R'` → resistors table
- `Reference = 'C'` → capacitors table
- `Reference = 'L'` → inductors table
- `Reference = 'FB'` → ferrites table
- `Reference = 'Q'` → transistors table
- `Reference = 'D'` → diodes table
- `Reference = 'J'` → connectors table
- `Reference = 'U'` → Needs sub-categorization by Component_Type or Description
  - ICs will need manual classification into driver/mcu/logic/memory/opamp/analog
- `Reference = 'LED'` → leds table
- `Reference = 'SW'` → switches table

**Field name conversions (old → new):**
```
Symbol_Name → part_id (or generate new ID)
MPN → mpn
Manufacturer → manufacturer
Package → package
Value → value
Description → description
Datasheet → datasheet
Manufacturer_Link → manufacturer_link
KiCad_Symbol → kicad_symbol
KiCad_Footprint → kicad_footprint
Altium_Symbol → altium_symbol
Altium_Footprint → altium_footprint
RoHS → rohs (convert 'Yes'/'No' to BOOLEAN)
RoHS_Document_Link → rohs_document_link
Allow_Substitution → allow_substitution (convert to BOOLEAN)
Tracking → tracking (convert to BOOLEAN)
Standards_Version → standards_version
BOM_Comment → bom_comment
```

**Type-specific field mappings:**
- Resistors: `Power_Rating` → `power_rating`, `Tolerance` → `tolerance`, `Temp_Coeff` → `temp_coeff`
- Capacitors: `Voltage_Rating` → `voltage_rating`, `Tolerance` → `tolerance`, `Material` → `dielectric`
- Etc. (to be documented per table)

## Build/Dump Workflow

### Build (SQL → DB)
```bash
make clean
make
# Concatenates all db/tables/*/*.sql files
# Creates single db/terra.db with all tables
```

### Dump (DB → SQL)
```bash
sqlite3 db/terra.db "UPDATE resistors SET tolerance='1%' WHERE part_id='RES-001'"
make dump
# Dumps each table to db/tables/{table}/{table}.sql
git diff db/tables/resistors/resistors.sql
```

### Verify Round-Trip
```bash
make verify
# SQL → DB → SQL → DB, checksums must match
```

## Rollback Plan

If migration fails:
1. Restore `db/terra.sql` from backup
2. Revert Makefile changes
3. Rebuild with `make clean && make`
4. Document issues for retry

## Success Criteria

- [ ] All 162 current components migrated to appropriate tables
- [ ] Round-trip verification passes for all tables
- [ ] `make` builds complete database without errors
- [ ] `make dump` produces deterministic, git-friendly SQL
- [ ] No data loss (checksums match)
- [ ] Documentation is complete and accurate

## Timeline

- **Day 1:** Schema design, field mapping
- **Day 2:** Tool development (db_to_tables.py, migrate_to_tables.py)
- **Day 3:** Makefile updates, testing
- **Day 4:** Migration execution, verification
- **Day 5:** Documentation, cleanup

## Notes

- Some ICs in current database will need manual review for categorization
- Custom asset paths will need updating to new `db/tables/{type}/kicad/` locations
- KiCad .kicad_dbl file may need updates to query from multiple tables or a UNION view
- Consider creating an `all_parts` view for cross-table searches
