-- db/schema/types/crystals.sql
-- Canonical parametric tail for quartz crystals (crystals_th and crystals_smt).
-- frequency is also the schematic value. Holder/case goes in core package;
-- pin_count and temp_operating_* are core fields, not repeated here.
    frequency TEXT,
    load_capacitance TEXT,
    frequency_tolerance TEXT,
    frequency_stability TEXT,
    esr_ohm TEXT,
    oscillation_mode TEXT,
    drive_level TEXT
