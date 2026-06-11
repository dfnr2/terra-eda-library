-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 4
--
-- To create the database, run:
--   sqlite3 output.db < ic_logic_1_migrated.sql
--

-- Create symbols table

BEGIN TRANSACTION;

INSERT INTO ic_logic ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max") VALUES ('Texas Instruments-SN74LVC1G123', 'IC_LOGIC 74LVC1G123', 'SN74LVC1G123', 'Texas Instruments', 'mssop-8', '74LVC1G123', 'Single Retrigerrable Monostabile Multivibrator, Low-Voltage CMOS', 'https://www.ti.com/lit/gpn/sn74lvc1g123', 'https://www.ti.com/product/SN74LVC1G123', 'terra_sym:IC_LOGIC 74LVC1G123', 'Package_SO:MSOP-8_3x3mm_P0.65mm', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'Yes', 'yes', '1.1', 'terra_sym', '100', '8', -40, 125, -65, 150);
INSERT INTO ic_logic ("unique_id", "part_locator", "mpn", "manufacturer", "value", "description", "datasheet", "kicad_symbol", "source", "dump_priority") VALUES ('Texas Instruments-SN74LVC1G123DCU', 'IC_LOGIC 74LVC1G123d', 'SN74LVC1G123DCU', 'Texas Instruments', '74LVC1G123d', 'Single Retrigerrable Monostabile Multivibrator, Low-Voltage CMOS', 'http://www.ti.com/lit/ds/symlink/sn74lvc1g123.pdf', 'terra_sym:IC_LOGIC 74LVC1G123d', 'terra_sym', '100');
INSERT INTO ic_logic ("unique_id", "part_locator", "mpn", "manufacturer", "value", "description", "datasheet", "kicad_symbol", "source", "dump_priority") VALUES ('Texas Instruments-SN74LVC1G139DCU', 'IC_LOGIC 74LVC1G139', 'SN74LVC1G139DCU', 'Texas Instruments', '74LVC1G139', 'Single 2-to-4-line decoder', 'www.ti.com/lit/ds/symlink/sn74lvc1g139.pdf', 'terra_sym:IC_LOGIC 74LVC1G139', 'terra_sym', '100');
INSERT INTO ic_logic ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max") VALUES ('Texas Instrument-SN74LVC1G139', 'IC_LOGIC TI SN74LV1G139 2-to-4 line decoder', 'SN74LVC1G139', 'Texas Instrument', 'SM8', 'SN74LV1G139', 'Single 2-to-4-line decoder', 'https://www.ti.com/lit/gpn/sn74lvc1g139', 'https://www.ti.com/product/SN74LVC1G139?keyMatch=SN74LVC1G139&tisearch=universal_search&usecase=GPN-ALT', 'terra_sym:IC_LOGIC TI SN74LV1G139 2-to-4 line decoder', 'Package_TO_SOT_SMD:SOT-23-5', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0026917336/TXII-E-A0026917336-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'No', 'No', '1.1', 'terra_sym', '100', '5', -40, 125, -65, 150);

COMMIT;
