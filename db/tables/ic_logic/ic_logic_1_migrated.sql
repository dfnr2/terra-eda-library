-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 4
--
-- To create the database, run:
--   sqlite3 output.db < ic_logic_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS ic_logic (
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
  "mpn" TEXT,
  "manufacturer" TEXT,
  "manufacturer_link" TEXT,
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

INSERT INTO ic_logic ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "mpn", "manufacturer", "manufacturer_link", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Texas Instruments-SN74LVC1G123', 'IC_LOGIC 74LVC1G123', 'Yes', NULL, 'n/a', 'IC', '74LVC1G123', 'https://www.ti.com/lit/gpn/sn74lvc1g123', 'Single Retrigerrable Monostabile Multivibrator, Low-Voltage CMOS', 'Package_SO:MSOP-8_3x3mm_P0.65mm', 'SN74LVC1G123', 'Texas Instruments', 'https://www.ti.com/product/SN74LVC1G123', 'n/a', '8', 'mssop-8', 'n/a', 'IC', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:IC_LOGIC 74LVC1G123', '-40C/125C', 'If applicable', '-65C/150C', NULL, 'n/a', 'yes', '74LVC1G123', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO ic_logic ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "mpn", "manufacturer", "manufacturer_link", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Texas Instruments-SN74LVC1G123DCU', 'IC_LOGIC 74LVC1G123d', NULL, NULL, NULL, NULL, NULL, 'http://www.ti.com/lit/ds/symlink/sn74lvc1g123.pdf', 'Single Retrigerrable Monostabile Multivibrator, Low-Voltage CMOS', NULL, 'SN74LVC1G123DCU', 'Texas Instruments', NULL, NULL, NULL, NULL, NULL, 'U', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'terra_sym:IC_LOGIC 74LVC1G123d', NULL, NULL, NULL, NULL, NULL, NULL, '74LVC1G123d', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO ic_logic ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "mpn", "manufacturer", "manufacturer_link", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Texas Instruments-SN74LVC1G139DCU', 'IC_LOGIC 74LVC1G139', NULL, NULL, NULL, NULL, NULL, 'www.ti.com/lit/ds/symlink/sn74lvc1g139.pdf', 'Single 2-to-4-line decoder', NULL, 'SN74LVC1G139DCU', 'Texas Instruments', NULL, NULL, NULL, NULL, NULL, 'U', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'terra_sym:IC_LOGIC 74LVC1G139', NULL, NULL, NULL, NULL, NULL, NULL, '74LVC1G139', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO ic_logic ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "mpn", "manufacturer", "manufacturer_link", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Texas Instrument-SN74LVC1G139', 'IC_LOGIC TI SN74LV1G139 2-to-4 line decoder', 'No', NULL, 'n/a', 'Level Shifter', 'SN74LVC1G139', 'https://www.ti.com/lit/gpn/sn74lvc1g139', 'Single 2-to-4-line decoder', 'Package_TO_SOT_SMD:SOT-23-5', 'SN74LVC1G139', 'Texas Instrument', 'https://www.ti.com/product/SN74LVC1G139?keyMatch=SN74LVC1G139&tisearch=universal_search&usecase=GPN-ALT', 'n/a', '5', 'SM8', 'n/a', 'U', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0026917336/TXII-E-A0026917336-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:IC_LOGIC TI SN74LV1G139 2-to-4 line decoder', '-40C/125C', NULL, '-65C/150C', 'n/a', 'n/a', 'No', 'SN74LV1G139', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
