-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 4
--
-- To create the database, run:
--   sqlite3 output.db < ferrites_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS ferrites (
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

INSERT INTO ferrites ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Bourns- MH2029-800Y', 'FERRITE Bourns  MH2029-800Y 80 ohm 3A', 'No', NULL, 'If applicable', 'Ferrite', '80 ohm@100 MHz, 3A', 'https://www.bourns.com/data/global/pdfs/mh.pdf', 'Ferrite Bead, 80 ohm@100MHz, 3A', 'Inductor_SMD:L_0805_2012Metric', 'Bourns', 'https://www.bourns.com', ' MH2029-800Y', 'If applicable', '2', '0805', 'If applicable', 'FB', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/BOUR/BOUR-E-A0004886223/BOUR-E-A0004886223-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:FERRITE Bourns  MH2029-800Y 80 ohm 3A', '-55C/150C', '230C @ 50 sec', '-55C/150C', 'If applicable', '25%', 'No', 'FB Bourns  MH2029-800Y 80 ohm 3A', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO ferrites ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Murata-BLM18EG121SN1D', 'FERRITE Murata Ferrite Bead 120 ohm 2000 mA 0603 BLM18EG121SN1D  ', 'No', NULL, 'If applicable', 'Ferrite Bead', '120 ohm @ 100 MHz', 'https://www.murata.com/products/productdata/8796747366430/ENFA0021.pdf?1730777412000', 'Ferrite Bead 120ohm@100 MHz, Imax=300 mA', 'Inductor_SMD:L_0603_1608Metric', 'Murata', 'https://www.murata.com/en-us/products/productdetail?partno=BLM18EG121SN1%23', 'BLM18EG121SN1D', 'If applicable', 'If applicable', '0603', 'If applicable', 'FB', 'Yes', 'https://www.murata.com/-/media/webrenewal/products/emc/emifil/certificate/r-eu-rohs-certificate-emi-emifil.ashx?la=en&cvid=20230801061916000000', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:FERRITE Murata Ferrite Bead 120 ohm 2000 mA 0603 BLM18EG121SN1D  ', '-55C / +125C', '270C (preheat 170C)', 'If applicable', 'If applicable', 'If applicable', 'No', 'CHOKE Murata Ferrite Bead 120 ohm 2000 mA 0603 BLM18EG121SN1D', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO ferrites ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Murata-BLM18BD221SN1D ', 'FERRITE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D ', 'No', NULL, 'If applicable', 'Ferrite Bead', '220 ohm @ 100 MHz', 'https://www.murata.com/products/productdata/8796738650142/ENFA0003.pdf?1636515039000', 'Ferrite Bead 220ohm@100 MHz, Imax=300 mA', 'Inductor_SMD:L_0603_1608Metric', 'Murata', 'https://www.murata.com/en-global/products/productdetail?partno=BLM18BD221SN1%23', 'BLM18BD221SN1D ', 'If applicable', 'If applicable', '0603', 'If applicable', 'FB', 'Yes', 'https://www.mouser.com/catalog/additional/Murata_BL_DL_PLT10_DX_NF_BNX02_RoHS_Certificate.pdf', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:FERRITE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D ', '-55C / +125C', '270C (preheat 170C)', 'If applicable', 'If applicable', 'If applicable', 'No', 'CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO ferrites ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Murata- BLM41PG600SN1L', 'FERRITE Murata Ferrite Bead 60 ohm 6A 1806 BLM41PG600SN1L', 'No', NULL, 'If applicable', 'Ferrite Bead', '60 ohm @ 100 MHz', 'https://www.murata.com/en-us/products/productdata/8796739862558/ENFA0007.pdf', 'Ferrite Bead 60ohm@100 MHz, Imax=6A', 'Inductor_SMD:L_1806_4516Metric_Pad1.45x1.90mm_HandSolder', 'Murata', 'https://pim.murata.com/en-us/pim/details/?partNum=BLM41PG600SN1%23', ' BLM41PG600SN1L', 'If applicable', '2', '1806', 'If applicable', 'FB', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/MURE/MURE-E-A0026527192/MURE-E-A0026527192-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:FERRITE Murata Ferrite Bead 60 ohm 6A 1806 BLM41PG600SN1L', '-55C / +125C', '270C (preheat 170C)', 'If applicable', 'If applicable', '25%', 'No', 'CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
