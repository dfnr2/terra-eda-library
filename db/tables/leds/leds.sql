-- Terra EDA Library - leds Table
-- Number of components: 7
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS leds;

CREATE TABLE leds (
            
        part_id TEXT PRIMARY KEY,
        mpn TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        package TEXT,
        value TEXT,
        description TEXT,
        datasheet TEXT,
        manufacturer_link TEXT,
        kicad_symbol TEXT,
        kicad_footprint TEXT,
        altium_symbol TEXT,
        altium_footprint TEXT,
        lifecycle_status TEXT DEFAULT 'Active',
        rohs BOOLEAN DEFAULT TRUE,
        rohs_document_link TEXT,
        allow_substitution BOOLEAN DEFAULT TRUE,
        tracking BOOLEAN DEFAULT FALSE,
        standards_version TEXT DEFAULT 'v1.0',
        bom_comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        sim_model_type TEXT,
        sim_device TEXT,
        sim_pins TEXT,
        sim_model_file TEXT,
        sim_params TEXT
    ,
            color TEXT,
            wavelength TEXT,
            forward_voltage TEXT,
            forward_current TEXT,
            luminous_intensity TEXT,
            viewing_angle TEXT,
            led_type TEXT,
            lens_type TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        );

-- Insert 7 components
BEGIN TRANSACTION;

INSERT INTO leds ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "color", "wavelength", "forward_voltage", "forward_current", "luminous_intensity", "viewing_angle", "led_type", "lens_type", "temp_operating", "temp_storage") VALUES ('LED Broadcom Orange, PLCC-4  HSML-A401-U40M1 ', 'HSML-A401-U40M1', 'Broadcom', 'SMT', 'LED Broadcom Orange, PLCC-4  HSML-A401-U40M1', 'Orange SMT LED , PLCC-4 SMT', 'https://docs.broadcom.com/docs/HSMx-A4xx-xxxxx-SMT-Surface-Mount-LED-Indicator-DS', 'https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/hsml-a401-u40m1', 'terra_sym:LED Broadcom Orange, PLCC-4  HSML-A401-U40M1 ', 'nema:ASMT-SWB5-NW703', NULL, NULL, 'Active', 1, 'https://www.mouser.com/catalog/additional/Broadcom_Limited_6305_RoHS_Certificate.pdf', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380869', '2025-11-11T22:05:47.380871', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'LED', NULL, '-40C/100C', '-40C/100C');
INSERT INTO leds ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "color", "wavelength", "forward_voltage", "forward_current", "luminous_intensity", "viewing_angle", "led_type", "lens_type", "temp_operating", "temp_storage") VALUES ('LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'ASMT-SWB5-NW703', 'Broadcom', 'SMT', 'LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'White SMT LED , PLCC-4 SMT', 'https://docs.broadcom.com/docs/ASMT-SWB5-Nxxxx-DS', 'https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/asmt-swb5-nw703', 'terra_sym:LED Broadcom White, PLCC-4 ASMT-SWB5-NW703', 'nema:ASMT-SWB5-NW703', NULL, NULL, 'Active', 1, 'https://www.mouser.com/catalog/additional/Broadcom_6305_RoHS_Certificate.pdf', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380990', '2025-11-11T22:05:47.380993', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'LED', NULL, '-40C/100C', '-40C/100C');
INSERT INTO leds ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "color", "wavelength", "forward_voltage", "forward_current", "luminous_intensity", "viewing_angle", "led_type", "lens_type", "temp_operating", "temp_storage") VALUES ('LED DUAL APHBM2012CGKSYKC ', 'APHBM2012CGKSYKC', 'Kingsbright', 'SMD', 'LED DUAL APHBM2012CGKSYKC', 'Dual Green/Yellow LED, SMD', 'https://www.kingbrightusa.com/images/catalog/SPEC/APHBM2012CGKSYKC.pdf', 'https://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APHBM2012CGKSYKC', 'terra_sym:LED DUAL APHBM2012CGKSYKC ', NULL, NULL, NULL, 'Active', 1, 'https://www.mouser.com/catalog/additional/Kingbright_6040_RoHS_Certificate.pdf', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.381172', '2025-11-11T22:05:47.381174', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, NULL, NULL, NULL, '20 ma', NULL, NULL, 'LED', NULL, '-40C/85C', 'If applicable');
INSERT INTO leds ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "color", "wavelength", "forward_voltage", "forward_current", "luminous_intensity", "viewing_angle", "led_type", "lens_type", "temp_operating", "temp_storage") VALUES ('LED Dialight CBI 5mm Green TH', '550-0205F', 'Dialight', 'TH CBI', 'Green', 'CBI 1x1 5mm green LED', 'https://s3-us-west-2.amazonaws.com/catsy.557/C17264.pdf', 'https://www.dialightsignalsandcomponents.com/550-series-cbi-5mm-1x1-g/#resources-btn', 'terra_sym:LED Dialight CBI 5mm Green TH', 'nema:Dialight-550-series', NULL, NULL, 'Active', 1, 'https://www.dialightsignalsandcomponents.com/550-series-cbi-5mm-1x1-g/#resources-btn', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.381213', '2025-11-11T22:05:47.381215', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'LED', NULL, '-40C/100C', '-40C/100C');
INSERT INTO leds ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "color", "wavelength", "forward_voltage", "forward_current", "luminous_intensity", "viewing_angle", "led_type", "lens_type", "temp_operating", "temp_storage") VALUES ('LED Dialight CBI 5mm Green/Red Common Cath TH', '550-3507F', 'Dialight', 'TH CBI', 'Green/Red', 'CBI 1x1 5mm Green/Red Commong Cathode LED', 'https://s3-us-west-2.amazonaws.com/catsy.557/C17264.pdf', 'https://www.dialightsignalsandcomponents.com/550-series-5-mm-cbi-r-g-3-leaded-slope-back-housing/', 'terra_sym:LED Dialight CBI 5mm Green/Red Common Cath TH', 'nema:Dialight-550-3x07', NULL, NULL, 'Active', 1, 'https://www.dialightsignalsandcomponents.com/550-series-5-mm-cbi-r-g-3-leaded-slope-back-housing/', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.381251', '2025-11-11T22:05:47.381253', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'LED', NULL, '-20C/85C', '-55C/100C');
INSERT INTO leds ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "color", "wavelength", "forward_voltage", "forward_current", "luminous_intensity", "viewing_angle", "led_type", "lens_type", "temp_operating", "temp_storage") VALUES ('LED Kingbright Blue  SMT 1608  APG1608QBC/D', ' APG1608QBC/D ', 'Kingbright', '1608', 'LED', 'Blue LED  SMT 1608  20mA', 'https://www.kingbrightusa.com/images/catalog/SPEC/APG1608QBC-D.pdf', 'http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APG1608QBC/D', 'terra_sym:LED Kingbright Blue  SMT 1608  APG1608QBC/D', 'nema:LED_0603_1608Metric', NULL, NULL, 'Active', 1, 'https://www.mouser.com/catalog/additional/Kingbright_6040_RoHS_Certificate.pdf', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.381328', '2025-11-11T22:05:47.381330', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'LED', NULL, '-40C/85C', '-40C/85C');
INSERT INTO leds ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "color", "wavelength", "forward_voltage", "forward_current", "luminous_intensity", "viewing_angle", "led_type", "lens_type", "temp_operating", "temp_storage") VALUES ('LED_green_525nm_360mcd_2.9v_5ma_smt_1608', '19-219/GHC-YR2T1B5Y/3T', 'Everlight', '1608', 'LED', 'Blue LED  SMT 1608  20mA', 'https://www.everlighteurope.com/custom/files/datasheets/DSE-0006814.pdf', 'https://www.everlighteurope.com/product-details?id=2934', 'Device:LED', 'nema:LED_0603_1608Metric', NULL, NULL, 'Active', 1, 'https://everlightamericas.com/img/cms/RoHS_Compliance.pdf', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.381289', '2025-11-11T22:05:47.381291', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2.9 V', '5mA', NULL, NULL, 'LED', NULL, '-40C/85C', '-40C/90C');

COMMIT;
