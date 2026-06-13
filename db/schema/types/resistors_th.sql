-- db/schema/types/resistors_th.sql
-- Canonical parametric tail for through-hole resistors (resistors_th).
-- Same resistor params as the SMT tail, plus through-hole lead geometry.
    tolerance TEXT,
    power_rating TEXT,
    temp_coeff TEXT,
    voltage_rating TEXT,
    composition TEXT,
    lead_spacing_mm REAL,
    body_style TEXT DEFAULT 'axial'
