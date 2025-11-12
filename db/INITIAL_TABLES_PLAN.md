# Initial Component Type Tables - Schema Plan

**Purpose:** This document defines the 15 initial component type tables for migrating from the single-table architecture. This is a starting point - tables will be refined, reorganized, and extended as the library evolves.

**Note:** New tables will be added and existing tables may be split into more specific categories over time. This plan focuses on getting the migration started.

---

## Standard Fields (All Tables)

Every table includes:
- **22 Core Fields** (identity, physical, documentation, CAD, supply chain, process control, metadata)
- **5 SPICE Fields** (sim_model_type, sim_device, sim_pins, sim_model_file, sim_params)

See `SPICE_INTEGRATION.md` for SPICE field documentation.

---

## 1. resistors

**Type-Specific Fields:**
```sql
resistance REAL,                    -- Resistance value in ohms
tolerance TEXT,                     -- '1%', '5%', etc.
power_rating TEXT,                  -- '0.1W', '0.25W', '1W'
temp_coeff TEXT,                    -- Temperature coefficient (e.g., '±100ppm/°C')
voltage_rating TEXT,                -- Maximum voltage
composition TEXT,                   -- 'Thick Film', 'Thin Film', 'Metal Film', 'Wirewound'
temp_operating TEXT,                -- Operating temperature range
temp_storage TEXT                   -- Storage temperature range
```

**SPICE:** Usually `sim_model_type='primitive'`, `sim_device='R'`

---

## 2. capacitors

**Type-Specific Fields:**
```sql
capacitance REAL,                   -- Capacitance in farads
tolerance TEXT,                     -- '10%', '20%', '±0.1pF'
voltage_rating TEXT,                -- Rated voltage
dielectric TEXT,                    -- 'X7R', 'X5R', 'C0G', 'NP0', 'Y5V', 'Electrolytic'
capacitor_type TEXT,                -- 'MLCC', 'Electrolytic', 'Tantalum', 'Film'
esr TEXT,                           -- Equivalent Series Resistance
ripple_current TEXT,                -- Ripple current rating (electrolytics)
temp_operating TEXT,
temp_storage TEXT,
temp_coeff TEXT                     -- Temperature coefficient (ceramics)
```

**SPICE:** Usually `sim_model_type='primitive'`, `sim_device='C'`

---

## 3. inductors

**Type-Specific Fields:**
```sql
inductance REAL,                    -- Inductance in henries
tolerance TEXT,                     -- '10%', '20%'
current_rating TEXT,                -- DC current rating
saturation_current TEXT,            -- Saturation current (Isat)
dc_resistance TEXT,                 -- DC resistance (DCR)
self_resonant_freq TEXT,            -- Self-resonant frequency
inductor_type TEXT,                 -- 'Power', 'RF', 'Common Mode'
core_material TEXT,                 -- 'Ferrite', 'Iron', 'Air'
shielded BOOLEAN,                   -- Is shielded?
temp_operating TEXT,
temp_storage TEXT
```

**SPICE:** Usually `sim_model_type='primitive'`, `sim_device='L'`

---

## 4. ferrites

**Type-Specific Fields:**
```sql
impedance_at_freq TEXT,             -- '120Ω @ 100MHz'
test_frequency TEXT,                -- '100MHz'
dc_resistance TEXT,                 -- DC resistance (DCR)
current_rating TEXT,                -- Rated current
tolerance TEXT,                     -- Impedance tolerance
ferrite_type TEXT,                  -- 'Chip Bead', 'Through-Hole', 'Multi-layer'
temp_operating TEXT,
temp_storage TEXT
```

**SPICE:** May not have standard model; use inductor approximation or leave NULL

---

## 5. transistors

**Type-Specific Fields:**
```sql
transistor_type TEXT,               -- 'NPN', 'PNP', 'N-Channel MOSFET', 'P-Channel MOSFET', 'JFET', 'IGBT'
polarity TEXT,                      -- 'NPN', 'PNP', 'N-Channel', 'P-Channel'
vce_vds_max TEXT,                   -- Max collector-emitter / drain-source voltage
ic_id_max TEXT,                     -- Max collector / drain current
vgs_vbe_threshold TEXT,             -- Gate-source / base-emitter threshold
rds_on TEXT,                        -- On-resistance (MOSFETs)
hfe_gain TEXT,                      -- Current gain (BJTs)
power_dissipation TEXT,             -- Maximum power dissipation
transition_freq TEXT,               -- Transition frequency (fT)
temp_operating TEXT,
temp_junction_max TEXT              -- Maximum junction temperature
```

**SPICE:** `sim_device='Q'` (BJT) or `'M'` (MOSFET), may use subcircuit models

---

## 6. diodes

**Type-Specific Fields:**
```sql
diode_type TEXT,                    -- 'Rectifier', 'Schottky', 'Zener', 'TVS', 'Switching'
forward_voltage TEXT,               -- Forward voltage drop (Vf)
forward_current TEXT,               -- Continuous forward current (If)
reverse_voltage TEXT,               -- Reverse breakdown voltage (Vr)
reverse_current TEXT,               -- Reverse leakage current (Ir)
power_dissipation TEXT,             -- Maximum power dissipation
recovery_time TEXT,                 -- Reverse recovery time (trr)
capacitance TEXT,                   -- Junction capacitance
zener_voltage TEXT,                 -- Zener voltage (Zener diodes)
clamping_voltage TEXT,              -- Clamping voltage (TVS diodes)
temp_operating TEXT,
temp_junction_max TEXT
```

**SPICE:** `sim_device='D'`, may use `.MODEL` or subcircuit

---

## 7. connectors

**Type-Specific Fields:**
```sql
connector_type TEXT,                -- 'Header', 'Socket', 'Terminal Block', 'USB', 'RF', 'Power Jack'
pin_count INTEGER,                  -- Number of pins/contacts
rows INTEGER,                       -- Number of rows (e.g., 2 for 2x8 header)
pitch TEXT,                         -- Pin pitch (e.g., '2.54mm', '1.27mm')
mounting_type TEXT,                 -- 'Through-Hole', 'SMD', 'Panel Mount'
orientation TEXT,                   -- 'Vertical', 'Right Angle', 'Horizontal'
current_rating TEXT,                -- Current rating per contact
voltage_rating TEXT,                -- Voltage rating
gender TEXT,                        -- 'Male', 'Female', 'N/A'
mating_cycles INTEGER,              -- Rated mating cycles
temp_operating TEXT,
temp_storage TEXT
```

**SPICE:** Usually NULL (no simulation model needed)

---

## 8. ic_drivers

**Type-Specific Fields:**
```sql
driver_type TEXT,                   -- 'Motor', 'LED', 'Gate', 'Line', 'LCD', 'Display'
channels INTEGER,                   -- Number of channels/outputs
output_current TEXT,                -- Output current per channel
supply_voltage_min TEXT,            -- Minimum supply voltage
supply_voltage_max TEXT,            -- Maximum supply voltage
logic_voltage TEXT,                 -- Logic level voltage
output_type TEXT,                   -- 'Push-Pull', 'Open-Drain', 'Half-Bridge', 'Full-Bridge'
switching_freq TEXT,                -- Maximum switching frequency
control_interface TEXT,             -- 'PWM', 'SPI', 'I2C', 'Parallel'
temp_operating TEXT,
temp_junction_max TEXT
```

**SPICE:** Usually subcircuit model or behavioral model

---

## 9. ic_microcontrollers

**Type-Specific Fields:**
```sql
mcu_family TEXT,                    -- 'STM32F4', 'AVR', 'PIC', 'ESP32', 'RP2040'
core_architecture TEXT,             -- 'ARM Cortex-M4', '8-bit AVR', 'RISC-V'
clock_speed TEXT,                   -- Maximum clock speed
flash_size TEXT,                    -- Program memory size
ram_size TEXT,                      -- RAM size
eeprom_size TEXT,                   -- EEPROM size (if applicable)
gpio_count INTEGER,                 -- Number of GPIO pins
adc_channels INTEGER,               -- Number of ADC channels
dac_channels INTEGER,               -- Number of DAC channels
timers INTEGER,                     -- Number of timers
uart_count INTEGER,                 -- Number of UART peripherals
spi_count INTEGER,                  -- Number of SPI peripherals
i2c_count INTEGER,                  -- Number of I2C peripherals
usb_support BOOLEAN,                -- USB support
can_support BOOLEAN,                -- CAN support
ethernet_support BOOLEAN,           -- Ethernet support
supply_voltage_min TEXT,
supply_voltage_max TEXT,
temp_operating TEXT,
temp_junction_max TEXT
```

**SPICE:** Usually no SPICE model (digital ICs rarely simulated at analog level)

---

## 10. ic_logic

**Type-Specific Fields:**
```sql
logic_family TEXT,                  -- '74HC', '74HCT', '74LVC', 'CD4000', '74AHC'
gate_type TEXT,                     -- 'AND', 'OR', 'NAND', 'NOR', 'XOR', 'NOT', 'Buffer', 'Mux', 'Latch', 'Flip-Flop'
gates_per_package INTEGER,          -- Number of gates per package
supply_voltage_min TEXT,
supply_voltage_max TEXT,
propagation_delay TEXT,             -- Propagation delay (tpd)
output_current TEXT,                -- Output drive current
input_type TEXT,                    -- 'Schmitt Trigger', 'Standard', 'TTL Compatible'
output_type TEXT,                   -- 'Push-Pull', 'Open-Drain', 'Tri-State'
temp_operating TEXT,
temp_storage TEXT
```

**SPICE:** Usually behavioral models or primitive gates

---

## 11. ic_memory

**Type-Specific Fields:**
```sql
memory_type TEXT,                   -- 'SRAM', 'DRAM', 'Flash', 'EEPROM', 'FRAM', 'MRAM'
capacity TEXT,                      -- Memory capacity (e.g., '256Kb', '1Mb', '16GB')
organization TEXT,                  -- Organization (e.g., '32K x 8', '64K x 16')
interface TEXT,                     -- 'Parallel', 'SPI', 'I2C', 'QSPI', 'SDR', 'DDR'
access_time TEXT,                   -- Access time
clock_speed TEXT,                   -- Clock speed (synchronous memory)
supply_voltage TEXT,                -- Supply voltage
write_cycles TEXT,                  -- Endurance (write/erase cycles)
data_retention TEXT,                -- Data retention time
temp_operating TEXT,
temp_storage TEXT
```

**SPICE:** Usually no SPICE model

---

## 12. ic_opamp

**Type-Specific Fields:**
```sql
opamp_type TEXT,                    -- 'General Purpose', 'Precision', 'Low Noise', 'High Speed', 'Instrumentation', 'Comparator'
channels INTEGER,                   -- Number of amplifiers (1, 2, 4)
gbw_product TEXT,                   -- Gain-bandwidth product
slew_rate TEXT,                     -- Slew rate
input_offset_voltage TEXT,          -- Input offset voltage
input_bias_current TEXT,            -- Input bias current
input_impedance TEXT,               -- Input impedance
cmrr TEXT,                          -- Common-mode rejection ratio
supply_voltage_min TEXT,
supply_voltage_max TEXT,
supply_current TEXT,                -- Quiescent current
output_current TEXT,                -- Output current capability
noise_voltage TEXT,                 -- Input voltage noise density
rail_to_rail BOOLEAN,               -- Rail-to-rail input/output
temp_operating TEXT,
temp_junction_max TEXT
```

**SPICE:** Usually subcircuit model from manufacturer

---

## 13. ic_analog

**Type-Specific Fields:**
```sql
function_type TEXT,                 -- 'ADC', 'DAC', 'Comparator', 'Voltage Regulator', 'Voltage Reference', 'Multiplexer', 'Switch'
resolution TEXT,                    -- Resolution in bits (ADC/DAC)
channels INTEGER,                   -- Number of channels
sample_rate TEXT,                   -- Sample rate (ADC) / update rate (DAC)
interface TEXT,                     -- 'SPI', 'I2C', 'Parallel'
output_voltage TEXT,                -- Output voltage (regulators)
output_current TEXT,                -- Output current capability
dropout_voltage TEXT,               -- Dropout voltage (LDOs)
efficiency TEXT,                    -- Efficiency (switching regulators)
propagation_delay TEXT,             -- Propagation delay (comparators)
input_offset_voltage TEXT,          -- Input offset voltage
reference_voltage TEXT,             -- Reference voltage output
temp_coeff TEXT,                    -- Temperature coefficient
supply_voltage_min TEXT,
supply_voltage_max TEXT,
supply_current TEXT,
temp_operating TEXT,
temp_junction_max TEXT
```

**SPICE:** Depends on function; regulators and references often have models

---

## 14. leds

**Type-Specific Fields:**
```sql
color TEXT,                         -- 'Red', 'Green', 'Blue', 'White', 'Amber', 'RGB', 'IR', 'UV'
wavelength TEXT,                    -- Peak wavelength (e.g., '630nm')
forward_voltage TEXT,               -- Forward voltage (Vf)
forward_current TEXT,               -- Rated forward current (If)
luminous_intensity TEXT,            -- Luminous intensity (e.g., '50mcd', '1000mcd')
viewing_angle TEXT,                 -- Viewing angle (e.g., '120°')
led_type TEXT,                      -- 'Standard', 'High Brightness', 'RGB', 'Multi-color'
lens_type TEXT,                     -- 'Clear', 'Diffused', 'Water Clear'
temp_operating TEXT,
temp_storage TEXT
```

**SPICE:** `sim_device='D'`, can use diode model with Vf

---

## 15. switches

**Type-Specific Fields:**
```sql
switch_type TEXT,                   -- 'Tactile', 'Toggle', 'DIP', 'Slide', 'Rotary', 'Pushbutton', 'Rocker'
poles INTEGER,                      -- Number of poles (SPST=1, DPDT=2)
throw INTEGER,                      -- Number of throw positions (ST=1, DT=2)
circuit_config TEXT,                -- 'SPST', 'SPDT', 'DPDT', 'DPST'
actuation_force TEXT,               -- Actuation force (tactile switches)
travel_distance TEXT,               -- Total travel distance
mounting_type TEXT,                 -- 'Through-Hole', 'SMD', 'Panel Mount'
orientation TEXT,                   -- 'Vertical', 'Right Angle'
current_rating TEXT,                -- Current rating
voltage_rating TEXT,                -- Voltage rating
mechanical_life INTEGER,            -- Mechanical life (cycles)
temp_operating TEXT,
temp_storage TEXT
```

**SPICE:** Usually no model (mechanical device)

---

## Migration Notes

### Categorization Strategy

Components from the old `symbols` table will be categorized by:

1. **Reference field** - Primary categorization
   - `R` → resistors
   - `C` → capacitors
   - `L` → inductors
   - `FB` → ferrites
   - `Q` → transistors
   - `D` → diodes
   - `J` → connectors
   - `LED` → leds
   - `SW` → switches
   - `U`, `IC` → Need sub-categorization (see below)

2. **Component_Type or Description** - Secondary categorization for ICs
   - ICs need manual review or pattern matching to determine:
     - ic_drivers
     - ic_microcontrollers
     - ic_logic
     - ic_memory
     - ic_opamp
     - ic_analog

### Field Mapping Priority

1. Map core fields (standardized names, BOOLEAN conversions)
2. Map SPICE fields (if present in old data)
3. Map type-specific fields (varies by component type)
4. Set defaults for new fields not in old schema
5. Generate `part_id` if `Symbol_Name` doesn't meet new convention

### Data Quality

- Some old records may have incomplete data
- Type-specific fields may be NULL for older entries
- Migration script should validate required fields (part_id, mpn, manufacturer)
- Consider generating reports on data quality issues

---

## Evolution Plan

**Expected Changes:**
- Split ic_analog into more specific tables (ADC, DAC, regulators, references)
- Add ic_interface table for USB, Ethernet, CAN controllers
- Add ic_power table for PMICs, battery management
- Split connectors by type (usb, rf, power, signal)
- Add sensors table
- Add crystals/oscillators table
- Add fuses/protection table

**Flexibility:**
- New tables can be added at any time
- Existing tables can be migrated to new structures
- Round-trip dump/load ensures schema evolution is tracked
