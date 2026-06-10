-- db/tables/cern_switches/cern_switches_0_schema.sql
-- Terra EDA Library - cern_switches table schema (CERN 'Switches').
-- Core fields match the go-forward core; tier defaults to 5 per TIER_TAG_SPEC.org.

CREATE TABLE cern_switches (
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

    -- Adopted-from-CERN core additions
    pin_count TEXT,
    component_height TEXT,

    -- Switches-specific tail
    -- switch_type derives deterministically from the CERN symbol-name prefix:
    --   PB -> push-button, 'SW … DIP Switch' -> dip, 'SW Rotary' -> rotary,
    --   Knob/KNB -> knob, 'Solder Jumper' -> jumper, 'Tilt Switch' -> tilt,
    --   remaining SW -> switch (toggle/slide/rocker generic).
    switch_type TEXT
);
