-- db/schema/types/ic_peripherals.sql
-- Canonical parametric tail for ic_peripherals (bus peripherals and system-support
-- chips for microprocessors: PIA/VIA/ACIA/UART, timers, CRTCs, interrupt and DMA
-- controllers, clock generators, bus controllers and drivers).
-- family/technology/max_clock/supply_* share names and values with ic_microprocessors.
-- Note: pin_count and temp_operating_* are core fields, not repeated here.
    family TEXT,
    peripheral_function TEXT,
    technology TEXT,
    max_clock TEXT,
    gpio_count INTEGER,
    channels INTEGER,
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    supply_rails TEXT,
    active_current TEXT,
    special_features TEXT
