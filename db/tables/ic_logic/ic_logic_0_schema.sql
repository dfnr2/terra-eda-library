-- Terra EDA Library - ic_logic Table Schema
-- This file contains only the table definition
-- Data is split by dump_priority and source into separate files
--
-- This file is auto-generated and suitable for git tracking.
--

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
