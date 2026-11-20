-- db/schema/types/nvram.sql
-- Canonical parametric tail for battery-backed nonvolatile SRAM modules (ic_nvram).
    capacity TEXT,                -- total bits, ic_memory format ('256 Kbit')
    word_size TEXT,               -- '8-bit'
    speed TEXT,                   -- read access time ('70 ns')
    supply_voltage_min REAL,      -- VCC min (V); with max, encodes the 5%/10% grade
    supply_voltage_max REAL,      -- VCC max (V)
    persistence_years TEXT,       -- data retention without VCC, as in ic_memory
    write_protect_voltage TEXT,   -- VTP, the VCC level that write-protects the RAM
    battery TEXT,                 -- 'integrated lithium' | 'SNAPHAT (replaceable)'
    sram_socket TEXT,             -- JEDEC SRAM it drops into: '6116', '6264', '62256'...
    rtc TEXT                      -- 'Yes' for timekeeper parts, else 'No'
