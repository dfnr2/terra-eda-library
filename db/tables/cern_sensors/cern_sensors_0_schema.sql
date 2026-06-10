-- db/tables/cern_sensors/cern_sensors_0_schema.sql
-- Terra EDA Library - cern_sensors table schema (CERN 'Sensors').
-- Core fields match the go-forward core; tier defaults to 5 per TIER_TAG_SPEC.org.
--
-- No type-specific tail: CERN 'Sensors' is a grab-bag (temperature, current,
-- Hall/magnetic, pressure, humidity, gas, optical, accelerometer/IMU, SiPM, image
-- sensors, …) with device-named symbols and no deterministic sensor-category
-- dimension. 'Component Type' is uniformly 'Standard', 'Component Kind' is only
-- Standard/Accessories, there is no 'Family' column, and the LibSymbol names are
-- the MPN/part name (185 distinct over 247 rows) — none of these yields a clean
-- parametric category. Per the port-cern-library skill, "no tail" is the correct
-- outcome for a grab-bag category. Adopts only the shared pin_count /
-- component_height core additions.

CREATE TABLE cern_sensors (
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
    component_height TEXT
);
