-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 2
--
-- To create the database, run:
--   sqlite3 output.db < switches_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS switches (
  "unique_id" TEXT PRIMARY KEY,
  "part_locator" TEXT,
  "allow_substitution" TEXT,
  "bom_comment" TEXT,
  "class" TEXT,
  "component_type" TEXT,
  "component_value" TEXT,
  "current_rating" TEXT,
  "datasheet" TEXT,
  "description" TEXT,
  "kicad_footprint" TEXT,
  "manufacturer" TEXT,
  "manufacturer_link" TEXT,
  "mpn" TEXT,
  "composition" TEXT,
  "number_of_pins" TEXT,
  "package" TEXT,
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

INSERT INTO switches ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Broadcom-ASMT-SWB5-NW703', 'LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'No', NULL, NULL, 'LED', 'ASMT-SWB5-NW703', NULL, 'https://docs.broadcom.com/docs/ASMT-SWB5-Nxxxx-DS', 'White SMT LED , PLCC-4 SMT', 'terra_sym:ASMT-SWB5-NW703', 'Broadcom', 'https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/asmt-swb5-nw703', 'ASMT-SWB5-NW703', NULL, NULL, 'SMT', 'LED', 'Yes', 'https://www.mouser.com/catalog/additional/Broadcom_6305_RoHS_Certificate.pdf', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', '-40C/100C', '260C max', '-40C/100C', NULL, NULL, 'No', 'LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO switches ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('CK Components-DF62J12S2AHQAA', 'SW DPDT CK DF62J12S2AHQAA ', 'No', NULL, 'If applicable', 'Switch', 'DPDT rocker', '16A', 'https://www.ckswitches.com/media/1443/df.pdf', 'DPDT rocker, right angle, through-hole', 'terra_sym:DF62J12S2AHQAA', 'CK Components', 'https://www.ckswitches.com/products/switches/product-details/Rocker/DF/DF62J12S2AHQA/', 'DF62J12S2AHQAA', 'If applicable', '4', 'n/a', 'SW', 'Yes', 'https://www.mouser.com/catalog/additional/CK_Components_6111_RoHS_Certificate.pdf', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:SW DPDT CK DF62J12S2AHQAA ', '-20C/85C', 'If applicable', 'If applicable', 'n/a', 'n/a', 'No', 'SW DPDT CK DF62J12S2AHQAA', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
