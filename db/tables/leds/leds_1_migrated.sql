-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 9
--
-- To create the database, run:
--   sqlite3 output.db < leds_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS leds (
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
  "voltage_rating" TEXT,
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

INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Broadcom-HSML-A401-U40M1', 'LED Broadcom Orange, PLCC-4  HSML-A401-U40M1 ', 'No', NULL, NULL, 'LED', 'HSML-A401-U40M1', NULL, 'https://docs.broadcom.com/docs/HSMx-A4xx-xxxxx-SMT-Surface-Mount-LED-Indicator-DS', 'Orange SMT LED , PLCC-4 SMT', 'terra_sym:ASMT-SWB5-NW703', 'Broadcom', 'https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/hsml-a401-u40m1', 'HSML-A401-U40M1', 'AS-AlInGaP', NULL, 'SMT', 'LED', 'Yes', 'https://www.mouser.com/catalog/additional/Broadcom_Limited_6305_RoHS_Certificate.pdf', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:LED Broadcom Orange, PLCC-4  HSML-A401-U40M1 ', '-40C/100C', '260C max', '-40C/100C', NULL, NULL, 'No', 'LED Broadcom Orange, PLCC-4  HSML-A401-U40M1', NULL, NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Broadcom-ASMT-SWB5-NW703', 'LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'No', NULL, NULL, 'LED', 'ASMT-SWB5-NW703', NULL, 'https://docs.broadcom.com/docs/ASMT-SWB5-Nxxxx-DS', 'White SMT LED , PLCC-4 SMT', 'terra_sym:ASMT-SWB5-NW703', 'Broadcom', 'https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/asmt-swb5-nw703', 'ASMT-SWB5-NW703', NULL, NULL, 'SMT', 'LED', 'Yes', 'https://www.mouser.com/catalog/additional/Broadcom_6305_RoHS_Certificate.pdf', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', '-40C/100C', '260C max', '-40C/100C', NULL, NULL, 'No', 'LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', NULL, NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Diodes, Inc-AL8843Q', 'LED DRIVER Diodes Inc AL8843Q', 'No', NULL, NULL, 'IC', 'AL8843Q', NULL, 'https://www.diodes.com/assets/Datasheets/AL8843Q.pdf', 'LED Driver 40V 3A Step-down', 'Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias', 'Diodes, Inc', 'https://www.diodes.com/part/view/AL8843Q/', 'AL8843Q', NULL, '8', 'SO-8EP', 'IC', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/DIOD/DIOD-E-A0004063887/DIOD-E-A0004063887-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:LED DRIVER Diodes Inc AL8843Q', '-40C/150C', '300C', '-65C/150C', NULL, '4%', 'Yes', 'LED DRIVER Diodes Inc AL8843Q', '40V', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Diodes, Inc-IS32LT3954', 'LED DRIVER Lumissil IS32LT3954', 'No', NULL, NULL, 'IC', 'IS32LT3954', NULL, 'http://www.lumissil.com/assets/pdf/core/IS32LT3954_DS.pdf', 'LED Driver 40V 3A Step-down', 'Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm_ThermalVias', 'Diodes, Inc', 'http://www.lumissil.com/home', 'IS32LT3954', NULL, '8', 'SO-8EP', 'IC', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/ISSI/ISSI-E-A0014960646/ISSI-E-A0014960646-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:LED DRIVER Lumissil IS32LT3954', '-40C/125C', '150C-200C, 60-120sec', '-65C/150C', NULL, 'n/a', 'Yes', 'LED DRIVER Lumissil IS32LT3954', '42V', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Texas Instruments-LM3410XMY/NOPB', 'LED DRIVER Texas Instruments LM3410XMY/NOPB', 'No', NULL, NULL, 'IC', 'LM3410XMY/NOPB', NULL, 'https://www.ti.com/lit/gpn/LM3410', 'LED Driver 24V 2.8A constant current w/internal compensation', 'terra_sym:LM3410XMY_NOPB', 'Texas Instruments', 'https://www.ti.com/store/ti/en/p/product/?p=LM3410XMY/NOPB', 'LM3410XMY/NOPB', NULL, '8', 'MSOP Powerpad 8', 'IC', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', NULL, NULL, NULL, NULL, '1.1', 'terra_sym:LED DRIVER Texas Instruments LM3410XMY/NOPB', '-40C/125C', 'standard', NULL, NULL, '20%', 'Yes', 'LED DRIVER Texas Instruments LM3410XMY{slash}NOPB', '10V', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Kingsbright-APHBM2012CGKSYKC', 'LED DUAL APHBM2012CGKSYKC ', 'Yes', NULL, 'n/a', 'LED', 'APHBM2012CGKSYKC', '20 ma', 'https://www.kingbrightusa.com/images/catalog/SPEC/APHBM2012CGKSYKC.pdf', 'Dual Green/Yellow LED, SMD', NULL, 'Kingsbright', 'https://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APHBM2012CGKSYKC', 'APHBM2012CGKSYKC', 'AlGaInP', '4', 'SMD', 'LED', 'Yes', 'https://www.mouser.com/catalog/additional/Kingbright_6040_RoHS_Certificate.pdf', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:LED DUAL APHBM2012CGKSYKC ', '-40C/85C', 'If applicable', 'If applicable', 'n/a', 'n/a', 'No', 'LED DUAL APHBM2012CGKSYKC', NULL, NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Dialight-550-0205F', 'LED Dialight CBI 5mm Green TH', 'Yes', NULL, NULL, 'LED', 'Green', NULL, 'https://s3-us-west-2.amazonaws.com/catsy.557/C17264.pdf', 'CBI 1x1 5mm green LED', 'terra_sym:Dialight-550-series', 'Dialight', 'https://www.dialightsignalsandcomponents.com/550-series-cbi-5mm-1x1-g/#resources-btn', '550-0205F', 'AS-AlInGaP', NULL, 'TH CBI', 'LED', 'Yes', 'https://www.dialightsignalsandcomponents.com/550-series-cbi-5mm-1x1-g/#resources-btn', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:LED Dialight CBI 5mm Green TH', '-40C/100C', '260C max', '-40C/100C', NULL, NULL, 'No', 'Green', NULL, NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Dialight-550-3507F', 'LED Dialight CBI 5mm Green/Red Common Cath TH', 'Yes', NULL, NULL, 'LED', 'Green/Red', NULL, 'https://s3-us-west-2.amazonaws.com/catsy.557/C17264.pdf', 'CBI 1x1 5mm Green/Red Commong Cathode LED', 'terra_sym:Dialight-550-3x07', 'Dialight', 'https://www.dialightsignalsandcomponents.com/550-series-5-mm-cbi-r-g-3-leaded-slope-back-housing/', '550-3507F', 'AS-AlInGaP', NULL, 'TH CBI', 'LED', 'Yes', 'https://www.dialightsignalsandcomponents.com/550-series-5-mm-cbi-r-g-3-leaded-slope-back-housing/', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:LED Dialight CBI 5mm Green/Red Common Cath TH', '-20C/85C', '260C max', '-55C/100C', NULL, NULL, 'No', 'Green/Red', NULL, NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO leds ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "voltage_rating", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Kingbright- APG1608QBC/D ', 'LED Kingbright Blue  SMT 1608  APG1608QBC/D', 'Yes', NULL, NULL, 'LED', 'LED', NULL, 'https://www.kingbrightusa.com/images/catalog/SPEC/APG1608QBC-D.pdf', 'Blue LED  SMT 1608  20mA', 'terra_sym:LED_0603_1608Metric', 'Kingbright', 'http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APG1608QBC/D', ' APG1608QBC/D ', NULL, NULL, '1608', 'LED', 'Yes', 'https://www.mouser.com/catalog/additional/Kingbright_6040_RoHS_Certificate.pdf', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:LED Kingbright Blue  SMT 1608  APG1608QBC/D', '-40C/85C', '260C max', '-40C/85C', NULL, NULL, 'No', 'LED', NULL, NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
