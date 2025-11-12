-- Terra EDA Library - ic_microcontrollers Table
-- Number of components: 2
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS ic_microcontrollers;

CREATE TABLE ic_microcontrollers (
            
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
            mcu_family TEXT,
            core_architecture TEXT,
            clock_speed TEXT,
            flash_size TEXT,
            ram_size TEXT,
            eeprom_size TEXT,
            gpio_count INTEGER,
            adc_channels INTEGER,
            dac_channels INTEGER,
            timers INTEGER,
            uart_count INTEGER,
            spi_count INTEGER,
            i2c_count INTEGER,
            usb_support BOOLEAN,
            can_support BOOLEAN,
            ethernet_support BOOLEAN,
            supply_voltage_min TEXT,
            supply_voltage_max TEXT,
            temp_operating TEXT,
            temp_storage TEXT,
            temp_junction_max TEXT
        );

-- Insert 2 components
BEGIN TRANSACTION;

INSERT INTO ic_microcontrollers ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "mcu_family", "core_architecture", "clock_speed", "flash_size", "ram_size", "eeprom_size", "gpio_count", "adc_channels", "dac_channels", "timers", "uart_count", "spi_count", "i2c_count", "usb_support", "can_support", "ethernet_support", "supply_voltage_min", "supply_voltage_max", "temp_operating", "temp_storage", "temp_junction_max") VALUES ('MCU ATSAMC20E18A-AUT 256 KB 5V TQFP-32', 'ATSAMC20E18A', 'Microchip', 'TQFP-32', 'ATSAMC20E18A', 'Arm MCU, 5V, 256KB, TQFP-32', 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAMC20_C21_Family_Data_Sheet_DS60001479D.pdf', 'https://www.microchip.com/en-us/product/atsamc20e18a', 'terra_sym:MCU ATSAMC20E18A-AUT 256 KB 5V TQFP-32', 'Package_QFP:TQFP-32_7x7mm_P0.8mm', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 1, 1, '1.1', NULL, '2025-11-11T22:05:47.381369', '2025-11-11T22:05:47.381371', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/85C', '-60C/150C', NULL);
INSERT INTO ic_microcontrollers ("part_id", "mpn", "manufacturer", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "mcu_family", "core_architecture", "clock_speed", "flash_size", "ram_size", "eeprom_size", "gpio_count", "adc_channels", "dac_channels", "timers", "uart_count", "spi_count", "i2c_count", "usb_support", "can_support", "ethernet_support", "supply_voltage_min", "supply_voltage_max", "temp_operating", "temp_storage", "temp_junction_max") VALUES ('MCU ATSAMC20G18A-AUT 256 KB 5V TQFP-48', 'ATSAMC20G18A', 'Microchip', 'TQFP-48', 'ATSAMC20G18A', 'Arm MCU, 5V, 256KB, TQFP-48', 'https://ww1.microchip.com/downloads/en/DeviceDoc/SAMC20_C21_Family_Data_Sheet_DS60001479D.pdf', 'https://www.microchip.com/en-us/product/atsamc20g18a', 'terra_sym:MCU ATSAMC20G18A-AUT 256 KB 5V TQFP-48', 'Package_QFP:TQFP-48_7x7mm_P0.5mm', NULL, NULL, 'Active', 1, 'https://4donline.ihs.com/images/VipMasterIC/IC/MCHP/MCHP-E-A0019744312/MCHP-E-A0019744312-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 1, 1, '1.1', NULL, '2025-11-11T22:05:47.381485', '2025-11-11T22:05:47.381488', 'migration_script', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '-40C/85C', '-60C/150C', NULL);

COMMIT;
