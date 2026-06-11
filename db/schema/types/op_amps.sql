-- db/schema/types/op_amps.sql
-- Canonical parametric tail for op_amps (ic_opamp + cern_op_amps).
    amplifier_type TEXT,
    channels INTEGER,
    gain_bandwidth TEXT,
    slew_rate TEXT,
    input_offset TEXT,
    input_noise TEXT,
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    power_rating TEXT