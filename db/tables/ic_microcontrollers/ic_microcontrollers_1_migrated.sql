-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 2
--
-- To create the database, run:
--   sqlite3 output.db < ic_microcontrollers_1_migrated.sql
--

-- Create symbols table

BEGIN TRANSACTION;

INSERT INTO ic_microcontrollers ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max") VALUES ('Microchip-ATSAMC20E18A', 'IC_MCU ATSAMC20E18A-AUT 256 KB 5V TQFP-32', 'ATSAMC20E18A', 'Microchip', 'TQFP-32', 'ATSAMC20E18A', 'Arm MCU, 5V, 256KB, TQFP-32', 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAMC20_C21_Family_Data_Sheet_DS60001479D.pdf', 'https://www.microchip.com/en-us/product/atsamc20e18a', 'terra_sym:IC_MCU ATSAMC20E18A-AUT 256 KB 5V TQFP-32', 'Package_QFP:TQFP-32_7x7mm_P0.8mm', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'Yes', 'Yes', '1.1', 'terra_sym', '100', '32', -40, 85, -60, 150);
INSERT INTO ic_microcontrollers ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max") VALUES ('Microchip-ATSAMC20G18A', 'IC_MCU ATSAMC20G18A-AUT 256 KB 5V TQFP-48', 'ATSAMC20G18A', 'Microchip', 'TQFP-48', 'ATSAMC20G18A', 'Arm MCU, 5V, 256KB, TQFP-48', 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAMC20_C21_Family_Data_Sheet_DS60001479D.pdf', 'https://www.microchip.com/en-us/product/atsamc20g18a', 'terra_sym:IC_MCU ATSAMC20G18A-AUT 256 KB 5V TQFP-48', 'Package_QFP:TQFP-48_7x7mm_P0.5mm', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'Yes', 'Yes', '1.1', 'terra_sym', '100', '48', -40, 85, -60, 150);

COMMIT;
