-- db/schema/types/ic_microcontrollers.sql
-- Canonical parametric tail for ic_microcontrollers (ic_microcontrollers).
-- Note: pin_count is a core field — not repeated here.
    family TEXT,
    core TEXT,
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    flash_size TEXT,
    eeprom_size TEXT,
    ram_size TEXT,
    gpio_count INTEGER,
    uart_count INTEGER,
    i2c_count INTEGER,
    timer_count INTEGER,
    special_features TEXT