-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 2
--
-- To create the database, run:
--   sqlite3 output.db < ic_microcontrollers_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS ic_microcontrollers (
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
    "tags" TEXT DEFAULT ''
);

-- Insert symbols
BEGIN TRANSACTION;

INSERT INTO ic_microcontrollers ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Microchip-ATSAMC20E18A', 'IC_MCU ATSAMC20E18A-AUT 256 KB 5V TQFP-32', 'Yes', NULL, 'If applicable', 'Microcontroller', 'ATSAMC20E18A', 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAMC20_C21_Family_Data_Sheet_DS60001479D.pdf', 'Arm MCU, 5V, 256KB, TQFP-32', 'Package_QFP:TQFP-32_7x7mm_P0.8mm', 'Microchip', 'https://www.microchip.com/en-us/product/atsamc20e18a', 'ATSAMC20E18A', 'If applicable', '32', 'TQFP-32', 'If applicable', 'U', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:IC_MCU ATSAMC20E18A-AUT 256 KB 5V TQFP-32', '-40C/85C', NULL, '-60C/150C', 'If applicable', 'If applicable', 'Yes', 'ATSAMC20E18A', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO ic_microcontrollers ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Microchip-ATSAMC20G18A', 'IC_MCU ATSAMC20G18A-AUT 256 KB 5V TQFP-48', 'Yes', NULL, 'na', 'Microcontroller', 'ATSAMC20G18A', 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAMC20_C21_Family_Data_Sheet_DS60001479D.pdf', 'Arm MCU, 5V, 256KB, TQFP-48', 'Package_QFP:TQFP-48_7x7mm_P0.5mm', 'Microchip', 'https://www.microchip.com/en-us/product/atsamc20g18a', 'ATSAMC20G18A', 'na', '48', 'TQFP-48', 'na', 'U', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:IC_MCU ATSAMC20G18A-AUT 256 KB 5V TQFP-48', '-40C/85C', NULL, '-60C/150C', 'na', 'If applicable', 'Yes', 'ATSAMC20G18A', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
