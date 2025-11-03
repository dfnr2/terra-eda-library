# Part Generation Scripts

This directory contains scripts for programmatically generating component SQL.

## Example: Resistor Generator

The `resistors_example.py` script demonstrates how to generate a series of resistors.

### Generate INSERT statements (for merging into existing library)

```bash
# Generate 0603 resistors with 1% tolerance
python3 generators/resistors_example.py > temp/resistors_batch.sql

# Generate 0805 resistors with 5% tolerance
python3 generators/resistors_example.py --package 0805 --tolerance 5% > temp/resistors_0805.sql
```

Then merge into existing library:

```bash
# Check for duplicates first
grep "Symbol_Name" db/terra_eda_lib.sql temp/resistors_batch.sql | sort | uniq -d

# If no duplicates, merge
cat temp/resistors_batch.sql >> db/terra_eda_lib.sql

# Rebuild
make
make verify
```

### Generate full library (for creating new library)

```bash
# Generate complete SQL with schema
python3 generators/resistors_example.py --full-library > db/terra_resistors.sql

# Build database
make  # Will automatically build db/terra_resistors.db if library is added to Makefile
```

## Creating Your Own Generator

1. Copy `resistors_example.py` as a template
2. Modify the component-specific data:
   - Specifications dictionary
   - Standard values (if applicable)
   - SQL field mappings
3. Customize the `generate_*_sql()` function
4. Test output before merging

### Template Structure

```python
def generate_component_sql(spec_params):
    """Generate SQL INSERT for your component."""
    symbol_name = f"TYPE {params}"

    return f"""INSERT INTO symbols (
        "Symbol_Name", "Reference", "Value",
        "KiCad_Symbol", "KiCad_Footprint",
        ...
    ) VALUES (
        '{symbol_name}',
        'R',  # Reference designator
        '{value}',
        'terra_eda_lib:{symbol_name}',
        '{footprint}',
        ...
    );"""
```

## Best Practices

1. **Consistent Naming**: Follow pattern `"TYPE MANU SPEC VALUE TOLERANCE PACKAGE"`
2. **Complete Metadata**: Include MPN, Manufacturer, Datasheet when available
3. **SPICE Fields**: Auto-populate for passives (R, L, C)
4. **Validation**: Test generated SQL before merging
5. **Documentation**: Add comments explaining the generation logic

## Common Patterns

### E-Series Values

For resistors and capacitors:

```python
E12_VALUES = ["10", "12", "15", "18", "22", "27", "33", "39", "47", "56", "68", "82"]
E24_VALUES = ["10", "11", "12", "13", "15", "16", "18", "20", "22", "24", "27", "30", ...]
```

### Package Specifications

```python
PACKAGES = {
    "0402": {
        "footprint": "Resistor_SMD:R_0402_1005Metric",
        "power": "0.063W",
        ...
    },
    "0603": {
        "footprint": "Resistor_SMD:R_0603_1608Metric",
        "power": "0.1W",
        ...
    }
}
```

### SQL Escaping

Always escape single quotes:

```python
def sql_escape(s):
    if s is None:
        return "NULL"
    return s.replace("'", "''")
```

## Future Enhancements

- Template system using Jinja2
- CSV import support
- Datasheet parsing
- Automatic MPN lookup from distributor APIs
