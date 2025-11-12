-- Terra EDA Library - mosfet Table
-- Number of components: 3
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS mosfet;

CREATE TABLE mosfet (
    -- Core fields
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
    sim_params TEXT,
    -- MOSFET-specific fields
    mosfet_type TEXT,        -- 'N-Channel', 'P-Channel'
    vds_max TEXT,
    vgs_max TEXT,
    vgs_th_min TEXT,
    vgs_th_typ TEXT,
    vgs_th_max TEXT,
    id_max TEXT,
    rds_on_typ TEXT,
    rds_on_max TEXT,
    qg_typ TEXT,             -- Total gate charge
    qgs_typ TEXT,            -- Gate-source charge
    qgd_typ TEXT,            -- Gate-drain charge
    ciss_typ TEXT,           -- Input capacitance
    coss_typ TEXT,           -- Output capacitance
    crss_typ TEXT,           -- Reverse transfer capacitance
    power_dissipation TEXT,
    temp_operating TEXT,
    temp_storage TEXT,
    temp_junction_max TEXT
);

-- Insert 3 components
BEGIN TRANSACTION;

INSERT INTO mosfet ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "mosfet_type", "vds_max", "vgs_max", "vgs_th_min", "vgs_th_typ", "vgs_th_max", "id_max", "rds_on_typ", "rds_on_max", "qg_typ", "qgs_typ", "qgd_typ", "ciss_typ", "coss_typ", "crss_typ", "power_dissipation", "temp_operating", "temp_storage", "temp_junction_max") VALUES ('FET DRIVER DUAL SZNUD3124DMT1G', ' SZNUD3124DMT1G', 'ON Semi', NULL, 'FET DRIVER DUAL SZNUD3124DMT1G', 'Dual MOSFET Relay driver SMT', 'https://www.onsemi.com/download/data-sheet/pdf/nud3124-d.pdf', 'https://www.onsemi.com/products/motor-control/motor-drivers/load-drivers-relay-drivers/nud3124', 'terra_sym:FET DRIVER DUAL SZNUD3124DMT1G', 'nema:SC-74-6_1.5x2.9mm_P0.95mm', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/ONSM/ONSM-E-A0015053231/ONSM-E-A0015053231-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.379556', '2025-11-11T22:05:47.379558', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/125C', 'If applicable', NULL);
INSERT INTO mosfet ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "mosfet_type", "vds_max", "vgs_max", "vgs_th_min", "vgs_th_typ", "vgs_th_max", "id_max", "rds_on_typ", "rds_on_max", "qg_typ", "qgs_typ", "qgd_typ", "ciss_typ", "coss_typ", "crss_typ", "power_dissipation", "temp_operating", "temp_storage", "temp_junction_max") VALUES ('MOSFET DMP3099L P-channel 30V 3.8A', 'DMP3099L', 'Diodes, Inc.', 'SOT-23', 'DMP3099L-7', 'P Channel MOSFET, 30V 3.8A SOT-23', 'https://www.diodes.com/assets/Datasheets/DMP3099L.pdf', 'https://www.diodes.com/part/view/DMP3099L', 'terra_sym:MOSFET DMP3099L P-channel 30V 3.8A', 'Package_TO_SOT_SMD:SOT-23', NULL, NULL, 'Active', 1, 'RoHs Link', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.381524', '2025-11-11T22:05:47.381526', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-55C/150C', '-55C/150C', NULL);
INSERT INTO mosfet ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "mosfet_type", "vds_max", "vgs_max", "vgs_th_min", "vgs_th_typ", "vgs_th_max", "id_max", "rds_on_typ", "rds_on_max", "qg_typ", "qgs_typ", "qgd_typ", "ciss_typ", "coss_typ", "crss_typ", "power_dissipation", "temp_operating", "temp_storage", "temp_junction_max") VALUES ('MOSFET Infineon IRLM2502 N-channel 4.2A 20V', 'IRLM2502TRPBF', 'Infineon', 'SOT-23', 'IRLML2502', 'N Channel MOSFET, 30V 3.8A SOT-23', 'https://www.infineon.com/dgdl/Infineon-IRLML2502-DataSheet-v01_01-EN.pdf?fileId=5546d462533600a401535668048e2606', 'https://www.infineon.com/cms/en/product/power/mosfet/n-channel/irlml2502/', 'terra_sym:MOSFET Infineon IRLM2502 N-channel 4.2A 20V', 'Package_TO_SOT_SMD:SOT-23', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/INFN/INFN-E-A0005477335/INFN-E-A0005477335-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.381557', '2025-11-11T22:05:47.381559', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-55C/150C', '-55C/150C', NULL);

COMMIT;
