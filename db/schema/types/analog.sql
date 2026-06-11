-- db/schema/types/analog.sql
-- Canonical parametric tail for analog (ic_analog + cern_analog_interface).
    function_type TEXT,
    channels INTEGER,
    resolution_bits TEXT,
    interface TEXT,
    supply_voltage_min REAL,
    supply_voltage_max REAL