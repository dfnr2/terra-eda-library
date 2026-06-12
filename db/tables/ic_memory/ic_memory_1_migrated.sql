-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 1
--
-- To create the database, run:
--   sqlite3 output.db < ic_memory_1_migrated.sql
--

-- Create symbols table

BEGIN TRANSACTION;

INSERT INTO ic_memory ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max", "memory_type") VALUES ('Microchip- 24LC32AT-I/OT', 'IC_MEMORY EEPROM Microchip 24LC32A 4kx8 SOT-23-5', ' 24LC32AT-I/OT', 'Microchip', 'SOT-23-5', '4k x 8 EEPROM', 'EEPROM 4k x 8 I2C SOT-23-5', 'https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/24AA32A-24LC32A-32-Kbit-I2C-Serial-EEPROM-DS20001713.pdf', 'https://www.microchip.com/en-us/product/24lc32a', 'terra_sym:IC_MEMORY EEPROM Microchip 24LC32A 4kx8 SOT-23-5', 'terra_sym:SOT95P270X145-5N', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'Yes', 'No', '1.1', 'terra_sym', '100', '5', -40, 85, -40, 85, 'EEPROM');

COMMIT;
