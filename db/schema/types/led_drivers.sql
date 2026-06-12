-- db/schema/types/led_drivers.sql
-- Canonical parametric tail for led_drivers.
    driver_topology TEXT,      -- linear | buck | boost | buck-boost | charge-pump
    channels INTEGER,          -- number of LED output channels
    output_current TEXT,       -- drive current per channel
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    output_voltage_max TEXT,   -- max LED-string voltage
    switching_freq TEXT,
    dimming_method TEXT,       -- pwm | analog | none
    interface TEXT,            -- i2c | spi | none
    current_accuracy TEXT