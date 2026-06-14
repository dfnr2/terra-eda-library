-- db/schema/types/batteries.sql
-- Canonical parametric tail for batteries / battery packs (batteries).
    chemistry TEXT,             -- 'Li-ion' | 'LiPo' | 'NiMH' | 'alkaline' | ...
    nominal_voltage_v REAL,     -- pack nominal voltage (V)
    capacity_ah REAL,           -- rated capacity (Ah)
    energy_wh REAL,             -- rated energy (Wh)
    rechargeable TEXT,          -- 'yes' | 'no'
    smart_interface TEXT        -- 'SMBus' | 'I2C' | 'none' | ...
