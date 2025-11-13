-- Terra EDA Library - mosfet Table Schema
-- This file contains only the table definition
-- Data is split by dump_priority and source into separate files
--
-- This file is auto-generated and suitable for git tracking.
--

CREATE TABLE mosfet (
    -- Core fields
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
    -- MOSFET-specific fields
    mosfet_type TEXT,        -- 'N-Channel', 'P-Channel'
    vds_max TEXT,
    vgs_max TEXT,
    vgs_th_min TEXT,
    vgs_th_typ TEXT,
    vgs_th_max TEXT,
    id_max TEXT,
    rds_on_typ TEXT,
    rds_on_max TEXT,
    qg_typ TEXT,             -- Total gate charge
    qgs_typ TEXT,            -- Gate-source charge
    qgd_typ TEXT,            -- Gate-drain charge
    ciss_typ TEXT,           -- Input capacitance
    coss_typ TEXT,           -- Output capacitance
    crss_typ TEXT,           -- Reverse transfer capacitance
    power_dissipation TEXT,
    temp_operating TEXT,
    temp_storage TEXT,
    temp_junction_max TEXT
);
