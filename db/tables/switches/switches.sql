-- Terra EDA Library - switches Table
-- Number of components: 1
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS switches;

CREATE TABLE switches (
            
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
            switch_type TEXT,
            poles INTEGER,
            throw INTEGER,
            circuit_config TEXT,
            actuation_force TEXT,
            travel_distance TEXT,
            mounting_type TEXT,
            orientation TEXT,
            current_rating TEXT,
            voltage_rating TEXT,
            mechanical_life INTEGER,
            temp_operating TEXT,
            temp_storage TEXT
        );

-- Insert 1 components
BEGIN TRANSACTION;

INSERT INTO switches ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "switch_type", "poles", "throw", "circuit_config", "actuation_force", "travel_distance", "mounting_type", "orientation", "current_rating", "voltage_rating", "mechanical_life", "temp_operating", "temp_storage") VALUES ('SW DPDT CK DF62J12S2AHQAA ', 'DF62J12S2AHQAA', 'CK Components', 'n/a', 'SW DPDT CK DF62J12S2AHQAA', 'DPDT rocker, right angle, through-hole', 'https://www.ckswitches.com/media/1443/df.pdf', 'https://www.ckswitches.com/products/switches/product-details/Rocker/DF/DF62J12S2AHQA/', 'terra_sym:SW DPDT CK DF62J12S2AHQAA ', 'nema:DF62J12S2AHQAA', NULL, NULL, 'Active', 1, 'https://www.mouser.com/catalog/additional/CK_Components_6111_RoHS_Certificate.pdf', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.383114', '2025-11-11T22:05:47.383116', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-20C/85C', 'If applicable');

COMMIT;
