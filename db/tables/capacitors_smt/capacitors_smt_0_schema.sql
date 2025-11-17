-- Terra EDA Library - capacitors_smt Table Schema
-- This file contains only the table definition
-- Data is split by dump_priority and source into separate files
--
-- This file is auto-generated and suitable for git tracking.
--

CREATE TABLE capacitors_smt (
        -- Core fields (shared across all component types)
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
        sim_model_type TEXT,
        sim_device TEXT,
        sim_pins TEXT,
        sim_model_file TEXT,
        sim_params TEXT,

        -- Electrical core (capacitor-specific)
        capacitance_f REAL,
        voltage_rating_v REAL,
        tolerance TEXT,
        cap_type TEXT,
        dielectric_class TEXT,
        polarized TEXT DEFAULT 'no',

        -- Performance / loss
        esr_typ_ohm REAL,
        esr_test_freq_hz REAL,
        ripple_current_max_a REAL,
        leakage_current_max_a REAL,

        -- Temperature / reliability
        temp_range_min_c INTEGER,
        temp_range_max_c INTEGER,
        temp_operating TEXT,
        temp_soldering TEXT,
        temp_storage TEXT,
        lifetime_hours_at_max_temp INTEGER,
        aec_q_rating TEXT,

        -- Mechanical
        height_max_mm REAL
    );
