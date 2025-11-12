-- Terra EDA Library - bjt Table
-- Number of components: 0
-- Sorted by: part_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
--

DROP TABLE IF EXISTS bjt;

CREATE TABLE bjt (
    -- Core fields (same as all tables)
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
    sim_params TEXT,
    -- BJT-specific fields
    bjt_type TEXT,           -- 'NPN', 'PNP'
    vce_max TEXT,
    vcb_max TEXT,
    veb_max TEXT,
    ic_max TEXT,
    ib_max TEXT,
    hfe_min TEXT,
    hfe_typ TEXT,
    hfe_max TEXT,
    power_dissipation TEXT,
    transition_freq TEXT,    -- fT
    temp_operating TEXT,
    temp_storage TEXT,
    temp_junction_max TEXT
);

-- No data in table bjt
