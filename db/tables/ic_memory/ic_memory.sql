-- Terra EDA Library - ic_memory Table
-- Number of components: 1
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS ic_memory;

CREATE TABLE ic_memory (
            
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
            memory_type TEXT,
            capacity TEXT,
            organization TEXT,
            interface TEXT,
            access_time TEXT,
            clock_speed TEXT,
            supply_voltage TEXT,
            write_cycles TEXT,
            data_retention TEXT,
            temp_operating TEXT,
            temp_storage TEXT
        );

-- Insert 1 components
BEGIN TRANSACTION;

INSERT INTO ic_memory ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "memory_type", "capacity", "organization", "interface", "access_time", "clock_speed", "supply_voltage", "write_cycles", "data_retention", "temp_operating", "temp_storage") VALUES ('IC EEPROM Microchip 24LC32A 4kx8 SOT-23-5', ' 24LC32AT-I/OT', 'Microchip', 'SOT-23-5', '4k x 8 EEPROM', 'EEPROM 4k x 8 I2C SOT-23-5', 'https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/24AA32A-24LC32A-32-Kbit-I2C-Serial-EEPROM-DS20001713.pdf', 'https://www.microchip.com/en-us/product/24lc32a', 'terra_sym:IC EEPROM Microchip 24LC32A 4kx8 SOT-23-5', 'nema:SOT95P270X145-5N', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 1, 0, '1.1', NULL, '2025-11-11T22:05:47.379697', '2025-11-11T22:05:47.379699', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/85C', '-40C/85C');

COMMIT;
