-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 9
--
-- To create the database, run:
--   sqlite3 output.db < diodes_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS diodes (
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

INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Diodes, Inc.-MMBD914-7-F', 'DIODE MMBD914 small signal switching diode SMT SOT23', 'Yes', NULL, 'If applicable', 'Diode', 'MMBD914', NULL, 'https://www.diodes.com/assets/Datasheets/BAS16_MMBD4148_MMBD914.pdf', 'DIODE SMT/TH 1n914/mmbd914 generic switching', 'Package_TO_SOT_SMD:SOT-23', 'Diodes, Inc.', 'https://www.diodes.com/part/view/MMBD914', 'MMBD914-7-F', 'If applicable', '3', 'SOT23', '350 mW / 200 mA', 'D', 'Yes', 'https://www.diodes.com/assets/Quality-Reliability-Docs/Master_CofC.pdf', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE MMBD914 small signal switching diode SMT SOT23', '-65C/150C', 'If applicable', 'If applicable', 'If applicable', 'na', 'No', 'MMBD914', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Nexperia-PNE20020ER', 'DIODE Nexperia PNE20020ERX 200V 2.8A Fast Recovery SOD123', 'Yes', NULL, 'If applicable', 'Diode', '200V 2.8A', '2A', 'https://assets.nexperia.com/documents/data-sheet/PNE20020ER.pdf', 'General Purpose DIode, fast recovery, Vf 400V, Iav 2A', 'terra_sym:Nexperia SOD-123W', 'Nexperia', 'https://www.nexperia.com/products/diodes/recovery-rectifiers/PNE20020ER.html', 'PNE20020ER', 'If applicable', '2', 'SOD123W', NULL, 'D', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/RECT/RECT-E-A0007327236/RECT-E-A0007327236-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE Nexperia PNE20020ERX 200V 2.8A Fast Recovery SOD123', '-55C/150C', NULL, '-55C/150C', NULL, 'n/a', 'No', '200V 2.8A', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('OnSemi-MBR0530T1G', 'DIODE OnSemi Schottky 30V 0.5A SOD-123 MBR0530', 'Yes', NULL, 'If applicable', 'Schottky Diode', '30V 0.5A', NULL, 'https://www.onsemi.com/pdf/datasheet/mbr0530t1-d.pdf', '30V 0.5A Schottky Power Rectifier Diode', 'Diode_SMD:D_SOD-123', 'OnSemi', 'https://www.onsemi.com/products/discrete-power-modules/schottky-diodes-schottky-rectifiers/mbr0530', 'MBR0530T1G', 'If applicable', NULL, 'SOD-123', 'If applicable', 'D', 'Yes', 'https://www.mouser.com/catalog/additional/On_Semiconductor_5121_RoHS_Certificate.pdf', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE OnSemi Schottky 30V 0.5A SOD-123 MBR0530', '-65C/+125C', 'If applicable', '-65C/+150C', 'If applicable', 'n/a', 'No', 'DIODE OnSemi Schottky 30V 0.5A SOD-123 MBR0530', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('ROHM-RFN10TB4SNZC9', 'DIODE ROHM RFN10TB4SNZC9 430V 10A', 'Yes', NULL, 'If applicable', 'Diode', '10A 430V', '10 Avg', 'RFN10TB4SNZC9', 'General Purpose DIode, fast recovery, Vf 430V, Iav 10A', 'Package_TO_SOT_THT:TO-220-2_Vertical', 'ROHM', 'https://www.rohm.com/products/diodes/fast-recovery-diodes/standard/rfn10tb4snz-product', 'RFN10TB4SNZC9', 'If applicable', '2', 'TO-220FN-2', NULL, 'D', 'Yes', 'https://fscdn.rohm.com/en/techdata_basic/diode/rohs-elv/ROHS_ELV_Diode-e.pdf', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE ROHM RFN10TB4SNZC9 430V 10A', '150C', NULL, '-55C/150C', NULL, 'If applicable', 'No', '_TEMPLATE MANUF [VALUE] [PARAMS] [PKG] [MPN]', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Rectron-FR204-B', 'DIODE Rectron  FR204-B 400V 2A Fast Recovery', 'Yes', NULL, 'If applicable', 'Diode', '400V 2A', '2A', 'https://www.rectron.com/public/product_datasheets/fr201-fr207.pdf', 'General Purpose DIode, fast recovery, Vf 400V, Iav 2A', 'Diode_THT:D_DO-15_P10.16mm_Horizontal', 'Rectron', 'https://www.rectron.com/category/4/50', 'FR204-B', 'If applicable', '2', 'DO-15', NULL, 'D', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/RECT/RECT-E-A0007327236/RECT-E-A0007327236-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE Rectron  FR204-B 400V 2A Fast Recovery', '-55C/150C', NULL, '-55C/150C', NULL, 'n/a', 'No', '400V 2A', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Vishay-VSSAF510-M3/H', 'DIODE Vishay VSSAF510  Schottky 5A', 'Yes', NULL, 'If applicable', 'Schottky Diode', 'VSSAF510', NULL, 'https://www.vishay.com/docs/87610/vssaf510.pdf', '100V 5A Schottky Power Rectifier Diode', 'terra_sym:Vishay_SlimSMA_D_DO-221AC', 'Vishay', 'https://www.vishay.com/en/product/87610/', 'VSSAF510-M3/H', 'If applicable', NULL, 'SMA (DO-214AC)', 'If applicable', 'D', 'Yes', 'https://www.vishay.com/en/how/leadfree/#summary', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE Vishay VSSAF510  Schottky 5A', '-65C/+150C', 'If applicable', '-65C/+150C', 'If applicable', 'n/a', 'No', 'VSSAF510', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Vishay-VSSAF512', 'DIODE Vishay VSSAF512  Schottky 5A', 'Yes', NULL, 'If applicable', 'Schottky Diode', 'VSSAF512', NULL, 'https://www.vishay.com/docs/87611/vssaf512.pdf', '120V 5A Schottky Power Rectifier Diode', 'terra_sym:Vishay_SlimSMA_D_DO-221AC', 'Vishay', 'https://www.vishay.com/en/product/87611/', 'VSSAF512', 'If applicable', NULL, 'SMA (DO-214AC)', 'If applicable', 'D', 'Yes', 'https://www.vishay.com/en/how/leadfree/#summary', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE Vishay VSSAF512  Schottky 5A', '-65C/+150C', 'If applicable', '-65C/+150C', 'If applicable', 'n/a', 'No', 'VSSAF512', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Vishay-VSSB410S', 'DIODE Vishay VSSB410S Schottky 4A', 'Yes', NULL, 'If applicable', 'Schottky Diode', 'VSSB410S', NULL, 'https://www.vishay.com/docs/89140/vssb410s-e3.pdf', '100V 4A Schottky Power Rectifier Diode', 'Diode_SMD:D_SMB', 'Vishay', 'https://www.vishay.com/en/product/89140/', 'VSSB410S', 'If applicable', NULL, 'SMB (DO-214AA)', 'If applicable', 'D', 'Yes', 'https://www.vishay.com/en/how/leadfree/#summary', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:DIODE Vishay VSSB410S Schottky 4A', '-65C/+150C', 'If applicable', '-65C/+150C', 'If applicable', 'n/a', 'No', 'VSSB410S', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO diodes ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "power_rating", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Unknown-UNKNOWN', 'DIODE_ARRAY PESD3V3L4UW', NULL, NULL, NULL, NULL, NULL, NULL, 'https://assets.nexperia.com/documents/data-sheet/PESDXL4UF_G_W.pdf', 'Low capacitance unidirectional quadruple ESD protection diode array, 3.3V, Common Anode, SOT-665', 'Package_TO_SOT_SMD:SOT-665', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'D', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'terra_sym:DIODE_ARRAY PESD3V3L4UW', NULL, NULL, NULL, NULL, NULL, NULL, 'PESD3V3L4UW', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
