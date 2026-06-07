# Capacitor Generator Script Prompt

This document contains a prompt for instructing an LLM to create capacitor database generator scripts from manufacturer datasheets.

## Usage

1. Provide this prompt to the LLM
2. Attach the reference script (`run_300_kemet_c0g_mlcc.py`)
3. Attach the database schema SQL file
4. Attach the manufacturer datasheet (PDF)
5. Answer any clarifying questions the LLM asks

---

## Prompt

```org
* Task: Create Capacitor Database Generator Script

Using the provided reference script, database schema, and manufacturer
datasheet, create a Python script that generates SQL INSERT statements
for this capacitor series.

** Reference Materials

- *Reference Script*: Adapt this pattern for the new manufacturer/series
- *Database Schema*: Target table structure (schema is authoritative for field names)
- *Datasheet*: Source of truth for part specifications and MPN encoding

** Script Requirements

*** Structure
Follow the reference script's organization:
1. User configuration section at top (tolerances, case/voltage enables, packaging)
2. Vendor specifications section (manufacturer info, URL templates, encoding tables)
3. Helper functions (capacitance encoding, MPN formatting, value generation)
4. Main generation function and entry point

*** Configuration Pattern
Use dictionaries with "yes"/"no" values for user-selectable options:
- Tolerance enables (human-readable keys like "5%", "0.5pF")
- Case size / voltage combination enables (keys like "0805/50V")
- Default packaging variant as a simple string variable

*** Database Conventions
- ~source = NULL~ and ~dump_priority = 0~ for generated data
- Booleans as 'Yes'/'No' strings
- Values in SPICE notation (100p, 10n, 1u)
- Timestamps and ~created_by~ (script filename) populated automatically
- Escape single quotes in SQL strings: ~'value''s'~ for ~value's~

*** Field Conventions (from project standards)
- *unique_id*: Format ~{manufacturer}-{mpn}~ (primary key)
- *part_locator*: Functional descriptor for finding equivalent parts, lowercase hyphenated
  - Example: ~cap-mlcc-x7r-100n-10pct-50v-0805~
  - Not unique - multiple manufacturers may share same locator
- *description*: Pattern ~"TYPE MANU SPEC VALUE TOLERANCE PACKAGE"~
- *kicad_footprint*: Use standard library format ~Capacitor_SMD:C_{size}_{metric}Metric~
  - Example: ~Capacitor_SMD:C_0805_2012Metric~
- *kicad_symbol*: Use ~Device:C~ for standard capacitors

** Datasheet Analysis

Extract from the datasheet:
1. MPN structure and encoding rules for each position
2. Code mappings (tolerance, voltage, packaging, etc.)
3. Capacitance ranges per case size and voltage from selection tables
4. Specifications (temperature ranges, dielectric class, compliance)

** Clarifying Questions

Before generating the script, ask the user:

1. *Default tolerances*: Which tolerances should be enabled by default?
   (e.g., "5% and 10%" or "all percentage tolerances")

2. *Default case/voltage coverage*: Which combinations should be enabled?
   (e.g., "common sizes 0402-1210 at 25V/50V/100V" or "all available")

3. *Packaging variant*: What should the default packaging suffix be?
   (e.g., tape-and-reel code, or leave blank for bulk)

4. *Fractional pF values*: Should the script include sub-10pF fractional
   values where available, or only standard E24 values?

5. *URL templates*: What are the manufacturer's URL patterns for:
   - Datasheet link
   - Product page link (with {mpn} placeholder)
   - RoHS certificate link (if available)

6. *Field mappings*: For fields not explicitly in the datasheet:
   - ~dielectric_class~: Use manufacturer's code (e.g., "X7R") or class (e.g., "Class II")?
   - ~cap_type~: Confirm type designation (e.g., "MLCC")
   - ~esr_typ_ohm~: Value available, or leave NULL?

** Output

Generate a complete, runnable Python script that:
- Follows the reference script's patterns and style
- Populates all schema fields appropriately
- Validates with SQLite when run
- Reports generation statistics on completion
```

---

## Notes

- The reference script demonstrates the complete pattern including special capacitance encoding for fractional pF values
- The schema file is authoritative for field names; it may have fields beyond the reference
- Absolute tolerances (±0.1pF, ±0.25pF, ±0.5pF) typically only apply to values < 10pF
- Percentage tolerances typically apply to values ≥ 10pF
- These should be handled as separate generation passes even for the same case/voltage
