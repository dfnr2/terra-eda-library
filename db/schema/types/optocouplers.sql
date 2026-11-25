-- db/schema/types/optocouplers.sql
-- Canonical parametric tail for optocouplers / optoisolators: LED input coupled to a
-- phototransistor, photodarlington, high-speed transistor, logic-gate, Schmitt or
-- phototriac (triac-driver) output. MOSFET-output photorelays live in relays_ssr.
    output_type TEXT,           -- phototransistor | darlington | logic | transistor-high-speed | schmitt | triac-driver | triac-driver-zc
    channels INTEGER,           -- independent couplers per package
    isolation_voltage TEXT,     -- I/O withstand isolation, e.g. 5000Vrms
    ctr TEXT,                   -- current transfer ratio with condition; NULL for logic/Schmitt/triac outputs
    led_forward_voltage TEXT,   -- LED Vf, with condition
    led_operate_current TEXT,   -- LED current needed to switch the output (IFT / IF(on) / ITH), max
    output_voltage_max TEXT,    -- VCEO, VDRM for triac drivers, or max output/supply voltage for logic outputs
    output_current_max TEXT,    -- max output (collector / on-state) current
    turn_on_time TEXT,          -- t_on or t_PHL; max, or typ where only typ is given (says which)
    turn_off_time TEXT          -- t_off or t_PLH; max, or typ where only typ is given (says which)
