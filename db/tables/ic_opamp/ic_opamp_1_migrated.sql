-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 1
--
-- To create the database, run:
--   sqlite3 output.db < ic_opamp_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS ic_opamp (
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
  "dump_priority" INTEGER
);

-- Insert symbols
BEGIN TRANSACTION;

INSERT INTO ic_opamp ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Texas Instruments-TL081HIDBVR', 'IC_OPAMP TI TL081HDBVR Single FET input opamp, In to V+, SOT-23-5', 'Yes', NULL, 'na', 'Op Amp', 'TL081H', 'https://www.ti.com/lit/gpn/tl081h', 'Single FET input opamp, 40-V, 5.25-MHz, In to V+, SOT-23-5', 'Package_TO_SOT_SMD:SOT-23-5', 'Texas Instruments', 'https://www.ti.com/product/TL081H#product-details', 'TL081HIDBVR', 'na', '5', 'SOT-23-5', 'na', 'U', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:IC_OPAMP TI TL081HDBVR Single FET input opamp, In to V+, SOT-23-5', '-40C/125C', NULL, '-40C/125C', 'na', 'na', 'No', 'TL081H', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
