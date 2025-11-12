-- Terra EDA Library - ic_logic Table
-- Number of components: 4
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS ic_logic;

CREATE TABLE ic_logic (
            
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
            logic_family TEXT,
            gate_type TEXT,
            gates_per_package INTEGER,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            propagation_delay TEXT,
            output_current TEXT,
            input_type TEXT,
            output_type TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        );

-- Insert 4 components
BEGIN TRANSACTION;

INSERT INTO ic_logic ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "logic_family", "gate_type", "gates_per_package", "supply_voltage_min", "supply_voltage_max", "propagation_delay", "output_current", "input_type", "output_type", "temp_operating", "temp_storage") VALUES ('74LVC1G139', 'UNKNOWN', 'Generic', NULL, '74LVC1G139', 'Single 2-to-4-line decoder', 'www.ti.com/lit/ds/symlink/sn74lvc1g139.pdf', NULL, 'terra_sym:74LVC1G139', NULL, NULL, NULL, 'Active', NULL, NULL, NULL, NULL, 'v1.0', NULL, '2025-11-11T22:05:47.377210', '2025-11-11T22:05:47.377212', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO ic_logic ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "logic_family", "gate_type", "gates_per_package", "supply_voltage_min", "supply_voltage_max", "propagation_delay", "output_current", "input_type", "output_type", "temp_operating", "temp_storage") VALUES ('IC TI SN74LV1G139 2-to-4 line decoder', 'SN74LVC1G139', 'Texas Instrument', 'SM8', 'SN74LV1G139', 'Single 2-to-4-line decoder', 'https://www.ti.com/lit/gpn/sn74lvc1g139', 'https://www.ti.com/product/SN74LVC1G139?keyMatch=SN74LVC1G139&tisearch=universal_search&usecase=GPN-ALT', 'terra_sym:IC TI SN74LV1G139 2-to-4 line decoder', 'Package_TO_SOT_SMD:SOT-23-5', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0026917336/TXII-E-A0026917336-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380382', '2025-11-11T22:05:47.380384', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/125C', '-65C/150C');
INSERT INTO ic_logic ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "logic_family", "gate_type", "gates_per_package", "supply_voltage_min", "supply_voltage_max", "propagation_delay", "output_current", "input_type", "output_type", "temp_operating", "temp_storage") VALUES ('IC TXU0104 4-bit level shifter 1.8v - 5v TSSOP-14', 'TXU0104PWR', 'Texas Instrument', 'TSSOP-14', 'TXU0104', '4-bit Level Shifting Buffer 1.8V <> 5V', 'https://www.ti.com/lit/gpn/TXU0104', 'https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758919582957', 'terra_sym:IC TXU0104 4-bit level shifter 1.8v - 5v TSSOP-14', 'Package_SO:TSSOP-14_4.4x5mm_P0.65mm', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0021022709/TXII-E-A0021022709-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380526', '2025-11-11T22:05:47.380528', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/125C', '-65C/150C');
INSERT INTO ic_logic ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "logic_family", "gate_type", "gates_per_package", "supply_voltage_min", "supply_voltage_max", "propagation_delay", "output_current", "input_type", "output_type", "temp_operating", "temp_storage") VALUES ('IC level shifter 1.8v - 5v SOT-23-5', 'SN74LV1T125DBV', 'NXP', 'SOT 23-5', 'SN74LV1T125DBV', 'Single Level Shifting Buffer 1.8V <> 5V', 'https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758962409857', 'https://www.ti.com/lit/ds/symlink/sn74lv1t125.pdf?ts=1758919582957', 'terra_sym:IC level shifter 1.8v - 5v SOT-23-5', 'Package_TO_SOT_SMD:SOT-23-5', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/TXII/TXII-E-A0026917336/TXII-E-A0026917336-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 0, 0, '1.1', NULL, '2025-11-11T22:05:47.380564', '2025-11-11T22:05:47.380566', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/125C', '-65C/150C');

COMMIT;
