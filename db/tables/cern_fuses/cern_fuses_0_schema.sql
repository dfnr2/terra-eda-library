-- db/tables/cern_fuses/cern_fuses_0_schema.sql
-- Terra EDA Library - cern_fuses table schema (CERN 'Fuses').
-- Core fields match the go-forward core; tier defaults to 5 per TIER_TAG_SPEC.org.

CREATE TABLE cern_fuses (
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
    keywords TEXT DEFAULT '',
    sim_model_type TEXT,
    sim_device TEXT,
    sim_pins TEXT,
    sim_model_file TEXT,
    sim_params TEXT,

    -- Adopted-from-CERN core additions
    pin_count TEXT,
    component_height TEXT,

    -- Fuses-specific tail
    fuse_kind TEXT,       -- deterministic type from the CERN 'Family' column: Fuse |
                          -- Fuse Resettable | Fuse Holder | Fuse Clip | Fuse & Holder |
                          -- Fuse Holder Cover | Surge Arrester | Fuse SCP
    current_rating TEXT   -- current/voltage rating, verbatim from the CERN 'Value'
                          -- column (e.g. '1A-32V', '500mA-63V'); blank for holders/
                          -- clips/covers which carry no rating
);
