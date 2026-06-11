-- db/schema/types/diodes.sql
-- Canonical parametric tail for diodes (cern_diodes + diodes).
    diode_type TEXT,        -- rectifier | schottky | zener | tvs | small-signal | ...
    voltage_rating TEXT,    -- Vr (reverse standoff / working)
    forward_voltage TEXT,   -- Vf
    forward_current TEXT,   -- If
    current_rating TEXT,    -- Io (rectifiers)
    power_rating TEXT        -- Pd where applicable (TVS/zener)
