-- db/schema/types/dc_dc.sql
-- Canonical parametric tail for isolated DC-DC converter modules (dc_dc_converters).
    input_voltage_nominal REAL,  -- nominal input (V)
    input_voltage_min REAL,      -- operating input range, low (V)
    input_voltage_max REAL,      -- operating input range, high (V)
    output_config TEXT,          -- 'single' | 'dual' (dual = +/-V about a common)
    output_voltage REAL,         -- magnitude of each output rail (V)
    output_current REAL,         -- max current per rail (A)
    output_power REAL,           -- max total output power (W)
    isolated TEXT,               -- 'yes' | 'no'
    isolation_voltage REAL,      -- input-to-output rating, 1 minute (Vdc)
    regulated TEXT,              -- 'yes' | 'no'
    efficiency REAL,             -- typical efficiency at full load (%)
    ripple_noise REAL            -- max ripple and noise (mVp-p)
