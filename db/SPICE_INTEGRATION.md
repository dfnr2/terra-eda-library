# SPICE Simulation Integration

This document describes how the Terra EDA Library integrates SPICE simulation models for both KiCad (ngspice) and Altium Designer (MixedSim).

## Design Philosophy

**Unified SPICE Scheme:** The Terra EDA Library uses a single set of SPICE fields that work with both KiCad and Altium Designer. This is possible because:

1. Both tools are based on **SPICE3f5** standard
2. Both support **built-in primitives** (R, C, L, D, Q, M, etc.) without external files
3. Both support **subcircuit models** (`.SUBCKT`) in external `.lib` files
4. Both use standard SPICE netlist syntax

**Benefits:**
- Single SPICE model file serves both tools
- Easier maintenance (one library to manage)
- Standard SPICE3f5 models work everywhere
- Users can source models from any standard SPICE library

**Limitations:**
- Encrypted/proprietary models are simulator-specific and cannot be shared
- Some LTSpice-specific primitives (OTA, SCHMITT) may not work in Altium
- Some PSpice extensions may require adaptation

---

## SPICE Fields in Database

Every component type table includes these SPICE simulation fields:

```sql
sim_model_type TEXT,              -- Model type: 'primitive', 'subckt', or NULL
sim_device TEXT,                  -- Device primitive or subcircuit name
sim_pins TEXT,                    -- Pin mapping
sim_model_file TEXT,              -- Path to external .lib file (if needed)
sim_params TEXT                   -- Additional SPICE parameters (optional)
```

### Field Definitions

#### `sim_model_type`
Specifies how the component should be simulated.

- **`'primitive'`** - Built-in SPICE primitive (R, C, L, D, Q, M, etc.)
  - No external file needed
  - Uses component's `value` parameter
  - Works identically in both KiCad and Altium

- **`'subckt'`** - External subcircuit model
  - Requires external `.lib` or `.subckt` file
  - Uses `.SUBCKT` definition from file
  - File should be in `db/tables/{component_type}/spice/` directory

- **`NULL`** - No simulation model available
  - Component cannot be simulated
  - Acceptable for mechanical parts, test points, mounting holes, etc.

#### `sim_device`
The SPICE device type or subcircuit name.

**For primitives:**
- `'R'` - Resistor
- `'C'` - Capacitor
- `'L'` - Inductor
- `'D'` - Diode
- `'Q'` - BJT Transistor (NPN/PNP)
- `'M'` - MOSFET
- `'J'` - JFET
- etc.

**For subcircuits:**
- Name of the subcircuit (e.g., `'LM358'`, `'2N2222'`, `'BSS138'`)
- Must match the `.SUBCKT` name in the model file

#### `sim_pins`
Maps schematic symbol pins to SPICE model pins.

**Format:** Space-separated `pin=node` pairs

**Examples:**
- Resistor: `'1=+ 2=-'`
- Capacitor: `'1=+ 2=-'`
- Diode: `'1=A 2=K'` (Anode, Kathode)
- BJT: `'1=C 2=B 3=E'` (Collector, Base, Emitter)
- Op-Amp: `'1=IN+ 2=IN- 3=VCC 4=VEE 5=OUT'`

**Pin Numbering:**
- Numbers correspond to schematic symbol pin numbers
- Node names correspond to SPICE model pin order/names
- Order matters for primitives, names matter for subcircuits

#### `sim_model_file`
Path to external SPICE model file (`.lib`, `.subckt`, `.mod`).

**Format:** Use `${TERRA_EDA_LIB}` environment variable for portability

**Examples:**
- `'${TERRA_EDA_LIB}/db/tables/ic_opamp/spice/LM358.lib'`
- `'${TERRA_EDA_LIB}/db/tables/transistors/spice/2N2222.lib'`
- `NULL` for built-in primitives

**File Location Convention:**
```
db/tables/{component_type}/spice/{model_name}.lib
```

#### `sim_params`
Additional SPICE parameters (optional).

**Format:** Space-separated `param=value` pairs

**Examples:**
- BJT: `'BF=100 IS=1E-14 VAF=100'`
- MOSFET: `'VTO=2.0 KP=20u LAMBDA=0.01'`
- Resistor with temp coeff: `'TC1=0.001 TC2=0.000005'`

This field is rarely needed for standard models but allows fine-tuning.

---

## Usage Examples

### Example 1: Simple Resistor (Passive Primitive)

**Database Record:**
```sql
INSERT INTO resistors (
    part_id, mpn, manufacturer, value, resistance,
    kicad_symbol, kicad_footprint,
    sim_model_type, sim_device, sim_pins, sim_model_file, sim_params
) VALUES (
    'RES-001', 'RC0603FR-0710KL', 'Yageo', '10kΩ', 10000.0,
    'Device:R', 'Resistor_SMD:R_0603_1608Metric',
    'primitive', 'R', '1=+ 2=-', NULL, NULL
);
```

**How KiCad Uses This:**
```
Component Properties:
  Sim.Device = 'R'
  Sim.Pins = '1=+ 2=-'
  Value = '10k'

Generated Netlist:
  R1 Net-1 Net-2 10k
```

**How Altium Uses This:**
```
Component Properties:
  Sim Model Type = Generic SPICE Primitive
  Device = 'R'
  Value = '10k'

Generated Netlist:
  R1 Net-1 Net-2 10k
```

### Example 2: Simple Capacitor (Passive Primitive)

**Database Record:**
```sql
INSERT INTO capacitors (
    part_id, mpn, manufacturer, value, capacitance,
    kicad_symbol, kicad_footprint,
    sim_model_type, sim_device, sim_pins, sim_model_file, sim_params
) VALUES (
    'CAP-001', 'C0603C104K4RACTU', 'Kemet', '0.1µF', 0.0000001,
    'Device:C', 'Capacitor_SMD:C_0603_1608Metric',
    'primitive', 'C', '1=+ 2=-', NULL, NULL
);
```

**Generated Netlist (Both Tools):**
```
C1 Net-1 Net-2 0.1u
```

### Example 3: Operational Amplifier (Subcircuit)

**Database Record:**
```sql
INSERT INTO ic_opamp (
    part_id, mpn, manufacturer, value, channels, gbw_product,
    kicad_symbol, kicad_footprint,
    sim_model_type, sim_device, sim_pins, sim_model_file, sim_params
) VALUES (
    'OPAMP-001', 'LM358P', 'Texas Instruments', 'LM358', 2, '1MHz',
    'Amplifier_Operational:LM358', 'Package_DIP:DIP-8_W7.62mm',
    'subckt', 'LM358', '1=OUT 2=IN- 3=IN+ 4=VCC 5=VEE',
    '${TERRA_EDA_LIB}/db/tables/ic_opamp/spice/LM358.lib', NULL
);
```

**SPICE Model File:** `db/tables/ic_opamp/spice/LM358.lib`
```spice
* LM358 OPAMP MACRO-MODEL
.SUBCKT LM358 OUT IN- IN+ VCC VEE
  * (Standard SPICE3 subcircuit definition)
  * Internal circuitry...
.ENDS LM358
```

**Generated Netlist (Both Tools):**
```
XU1 Net-Out Net-InMinus Net-InPlus Net-VCC Net-VEE LM358
.INCLUDE '${TERRA_EDA_LIB}/db/tables/ic_opamp/spice/LM358.lib'
```

### Example 4: MOSFET (Primitive with Model)

**Database Record:**
```sql
INSERT INTO transistors (
    part_id, mpn, manufacturer, value, transistor_type,
    kicad_symbol, kicad_footprint,
    sim_model_type, sim_device, sim_pins, sim_model_file, sim_params
) VALUES (
    'MOSFET-001', 'BSS138', 'NXP', 'BSS138', 'N-Channel MOSFET',
    'Device:Q_NMOS_GDS', 'Package_TO_SOT_SMD:SOT-23',
    'primitive', 'M', '1=D 2=G 3=S',
    '${TERRA_EDA_LIB}/db/tables/transistors/spice/BSS138.lib', NULL
);
```

**SPICE Model File:** `db/tables/transistors/spice/BSS138.lib`
```spice
* BSS138 N-Channel MOSFET Model
.MODEL BSS138 NMOS (
+  LEVEL=3
+  VTO=1.8
+  KP=0.03
+  LAMBDA=0.01
+  ... )
```

**Generated Netlist (Both Tools):**
```
M1 Net-Drain Net-Gate Net-Source 0 BSS138
.INCLUDE '${TERRA_EDA_LIB}/db/tables/transistors/spice/BSS138.lib'
```

### Example 5: Connector (No Simulation Model)

**Database Record:**
```sql
INSERT INTO connectors (
    part_id, mpn, manufacturer, connector_type, pin_count,
    kicad_symbol, kicad_footprint,
    sim_model_type, sim_device, sim_pins, sim_model_file, sim_params
) VALUES (
    'CONN-001', '22-28-6040', 'Molex', 'Header', 4,
    'Connector:Conn_01x04_Pin', 'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
    NULL, NULL, NULL, NULL, NULL
);
```

**Result:** Component has no simulation model. If used in simulation, it acts as simple wire connections.

---

## Directory Structure for SPICE Models

```
db/tables/
├── resistors/
│   ├── resistors.sql
│   └── spice/                              # Optional: for special resistor models
│       └── high_voltage_divider.lib
├── capacitors/
│   ├── capacitors.sql
│   └── spice/                              # Optional: for complex capacitor models
│       └── tantalum_model.lib
├── transistors/
│   ├── transistors.sql
│   └── spice/
│       ├── 2N2222.lib                      # BJT model
│       ├── BSS138.lib                      # MOSFET model
│       └── README.md
├── diodes/
│   ├── diodes.sql
│   └── spice/
│       ├── 1N4148.lib
│       └── BAT54.lib
├── ic_opamp/
│   ├── ic_opamp.sql
│   └── spice/
│       ├── LM358.lib
│       ├── TL072.lib
│       └── OPA2134.lib
└── ic_analog/
    ├── ic_analog.sql
    └── spice/
        ├── LM317.lib
        └── TL431.lib
```

**Guidelines:**
- Store SPICE models alongside their component type
- Use standard `.lib` extension for SPICE files
- Include README.md documenting model sources and licenses
- Models should be standard SPICE3f5 format (not encrypted)

---

## Tool-Specific Behavior

### KiCad (ngspice)

**Primitive Behavior:**
- Reads `sim_device` and `sim_pins` from component properties
- Uses component's `Value` field for primitive value
- Built-in primitives: R, C, L, D, Q, M, J, etc.

**Subcircuit Behavior:**
- Reads `.SUBCKT` from `sim_model_file`
- Pin mapping from `sim_pins`
- Supports nested subcircuits

**Netlist Generation:**
```
* KiCad netlist format
R1 Net1 Net2 10k
C1 Net3 0 100n
XU1 NetOut NetInP NetInN NetVCC NetVEE LM358
.include /path/to/LM358.lib
```

### Altium Designer (MixedSim)

**Primitive Behavior:**
- Uses built-in generic simulation components
- Component value parameter sets primitive value
- Supports same primitives as ngspice

**Subcircuit Behavior:**
- Links to external `.lib` or `.mdl` file via Sim Model
- Supports `.SUBCKT` definitions
- Compatible with PSpice and LTSpice model variants (as of AD21+)

**Netlist Generation:**
```
* Altium MixedSim netlist format (SPICE3 compatible)
R1 Net1 Net2 10k
C1 Net3 0 100n
XU1 NetOut NetInP NetInN NetVCC NetVEE LM358
.include /path/to/LM358.lib
```

---

## Sourcing SPICE Models

### Standard Passives (R, C, L)
**No external model needed.** Use built-in primitives with `sim_model_type='primitive'`.

### Semiconductors (Diodes, Transistors)

**Sources:**
1. **Manufacturer websites** - Most semiconductor vendors provide SPICE models
2. **Component distributors** - Digi-Key, Mouser often host model files
3. **Community libraries:**
   - [KiCad-Spice-Library](https://github.com/kicad-spice-library/KiCad-Spice-Library)
   - [LTspice component library](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
   - Ensure models are unencrypted SPICE3 format

### ICs (Op-Amps, Regulators, etc.)

**Sources:**
1. **Manufacturer websites** - TI, Analog Devices, NXP, etc.
2. **Check license** - Most manufacturers allow free use for simulation
3. **Verify format** - Must be standard SPICE3, not encrypted

**License Note:** Always check model license terms. Most manufacturers provide models free for simulation but may restrict redistribution.

---

## Validation and Testing

### Testing a SPICE Model

**In KiCad:**
1. Create test schematic with component
2. Open Simulator (Tools → Simulator)
3. Run operating point analysis
4. Verify component appears in netlist correctly

**In Altium:**
1. Create test schematic with component
2. Open Mixed Sim (Simulate → Mixed Sim)
3. Run DC operating point analysis
4. Check component netlist in simulation setup

### Common Issues

**Issue:** "Unknown device type"
- **Cause:** `sim_device` doesn't match SPICE primitive or subcircuit name
- **Fix:** Verify device name matches model definition

**Issue:** "Pin mismatch"
- **Cause:** `sim_pins` mapping doesn't match schematic or model
- **Fix:** Check pin numbers in symbol vs. model pin order

**Issue:** "Cannot find model file"
- **Cause:** `sim_model_file` path is incorrect or file doesn't exist
- **Fix:** Verify path and that `${TERRA_EDA_LIB}` is set correctly

**Issue:** "Model convergence failed"
- **Cause:** SPICE model has numerical issues or component values are extreme
- **Fix:** Check component values, add .OPTIONS statements, or simplify model

---

## Best Practices

1. **Always populate SPICE fields for active components** (transistors, ICs)
2. **Populate SPICE fields for passives** when simulation is expected
3. **Leave SPICE fields NULL** for mechanical parts (connectors, mounting holes)
4. **Test models** in both KiCad and Altium before committing
5. **Document model sources** in `spice/README.md` files
6. **Use standard SPICE3 format** for maximum compatibility
7. **Avoid encrypted models** - they're simulator-specific
8. **Keep models organized** by component type in separate directories

---

## Future Enhancements

- **Automated model validation** during database build
- **Model library browser** tool
- **Automatic model download** from manufacturer websites
- **Simulation test suite** for all components with models
- **Model performance database** (convergence, accuracy ratings)

---

## References

- [SPICE3 Manual](http://bwrcs.eecs.berkeley.edu/Classes/IcBook/SPICE/)
- [ngspice Documentation](https://ngspice.sourceforge.io/docs.html)
- [KiCad SPICE Simulation](https://www.kicad.org/discover/spice/)
- [Altium SPICE Simulation](https://www.altium.com/documentation/altium-designer/circuit-simulation)
- [SPICE Model Guidelines (IEEE)](https://standards.ieee.org/)
