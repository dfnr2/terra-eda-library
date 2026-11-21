-- db/schema/types/potentiometers.sql
-- Canonical parametric tail for trimming potentiometers (potentiometers_th).
-- value is the end-to-end resistance. tolerance/power_rating/temp_coeff/composition
-- share names and formats with resistors_th; turns (1 vs 25) and adjustment
-- (top/side) are what separate trimmer styles.
-- Note: pin_count and temp_operating_* are core fields, not repeated here.
    tolerance TEXT,
    power_rating TEXT,
    temp_coeff TEXT,
    composition TEXT,
    turns INTEGER,
    adjustment TEXT
