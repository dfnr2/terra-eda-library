-- Terra EDA Library - inductors Table
-- Number of components: 3
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS inductors;

CREATE TABLE inductors (
            
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
            tolerance TEXT,
            current_rating TEXT,
            saturation_current TEXT,
            dc_resistance TEXT,
            self_resonant_freq TEXT,
            inductor_type TEXT,
            core_material TEXT,
            shielded BOOLEAN,
            temp_operating TEXT,
            temp_storage TEXT
        );

-- Insert 3 components
BEGIN TRANSACTION;

INSERT INTO inductors ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "tolerance", "current_rating", "saturation_current", "dc_resistance", "self_resonant_freq", "inductor_type", "core_material", "shielded", "temp_operating", "temp_storage") VALUES ('IND Bourns 10uH 1.1A rms SRR6603-100ML', 'SRR6603-100ML q q', 'Bourns', 'SMT', 'IND Bourns 10uH 1.1A rms SRR6603-100ML', 'Power inductor, 10 mH, 75 mOhm, 1A rms,  20% SMT 6.8x4.4mm', 'https://www.bourns.com/pdfs/SRR6603.pdf', 'https://www.bourns.com/resources/rohs/magnetics/power-inductors-smd-shielded', 'terra_sym:IND Bourns 10uH 1.1A rms SRR6603-100ML', 'Isopoint:Coilcraft MSS7341 Shileded power inductor', NULL, NULL, 'Active', 1, 'https://www.bourns.com/docs/rohs-cofc/cofc_srr.pdf?sfvrsn=7557d913_18', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380658', '2025-11-11T22:05:47.380660', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, '30%', '1.1A rms, 40C rise, 1.5ADC, 10% drop', NULL, NULL, NULL, 'Inductor', NULL, NULL, '-40C/+125C', '-40C/+125C');
INSERT INTO inductors ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "tolerance", "current_rating", "saturation_current", "dc_resistance", "self_resonant_freq", "inductor_type", "core_material", "shielded", "temp_operating", "temp_storage") VALUES ('IND Bourns 68uH 3A rms  SRR1210-680M ', 'SRR1210-680M', 'Bourns', 'SMT', 'IND Bourns 68uH 3A rms  SRR1210-680M', 'Power inductor, 68 mH, 102 mOhm, 3A rms,  20% SMT 12mm x 12mm', 'https://www.bourns.com/docs/Product-Datasheets/SRR1210.pdf', 'https://www.bourns.com/resources/rohs/magnetics/power-inductors-smd-shielded', 'terra_sym:IND Bourns 68uH 3A rms  SRR1210-680M ', 'nema:Bourns SRR1210', NULL, NULL, 'Active', 1, 'https://www.bourns.com/docs/rohs-cofc/cofc_srr.pdf?sfvrsn=7557d913_18', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380784', '2025-11-11T22:05:47.380787', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, '20%', '3A rms, 40C rise, 10% drop', NULL, NULL, NULL, 'Inductor', NULL, NULL, '-40C/+125C', '-40C/+125C');
INSERT INTO inductors ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "tolerance", "current_rating", "saturation_current", "dc_resistance", "self_resonant_freq", "inductor_type", "core_material", "shielded", "temp_operating", "temp_storage") VALUES ('IND CoilCraft 10uH 2.8A MSS7341-103ML', 'MSS7341-103ML', 'CoilCraft', 'SMT', 'IND CoilCraft 10uH 2.8A MSS7341-103ML', 'Power inductor, 10 mH, 38 mOhm, 2.8A, 20% SMT 7.1x7.1 mm', 'https://www.coilcraft.com/getmedia/7b464459-a4d6-47b0-83ca-9d96d4410863/MSS7341.pdf', 'https://www.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum/mss-mos/mss7341/mss7341-103/', 'terra_sym:IND CoilCraft 10uH 2.8A MSS7341-103ML', 'Isopoint:Coilcraft MSS7341 Shileded power inductor', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/COLC/COLC-E-A0007342590/COLC-E-A0007342584-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380828', '2025-11-11T22:05:47.380830', 'migration_script', 'primitive', 'L', '1=+ 2=-', NULL, NULL, '30%', '2.8A rms, 20C rise, 1.64ADC, 10% ind. drop', NULL, NULL, NULL, 'Inductor', NULL, NULL, '-40C/+85C', '-40C/+125C');

COMMIT;
