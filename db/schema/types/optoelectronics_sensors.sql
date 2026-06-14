-- db/schema/types/optoelectronics_sensors.sql
-- Canonical parametric tail for optoelectronic sensors (reflective/transmissive
-- object sensors, photointerrupters, ambient-light / proximity sensors).
    sensor_type TEXT,           -- 'reflective' | 'transmissive' | 'ambient-light' | 'proximity'
    output_device TEXT,         -- 'phototransistor' | 'photodiode' | 'photo-IC' | 'analog' | 'digital'
    emitter_type TEXT,          -- 'IR LED' | 'visible LED' | ...
    peak_wavelength_nm REAL,    -- emitter peak emission wavelength
    sensing_distance TEXT,      -- optimal sensing range
    forward_current_ma REAL,    -- emitter forward current (max)
    collector_current_ma REAL   -- detector collector current (max)
