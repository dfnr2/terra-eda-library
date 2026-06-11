-- db/schema/types/switches.sql
-- Canonical parametric tail for switches (switches + cern_switches).
    switch_type TEXT,
    poles INTEGER,
    throws INTEGER,
    current_rating TEXT,
    voltage_rating TEXT,
    actuation_force TEXT