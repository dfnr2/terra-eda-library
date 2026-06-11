-- db/schema/types/connectors.sql
-- Canonical parametric tail for connectors (connectors + all cern_* connector tables).
    -- Connector Classification
    connector_category TEXT,      -- e.g. 'board-to-board', 'wire-to-board', 'io', 'terminal_block'
    connector_family TEXT,        -- e.g. 'JST-XH', 'Molex MicroFit', 'USB-C', 'RJ45'
    connector_series TEXT,        -- vendor series name/number (e.g. '5557', '171823', etc.)
    connector_type TEXT,          -- e.g. 'header', 'receptacle', 'plug', 'jack', 'socket', 'terminal_block'
    -- Positioning / Geometry
    positions INTEGER,            -- total number of contacts (positions)
    rows INTEGER DEFAULT 1,       -- 1, 2, 3...
    pitch_mm REAL,                -- contact pitch along row (mm)
    row_pitch_mm REAL,            -- distance between rows, if applicable (mm)
    orientation TEXT,             -- 'vertical', 'right-angle', 'inline', 'top-entry', 'side-entry'
    termination_type TEXT,        -- 'SMT', 'Through Hole', 'crimp', 'idc', 'solder_cup', 'poke_in', 'press_fit', etc.
    -- Mating / Mechanical Features
    gender TEXT,                  -- 'male', 'female', 'plug', 'receptacle', 'jack'
    polarized TEXT,               -- 'yes'/'no' (keying present?)
    keying_detail TEXT,           -- e.g. 'polarizing tab', 'asymmetric shroud', 'dual key'
    locking_mechanism TEXT,       -- 'friction', 'latch', 'screw', 'bayonet', 'push-pull', 'none'
    shielding TEXT,               -- 'shielded', 'unshielded', or detail like 'metal shell'
    panel_mount_style TEXT,       -- 'through-hole', 'snap-in', 'flange', 'nut', 'none'
    color TEXT,                   -- housing color if functionally relevant (e.g. USB, coded headers)
    -- Electrical Rating
    current_rating REAL,          -- per contact continuous rating (A)
    voltage_rating REAL,          -- working voltage rating (V)
    contact_resistance_mohm REAL, -- typical/max contact resistance
    insulation_resistance_mohm REAL, -- insulation resistance
    dielectric_withstand_vrms REAL,  -- hi-pot test rating
    signal_type TEXT,             -- 'signal', 'power', 'mixed', 'rf', 'high-speed'
    -- Wire/Cable Compatibility (for wire/cable connectors)
    wire_gauge_min_awg INTEGER,  -- minimum supported wire gauge
    wire_gauge_max_awg INTEGER,  -- maximum supported wire gauge
    insulation_dia_min_mm REAL,  -- min insulation OD (mm)
    insulation_dia_max_mm REAL,  -- max insulation OD (mm)
    cable_type TEXT,              -- 'discrete', 'ribbon', 'coax', 'twisted_pair', etc.
    -- Environmental / Standards
    flammability_rating TEXT,     -- e.g. 'UL94-V0'
    ip_rating TEXT,               -- e.g. 'IP20', 'IP67'
    creepage_clearance_note TEXT, -- notes if creepage/clearance are special / safety rated
    -- Mating / System Integration
    mating_family TEXT,           -- e.g. 'mates with MicroFit receptacles'
    mating_part_hint TEXT