-- db/schema/types/ic_microprocessors.sql
-- Canonical parametric tail for ic_microprocessors (bus CPUs with no on-chip
-- program memory: 6502, 6800/6809, Z80, 8080/8085, 8086/8088, 68000, TMS9900, 1802).
-- Note: pin_count and temp_operating_* are core fields, not repeated here.
    family TEXT,
    core TEXT,
    technology TEXT,
    architecture_bits INTEGER,
    data_bus_bits INTEGER,
    address_bus_bits INTEGER,
    max_clock TEXT,
    clock_source TEXT,
    supply_voltage_min REAL,
    supply_voltage_max REAL,
    supply_rails TEXT,
    active_current TEXT,
    special_features TEXT
