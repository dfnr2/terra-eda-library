-- db/schema/types/ic_drivers.sql
-- Canonical parametric tail for ic_drivers (ic_drivers).
    driver_type TEXT,
    channels INTEGER,
    data_rate TEXT,            -- signaling rate (transceivers/translators), e.g. '12 Mbps'
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    i_max_device TEXT,
    i_max_channel TEXT,
    logic_polarity TEXT,
    output_type TEXT,
    power_rating TEXT