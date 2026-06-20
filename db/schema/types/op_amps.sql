-- db/schema/types/op_amps.sql
-- Canonical parametric tail for op_amps (ic_opamp + cern_op_amps).
    amplifier_type TEXT,          -- general-purpose | precision | zero-drift | high-speed | ...
    input_type TEXT,              -- CMOS | JFET | bipolar input stage
    channels INTEGER,
    gain_bandwidth TEXT,          -- GBW product
    slew_rate TEXT,
    input_offset TEXT,            -- Vos (input offset voltage)
    input_offset_drift TEXT,      -- Vos drift vs temperature
    input_bias_current TEXT,      -- Ib
    input_noise TEXT,             -- input voltage-noise density
    cmrr TEXT,                    -- common-mode rejection ratio
    psrr TEXT,                    -- power-supply rejection ratio
    quiescent_current TEXT,       -- Iq per amplifier
    output_current TEXT,          -- output drive current
    rail_to_rail TEXT,            -- quick reference: RRIO | RRI | RRO | no
    positive_rail TEXT,           -- input common-mode reach vs V+ (e.g. 'Vcc', 'Vdd+1.0V')
    negative_rail TEXT,           -- input common-mode reach vs V- (e.g. 'Vss-2.0V', 'GND')
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    power_rating TEXT
