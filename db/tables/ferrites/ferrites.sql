-- Terra EDA Library - ferrites Table
-- Number of components: 4
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS ferrites;

CREATE TABLE ferrites (
            
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
            impedance_at_freq TEXT,
            test_frequency TEXT,
            dc_resistance TEXT,
            current_rating TEXT,
            tolerance TEXT,
            ferrite_type TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        );

-- Insert 4 components
BEGIN TRANSACTION;

INSERT INTO ferrites ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "impedance_at_freq", "test_frequency", "dc_resistance", "current_rating", "tolerance", "ferrite_type", "temp_operating", "temp_storage") VALUES ('CHOKE Murata Ferrite Bead 120 ohm 2000 mA 0603 BLM18EG121SN1D  ', 'BLM18EG121SN1D', 'Murata', '0603', 'CHOKE Murata Ferrite Bead 120 ohm 2000 mA 0603 BLM18EG121SN1D', 'Ferrite Bead 120ohm@100 MHz, Imax=300 mA', 'https://www.murata.com/products/productdata/8796747366430/ENFA0021.pdf?1730777412000', 'https://www.murata.com/en-us/products/productdetail?partno=BLM18EG121SN1%23', 'terra_sym:CHOKE Murata Ferrite Bead 120 ohm 2000 mA 0603 BLM18EG121SN1D  ', 'Inductor_SMD:L_0603_1608Metric', NULL, NULL, 'Active', 1, 'https://www.murata.com/-/media/webrenewal/products/emc/emifil/certificate/r-eu-rohs-certificate-emi-emifil.ashx?la=en&cvid=20230801061916000000', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.378022', '2025-11-11T22:05:47.378024', 'migration_script', NULL, NULL, NULL, NULL, NULL, 'CHOKE Murata Ferrite Bead 120 ohm 2000 mA 0603 BLM18EG121SN1D', NULL, NULL, NULL, 'If applicable', 'Ferrite Bead', '-55C / +125C', 'If applicable');
INSERT INTO ferrites ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "impedance_at_freq", "test_frequency", "dc_resistance", "current_rating", "tolerance", "ferrite_type", "temp_operating", "temp_storage") VALUES ('CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D ', 'BLM18BD221SN1D ', 'Murata', '0603', 'CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D', 'Ferrite Bead 220ohm@100 MHz, Imax=300 mA', 'https://www.murata.com/products/productdata/8796738650142/ENFA0003.pdf?1636515039000', 'https://www.murata.com/en-global/products/productdetail?partno=BLM18BD221SN1%23', 'terra_sym:CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D ', 'Inductor_SMD:L_0603_1608Metric', NULL, NULL, 'Active', 1, 'https://www.mouser.com/catalog/additional/Murata_BL_DL_PLT10_DX_NF_BNX02_RoHS_Certificate.pdf', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.378120', '2025-11-11T22:05:47.378122', 'migration_script', NULL, NULL, NULL, NULL, NULL, 'CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D', NULL, NULL, NULL, 'If applicable', 'Ferrite Bead', '-55C / +125C', 'If applicable');
INSERT INTO ferrites ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "impedance_at_freq", "test_frequency", "dc_resistance", "current_rating", "tolerance", "ferrite_type", "temp_operating", "temp_storage") VALUES ('CHOKE Murata Ferrite Bead 60 ohm 6A 1806 BLM41PG600SN1L', ' BLM41PG600SN1L', 'Murata', '1806', 'CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D', 'Ferrite Bead 60ohm@100 MHz, Imax=6A', 'https://www.murata.com/en-us/products/productdata/8796739862558/ENFA0007.pdf', 'https://pim.murata.com/en-us/pim/details/?partNum=BLM41PG600SN1%23', 'terra_sym:CHOKE Murata Ferrite Bead 60 ohm 6A 1806 BLM41PG600SN1L', 'Inductor_SMD:L_1806_4516Metric_Pad1.45x1.90mm_HandSolder', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/MURE/MURE-E-A0026527192/MURE-E-A0026527192-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.378153', '2025-11-11T22:05:47.378155', 'migration_script', NULL, NULL, NULL, NULL, NULL, 'CHOKE Murata Ferrite Bead 220 ohm 300 mA 0603 BLM18BD221SN1D', NULL, NULL, NULL, '25%', 'Ferrite Bead', '-55C / +125C', 'If applicable');
INSERT INTO ferrites ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "impedance_at_freq", "test_frequency", "dc_resistance", "current_rating", "tolerance", "ferrite_type", "temp_operating", "temp_storage") VALUES ('FB Bourns  MH2029-800Y 80 ohm 3A', ' MH2029-800Y', 'Bourns', '0805', 'FB Bourns  MH2029-800Y 80 ohm 3A', 'Ferrite Bead, 80 ohm@100MHz, 3A', 'https://www.bourns.com/data/global/pdfs/mh.pdf', 'https://www.bourns.com', 'terra_sym:FB Bourns  MH2029-800Y 80 ohm 3A', 'Inductor_SMD:L_0805_2012Metric', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/BOUR/BOUR-E-A0004886223/BOUR-E-A0004886223-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.379526', '2025-11-11T22:05:47.379527', 'migration_script', NULL, NULL, NULL, NULL, NULL, 'FB Bourns  MH2029-800Y 80 ohm 3A', NULL, NULL, NULL, '25%', 'Ferrite', '-55C/150C', '-55C/150C');

COMMIT;
