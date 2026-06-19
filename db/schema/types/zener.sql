-- db/schema/types/zener.sql
-- Canonical parametric tail for Zener (voltage-regulator) diodes (diodes_zener).
    zener_voltage TEXT,          -- Vz nominal, e.g. '5.1V'
    zener_voltage_min REAL,      -- graded Vz min at test_current (V)
    zener_voltage_max REAL,      -- graded Vz max at test_current (V)
    tolerance TEXT,              -- '1%' (A) | '2%' (B) | '5%' (C)
    test_current TEXT,           -- Iz at which Vz is specified, e.g. '5mA'
    power_rating TEXT,           -- Ptot total power dissipation
    forward_voltage TEXT,        -- Vf max
    impedance_max REAL,          -- rdif max at the datasheet's quoted Iz (ohms)
    capacitance TEXT,            -- Cd max at 1 MHz, Vr=0 (pF)
    peak_reverse_current TEXT    -- Izsm non-repetitive peak reverse current (A)
