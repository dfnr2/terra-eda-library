-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 2
--
-- To create the database, run:
--   sqlite3 output.db < switches_1_migrated.sql
--

-- Create symbols table

BEGIN TRANSACTION;

INSERT INTO switches ("unique_id", "part_locator", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "sim_device", "sim_pins", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max", "temp_soldering") VALUES ('Broadcom-ASMT-SWB5-NW703', 'LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'ASMT-SWB5-NW703', 'Broadcom', 'SMT', 'LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'White SMT LED , PLCC-4 SMT', 'https://docs.broadcom.com/docs/ASMT-SWB5-Nxxxx-DS', 'https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/asmt-swb5-nw703', 'terra_sym:LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'terra_sym:ASMT-SWB5-NW703', 'Yes', 'https://www.mouser.com/catalog/additional/Broadcom_6305_RoHS_Certificate.pdf', 'No', 'No', '1.1', 'terra_sym', '100', 'L', '1=+ 2=-', -40, 100, -40, 100, 260);
INSERT INTO switches ("unique_id", "part_locator", "mpn", "manufacturer", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "source", "dump_priority", "pin_count", "temp_operating_min", "temp_operating_max", "current_rating") VALUES ('CK Components-DF62J12S2AHQAA', 'SW DPDT CK DF62J12S2AHQAA ', 'DF62J12S2AHQAA', 'CK Components', 'SW DPDT CK DF62J12S2AHQAA', 'DPDT rocker, right angle, through-hole', 'https://www.ckswitches.com/media/1443/df.pdf', 'https://www.ckswitches.com/products/switches/product-details/Rocker/DF/DF62J12S2AHQA/', 'terra_sym:SW DPDT CK DF62J12S2AHQAA ', 'terra_sym:DF62J12S2AHQAA', 'Yes', 'https://www.mouser.com/catalog/additional/CK_Components_6111_RoHS_Certificate.pdf', 'No', 'No', '1.1', 'terra_sym', '100', '4', -20, 85, '16A');

COMMIT;
