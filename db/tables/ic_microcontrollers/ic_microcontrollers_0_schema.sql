-- Terra EDA Library - ic_microcontrollers Table Schema
-- This file contains only the table definition
-- Data is split by dump_priority and source into separate files
--
-- This file is auto-generated and suitable for git tracking.
--

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
