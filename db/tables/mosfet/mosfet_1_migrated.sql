-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 3
--
-- To create the database, run:
--   sqlite3 output.db < mosfet_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS mosfet (
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

INSERT INTO mosfet ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Infineon-BTS5030-1EJA', 'IC_SSR Infineon BTS5030-1EJA MOSFET high-side switch 30 mOhm 5A 28V DSO-8', 'No', NULL, 'na', 'MOSFET Switch', 'BTS5030', 'https://www.infineon.com/dgdl/Infineon-BTS5030-1EJA-DS-v02_20-EN.pdf?fileId=5546d46259d9a4bf015a84f3e686758a', 'Smart High-Side Power Switch, PROFET, Single, 30mOhm, 5A, 28V, DSO-8', 'Package_SO:Infineon_PG-DSO-8-43', 'Infineon', 'https://www.infineon.com/cms/en/product/power/smart-power-switches/high-side-switches/profet-plus-12v-automotive-smart-high-side-switch/bts5030-1eja/', 'BTS5030-1EJA', 'na', '9', 'DSO-8-EP', '28V 5A', 'U', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/INFN/INFN-E-A0005477335/INFN-E-A0005477335-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:IC_SSR Infineon BTS5030-1EJA MOSFET high-side switch 30 mOhm 5A 28V DSO-8', '-40C/150C', NULL, '-55C/150C', 'na', 'na', 'No', 'BTS5030', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO mosfet ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Diodes, Inc.-DMP3099L', 'MOSFET DMP3099L P-channel 30V 3.8A', 'Yes', NULL, 'na', 'MOSFET', 'DMP3099L', 'https://www.diodes.com/assets/Datasheets/DMP3099L.pdf', 'P Channel MOSFET, 30V 3.8A SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Diodes, Inc.', 'https://www.diodes.com/part/view/DMP3099L', 'DMP3099L', 'na', '3', 'SOT-23', '30V, 3.8A', 'Q', 'Yes', 'RoHs Link', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:MOSFET DMP3099L P-channel 30V 3.8A', '-55C/150C', 'f applicable', '-55C/150C', 'na', 'na', 'No', 'DMP3099L-7', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO mosfet ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Infineon-IRLM2502TRPBF', 'MOSFET Infineon IRLM2502 N-channel 4.2A 20V', 'Yes', NULL, 'na', 'MOSFET', 'IRLML2502', 'https://www.infineon.com/dgdl/Infineon-IRLML2502-DataSheet-v01_01-EN.pdf?fileId=5546d462533600a401535668048e2606', 'N Channel MOSFET, 30V 3.8A SOT-23', 'Package_TO_SOT_SMD:SOT-23', 'Infineon', 'https://www.infineon.com/cms/en/product/power/mosfet/n-channel/irlml2502/', 'IRLM2502TRPBF', 'na', '3', 'SOT-23', '20V, 4.2A', 'Q', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/INFN/INFN-E-A0005477335/INFN-E-A0005477335-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:MOSFET Infineon IRLM2502 N-channel 4.2A 20V', '-55C/150C', NULL, '-55C/150C', 'na', 'na', 'No', 'IRLML2502', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
