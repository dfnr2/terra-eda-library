# Vintage computer parts

**Date:** 2026-11-17
**Status:** Phase 1 done (see Results). Decisions in "Open questions" are needed before
phases 3, 4 and 6.
**Scope:** bring terra up to the point where a 1975-85 microcomputer (KIM-1, Apple I/II,
SWTPC, S-100, COSMAC ELF, TRS-80, Z80 SBC, or a modern retro build) can be drawn with
fully qualified parts. That means the bus buffers, memory, CPUs and their support chips,
plus the passives and connectors those boards are built from.

## Starting point

What terra already has (row counts from `db/terra.db`, 2026-11-17):

| Area | Table | Today |
|---|---|---|
| Bus buffers | `ic_logic` (790) | 74LS/HC '240/'241/'244/'365-'368. No 8T parts. |
| Memory | `ic_memory` (4) | Only the 24LC32A. No parallel SRAM, EPROM or EEPROM. |
| CPUs, peripherals | `ic_microcontrollers` (71) | Modern MCUs (ATmega etc.). No CPU table, no peripheral table. |
| Electrolytics | `capacitors_electrolytic_th` (118) | Chemi-Con KYC low-ESR radial only. No axial. |
| Connectors | `connectors` (151) | EDAC 307 44-pin 0.156" card edge, KK 254. No KK 396. |
| Crystals | none | No table. |
| Trimpots | none | No table. |

KiCad 10's stock libraries already have symbols for a good share of these, and we should
use them where the pinout matches (checked in `/usr/share/kicad/symbols`):

- **CPU:** MC6800/6802/6809/6809E (+A/B speed grades), CDP1802ACE/BCE, Z84C00 (Z80),
  8080/8080A, 8088.
- **Peripherals:** 6821, MC6840/6843/6844, MC6845, MC6850, Z8420/Z84C20 (PIO), Z8530 (SCC),
  8253, 8255/8255A, 8259/8259A.
- **Memory:** MK4116, MK4164, HY6264, 62256 (CY/HM/KM), 2764/27128/27256/27512, 27C64-27C080,
  28C256, KM28C64A.
- **Passives:** `Device:Crystal`, `Device:R_Potentiometer_Trim`, with stock
  `Crystal:` and `Potentiometer_THT:` footprints (Bourns 3296/3362 among them).

Missing, so these need custom symbols: 6502/65C02, 6520 (but it shares the 6821 pinout,
so check whether `Interface:6821` can be reused), 6522, 6530/6532, 6551, 6847, 8085, 8212,
8216, 8224, 8228, 8238, 8251, Z80 CTC/SIO/DART/DMA, CDP1852/1853/1854/1861, every 8T part,
and the 1702/2101/2102/2111/2114/6116/2708/2716/2516/2732/2532/2816/2817 memories.

## Cross-cutting decisions

**Lifecycle and orderability.** Most of these are no longer made. Their rows carry
`lifecycle_status = 'Obsolete'` and are still useful: they are what restorers and kit
builders order as NOS/surplus, and Rochester Electronics still sells a number of them as
an authorized after-market source. Check each family against Digi-Key/Mouser and Rochester
before marking it, as the lifecycle memory says, and don't assume. Where a modern
drop-in is still in production, add it as its own Active row next to the original,
for example WDC W65C02S/W65C22/W65C51N, Alliance AS6C6264/AS6C62256 for 6264/62256, and
Microchip AT28C64B/AT28C256.

**Manufacturer coverage.** These parts were heavily second-sourced (a 2114 came from
Intel, AMD, NEC, Hitachi, Mostek and more), and every manufacturer-MPN pair is its own
row. Proposed default: the **originator**, plus **one common second source** where we can
park a datasheet for it, plus the **modern drop-in** if one exists. More second sources
can be switched on per family later. Needs Dave's call (Q1).

**Speed and package grades.** Every speed grade the datasheet lists is its own MPN
(2114-2/-3/-L, 6116-15/-20, MC68A09/MC68B09, 2716-1). Generate them all, since a
generator makes that cheap. Packages: plastic DIP and ceramic DIP where both were sold.
UV EPROMs are windowed ceramic only.

**Manufacturer link.** Use the successor's product page when there is one (Renesas for
CDP1802, Microchip for Atmel EEPROMs, Littelfuse/Zilog for Z80). For defunct
manufacturers (MOS, Signetics, Mostek, Synertek) leave it NULL rather than inventing
a link.

**Datasheets.** Park local PDFs in `datasheets/<mfr>/` as usual. The new manufacturer
directories will be `signetics`, `national`, `intel`, `mos`, `motorola`, `zilog`, `rca`,
`mostek`, `hitachi`, `synertek`, `rockwell`, `wdc`, `alliance` (plus existing `ti`,
`microchip`, `renesas`, `bourns`). Sources are bitsavers and manufacturer data books.
Name the data book in the plan section for each family so the scan can be found again.

**Symbol tooling.** About 40 custom DIP symbols is too many to draw by hand. Add a small
pin-table-driven writer, `tools/make_dip_symbol.py`: a pin list (number, name, electrical
type, side) goes in, and an entry in `kicad_symbols/terra_symbols_<table>.kicad_sym` comes
out, in the stock 74xx/Memory style. Each family's pin tables sit beside its generator,
so a pinout fix is one line plus a regenerate. Footprints are stock
`Package_DIP:DIP-nn_W7.62mm` / `W15.24mm` throughout, so no custom footprints are needed for
the ICs.

## Phases

Ordered by dependency and payoff. The passives/connectors phases (7-9) don't depend on
anything else and can run in parallel at any time.

### Phase 1: 8T bus buffers (`ic_logic`, `run_340_8t_buffers.py`)

Signetics 8T26/8T28 (quad inverting / non-inverting bus transceiver), 8T95/8T96/8T97/8T98
(hex 3-state buffers, the high-drive parts that 74LS365-368 replaced). Signetics N-grade
(commercial) in the N-suffix plastic and F-suffix ceramic DIPs (N8T97N, N8T97F), per the
Signetics Logic data book. National's DM8095-DM8098 should be the same functions; confirm
from their data book and add them as the second source if the page turns up. `logic_family = '8T'`, `output_current` from the datasheet (about 48 mA sink).
Custom symbols in `terra_symbols_ic_logic`. Small (about 12-16 rows) and needs no schema
change, so it's the shakedown for the datasheet/symbol-tool conventions above.

### Phase 2: memory (`ic_memory`)

Existing table. Its columns (`memory_type`, `capacity`, `word_size`, `speed`,
`interface`, `persistence_*`) fit, with one gap: vintage EPROMs and early RAMs need
multiple supply rails and a programming voltage, and those are exactly what decides
whether a part works in a given socket or programmer. Proposed fragment additions,
for review:

| Column | Type | Why |
|---|---|---|
| `supply_rails` | TEXT | `+5V` vs `+5V,-5V,+12V` (2708, TMS2716, 4116). Shared with phases 3-4. |
| `programming_voltage` | TEXT | Vpp: 25 V (2716/2732), 21 V (2732A/2764A), 12.5 V (27C); `n/a` for RAM. |

Families, each its own generator:

- `run_310_vintage_sram.py`: 2101 (256x4, 22-pin), 2102 (1Kx1), 2111/2112, 2114 (1Kx4),
  6116 (2Kx8), 6264 (8Kx8), 62256 (32Kx8), plus the Alliance AS6C drop-ins.
  CDP1822/CDP1824 go here too, for the 1802 boards.
- `run_320_eprom.py`: 1702A, 2708, Intel 2716 vs **TMS2716** (TI's three-supply part with a
  2708-like pinout; easy to confuse), TMS2516 (Intel-2716 pinout), 2732 vs 2732A vs TMS2532
  (different pins 18/20/21), 2764/27128/27256/27512 and CMOS 27C equivalents. The
  description must spell out each pinout/Vpp difference, because swapping these is the
  classic way to kill a part.
- `run_330_parallel_eeprom.py`: 2816/2817 (Xicor/Seeq), 28C16, 28C64/AT28C64B, 28C256/AT28C256.
- DRAM (4116/4164/41256) is not on the list but sits next to the 2114 in this era. Q5.

### Phase 3: CPUs (new table `ic_microprocessors`)

`ic_microcontrollers` is the wrong home: its tail is flash/RAM/GPIO/peripheral counts,
and all of those would be NULL for a 6502. Proposed fragment `ic_microprocessors`
(reusing names from `ic_microcontrollers` where the meaning matches):

| Column | Type | Why |
|---|---|---|
| `family` | TEXT | reuse: `6502`, `6800`, `6809`, `Z80`, `8080`, `8085`, `1802` |
| `core` | TEXT | reuse: `NMOS 6502`, `CMOS 65C02`, `Z80A` … |
| `technology` | TEXT | new: NMOS / CMOS / HMOS; drives power, static clocking, 5 V tolerance |
| `architecture_bits` | INTEGER | reuse |
| `address_bus_bits` | INTEGER | new: 16 for most, 20 for 8088 |
| `max_clock` | TEXT | reuse: speed grade, e.g. `2 MHz` (MC68B09) |
| `supply_voltage_min` / `_max` | REAL | reuse |
| `supply_rails` | TEXT | shared with `ic_memory`: 8080 needs +5/-5/+12 |
| `special_features` | TEXT | reuse: on-chip clock (6802, 8085), on-chip RAM (6802), DRAM refresh (Z80) |

Generators by family: `run_300_6502.py` (MOS/Rockwell/Synertek 6502/6503-6507, WDC W65C02S),
`run_310_6800.py` (6800/6802/6808/6809/6809E), `run_320_z80.py` (Zilog Z80/Z80A/Z80B NMOS,
Z84C00 CMOS), `run_330_8080.py` (8080A/8085A), `run_340_1802.py` (CDP1802A/AC/BC).

### Phase 4: support chips (new table `ic_peripherals`)

Same reasoning as phase 3. A separate table rather than one "vintage" table, because
modern bus peripherals (16550 UART, 82C55) belong here later too.

| Column | Type | Why |
|---|---|---|
| `family` | TEXT | bus family it was designed for: `6800`, `6502`, `8080`, `Z80`, `1802` |
| `peripheral_function` | TEXT | PIA / VIA / ACIA / UART / CRTC / VDG / PPI / timer / interrupt controller / DMA / clock generator / system controller / bus driver |
| `technology` | TEXT | shared with phase 3 |
| `max_clock` | TEXT | bus speed grade (6821 vs 68A21 vs 68B21) |
| `io_lines` | INTEGER | e.g. 20 for 6522 (PA, PB, CA1/2, CB1/2) |
| `channels` | INTEGER | reuse from `ic_logic`: timers, serial channels |
| `supply_voltage_min` / `_max`, `supply_rails` | REAL / TEXT | shared |
| `special_features` | TEXT | e.g. 6532 has 128 B RAM; 6530 has mask ROM |

Families:

- **6502:** 6520, 6522, 6530, 6532, 6551 (+ W65C22, W65C51N). Q3 covers "6550".
- **6800/6809:** 6820/6821, 6840, 6843, 6844, 6845, 6847, 6850, 6852, 6854.
- **Z80:** PIO (Z8420), CTC (Z8430), SIO/0-2 (Z8440-2), DART (Z8470), DMA (Z8410), CMOS Z84Cxx.
- **8080:** 8212, 8216/8226, 8224, 8228/8238, 8251, 8253, 8255, 8257, 8259, 8279.
- **1802:** CDP1852, CDP1853, CDP1854, CDP1861 (Pixie).

### Phase 5: modern parallel EEPROM

Folded into phase 2 (`run_330_parallel_eeprom.py`). Listed here only because the request
named it separately.

### Phase 6: crystals (new table `crystals`)

| Column | Type | Why |
|---|---|---|
| `frequency` | TEXT | `3.579545MHz`; also `value` on the schematic |
| `load_capacitance` | TEXT | `18pF` or `series`. Vintage oscillator circuits often want series-resonant. |
| `frequency_tolerance` | TEXT | ±ppm at 25 °C |
| `frequency_stability` | TEXT | ±ppm over temperature |
| `esr_ohm` | TEXT | reuse name from electrolytics |
| `oscillation_mode` | TEXT | fundamental / 3rd overtone (matters above ~20 MHz) |
| `drive_level` | TEXT | µW max |

Package (HC-49/U, HC-49/US) goes in core `package`. Seed: one current HC-49 family
(Abracon AB/ABL or ECS) at the classic frequencies: 1.0, 1.8432, 2.0, 2.4576, 3.579545,
3.6864, 4.0, 4.194304, 4.9152, 6.0, 7.3728, 8.0, 10.0, 12.0, 14.31818, 16.0, 17.734475,
18.432, 20.0 MHz. Whether DIP-14/DIP-8 can oscillators share this table is Q4.

### Phase 7: through-hole trimpots (new table `potentiometers_th`)

The tail reuses `resistors_th` names. `value` is the resistance.

| Column | Type | Why |
|---|---|---|
| `tolerance`, `power_rating`, `temp_coeff` | TEXT | reuse from `resistors_th` |
| `composition` | TEXT | reuse: cermet / carbon |
| `turns` | INTEGER | new: 1 vs 25 changes the part's use |
| `adjustment` | TEXT | new: top / side |

Seed: Bourns 3296 (W top, Y side; 25-turn 3/8") and 3362 (P/H/U; single-turn 1/4") in the
standard 1-2-5 decade values, 10 Ω-2 MΩ, on stock `Potentiometer_THT:` footprints.

### Phase 8: vintage connectors (`connectors`)

- `run_370_molex_kk396.py`: Molex KK 396 (0.156") friction-lock headers, straight and
  right-angle, 2-18 positions, plus the mating crimp housings (`mates_with` filled both
  ways). This is the SWTPC/arcade/power-harness connector.
- `run_380_card_edge.py`: card-edge sockets by bus (Q2). Candidates are S-100 (100 pos,
  0.125"), Apple II slot (50 pos, 0.100"), KIM-1/AIM-65 (44 pos, 0.156", same as the EDAC 307
  already in terra) and 22/44-pin 0.156" generic. The EDAC 307 work showed the hard part:
  card-edge datasheets are scarce. Sullins EBC was dropped for lack of one, so we only
  commit to series with a parked drawing.

### Phase 9: through-hole electrolytics (`capacitors_electrolytic_th`)

KYC is low-ESR. Vintage boards want general-purpose radials and, on restorations,
**axials**. Proposed: one general-purpose radial family (Nichicon UVR or Panasonic ECA)
as `run_510_*`, and one axial family (Vishay BCcomponents 021 ASM or Nichicon TVX) as
`run_520_*`. Axial vs radial goes in core `package`, so the schema doesn't change.
Watch the fragment's `low_esr DEFAULT 'yes'`: these generators must set `'no'`
explicitly.

## Open questions for Dave

1. **Second sources:** originator + one second source + modern drop-in (proposed), or
   originator only, or everyone we can find a datasheet for?
2. **Card-edge buses:** which of S-100 / Apple II / KIM-1 / generic 0.156" do you need?
3. **"6550":** the MOS 6550 is the PET 2001's 1Kx4 static RAM, not an I/O chip. Did you
   mean the 6530 (RRIOT) or 6532 (RIOT)? Or do you want the 6550 RAM in phase 2?
4. **Crystal oscillators** (DIP-14/DIP-8 cans): in `crystals` with an output/supply
   column, a separate table later, or not at all?
5. **DRAM** (4116/4164/41256): add to phase 2?
6. **Schema reviews:** the column tables in phases 2, 3, 4, 6 and 7 need sign-off before
   their fragments are written.

## Results

### Phase 1: 8T bus buffers (done 2026-11-18)

17 parts in `ic_logic` from `run_340_8t_buffers.py`, `logic_family = '8T'`, all Obsolete.

- **Coverage:** every code in the ordering tables of the Signetics *Logic Interface*
  book (Oct 1981). Commercial N8T26AN/AF, N8T28N/F, N8T95-N8T98 N/F, plus military
  S8T26AF, S8T28F, S8T95F, S8T97F, S8T98F. The book lists no S8T96.
- **Datasheets:** the two sections were extracted from the bitsavers scan into
  `datasheets/signetics/8t26a-8t28-quad-bus-transceiver.pdf` (book pp. 65-70) and
  `8t95-8t98-hex-3-state-buffers.pdf` (pp. 71-74).
- **Symbols (IEEE style):** 8T95/96/97/98 match the 74365/366/367/368 pin for pin and use
  stock `74xx_IEEE:74LS365`-`368`. 8T26A/8T28 got new IEEE-style symbols in
  `terra_symbols_ic_logic` (`8T26A`, `8T28`), following `74xx_IEEE:74LS242` and the
  book's IEEE/IEC drawing: a control block (~RE pin 1, DE pin 15) over four sections
  of Rn / Bn / Dn. The bus pins are bidirectional, and the 8T26A's are named ~Bn
  because both its directions invert.
- **Footprint:** `Package_DIP:DIP-16_W7.62mm` for both plastic and ceramic. KiCad's
  `CERDIP-16` footprints are side-brazed, which the F package is not.
- **Manufacturer link:** NXP's obsolete-products page (the Signetics successor's
  route to authorized EOL resellers), because no product page exists.

Follow-ups:
- National DM8095-DM8098 (second source) not added: no data book page parked yet.
- A Rochester Electronics "8T28PC" turned up in a reseller listing. That may be a
  current after-market 8T28 worth adding if a datasheet can be found.
