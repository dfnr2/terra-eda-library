-- Terra EDA Library - resistors_smt Table Schema
-- This file contains only the table definition
-- Data is split by dump_priority and source into separate files
--
-- This file is auto-generated and suitable for git tracking.
--

CREATE TABLE resistors_smt (
        -- Core fields (shared across all component types)
        unique_id TEXT PRIMARY KEY,
        part_locator TEXT,
        mpn TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        variant TEXT,
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
        rohs TEXT DEFAULT 'no',
        rohs_document_link TEXT,
        allow_substitution TEXT DEFAULT 'no',
        tracking TEXT DEFAULT 'no',
        standards_version TEXT DEFAULT 'v1.0',
        bom_comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        source TEXT DEFAULT 'static',
        dump_priority INTEGER DEFAULT 1,
        tier INTEGER DEFAULT 5,
        tags TEXT DEFAULT '',
        sim_model_type TEXT,
        sim_device TEXT,
        sim_pins TEXT,
        sim_model_file TEXT,
        sim_params TEXT,

        -- Resistor-specific fields
        tolerance TEXT,
        power_rating TEXT,
        temp_coeff TEXT,
        voltage_rating TEXT,
        composition TEXT,
        temp_operating TEXT,
        temp_soldering TEXT,
        temp_storage TEXT
    );
