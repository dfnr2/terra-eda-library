-- db/schema/types/logic.sql
-- Canonical parametric tail for logic (ic_logic + cern_logic + cern_standard_logic).
    logic_family TEXT,
    gate_function TEXT,
    channels INTEGER,
    propagation_delay TEXT,
    supply_voltage_min REAL,
    supply_voltage_max REAL