-- db/tables/cern_thermistors_varistors/cern_thermistors_varistors_0_schema.sql
-- Terra EDA Library - cern_thermistors_varistors table schema
-- (CERN 'Thermistors And Varistors'). Core fields match the go-forward core;
-- tier defaults to 5 per TIER_TAG_SPEC.org.

CREATE TABLE cern_thermistors_varistors (
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

    -- Thermistor/Varistor-specific tail
    device_type TEXT,   -- deterministic type from the CERN 'LibSymbol' name:
                        -- NTC | PTC | Varistor | TCO. The table cleanly splits on
                        -- the symbol (Thermistor NTC / Thermistor PTC[ - polarized]
                        -- / Varistor / TCO Resistor + Fuse).
    voltage TEXT        -- working / clamping voltage, verbatim from the CERN
                        -- 'Voltage' column (e.g. '460VAC', '650V', '250VAC');
                        -- mostly filled for varistors, blank for most thermistors.
);
