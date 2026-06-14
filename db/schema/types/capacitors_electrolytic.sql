-- db/schema/types/capacitors_electrolytic.sql
-- Canonical parametric tail for through-hole aluminum electrolytic capacitors.
    capacitance TEXT,
    tolerance TEXT,
    voltage_rating TEXT,
    esr_ohm TEXT,
    ripple_current_ma TEXT,
    diameter_mm REAL,
    length_mm REAL,
    lead_spacing_mm REAL,
    endurance_hours TEXT,
    low_esr TEXT DEFAULT 'yes',
    polarized TEXT DEFAULT 'yes'
