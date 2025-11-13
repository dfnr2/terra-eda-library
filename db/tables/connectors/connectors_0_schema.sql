-- Terra EDA Library - connectors Table Schema
-- This file contains only the table definition
-- Data is split by dump_priority and source into separate files
--
-- This file is auto-generated and suitable for git tracking.
--

CREATE TABLE connectors (
            
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
            connector_type TEXT,
            pin_count INTEGER,
            rows INTEGER,
            pitch TEXT,
            mounting_type TEXT,
            orientation TEXT,
            current_rating TEXT,
            voltage_rating TEXT,
            gender TEXT,
            mating_cycles INTEGER,
            temp_operating TEXT,
            temp_storage TEXT
        );
