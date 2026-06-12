-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 1
--
-- To create the database, run:
--   sqlite3 output.db < ic_analog_1_migrated.sql
--

-- Create symbols table

BEGIN TRANSACTION;

INSERT INTO ic_analog ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "function_type") VALUES ('Texas Instruments-INA180A2', 'IC_AMP INA180A2', 'INA180A2', 'Texas Instruments', 'SOT-23-5', 'INA180A2', '(type) Value,  params, pkg', 'http://www.ti.com/lit/ds/symlink/ina180.pdf', 'https://www.ti.com/product/INA180', 'terra_sym:IC_AMP INA180A2', 'Package_TO_SOT_SMD:SOT-23-5', 'Yes', 'RoHs Link', 'No', 'No', '1.1', 'terra_sym', '100', '5', -40, 125, 'current sense amplifier');

COMMIT;
