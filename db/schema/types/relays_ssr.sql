-- db/schema/types/relays_ssr.sql
-- Canonical parametric tail for MOSFET-output solid-state relays (PhotoMOS,
-- OptoMOS, photorelays) and DC-output SSR modules. Triac/AC-output relays are a
-- separate future table.
    contact_form TEXT,          -- 1 Form A | 1 Form B | 2 Form A | 2 Form B | 1 Form C | 1 Form A + 1 Form B
    channels INTEGER,           -- independent switches per package
    load_type TEXT,             -- AC/DC | DC
    voltage_rating TEXT,        -- max load (off-state) voltage, peak AC/DC
    current_rating TEXT,        -- max continuous load current
    on_resistance TEXT,         -- Ron max, with condition
    off_capacitance TEXT,       -- Coff typ, where specified
    led_operate_current TEXT,   -- max LED current needed to turn on (I_Fon)
    led_forward_voltage TEXT,   -- LED Vf, with condition
    control_voltage TEXT,       -- input range for voltage-driven modules (no LED input)
    isolation_voltage TEXT,     -- I/O isolation, e.g. 5000Vrms
    turn_on_time TEXT,          -- t_on max
    turn_off_time TEXT          -- t_off max
