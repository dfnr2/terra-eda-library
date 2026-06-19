-- db/schema/types/tvs.sql
-- Canonical parametric tail for transient-voltage-suppressor (TVS) diodes (diodes_tvs).
    directionality TEXT,          -- unidirectional | bidirectional
    standoff_voltage TEXT,        -- Vrwm reverse standoff / working voltage
    breakdown_voltage_min REAL,   -- Vbr min at IT (V)
    breakdown_voltage_max REAL,   -- Vbr max at IT (V)
    breakdown_test_current TEXT,  -- IT, the Vbr test current
    clamping_voltage TEXT,        -- Vc max at Ipp
    peak_pulse_current TEXT,      -- Ipp (10/1000 us)
    peak_pulse_power TEXT,        -- Ppp peak pulse power
    leakage_current TEXT,         -- IR max at Vrwm
    capacitance TEXT              -- Cj typ (pF) where specified
