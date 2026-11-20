# Vintage computer parts

**Date:** 2026-11-17
**Status:** Phase 1 done; phase 2 schema, SRAM and DRAM done (see Results). EPROM,
EEPROM and PROM are next. Decisions in "Open questions" are needed before phases 3, 4
and 6.
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

**Manufacturer coverage (decided 2026-11-18).** These parts were heavily second-sourced
(a 2114 came from Intel, AMD, NEC, Hitachi, Mostek and more), and every manufacturer-MPN
pair is its own row. **One classic example per chip**, usually the originator or the
best-known maker (Intel 2114, MOS 6502, Zilog Z80). Nobody buys these from the
manufacturer any more, so extra second-source rows add nothing. A **modern drop-in that
is still in production** (W65C02S, AS6C62256, AT28C256) is a different, orderable part
and still gets its own Active row.

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
Signetics Logic data book. `logic_family = '8T'`, `output_current` from the datasheet (about 48 mA sink).
Custom symbols in `terra_symbols_ic_logic`. Small (about 12-16 rows) and needs no schema
change, so it's the shakedown for the datasheet/symbol-tool conventions above.

### Phase 2: memory (`ic_memory`)

Existing table. Its columns (`memory_type`, `capacity`, `word_size`, `speed`,
`interface`, `persistence_*`) fit, plus two additions (approved 2026-11-18):

| Column | Type | Why |
|---|---|---|
| `supply_rails` | TEXT | `+5V` vs `+5V,-5V,+12V` (2708, TMS2716, 4116). Shared with phases 3-4. |
| `programming_voltage` | TEXT | Vpp: 25 V (2716/2732), 21 V (2732A/2764A), 12.5 V (27C); NULL for RAM and mask/fuse parts where it doesn't apply. |

`memory_type` values: `SRAM`, `DRAM`, `NVRAM`, `EPROM` (UV-erasable), `OTP EPROM`,
`EEPROM`, `flash`, `PROM` (bipolar fusible link).

**Grades and packages (decided 2026-11-18):** one row for each speed/power grade the
classic datasheet lists (2114-2/-3/-4 and the L versions, HM6116P-2/-3/-4, 2716 and
2716-1). All grades of a chip share its symbol and footprint, so the extra rows cost
nothing. Each maker's speed suffixes mean something different (one maker's -2 is
250 ns, another's is 200 ns), so `speed` comes from that book's grade table, never
from the suffix. Commercial temperature only, plastic DIP. Ceramic only where it is the
only option: windowed UV EPROMs and some bipolar PROMs.

**Symbols:** stock KiCad already covers 2764/27128/27256/27512, 27C64-27C080, 28C256,
KM28C64A (28C64 pinout), MK4116, MK4164, TMM41256, HY6264, HM62256, HM628128 and
AS6C1008/4008. The rest need custom symbols in `terra_symbols_ic_memory`, one per distinct
pinout rather than per chip, drawn in the stock Memory_* style (pin-labeled rectangle
with address/data/control grouped).

The candidate list below names one classic example per chip (see "Manufacturer coverage").
Pinouts, pin counts and supplies are from memory and get checked against each data
book before generation.

#### Static RAM (`run_310_sram.py`)

| Chip | Classic example | Org | Pins | Notes |
|---|---|---|---|---|
| 2101A | Intel | 256x4 | 22 | separate I/O |
| 2102A | Intel | 1Kx1 | 16 | Altair-era memory boards |
| 2111A, 2112A | Intel | 256x4 | 18, 16 | common I/O |
| 2114, 2114L | Intel | 1Kx4 | 18 | the classic small-system RAM |
| 2147 | Intel | 4Kx1 | 18 | fast NMOS |
| 5101 | Intel | 256x4 | 22 | CMOS, battery backup |
| MCM6810 | Motorola | 128x8 | 24 | 6800-family RAM |
| 7489, 74S189 | TI | 16x4 | 16 | TTL scratchpad RAM (OC / 3-state) |
| CDP1822, CDP1824 | RCA | 256x4, 32x8 | | 1802 systems |
| HM6116 | Hitachi | 2Kx8 | 24 | CMOS, JEDEC byte-wide |
| HM6264 | Hitachi | 8Kx8 | 28 | |
| HM62256 | Hitachi | 32Kx8 | 28 | |
| HM628128 | Hitachi | 128Kx8 | 32 | retro builds |
| AS6C6264, AS6C62256, AS6C1008, AS6C4008 | Alliance | 8K-512Kx8 | 28/32 | modern drop-ins, Active |
| DS1225, DS1230 | Dallas | 8Kx8, 32Kx8 | 28 | battery-backed NVRAM, 6264/62256 sockets (optional) |

#### Dynamic RAM (`run_320_dram.py`)

| Chip | Classic example | Org | Pins | Supplies |
|---|---|---|---|---|
| 1103 | Intel | 1Kx1 | 18 | multi-rail, the first commercial DRAM |
| MK4096, MK4027 | Mostek | 4Kx1 | 16 | +12/+5/-5 |
| 2118 | Intel | 16Kx1 | 16 | +5 only (optional) |
| MK4116 | Mostek | 16Kx1 | 16 | +12/+5/-5 (TRS-80, Apple II) |
| MK4164 | Mostek | 64Kx1 | 16 | +5 |
| TMM41256 | Toshiba | 256Kx1 | 16 | +5 |
| TMS4416 | TI | 16Kx4 | 18 | +5 |
| TMS4464 | TI | 64Kx4 | 18 | +5 (41464 equivalent) |

#### UV EPROM (`run_330_eprom.py`)

| Chip | Classic example | Org | Pins | Supplies / Vpp |
|---|---|---|---|---|
| 1702A | Intel | 256x8 | 24 | multi-rail PMOS |
| 2704, 2708 | Intel | 512x8, 1Kx8 | 24 | +12/+5/-5; pulsed programming |
| TMS2716 | TI | 2Kx8 | 24 | three-supply, 2708-like pinout, **not** an Intel 2716 |
| 2716 | Intel | 2Kx8 | 24 | +5, Vpp 25 V |
| TMS2516 | TI | 2Kx8 | 24 | Intel-2716 pinout |
| 2732, 2732A | Intel | 4Kx8 | 24 | Vpp 25 V / 21 V on OE |
| TMS2532 | TI | 4Kx8 | 24 | different pins 18/20/21 from 2732 (Commodore) |
| MCM68764 | Motorola | 8Kx8 | 24 | 24-pin 8K for 2364 mask-ROM sockets (optional) |
| 2764, 2764A | Intel | 8Kx8 | 28 | Vpp 21 V / 12.5 V |
| 27128, 27128A | Intel | 16Kx8 | 28 | |
| 27256, 27512 | Intel | 32Kx8, 64Kx8 | 28 | |
| M27C64A ... M27C512, M27C1001-M27C4001 | ST | 8Kx8-512Kx8 | 28/32 | CMOS, 12.5 V; the last big UV maker |

Modern, still in production (Active): Microchip AT27C256R, AT27C512R, AT27C010,
AT27C020, AT27C040 (OTP, not erasable), and SST39SF010A/020A/040 (5 V flash, reads
in 27C010-040 sockets).

#### Parallel EEPROM (`run_340_parallel_eeprom.py`)

| Chip | Classic example | Org | Pins | Notes |
|---|---|---|---|---|
| 2816 | Intel | 2Kx8 | 24 | 21 V write |
| X2816 | Xicor | 2Kx8 | 24 | 5 V-only |
| 2817A | Intel | 2Kx8 | 28 | RDY/BUSY |
| AT28C16 | Atmel | 2Kx8 | 24 | 6116/2716 socket |
| AT28C64B | Microchip | 8Kx8 | 28 | Active |
| AT28C256 | Microchip | 32Kx8 | 28 | Active; retro-build favorite |
| AT28C010 | Microchip | 128Kx8 | 32 | Active (optional) |

#### Bipolar fusible-link PROM (`run_350_bipolar_prom.py`)

Signetics 82S is the family name arcade and MAME documentation uses, so it is the
classic example. TI/MMI equivalents (74S288, TBP18S030, 6331) go into keywords.

| Chip | Org | Pins | Output |
|---|---|---|---|
| 82S23 / 82S123 | 32x8 | 16 | OC / 3-state |
| 82S126 / 82S129 | 256x4 | 16 | OC / 3-state |
| 82S130 / 82S131 | 512x4 | 16 | OC / 3-state |
| 82S137 | 1Kx4 | 18 | 3-state |
| 82S185 | 2Kx4 | 18 | 3-state |
| 82S147 | 512x8 | 20 | 3-state |
| 82S181 | 1Kx8 | 24 | 3-state |
| 82S191 | 2Kx8 | 24 | 3-state |

Out of scope: mask ROMs (custom-programmed, so nothing to order) and programmable logic
(82S100 FPLA, PAL/GAL). A later phase could cover GALs, since ATF16V8B/ATF22V10C are
still made and widely used in retro builds.

#### Phase 2 implementation guide

Written so phase 2 can be picked up cold. Read the `add-terra-table` skill first. The
closest worked example is phase 1, `db/tables/ic_logic/run_340_8t_buffers.py`, and its
commit `0bcfb97`: data-book extraction, every ordering code, Obsolete lifecycle,
symbol reuse plus custom symbols.

**Order of work.** Schema first, then the families in this order: SRAM (the shakedown,
and it builds the symbol tool), DRAM, EPROM, EEPROM, PROM. Make one commit per family
(generator, extracted datasheets, symbols, Results entry). The schema change goes in
with the SRAM commit.

**Step 0: schema.** Add `supply_rails TEXT` and `programming_voltage TEXT` to
`db/schema/types/ic_memory.sql` after `persistence_years`, then run `make schema`. That
regenerates `ic_memory_0_schema.sql`; never hand-edit it. The existing
`run_300_terra_sym_harvest.py` uses named INSERTs, so it is unaffected. New columns
become KiCad fields automatically (`tools/generate_kicad_dbl_files.py` maps every column
except a fixed skip list), so no tool changes are needed.

**Step 1: sources.** Every chip's datasheet comes from a manufacturer data book, cut down
to that chip's pages. Data books on bitsavers (mirror
`https://ftp.mirrorservice.org/sites/www.bitsavers.org/components/<mfr>/_dataBooks/`):

| Maker | Book(s) | Covers |
|---|---|---|
| Intel | 1978/1979/1981 Component Data Catalog; 1983 Memory Component Handbook; 1981 E2PROM Family Applications Handbook | 1103, 2101A-2147, 5101, 2118, 1702A, 2704/2708, 2716, 2732/A, 2764/A, 27128/A, 27256, 27512, 2816, 2817A |
| Mostek | 1980 Memory Data Book and Designers Guide | MK4096, MK4027, MK4116, MK4164 |
| TI | 1980 MOS Memory Data Book; 1984 MOS Memory Data Book; TTL data book for 7489/74S189 | TMS2516, TMS2532, TMS2716, TMS4416, TMS4464 |
| Hitachi | 1984 IC Memory Data Book; 1988/1990 M11 IC Memory Data Book | HM6116, HM6264, HM62256, HM628128 |
| Signetics | 1984 Bipolar LSI Data Manual; 1977 Bipolar and MOS Memory | 82S PROMs |
| Motorola | 1979 Memory Data Book | MCM6810, MCM68764 |
| RCA | 1982 CMOS Microprocessors, Memories and Peripherals | CDP1822, CDP1824 |
| Xicor | `components/xicor/1985_Xicor_Data_Book.pdf` | X2816 |

Not on bitsavers: Toshiba TMM41256 and ST M27C (try st.com, then datasheet archives),
Dallas DS1225/DS1230 (analog.com). Use the manufacturer's current site for the modern
parts: Microchip AT27C/AT28C/SST39SF and Alliance AS6C.

Procedure, as in phase 1:
1. Download the book into its own scratch directory.
2. Find the chip's pages with a per-page `pdftotext` scan for the part number.
3. Render the pin-configuration, ordering-code and package-outline pages with `pdftoppm`
   and read them. Pinouts are drawn as images and the text layer misses them.
4. Cut the section out with `pdfseparate` + `pdfunite` into `datasheets/<mfr>/<slug>.pdf`
   (Git LFS picks it up). Slugs look like `2114-1kx4-static-ram.pdf` or
   `82s123-82s23-32x8-bipolar-prom.pdf`.
5. Record the book title and page range in the generator docstring and in Results.

**Step 2: ordering codes and MPNs.** Emit only codes the book's ordering table lists,
and never build one from a pattern. Prefix and suffix letters encode package,
temperature and speed, and they differ by maker. These examples need checking against
each book: Intel P (plastic) / D (CERDIP) / C (ceramic) prefixes such as P2114 and
D2716; Hitachi HM6116P-3; Mostek MK4116N-3; TI TMS2516JL; Signetics N82S123N. Emit
every speed/power grade in the ordering table, one row each, all sharing the chip's
symbol and footprint. Fill `speed` from the grade table's access time. Take commercial
temperature only.

**Step 3: field conventions.**

| Column | Convention |
|---|---|
| `unique_id` | `<Manufacturer>-<MPN>`; fail on a duplicate |
| `value` | chip name: `2114`, `2716`, `82S123`, `AT28C256` |
| `part_locator` | lowercase functional key, e.g. `mem-sram-1kx4-dip18`, `mem-eprom-2kx8-dip24` |
| `description` | maker, chip, organization, type, speed, package, plus any pinout or Vpp caution (see pitfalls) |
| `memory_type` | one of the values listed at the top of phase 2 |
| `capacity`, `word_size` | match the existing row's format: `4 Kbit`, `4-bit` |
| `speed` | access time of the grade: `450 ns` |
| `interface` | `parallel` |
| `supply_rails` | most positive first, comma-separated: `+5V` or `+12V, +5V, -5V` |
| `programming_voltage` | `25V`, `21V`, `12.5V`; NULL for RAM; for fuse PROMs only if the book gives one figure |
| `persistence_cycles` / `_years` | EEPROM endurance/retention, and EPROM retention, when the book states them; else NULL |
| `lifecycle_status` | `Obsolete` for vintage parts. Modern parts: check Digi-Key/Mouser and recent PCNs; `Active` only if an authorized distributor still sells it. |
| `rohs` | `No` for vintage; modern parts per their datasheet |
| `manufacturer_link` | the product page if one still exists; else the successor's obsolete-parts page (as Signetics -> NXP in phase 1); else NULL |
| `keywords` | chip name, organization (`1Kx4`), type words (`SRAM, static RAM`), `vintage`, equivalent part numbers |
| `source` / `dump_priority` / `tier` | NULL / 0 / 2; `created_by` = script name; INSERTs name their columns |

**Step 4: footprints.** Take the row spacing from the book's package-outline page, never
from the pin count:
- 16/18/20-pin parts are normally 0.3": `Package_DIP:DIP-nn_W7.62mm`.
- 22-pin parts (2101A, 5101) are often 0.4": `DIP-22_W10.16mm`. Check each.
- 24/28/32-pin byte-wide parts are normally 0.6": `DIP-nn_W15.24mm`. But bipolar PROMs
  and "skinny" RAMs (some 82S181/82S191 codes, 62256 "SP" parts) come in 0.3" bodies
  that need `DIP-nn_W7.62mm`. The ordering code tells them apart.
- Ceramic and windowed packages use the same land pattern, so use the stock DIP
  footprint. KiCad's `CERDIP-*` footprints are side-brazed only.

**Step 5: symbols.** Reuse a stock symbol only when its pinout matches the chip pin for
pin: Memory_EPROM 2764/27128/27256/27512/27C64-27C080, Memory_EEPROM 28C256/KM28C64A,
Memory_RAM MK4116N/MK4164N/TMM41256AP/HY6264/HM62256/HM628128/AS6C1008/AS6C4008.
Everything else gets a custom symbol in `kicad_symbols/terra_symbols_ic_memory.kicad_sym`,
one per distinct pinout, named after the first chip that uses it. Other chips with
identical pins point at the same symbol, the way the 8T95 points at `74LS365`.

These are plain memory-style symbols, not IEEE style. Match `Memory_EPROM:27C256`:
- body 15.24 mm wide; pins on the 2.54 mm grid;
- address pins on the left in order with A0 at the top; data pins on the right with
  D0 at the top;
- control pins (~CE, ~OE, ~WE, VPP, PGM) at the bottom left;
- VCC at top center and GND at bottom center, with extra rails (VDD +12V, VBB -5V) beside them;
- pin names as the book prints them, active-low as `~{CE}`.

Pin types: address and control `input`; ROM data `tri_state`; common-I/O RAM data
`bidirectional`; separate-I/O RAM `input` for DIN and `tri_state` for DOUT;
open-collector PROM outputs `open_collector`; supplies `power_in`; NC `no_connect`.

Build `tools/make_dip_symbol.py` during the SRAM family, starting from the 8T26A
script approach. It reads pin tables kept beside the generators
(`db/tables/ic_memory/_pinouts.py`: number, name, type, side, order) and writes or
replaces the named symbol in the library, so it can be run again safely. Check every
symbol by rendering it (`kicad-cli sym export svg`) and comparing it pin for pin with
the book's pin-configuration drawing.

**Step 6: build, check, record.** Run `make ic_memory-generate && make ic_memory-build`,
then `make && make verify`. Spot-check at least three rows per family against the
book: MPN, organization, speed, supplies, Vpp, pin count and footprint width. Then add
counts, sources and follow-ups to Results.

**Pitfalls to write into descriptions** (each to be confirmed from the book):
- TMS2716 is a three-supply part with a 2708-like pinout; it is not the Intel 2716.
- TMS2532 differs from the Intel 2732 on pins 18, 20 and 21.
- 2732 programs at 25 V and 2732A at 21 V; 2764 at 21 V and 2764A at 12.5 V. The wrong
  Vpp destroys the part.
- MK4116 and other three-supply DRAMs need the -5 V (VBB) rail up before the others.
- The 1103 needs external precharge and clock timing; it does not drop into other DRAM sockets.
- The 82S open-collector/3-state pairs (82S23/82S123, 82S126/82S129, 82S130/82S131) are
  not interchangeable on a shared bus.

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

- **6502:** 6520, 6522, 6530, 6532, 6551 ACIA (+ W65C22, W65C51N). The request's "6550"
  meant the 6551.
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
18.432, 20.0 MHz. Crystals only for now. DIP-14/DIP-8 can oscillators are out of scope
(decided 2026-11-18).

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
- **Bus and card-edge connectors (decided 2026-11-18): all of the following.** Pitches and
  position counts here are from memory; confirm each against the computer's own
  documentation and the connector drawing.
  - `run_380_card_edge.py`, card-edge sockets:
    - S-100: 100 positions (2x50), 0.125".
    - Apple II slot: 50 positions (2x25), 0.100".
    - Apple I expansion: 44 positions (2x22), 0.156".
    - KIM-1 application and expansion: 44 positions (2x22), 0.156". Same family as the
      EDAC 307 already in terra.
    - AIM-65 application and expansion: 44 positions (2x22), 0.156".
    - Generic 0.156" card edge in the common sizes (2x6 to 2x43).
  - `run_390_bus_molex.py`, Molex 0.156" bus connectors:
    - OSI 48-pin backplane bus.
    - SWTPC SS-50 (50-pin) and SS-30 (30-pin) buses: motherboard pin headers and the
      mating card-side sockets.
    These may share parts with KK 396, so check `run_370` first.
  - `run_400_din41612.py`: Eurocard DIN 41612. Type C 96-pin (3x32), type B 64-pin
    (2x32), and the 2-row a+c 64-pin, each as a right-angle male (board) and vertical
    female (backplane). Pick one classic maker per variant (ERNI, Harting or TE) that
    publishes drawings.
  - The hard part, from the EDAC 307 work: card-edge datasheets are scarce. Sullins EBC
    was dropped for lack of one, so commit only to series with a parked drawing. Use the
    3D-model and footprint-provenance cautions in `plans/connectors-edac-307-card-edge.md`.

### Phase 9: through-hole electrolytics (`capacitors_electrolytic_th`)

KYC is low-ESR. Vintage boards want general-purpose radials and, on restorations,
**axials**. Proposed: one general-purpose radial family (Nichicon UVR or Panasonic ECA)
as `run_510_*`, and one axial family (Vishay BCcomponents 021 ASM or Nichicon TVX) as
`run_520_*`. Axial vs radial goes in core `package`, so the schema doesn't change.
Watch the fragment's `low_esr DEFAULT 'yes'`: these generators must set `'no'`
explicitly.

## Open questions for Dave

1. ~~**Second sources**~~ Decided: one classic example per chip, plus any modern
   drop-in still in production. See "Manufacturer coverage".
2. ~~**Card-edge buses**~~ Decided: S-100, Apple II, Apple I, KIM-1, AIM-65 and generic
   0.156" card edge, plus Molex for the OSI 48-pin and SWTPC SS-50/SS-30 buses, plus
   Eurocard DIN 41612. See phase 8.
3. ~~**"6550"**~~ Decided: it meant the 6551 ACIA, already in phase 4.
4. ~~**Crystal oscillators**~~ Decided: crystals only for now.
5. ~~**DRAM**~~ Decided: included in phase 2 (2026-11-18).
6. **Schema reviews:** phase 2's columns are approved. Phases 3, 4, 6 and 7 still need
   sign-off before their fragments are written.
7. ~~**Phase 2 grades**~~ Decided: one row per speed/power grade, sharing symbol and
   footprint.
8. ~~**Phase 2 optional parts**~~ Decided (2026-11-19): all in (DS1225/DS1230, 2118,
   MCM68764, AT28C010), plus battery-backed NVRAMs generally and the Mostek MK4564
   (the production 64K DRAM that replaced the preliminary MK4164).

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
- National DM8095-DM8098 (second source) dropped under the one-classic-example rule.
- A Rochester Electronics "8T28PC" turned up in a reseller listing. That may be a
  current after-market 8T28 worth adding if a datasheet can be found.

### Phase 2 schema and static RAM (done 2026-11-19)

`supply_rails` and `programming_voltage` added to the `ic_memory` fragment. 80 SRAM rows
in `ic_memory` from `run_310_sram.py`, which shares its row builder and writer with
the later memory families through `_memory.py`.

- **Coverage (one row per grade, plastic DIP, commercial temperature):**
  - Intel: 2101A, 2102A/AL, 2111A, 2112A, 2114/L, 2114A/AL, 2147/L, 5101L.
    (2114A was not in the candidate list; it is the later HMOS 2114 and the one most
    boards actually carry.)
  - Motorola MCM6810/68A10/68B10; TI SN7489, SN74S189A; RCA CDP1822, CDP1824 (both
    voltage grades).
  - Hitachi HM6116 (P, LP, AP, ALP), HM6264, HM62256, HM628128 (P and LP).
  - Alliance AS6C6264, AS6C62256, AS6C1008, AS6C4008 (-55PCN).
- **Sources:**
  - Intel 1979 Component Data Catalog. The 2114A is from the 1981 catalog.
  - Motorola 1979 Memory Data Book.
  - TI 1981 Bipolar Microcomputer Components Data Book. TI has dropped both chips
    from ti.com.
  - RCA 1982 CMOS Microprocessors, Memories and Peripherals.
  - Hitachi IC Memory Data Book 1984 (HM6116, HM6264), M11 1987 (HM62256) and M18 SRAM
    1990 (HM628128).
  - Current Alliance datasheets.
  - Page ranges are in the generator docstring. Sections are in `datasheets/{intel,
    motorola,ti,rca,hitachi,alliance}/`.
- **Ordering codes that had to be built** (exceptions to "never build one from a
  pattern"):
  - Intel's sections print grade tables but no ordering table. The codes follow the
    catalog's own rule (p. 2-3, example `P5101L`): P = plastic, plus the grade.
  - The datasheets state plastic for the 2101A, 2111A, 2112A, 2114 and 2102AL. P is
    assumed for the 2102A, 2114A and 2147.
  - TI and RCA name their packages (J/N, D/E) instead of printing a table.
  - Motorola's table prints `MC6810P` rather than `MCM6810P`, and the rows keep that.
- **Lifecycle:** Alliance discontinued the AS6C6264 and AS6C62256 on 30-Oct-2026
  (PDN#301020261/2, no PDIP replacement, last-time buy 30-Apr-2027), so those rows
  are `EOL`. The notices are parked in `datasheets/alliance/`. The AS6C1008 and AS6C4008
  are Active per Alliance's product list. Digi-Key and Mouser blocked automated fetches,
  so distributor status is still unconfirmed.
- **Symbols:**
  - `tools/make_dip_symbol.py` writes symbols from the pin tables in
    `db/tables/ic_memory/_pinouts.py` (27C256 style; replaces a symbol in place, so
    reruns are safe).
  - 11 new symbols: 2101A (shared by the 5101 and CDP1822, same pins), 2102A, 2111A,
    2112A, 2114 (shared by the 2114A), 2147, 7489, 74S189A, MCM6810, CDP1824, HM6116.
    The 74S189A has the 7489's pins but 3-state rather than open-collector outputs,
    so it gets its own symbol for ERC.
  - Each symbol was rendered and compared with the book's drawing.
  - Stock Memory_RAM symbols cover HM6264/AS6C6264 (`HY6264AxP`), HM62256/AS6C62256
    (`HM62256BLP`), HM628128 and AS6C1008/AS6C4008.
- **Footprints:** 22-pin parts (2101A, 5101, CDP1822) are 0.4" (`DIP-22_W10.16mm`) per
  the package outlines.

Follow-ups:
- Confirm the AS6C1008/AS6C4008 Active status on Digi-Key/Mouser by hand.
- Left out: Hitachi 0.3" skinny HM6116ASP/ALSP, the HM62256 SL grades (marked
  preliminary), TI SN74S289A (open-collector 'S189A), and the plain 5101 (in the
  selector guide but not specified in the datasheet).
- DS1225/DS1230 wait on open question 8.

### Phase 2 dynamic RAM (done 2026-11-19)

33 DRAM rows in `ic_memory` from `run_320_dram.py`.

- **Coverage (one row per grade, plastic DIP, commercial temperature):**
  - Intel P1103, P1103-1, P1103A, P1103A-1, P1103A-2. The -1 and A-1/-2 grades are rated
    0 to 55 C only, with 19 V/22 V rails instead of 16 V/19 V.
  - Intel D2118-10/-12/-15 (optional part, added 2026-11-19).
  - Mostek MK4096N, MK4027N, MK4116N (-2/-3/-4), MK4164N-12/-15, and the MK4564N-12/-15/-20
    that replaced the preliminary MK4164 in production.
  - TI TMS4416 and TMS4464 (-12/-15/-20 NL).
  - Toshiba TMM41256P-12/-15 and the TMM41256AP-10/-12/-15 die revision.
- **Sources:**
  - Intel 1975 Data Catalog (the 1979 catalog only mentions the 1103), and the 1981
    Component Data Catalog for the 2118.
  - Mostek 1980 Memory Data Book and Designers Guide. The MK4564 is from the 1984/1985
    Microelectronic Data Book, because its 1982 sheet is preliminary.
  - TI 1986 MOS Memory Data Book (SMYD006). The 1984 book has both chips only as
    product previews.
  - Toshiba 1987 MOS Memory (on bitsavers after all). Both TMM41256 sheets are in one PDF.
  - Page ranges are in the generator docstring. Sections are in
    `datasheets/{intel,mostek,ti,toshiba}/`.
- **Ordering codes that had to be built:**
  - Mostek prints no ordering table. The codes combine each title's package/grade
    pattern (`MK4116(J/N/E)-2/3`) with the p. II-1 rule (N = plastic).
  - TI's sheets print grades and packages but not whole codes. The codes follow the
    book's numbering key (p. 11-3): `-12` + N (plastic) + L (0 to 70 C).
  - Intel's 1975 ordering instructions print "P 1103" as their example, and Toshiba's
    selection guide prints its codes, so neither had to be built.
  - No Intel book prints a plastic P2118. The only package-coded 2118s are the 1983
    Express codes `QD 2118-3/-4/-7` (CERDIP), so the rows are D2118, CERDIP being the
    only package on record. They keep the 1981 catalog's -10/-12/-15 grade names; the
    1979 and 1983 books give the same speeds as -3/-4/-7, and the descriptions and
    keywords carry both.
- **Lifecycle:** all `Obsolete`. TI's product pages for both chips return 404.
- **Symbols:**
  - Stock Memory_RAM `MK4116N`, `MK4164N` (pin 1 ~RFSH) and `TMM41256AP` match their
    chips pin for pin.
  - 6 new symbols:
    - `2118`: the MK4116 address pins with +5V on pin 8 and N/C on pins 1 and 9.
    - `MK4564`: the stock MK4164N with pin 1 N/C instead of ~RFSH (the usual JEDEC 4164).
    - `1103`, and `1103A` (pin 5 N.C. instead of the precharge clock).
    - `MK4096`: the MK4116 layout with ~CS on pin 13 instead of A6. Shared by the MK4027.
    - `TMS4416`: shared by the TMS4464, whose sheet says "Pinout Identical to TMS4416".
  - `tools/make_dip_symbol.py` gained an `oe` (open-emitter) pin type for the 1103's
    current-sourcing ~DOUT.
- **Pitfalls in the descriptions:**
  - The three-supply Mostek parts carry "apply VBB first". The MK4096 sheet asks for
    VBB within 5 s of VDD.
  - The 1103 descriptions say it needs a precharge clock, MOS-level inputs and a sense
    amplifier on the output.

Follow-ups:
- The MK4164 rows stay, although their sheet is marked PRELIMINARY; the MK4564 rows are
  the production part. The MK4564-25 grade appears only in the preliminary 1982 sheet,
  so it is not included.
- Left out: the MK4027-1 (named in the features list but given no timing column) and
  the 1984-preview-only TMS4464-10.

