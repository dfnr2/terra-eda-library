-- db/schema/types/logic.sql
-- Canonical parametric tail for logic (ic_logic + cern_logic + cern_standard_logic).
-- Covers TTL (74/74S/74LS/74F/74AS/74ALS) and the pin-compatible CMOS-TTL
-- families (74HC/HCT/AC/ACT/LV/LVC). logic_family is the discriminator;
-- base_number ('00','138','244') gives cross-family equivalence (74LS00<->74HC00).
-- channels = count of independent functional units (quad NAND=4, dual FF=2,
-- octal buffer=8, single counter=1). inputs_per_gate is for simple gates only;
-- bit_width is the data width of MSI parts (4-bit counter=4, octal register=8).
    logic_family TEXT,
    base_number TEXT,
    gate_function TEXT,
    function_category TEXT,
    channels INTEGER,
    inputs_per_gate INTEGER,
    bit_width INTEGER,
    logic_polarity TEXT,
    output_type TEXT,
    schmitt_trigger TEXT,
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    vih_min REAL,
    vil_max REAL,
    voh_min REAL,
    vol_max REAL,
    propagation_delay TEXT,
    max_frequency TEXT,
    output_current TEXT,
    supply_current TEXT
