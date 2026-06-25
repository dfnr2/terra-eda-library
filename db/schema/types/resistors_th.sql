-- db/schema/types/resistors_th.sql
-- Canonical parametric tail for through-hole resistors (resistors_th).
-- Same electrical tail as SMT resistors (resistors.sql) plus axial mechanical
-- fields: lead_spacing_mm is the formed lead pitch (= the footprint pitch),
-- body_style is the DIN axial body code (DIN0207, DIN0309, ...).
    tolerance TEXT,
    power_rating TEXT,
    temp_coeff TEXT,
    voltage_rating TEXT,
    composition TEXT,
    lead_spacing_mm REAL,
    body_style TEXT
