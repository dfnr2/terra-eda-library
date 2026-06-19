-- db/tables/cern_transformers/cern_transformers_0_schema.sql
-- Terra EDA Library - cern_transformers table schema (CERN 'Transformers').
-- Core fields match the go-forward core; tier defaults to 5 per TIER_TAG_SPEC.org.
--
-- No type-specific tail: CERN 'Transformers' is a grab-bag (mains power, signal/
-- audio, pulse, RF balun, gate-drive, current-sense, common-mode choke, …) with
-- bespoke vendor-part-named symbols and no deterministic transformer-type
-- dimension. 'Component Type' and 'Component Kind' are uniformly 'Standard'
-- (230/230 each), there is no 'Family' column, and the LibSymbol names are either
-- the vendor part (XFMR_<VENDOR>_<PART>, 160 distinct over 230 rows) or generic
-- winding-topology symbols ('Transformer 2xPrim 2xSec Type1') — none of these
-- yields a clean parametric category. Forcing a turns-ratio / inductance parse
-- from free-text 'Part Description' is explicitly out of scope per the
-- port-cern-library skill, so "no tail" is the correct outcome. Adopts only the
-- shared pin_count / component_height core additions.

CREATE TABLE cern_transformers (
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
    component_height TEXT
);
