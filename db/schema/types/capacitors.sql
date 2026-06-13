-- db/schema/types/capacitors.sql
-- Canonical parametric tail for capacitors (capacitors_smt, capacitors_th).
    voltage_rating_v REAL,
    tolerance TEXT,
    cap_type TEXT,
    dielectric_class TEXT,
    polarized TEXT DEFAULT 'No',
    esr_typ_ohm REAL,
    esr_test_freq_hz REAL,
    ripple_current_max_a REAL,
    leakage_current_max_a REAL,
    lifetime_hours_at_max_temp INTEGER,
    aec_q_rating TEXT,
    height_max_mm REAL
