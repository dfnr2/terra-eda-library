-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 1
--
-- To create the database, run:
--   sqlite3 output.db < ic_opamp_1_migrated.sql
--

-- Create symbols table

BEGIN TRANSACTION;

INSERT INTO ic_opamp ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max") VALUES ('Texas Instruments-TL081HIDBVR', 'IC_OPAMP TI TL081HDBVR Single FET input opamp, In to V+, SOT-23-5', 'TL081HIDBVR', 'Texas Instruments', 'SOT-23-5', 'TL081H', 'Single FET input opamp, 40-V, 5.25-MHz, In to V+, SOT-23-5', 'https://www.ti.com/lit/gpn/tl081h', 'https://www.ti.com/product/TL081H#product-details', 'terra_sym:IC_OPAMP TI TL081HDBVR Single FET input opamp, In to V+, SOT-23-5', 'Package_TO_SOT_SMD:SOT-23-5', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'Yes', 'No', '1.1', 'terra_sym', '100', '5', -40, 125, -40, 125);

COMMIT;
