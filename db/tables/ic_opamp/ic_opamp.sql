-- Terra EDA Library - ic_opamp Table
-- Number of components: 1
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS ic_opamp;

CREATE TABLE ic_opamp (
            
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
            opamp_type TEXT,
            channels INTEGER,
            gbw_product TEXT,
            slew_rate TEXT,
            input_offset_voltage TEXT,
            input_bias_current TEXT,
            input_impedance TEXT,
            cmrr TEXT,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            supply_current TEXT,
            output_current TEXT,
            noise_voltage TEXT,
            rail_to_rail BOOLEAN,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        );

-- Insert 1 components
BEGIN TRANSACTION;

INSERT INTO ic_opamp ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "opamp_type", "channels", "gbw_product", "slew_rate", "input_offset_voltage", "input_bias_current", "input_impedance", "cmrr", "supply_voltage_min", "supply_voltage_max", "supply_current", "output_current", "noise_voltage", "rail_to_rail", "temp_operating", "temp_storage", "temp_junction_max") VALUES ('IC TI TL081HDBVR Single FET input opamp, In to V+, SOT-23-5', 'TL081HIDBVR', 'Texas Instruments', 'SOT-23-5', 'TL081H', 'Single FET input opamp, 40-V, 5.25-MHz, In to V+, SOT-23-5', 'https://www.ti.com/lit/gpn/tl081h', 'https://www.ti.com/product/TL081H#product-details', 'terra_sym:IC TI TL081HDBVR Single FET input opamp, In to V+, SOT-23-5', 'Package_TO_SOT_SMD:SOT-23-5', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0013673131/TXII-E-A0013673131-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.380414', '2025-11-11T22:05:47.380416', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/125C', '-40C/125C', NULL);

COMMIT;
