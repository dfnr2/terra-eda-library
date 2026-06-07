-- Terra EDA Library - capacitors_th Table Schema
-- This file contains only the table definition
-- Data is split by dump_priority and source into separate files
--
-- This file is auto-generated and suitable for git tracking.
--

CREATE TABLE capacitors_th (
        -- Core fields (shared across all component types)
        unique_id TEXT PRIMARY KEY,
        part_locator TEXT,
        mpn TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        value TEXT,
        description TEXT,
        datasheet TEXT,
        manufacturer_link TEXT,
        kicad_symbol TEXT,
        kicad_footprint TEXT,
        altium_symbol TEXT,
        altium_footprint TEXT,
        lifecycle_status TEXT DEFAULT 'Active',
        rohs TEXT DEFAULT 'No',
        rohs_document_link TEXT,
        allow_substitution TEXT DEFAULT 'No',
        tracking TEXT DEFAULT 'No',
        standards_version TEXT DEFAULT 'v1.0',
        bom_comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT,
        source TEXT DEFAULT 'static',
        dump_priority INTEGER DEFAULT 1,
        tier INTEGER DEFAULT 0,
        tags TEXT DEFAULT '',
        sim_model_type TEXT,
        sim_device TEXT,
        sim_pins TEXT,
        sim_model_file TEXT,
        sim_params TEXT,

        -- Through-hole specific fields (replaces 'package')
        lead_spacing_mm REAL,
        body_diameter_mm REAL,
        body_length_mm REAL,
        height_max_mm REAL,
        body_style TEXT DEFAULT 'radial',

        -- Electrical core (capacitor-specific)
        voltage_rating_v REAL,
        tolerance TEXT,
        cap_type TEXT,
        dielectric_class TEXT,
        polarized TEXT DEFAULT 'No',

        -- Performance / loss
        esr_typ_ohm REAL,
        esr_test_freq_hz REAL,
        ripple_current_max_a REAL,
        leakage_current_max_a REAL,

        -- Temperature / reliability
        temp_operating TEXT,
        temp_soldering TEXT,
        temp_storage TEXT,
        lifetime_hours_at_max_temp INTEGER,
        aec_q_rating TEXT
    );
