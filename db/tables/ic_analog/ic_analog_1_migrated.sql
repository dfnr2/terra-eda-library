-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 1
--
-- To create the database, run:
--   sqlite3 output.db < ic_analog_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS ic_analog (
  "unique_id" TEXT PRIMARY KEY,
  "part_locator" TEXT,
  "allow_substitution" TEXT,
  "bom_comment" TEXT,
  "class" TEXT,
  "component_type" TEXT,
  "component_value" TEXT,
  "datasheet" TEXT,
  "description" TEXT,
  "kicad_footprint" TEXT,
  "manufacturer" TEXT,
  "manufacturer_link" TEXT,
  "mpn" TEXT,
  "composition" TEXT,
  "number_of_pins" TEXT,
  "package" TEXT,
  "power_rating" TEXT,
  "reference" TEXT,
  "rohs" TEXT,
  "rohs_document_link" TEXT,
  "sim_device" TEXT,
  "sim_library" TEXT,
  "sim_pins" TEXT,
  "sim_type" TEXT,
  "standards_version" TEXT,
  "kicad_symbol" TEXT,
  "temp_operating" TEXT,
  "temp_soldering" TEXT,
  "temp_storage" TEXT,
  "temp_coeff" TEXT,
  "tolerance" TEXT,
  "tracking" TEXT,
  "value" TEXT,
  "altium_footprint" TEXT,
  "altium_symbol" TEXT,
  "variant" TEXT,
  "source" TEXT,
  "dump_priority" INTEGER,
    "tier" INTEGER DEFAULT 5,
    "tags" TEXT DEFAULT '',
    "lifecycle_status" TEXT DEFAULT 'Active',
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "created_by" TEXT,
    "sim_model_type" TEXT,
    "sim_model_file" TEXT,
    "sim_params" TEXT
);

-- Insert symbols
BEGIN TRANSACTION;

INSERT INTO ic_analog ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Texas Instruments-INA180A2', 'IC_AMP INA180A2', 'No', NULL, 'If applicable', 'Current sens amplifier', 'INA180A2', 'http://www.ti.com/lit/ds/symlink/ina180.pdf', '(type) Value,  params, pkg', 'Package_TO_SOT_SMD:SOT-23-5', 'Texas Instruments', 'https://www.ti.com/product/INA180', 'INA180A2', 'n/a', '5', 'SOT-23-5', 'n/a', 'IC', 'Yes', 'RoHs Link', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:IC_AMP INA180A2', '-40C/125C', 'If applicable', 'If applicable', 'n/a', 'n/a', 'No', 'INA180A2', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
