# Vintage computer parts

**Date:** 2026-11-17
**Status:** Phases 1, 2 (schema, SRAM, DRAM, NVRAM, EPROM, EEPROM, bipolar PROM),
3 (CPUs), 4 (support chips), 6 (crystals) and 7 (trimpots) done (see Results).
Phase 8 (connectors) is done apart from a lifecycle check on the card-edge sockets
(KK 396, the 0.156" pin buses, card edge and DIN 41612 generated). Phase 9
(electrolytics) is done: Panasonic M-A radials and Vishay 021 ASM axials.
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
| Crystals | none (now `crystals_th`, `crystals_smt`) | No table before phase 6. |
| Trimpots | none (now `potentiometers_th`) | No table before phase 7. |

KiCad 10's stock libraries already have symbols for a good share of these, and we should
use them where the pinout matches (checked in `/usr/share/kicad/symbols`):

- **CPU:** MC6800/6802/6809/6809E (+A/B speed grades), CDP1802ACE/BCE, Z84C00 (Z80),
  8080/8080A, 8088.
- **Peripherals:** 6821, MC6840/6843/6844, MC6845, MC6850, Z8420/Z84C20 (PIO), Z8530 (SCC),
  8253, 8255/8255A, 8259/8259A.
- **Memory:** MK4116, MK4164, HY6264, 62256 (CY/HM/KM), 2764/27128/27256/27512, 27C64-27C080,
  28C256, KM28C64A.
- **Passives:** `Device:Crystal`, `Device:R_Potentiometer_Trim`, with stock
  `Crystal:` and `Potentiometer_THT:` footprints (Bourns 3296, but no 3362; see the
  phase 7 results).

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

**Exception for programmable memories (decided 2026-11-20):** for UV/OTP EPROMs,
parallel EEPROMs and bipolar PROMs, multiple manufacturers are worth having. Builders
buy whatever surplus parts turn up, and makers differ in programming voltage and
algorithm (Intel 2764 at 21V vs AMD/Intel 2764A at 12.5V), so each maker's sheet is its
own row set (EPROMs so far: Intel, AMD, ST, TI, Motorola).

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
| DS1225, DS1230 | Dallas | 8Kx8, 32Kx8 | 28 | battery-backed NVRAM, 6264/62256 sockets (optional; moved to its own `ic_nvram` table, see Results) |

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
and all of those would be NULL for a 6502. Fragment `db/schema/types/ic_microprocessors.sql`
(columns approved 2026-11-20; names reused from `ic_microcontrollers`/`ic_memory` where
the meaning matches):

| Column | Type | Why |
|---|---|---|
| `family` | TEXT | reuse: `6502`, `6800`, `6809`, `68000`, `Z80`, `8080`, `8085`, `8086`, `1802`, `9900` |
| `core` | TEXT | reuse: `NMOS 6502`, `CMOS 65C02`, `NMOS Z80` … |
| `technology` | TEXT | new: NMOS / CMOS / HMOS; drives power, static clocking. Shared with phase 4. |
| `architecture_bits` | INTEGER | reuse |
| `data_bus_bits` | INTEGER | new: 8088 is 16-bit inside with an 8-bit bus; 68008 vs 68000 |
| `address_bus_bits` | INTEGER | new: 16 for most, 20 for 8086/8088/68008, 24 for 68000/65816 |
| `max_clock` | TEXT | reuse: speed grade, e.g. `2MHz` (MC68B09) |
| `clock_source` | TEXT | new: `on-chip oscillator`, `external single-phase`, `external two-phase`, `external four-phase`; decides which clock chip the board needs |
| `supply_voltage_min` / `_max` | REAL | reuse |
| `supply_rails` | TEXT | shared with `ic_memory`: 8080A/TMS9900 need +12/+5/-5 |
| `active_current` | TEXT | reuse: ICC max, or the power dissipation the book gives |
| `special_features` | TEXT | reuse: on-chip RAM (6802), DRAM refresh (Z80), SID/SOD (8085) … |

Scope (decided 2026-11-20): the families above plus 8086/8088, 68000/68010/68008,
65802/65816 and TMS9900. Generators by family: `run_300_6502.py` (MOS 6502-6507, GTE
G65SC802, WDC W65C02S/W65C816S), `run_310_6800.py` (6800/6802/6808/6809/6809E),
`run_320_68000.py`, `run_330_z80.py` (Z80/A/B/H, Z84C00), `run_340_intel.py`
(8080A/8085A/8086/8088), `run_350_1802.py`, `run_360_tms9900.py`. Shared row builder
in `_cpu.py`, custom pin tables in `_pinouts.py`.

### Phase 4: support chips (new table `ic_peripherals`)

Same reasoning as phase 3. A separate table rather than one "vintage" table, because
modern bus peripherals (16550 UART, 82C55) belong here later too. Columns approved
2026-11-20 (fragment `db/schema/types/ic_peripherals.sql`):

| Column | Type | Why |
|---|---|---|
| `family` | TEXT | bus family it was designed for, same values as `ic_microprocessors.family`: `6502`, `6800`, `Z80`, `8080`, `8086`, `68000`, `1802`, `9900` |
| `peripheral_function` | TEXT | PIA / VIA / ACIA / UART / CRTC / VDG / PPI / timer / interrupt controller / DMA / floppy controller / clock generator / bus controller / system controller / bus driver / I/O port |
| `technology` | TEXT | shared with phase 3 |
| `max_clock` | TEXT | bus speed grade (6821 vs 68A21 vs 68B21) |
| `gpio_count` | INTEGER | programmable parallel I/O lines (16 on a 6522, 24 on an 8255); name reused from `ic_microcontrollers` |
| `channels` | INTEGER | reused from `ic_logic`: timers, serial channels, DMA channels |
| `supply_voltage_min` / `_max`, `supply_rails` | REAL / TEXT | shared |
| `active_current` | TEXT | ICC max as printed, as in phase 3 |
| `special_features` | TEXT | e.g. 6532 has 128 B RAM; 6530 has mask ROM |

Families (every speed grade, plastic DIP, commercial temperature):

- **6502:** 6520, 6522, 6530, 6532, 6551 ACIA (+ Active WDC W65C21N/S, W65C22N/S,
  W65C51N). The request's "6550" meant the 6551.
- **6800/6809:** 6820/6821, 6840, 6843, 6844, 6845, 6847, 6850, 6852, 6854.
- **Z80:** PIO (Z8420), CTC (Z8430), SIO/0-2 (Z8440-2), DART (Z8470), DMA (Z8410), CMOS Z84Cxx.
- **8080:** 8212, 8216/8226, 8224, 8228/8238, 8251, 8253, 8255, 8257, 8259, 8279.
- **8086/8088 (added 2026-11-20):** 8284A clock generator, 8288 bus controller.
- **68000 (added 2026-11-20):** MC68230 PI/T, MC68901 MFP, MC68681 DUART.
- **TMS9900 (added 2026-11-20):** TIM9904 four-phase clock generator, TMS9901, TMS9902.
- **1802:** CDP1852, CDP1853, CDP1854, CDP1861 (Pixie).

Modern drop-ins checked on Mouser 2026-11-20: the WDC DIPs are Active and stocked; the
Renesas/Intersil CP82C55A and CP82C59A and the Zilog CMOS Z84C20 family are End of Life,
so they get no Active rows (Zilog CMOS codes from the 1989 book are Obsolete rows).

### Phase 5: modern parallel EEPROM

Folded into phase 2 (`run_340_parallel_eeprom.py`). Listed here only because the request
named it separately.

### Phase 6: crystals (new tables `crystals_th` and `crystals_smt`)

Approved 2026-11-20: one type fragment, `db/schema/types/crystals.sql`, shared by a
through-hole and an SMT table (the repo's `_th`/`_smt` split). Scope: through-hole for
the vintage frequencies, plus the standard jellybean SMT families.

| Column | Type | Why |
|---|---|---|
| `frequency` | TEXT | `3.579545MHz`, `32.768kHz`; also `value` on the schematic |
| `load_capacitance` | TEXT | `18pF` or `series`. The 8224 and 8284 want series-resonant crystals. |
| `frequency_tolerance` | TEXT | `±20ppm` at 25 °C |
| `frequency_stability` | TEXT | `±50ppm` over temperature; tuning forks give the parabolic coefficient |
| `esr_ohm` | TEXT | maximum; name and `Ω` sign reused from `capacitors_electrolytic_th` |
| `oscillation_mode` | TEXT | fundamental / 3rd overtone / tuning fork |
| `drive_level` | TEXT | `1000µW max` |

Holder (HC-49/U, HC-49/US, SMD 3.2x2.5mm 4-pad, ...) goes in core `package`; operating
temperature in the core temperature columns. Crystals only: DIP-14/DIP-8 can
oscillators are out of scope (decided 2026-11-18).

### Phase 7: through-hole trimpots (new table `potentiometers_th`)

The tail reuses `resistors_th` names. `value` is the resistance.

| Column | Type | Why |
|---|---|---|
| `tolerance`, `power_rating`, `temp_coeff` | TEXT | reuse from `resistors_th` |
| `composition` | TEXT | reuse: cermet / carbon |
| `turns` | INTEGER | new: 1 vs 25 changes the part's use |
| `adjustment` | TEXT | new: top / side |

Approved 2026-11-21. Type `potentiometers` (fragment
`db/schema/types/potentiometers.sql`), so a later `potentiometers_smt` can share it.
Seed: Bourns 3296 (25-turn 3/8"; all five pin styles: W and Y top adjust, P, X and Z side
adjust) and 3362 (single-turn 1/4"; P, H and U, all top adjust) in the datasheets'
standard resistance table, 10 Ω-2 MΩ (the 1-2-5 values plus 25 kΩ and 250 kΩ).

### Phase 8: vintage connectors (`connectors`)

- `run_370_molex_kk396.py` (**done 2026-11-21**, see `plans/connectors-molex-kk396.md`):
  Molex KK 396 (0.156") friction-lock headers, 41791 vertical and 41792 right-angle,
  2-18 positions, 34 rows. The crimp housings are named in `mating_family`/`mates_with`
  rather than generated (no board footprint). This is the SWTPC/arcade/power-harness
  connector.
- **Bus and card-edge connectors (decided 2026-11-18): all of the following.** Pitches and
  position counts here are from memory; confirm each against the computer's own
  documentation and the connector drawing.
  - `run_380_card_edge.py`, card-edge sockets (**generated 2026-11-22**, 56 EDAC parts
    + `-pins` twins, see `plans/connectors-card-edge.md`; lifecycle still to check at
    Mouser/Digi-Key). Original scope:
    - S-100: 100 positions (2x50), 0.125".
    - Apple II slot: 50 positions (2x25), 0.100".
    - Apple I expansion: 44 positions (2x22), 0.156".
    - KIM-1 application and expansion: 44 positions (2x22), 0.156". Same family as the
      EDAC 307 already in terra.
    - AIM-65 application and expansion: 44 positions (2x22), 0.156".
    - Generic 0.156" card edge in the common sizes (2x6 to 2x43).
  - **0.156" pin buses (done 2026-11-21, see `plans/connectors-0156-bus.md`):** OSI's
    48-line bus (4 x 12-pin) and SWTPC SS-50/SS-30 (5 / 3 x 10-pin, one pin pulled as
    the key). Male side in round posts, as Dave asked: `run_390_te_mta156_round_post.py`,
    TE MTA-156 640384, 2-15 positions (14 rows; 16-21 obsolete at TE). Card side:
    `run_395_molex_kk156_41815.py`, Molex KK 156 41815 PCB receptacles (successors to
    OSI's obsolete 09-52-3121/3123; 09-48-2101 for SWTPC), every Mouser-listed tin build
    in right-angle, top-entry and bottom-entry styles (141 rows). Added 2026-11-22:
    `run_372_molex_kk396_round_pin.py`, Molex round-pin KK 396 headers 3190 (polarizing
    wall) and 3192 (flat wafer), 38 rows, and the TE voltage/temperature ratings from
    spec 108-1051 and the 7 A rating from catalog 82056. Custom footprints for all three.
  - **Connector conventions (Dave, 2026-11-22), `plans/connectors-conventions.md`:**
    every connector needs symbol, footprint and 3D model, plus a `-pins` per-pin symbol
    row; retro-documented parts may go in without a drawing. Backfilled to run_340,
    run_370, run_372, run_390 and run_395 (228 parts, 94 generated models).
  - `run_400_din41612.py` (**done 2026-11-23**, Harting DIN-Signal, 6 parts + `-pins`
    twins, see `plans/connectors-din41612.md`): Eurocard DIN 41612. Type C 96-pin (3x32), type B 64-pin
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

**Done (2026-11-23):** `run_510_panasonic_eca.py` writes Panasonic M-A (ECA-xxM), 130
radial rows. `run_520_vishay_021asm.py` writes Vishay 021 ASM (ex-Philips 2222 021),
102 axial rows. Both use stock `Device:CP` symbols and stock KiCad footprints, and both
set `low_esr = 'no'`. Nichicon UVR was passed over because many of its values went
obsolete in 2023. Details are in `plans/capacitors-electrolytic-th-general-purpose.md`.

## Open questions for Dave

1. ~~**Second sources**~~ Decided: one classic example per chip, plus any modern
   drop-in still in production. See "Manufacturer coverage".
2. ~~**Card-edge buses**~~ Decided: S-100, Apple II, Apple I, KIM-1, AIM-65 and generic
   0.156" card edge, plus Molex for the OSI 48-pin and SWTPC SS-50/SS-30 buses, plus
   Eurocard DIN 41612. See phase 8.
3. ~~**"6550"**~~ Decided: it meant the 6551 ACIA, already in phase 4.
4. ~~**Crystal oscillators**~~ Decided: crystals only for now.
5. ~~**DRAM**~~ Decided: included in phase 2 (2026-11-18).
6. **Schema reviews:** phase 2's, 3's and 4's columns are approved (phase 3 on
   2026-11-20, adding `data_bus_bits` and `clock_source`; phase 4 on 2026-11-20, with
   `gpio_count` and `active_current`; phase 6 on 2026-11-20; phase 7 on 2026-11-21).
   Phases 8 and 9 add to existing tables and need no new columns.
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

### Phase 2 UV EPROM (done 2026-11-20)

165 rows in `ic_memory` from `run_330_eprom.py`: 153 UV EPROMs, 9 OTP EPROMs and 3 5 V
flash parts.

- **Coverage (one row per grade, commercial temperature, windowed ceramic DIP):**
  - Intel B1702A (-2/base/-6), D2704, D2708 (-1/base/L), D2716 (-1/-2/base/-5/-6),
    D2732 (-4/base/-6), D2732A (7 grades), D2764 (7), D2764A (9), D27128 (6), D27256 (6).
  - TI TMS2716-30/-45JL, TMS2516-25/-35/-45JL, TMS2532-30/-35/-45JL, TMS25L32-45JL.
  - Motorola MCM68764C/C35 and MCM68L764C/C35.
  - AMD Am2764A, Am27128A, Am27256, Am27512 (36 rows, every DC valid combination).
    It fills the 27128A/27512 gaps the Intel books leave; its Am2764A/Am27256 rows sit
    alongside Intel's, per the programmable-memory exception under "Manufacturer coverage".
  - SGS-Thomson NMOS M27128A (7 grades) and M27512 (5), also supplied by Dave.
  - ST M27C64A, M27C256B, M27C512, M27C1001, M27C2001, M27C4001, M27C801 (42 rows).
  - Microchip AT27C256R/512R/010/020/040 OTP (PDIP) and SST39SF010A/020A/040 flash.
- **Sources:**
  - Intel 1979/1981 Component Data Catalogs, 1983 and 1984 Memory Components
    Handbooks, using the latest final sheet for each chip. The 1981 2732A/2764
    sheets are PRELIMINARY; the 27256 has only the 1984 PRELIMINARY sheet, and its
    descriptions say so. The 1984 handbook was added to the sources.
  - TI 1982 MOS Memory Data Book (prints full codes; 1984 drops grades), Motorola
    1980 Memory Data Book.
  - AMD 8-Bit EPROM Family, publication 08005 Rev. A (May 1986), a scan in
    `datasheets/amd/`.
  - ST's M27C pages and datasheets are gone from st.com (the EPROM line went to
    Numonyx/Micron); the datasheets are Digi-Key's copies.
  - Page ranges are in the generator docstring.
- **Ordering codes that had to be built:**
  - Intel: D + grade (Type D windowed CERDIP, the catalog's prefix rule); B1702A
    from the 1979 order form, Type B being the 1702A's ceramic transparent-lid package.
  - ST prints an ordering scheme, not a list: F (windowed FDIP) + 1 (0 to 70 C),
    VCC +/-10%, one code per standard speed column of the read AC tables. The
    footnoted "High Speed" columns (-35/-45/-55) are left out.
  - TI, Motorola, AMD and Microchip codes are printed. The ST NMOS M27128A/M27512
    schemes list every speed/VCC code; only F (FDIP) and 1 (0 to 70 C) are added.
- **Lifecycle:** vintage parts and ST all Obsolete (Digi-Key lists the M27C as
  Obsolete). Microchip: AT27C256R/512R PDIP Active on Digi-Key; the AT27C010/020/040
  and SST39SF PDIP codes are Obsolete on both Digi-Key and Mouser, although
  microchip.com shows the families "In Production" (the PLCC/TSOP codes live on).
- **Programming voltage** (`programming_voltage`): 1702A -48V; 2704/2708/TMS2716 26V
  pulse; 2716/2732/TMS2516/TMS2532/MCM68764 25V; 2732A/2764/27128 21V; 2764A/27256,
  the AMD family, M27128A, M27512 and M27C64A 12.5V; other M27C 12.75V; AT27C 13V. Descriptions carry the
  wrong-VPP cautions (2732 vs 2732A, 2764 vs 2764A).
- **Symbols:**
  - Stock Memory_EPROM `2764`, `27128`, `27256`, `27C64`, `27C256`, `27C512`,
    `27C010`, `27C020`, `27C040`, `27C080`. The stock `27C010` has no pin 30, which is
    NC on the AT27C010 and M27C1001.
  - 10 new symbols: `1702A` (three VCC pins stacked as `[12,22,23]`), `2708` (also the
    2704), `2716` (also the TMS2516), `2732` (also the 2732A), `TMS2716`, `TMS2532`,
    `MCM68764`, and `SST39SF010A`/`020A`/`040`, which replace the stock Memory_Flash
    symbols (they name ~WE "PGM", drop the active-low bars and type NC pins as inputs).
  - `tools/make_dip_symbol.py` now stacks same-name power pins into one pin.
- **Footprints:** all 0.6" rows. Intel Type D, ST FDIP28W and TI's 600-mil cerpak give
  it explicitly; for the commercial TMS2516/TMS2532 the 600-mil statement is in the 1984
  book's J-package text. The AMD sheet has no outline; its 28-pin ceramic DIP is taken
  as 0.6".

Follow-ups:
- Not generated: Intel 27128A (1984 advance information, no VPP or grades) and Intel
  27512 (in no book through 1984); the AMD and ST NMOS rows cover both chips. ST
  M27C128A (CMOS) has no datasheet on st.com or Digi-Key.
- Left out: Motorola MCM68766 (same sheet family, ~G/VPP on pin 20, Advance
  Information), the side-braze MCM68764L codes (built from a rule only), Intel P2732A/
  P2764 plastic "production EPROMs", TI TMS2564/TMS2764.

### Phase 2 parallel EEPROM (done 2026-11-20)

74 rows in `ic_memory` from `run_340_parallel_eeprom.py`, `memory_type = 'EEPROM'`,
from five makers per the programmable-memory exception.

- **Coverage (one row per grade, commercial temperature, plastic DIP where offered):**
  - Intel D2816 (2), D2816A (4), D2817A (5), CERDIP.
  - Xicor X2816AP (4), X2816BP (2), X2816CP-20, X2864AP (4), X28C64P (4), X28256P (3),
    X28C256P (4), and X28C010D-20 (cerdip only).
  - SEEQ DQ2816A/AH (5), DQ2864/H (4), DQ52B13/H (6), DQ52B33/H (5), all CERDIP (the
    only package SEEQ offered).
  - Atmel 1990 AT28C16, AT28C17, AT28C64, AT28C64X, AT28C256 (-15/-20/-25PC each) and
    AT28C010-15/-20/-25BC (side-braze ceramic, the only DIP in 1990).
  - Microchip AT28C64B-15PU and AT28C256-15PU, Active (Mouser stock and factory lead
    time, 2026-11-20; Digi-Key showed a bot check). The current AT28C010 comes only in
    PLCC/TSOP, so it has no modern row.
- **Sources:** Intel 1981 Component Data Catalog (2816) and 1984 Memory Components
  Handbook (2816A, 2817A; all three sheets PRELIMINARY); Xicor 1985 (X2816A) and 1990
  data books; SEEQ 1985 Data Book; Atmel 1990 Data Book; current Microchip sheets. Page
  ranges are in the generator docstring. Datasheets in `datasheets/intel`, `xicor`,
  `seeq`, `atmel` and `microchip`.
- **Ordering codes that had to be built:**
  - Intel prints none: D (Type D hermetic DIP) + device + grade, as for the EPROMs.
  - Xicor 1985 and SEEQ print a key, not a list; codes take the key's package and
    temperature letters and one suffix per AC-table column.
  - Left out: grades only in a key (X28256-20, X28C010-15) or only in an AC table
    (SEEQ 2864-35), the SEEQ 2817A (no ordering box or outline on the commercial
    sheet), and Atmel's E/F endurance and fast-write options.
- **Write behaviour** is in each description, since it decides whether a part works in
  a given board: the 2816 needs a shaped 21V VPP pulse (`programming_voltage = 21V`);
  the 2816A and SEEQ 52B13/52B33 need ~WE held for the whole write and a byte erase
  first; the rest are self-timed, later ones with page writes, DATA polling and software
  data protection. `programming_voltage` is NULL for the 5V-only parts.
- **Symbols:**
  - Stock Memory_EEPROM `KM28C64A` (8Kx8, pins 1 and 26 NC: X2864A, X28C64, AT28C64X,
    AT28C64B), `KM28C65A` (RDY/~BUSY on pin 1: SEEQ 2864, AT28C64) and `28C256`
    (X28256, X28C256, AT28C256). The stock symbols type the data pins tri-state.
  - 5 new symbols in `terra_symbols_ic_memory` with bidirectional data pins: `2816`
    (2716 pinout, VPP on pin 21), `2816A` (6116 pinout, ~WE on pin 21; also the Xicor
    X2816A/B/C, SEEQ 2816A/52B13 and AT28C16), `2817A` (also the AT28C17), `52B33`
    (chip clear ~CC on pin 1) and `28C010` (AT28C010 and X28C010).
- **Footprints:** every DIP outline in these books is 0.6" (`DIP-nn_W15.24mm`). The Intel
  sheets name no package, so they use the Type D outline appended to each PDF.

Follow-ups:
- More makers if wanted: National NMC2816, Catalyst CAT28C16/64/256, ST M28C16/M28C64,
  Hitachi HN58C65/HN58C256. The 1996 Atmel book adds the AT28C010-12/-15/-20PC plastic
  DIP codes.

### Phase 2 bipolar PROM (done 2026-11-20)

149 rows in `ic_memory` from `run_350_bipolar_prom.py`, `memory_type = 'PROM'`, from
five makers per the programmable-memory exception. All Obsolete.

- **Coverage:** 32x8, 256x4, 512x4, 1Kx4, 2Kx4, 512x8 (20-pin and 24-pin), 1Kx8 and
  2Kx8, open-collector and 3-state, one row per printed speed grade:
  - Signetics N82S23/123 ... N82S190/191 (14). 82S184/185 and 82S190/191 come only in
    the I ceramic package; 82S146/147 have no sheet in the 1977 book.
  - AMD Am27S18/19 ... Am27S190/191 plus the 300-mil Am27S280/281/290/291, the A, SA,
    LS and PS grades (53), PC codes.
  - MMI 6330/6331 ... 6380/6381 (NiCr, ceramic J and 0.3" JS only) and the Ti-W
    63S/63LS140/141/240/241 in plastic (37). No 2Kx8 in the 1981 book.
  - TI TBP18S030, TBP14S10, TBP24S10/41/81, TBP18S42, TBP28S42, TBP18S46, TBP28S46,
    TBP28S86, TBP28L86, TBP28S166 and their SA open-collector twins (23), N codes.
    No 512x4 part in the 1981 book.
  - National DM74S188/288 ... DM87S190/191 plus the 0.3" DM87S280/281/290/291 (22).
- **Sources:** Signetics 1977 Bipolar and MOS Memory (the 1984 Bipolar LSI manual has
  no PROMs), AMD 1984 Bipolar/MOS Memories, MMI 1981 Bipolar LSI 4th ed., TI 1981
  Bipolar Microcomputer Components (the 1983 Field-Programmable Logic book has no
  PROMs), National 1983 Bipolar Memory. Page ranges are in the generator docstring.
  TI's two family sheets are filed once each (`tbp14-tbp18-series`, `tbp24-tbp28-series`).
- **Ordering codes that had to be built:** Signetics ("specify N82S23/123, N or F"),
  MMI (key only) and TI (key only) print no full codes; National's 2Kx4/2Kx8 sheets
  list packages but no order numbers. Left out: National A/B grades (never given an
  order number), TI -55/-60 grades and "design goals" parts, AMD LS-A and burn-in codes.
- **Descriptions** carry the fuse type (NiCr, PtSi, Ti-W, W) and whether unprogrammed
  outputs read high or low, which differs by maker (MMI NiCr and TI Series 24/28 ship
  high, the rest low). `programming_voltage` is NULL: each maker's procedure uses
  several voltages. Signetics and MMI commercial range is 0 to 75 C.
- **Symbols:** every maker uses the same pinout for a given organization, so 18 new
  symbols in `terra_symbols_ic_memory` cover all rows: an open-collector and a 3-state
  symbol per pinout, `82S23`/`82S123`, `82S126`/`82S129`, `82S130`/`82S131`,
  `82S136`/`82S137`, `82S184`/`82S185`, `27S28`/`27S29` (20-pin 512x8), `6340`/`6341`
  (24-pin 512x8), `82S180`/`82S181`, `82S190`/`82S191`. Outputs are named O0..On and
  enables CE1..CE4 whatever the maker prints (B, Q; E, G, CS).
- **Footprints:** 16/18/20-pin parts are 0.3". 24-pin parts are 0.6" except AMD
  Am27S28x/29x, MMI JS and National DM87S28x/29x, which are 0.3" (`DIP-24_W7.62mm`).

Follow-ups:
- More makers: Harris HM76xx, Fairchild 93xxx, Intel 36xx, Raytheon 29xxx.
- Later Signetics (82S147, 82S191 in plastic) need a 1980s Signetics bipolar memory book.

### Battery-backed NVRAM (done 2026-11-20)

NVRAMs got their own table, `ic_nvram` (decided 2026-11-19), with the core columns plus
a `nvram` fragment: `capacity`, `word_size`, `speed`, `supply_voltage_min/max` (REAL),
`persistence_years`, `write_protect_voltage`, `battery`, `sram_socket`, `rtc`.
20 rows from `db/tables/ic_nvram/run_300_nvram.py`.

- **Coverage (every code the current datasheet lists, commercial temperature, DIP):**
  - Analog Devices (Dallas) DS1220AB/AD-100+ (2Kx8), DS1225AB/AD-70+ (8Kx8),
    DS1230AB/Y-70+ (32Kx8), DS1245AB/Y-70+ (128Kx8), DS1250AB/Y-70+ (512Kx8).
  - ST ZEROPOWER M48Z02/M48Z12-70PC1 and -150PC1 (2Kx8), M48Z08/M48Z18-100PC1 and
    M48Z58/M48Z58Y-70PC1 (8Kx8), M48Z35/M48Z35Y-70PC1 (32Kx8).
  - Each chip has two VCC grades, so there are two `value`s per chip. Dallas AB = 5 V ±5%,
    AD/Y = ±10%. ST M48Zx2/x8/35/58 = 4.75-5.5 V, the 12/18/35Y/58Y = 4.5-5.5 V. The grade
    also sets the write-protect window (`write_protect_voltage`).
- **Sources:** the current ADI and ST datasheets, fetched through Chrome, in
  `datasheets/analog-devices/` and `datasheets/st/`. The DS1245 PDF has the 32-pin module
  drawing from its 2006 revision appended as p. 11, because the 2010 revisions dropped
  package drawings.
- **Lifecycle:** all Active on Digi-Key (2026-11-20), and the ST codes on the ST eStore.
  Only the lead-free "+" Dallas codes are Active; the leaded ones are Obsolete.
  analog.com refuses every product page even in a real browser, so ADI rows have no
  `manufacturer_link`. All 8 ST product pages were checked.
- **Footprints:** the modules are wider than a DIP (Dallas 720/740-mil body, ST CAPHAT
  18 mm) but sit on 600-mil rows (Dallas 0.590-0.630", ST 0.600-0.630"). The 24-pin parts
  use KiCad's 18 mm-body `DIP-24_18.0mmx34.29mm_W15.24mm`. The 28/32-pin parts use the
  plain `W15.24mm` patterns, whose silkscreen is narrower than the module.
- **Symbols:**
  - Stock `Memory_RAM:M48Zx2` (2Kx8), `HM62256BLP` (32Kx8) and `AS6C4008-55PCN`
    (512Kx8) match pin for pin.
  - 2 new symbols in `terra_symbols_ic_nvram`: `DS1225` (8Kx8; also the M48Z08/18/58)
    and `DS1245` (128Kx8). Both are the JEDEC SRAM pinout with the active-high CE2 pin
    NC (6264 pin 26, 628128 pin 30), so they also fit 2764/27C010 EPROM sockets.

Follow-ups:
- The 2010 Dallas revisions list only -70 (DS1220: -100). Digi-Key still shows -85 to
  -200 grades of some as Active; add them if an older revision's timing table is filed.
- Not included: IND grades, the Dallas 34-pin PowerCap modules (DS9034PC battery cap),
  and the ST SOH28 SNAPHAT parts (M48Z35Y/M48Z58Y-70MH1F). They need SMT footprints.
- Timekeepers (`rtc` = Yes): the ST M48T02/08/35/58 and Dallas DS1643/DS1644 are the
  obvious next rows. Stock `Memory_RAM:M48Tx2` covers the 24-pin ones.

### Phase 3: CPUs (done 2026-11-20)

New table `ic_microprocessors` (fragment `db/schema/types/ic_microprocessors.sql`,
registered in `table_map.json`, `PAIRS` and the chooser as "Microprocessors"). 70 rows,
one classic maker per chip, every speed grade, plastic DIP, commercial temperature
unless the book gives only a wider range:

| Generator | Rows | Parts | Source |
|---|---|---|---|
| `run_300_6502.py` | 24 | MOS MPS6502-6507 (1/2/3 MHz: none/A/B), GTE G65SC802P-2..-8, WDC W65C02S6TPG-14, W65C816S6PG-14 | 1982 MOS Technology Data Catalog 2-14..2-24; 1987 GTE Microcircuits Data Book 1-83..1-103; current WDC sheets |
| `run_310_6800.py` | 16 | Motorola MC6800/68A00/68B00, MC6802/A/B + MC6802NS, MC6808/A/B, MC6809/A/B, MC6809E/A/B, P suffix | 1983 Motorola 8-Bit Microprocessor and Peripheral Data |
| `run_320_68000.py` | 9 | MC68000G4-G12, MC68008P8/P10, MC68010P8/P10 | Motorola data sheets, Apr 1983 / Apr 1985 / May 1985 |
| `run_330_z80.py` | 8 | Zilog Z8400PS/APS/BPS, Z0840008PSC (Z80H), Z84C0004/06/08PSC, Z84C0010PEC | 1982 Zilog Data Book; 1989 Zilog Z80 Family Data Book |
| `run_340_intel.py` | 9 | P8080A/-1/-2, P8085A/-2, P8086/-2/-1, P8088 | 1981 Intel Component Data Catalog |
| `run_350_1802.py` | 3 | RCA CDP1802AE, CDP1802ACE, CDP1802BCE | 1982 RCA CMOS LSI Products |
| `run_360_tms9900.py` | 1 | TI TMS9900NL | TMS 9900 Data Manual (May 1976); 1978 9900 Family Systems Design and Data Book |

- **Lifecycle:** WDC W65C02S6TPG-14 and W65C816S6PG-14 Active (Mouser stock,
  2026-11-20). Everything else Obsolete, including the Z84C00 (Zilog EOL notice
  2024-04-15, Digi-Key Obsolete). Renesas still lists the CDP1802A, but only as the
  military ceramic CDP1802ACD3, which no distributor carries, so there is no Active
  1802 row; its Renesas page is the `manufacturer_link`.
- **Codes built from a book's key, not printed per chip:** MOS MPS codes ("MXS 65XX"
  key), GTE G65SC802P-n, Intel P-prefix codes (catalog ordering rule; only P8085A-2 is
  printed), RCA E-suffix codes, TMS9900NL (TI numbering key). WDC PDIP codes are taken
  from Mouser because the sheets print only a PLCC example.
- **Footprints:** stock DIP. The 64-pin MC68000/MC68010 and TMS9900 are 0.9" wide
  (`DIP-64_W22.86mm`); the MOS book has no 28-pin outline, so the 6503-6507 are taken
  as 0.6".
- **Symbols:** stock where the pinout matches pin for pin (checked against each book):
  `CPU_NXP_6800` per grade (6808 and 6802NS on the MC6802 symbols), `CPU_NXP_68000`
  MC68000P/MC68008P/MC68010P, `CPU:Z84C00xxP` for all Z80s, `MCU_Intel:8080A`,
  `CPU:CDP1802ACE/BCE`. 12 custom symbols in
  `kicad_symbols/terra_symbols_ic_microprocessors.kicad_sym`: MPS6502 (also the
  G65SC802), MPS6503-MPS6507, W65C02S, W65C816S, 8085A, 8086, 8088 (both with min-
  and max-mode pin names; the stock 8088 symbols drop the bar on ~{DEN}), TMS9900.

Follow-ups:
- 8088-2: not in the 1981 Intel catalog; add from a later Intel book if wanted. The
  1989 Zilog NMOS codes Z0840004/06PSC repeat the Z80A/Z80B grades and are not
  generated.
- TMS9900-40 (4 MHz): left out because the TI key doesn't show where the speed suffix
  goes.
- PLCC versions (MC68000FN, W65C02S PLCC/QFP, Z84C00 VEC) are out of scope (DIP only).
- Rockwell R65C02 and the NMOS 6510/6512-6515 are not generated.

### Phase 4: support chips (done 2026-11-20)

New table `ic_peripherals` (fragment `db/schema/types/ic_peripherals.sql`, registered
in `table_map.json`, `PAIRS` and the chooser as "Microprocessor Peripherals"). 109
rows, one classic maker per chip, every speed grade, plastic DIP, commercial
temperature unless the book gives only a wider range:

| Generator | Rows | Parts | Source |
|---|---|---|---|
| `run_300_6502.py` | 14 | MOS MPS6520/A, MPS6522/A, MPS6530, MPS6532/A, MPS6551/A; WDC W65C21N/S6TPG-14, W65C22N/S6TPG-14, W65C51N6TPG-14 | 1982-83 MOS/Commodore Data Catalog; current WDC sheets |
| `run_310_6800.py` | 24 | Motorola MC6821, MC6840, MC6844, MC6845, MC6850, MC6852, MC6854 (each P, AP, BP); MC6843P; MC6847P, MC6847YP | 1983 Motorola 8-Bit Microprocessor and Peripheral Data; 1981 Motorola Microprocessors Data Manual (MC6843) |
| `run_320_68000.py` | 4 | MC68230P8/P10, MC68901P, MC68681P | 1981 Microprocessors Data Manual; MC68901 manual (Jan 1984); MC68681 manual (Sep 1985) |
| `run_330_z80.py` | 37 | Zilog Z8420/Z8430/Z8440/Z8441/Z8442/Z8470 PS/APS/BPS, Z8410PS/APS; Z84C20/30/40/42 04/06/08PSC, Z84C4104/06PSC, Z84C1004/06/08PEC | 1982 Zilog Data Book; 1989 Zilog Z80 Family Data Book |
| `run_340_intel.py` | 20 | P8212, P8216, P8226, P8224, P8228, P8238, P8251A, P8253/-5, P8255A/-5, P8257/-5, P8259A/-2/-8, P8279/-5, P8284A, P8288 | 1981 Intel Component Data Catalog |
| `run_350_1802.py` | 7 | RCA CDP1852E/CE, CDP1853E/CE, CDP1854AE/ACE, CDP1861CE | 1982 RCA CMOS LSI Products |
| `run_360_tms9900.py` | 3 | TI TMS9901NL, TMS9902NL, SN74LS362N (TIM9904) | 1978 9900 Family Systems Design and Data Book |

- **Lifecycle:** the five WDC parts are Active (Mouser stock, 2026-11-20). Everything
  else is Obsolete. The Zilog CMOS peripherals (Z84C2008PEG etc.) are End of Life at
  Mouser, and the Renesas/Intersil CP82C55A and CP82C59A are too, so the Intel family
  has no Active CMOS row.
- **Codes built from a book's key or a package note, not printed per chip:** Intel
  P-prefix codes (catalog ordering rule), RCA CDP1852E/CE and CDP1853E/CE (suffix
  key), MC6847P/MC6847YP and MC6843P ("P SUFFIX PLASTIC PACKAGE"), MC68230P8/P10
  (the sheet prints only L8/L10 and "P suffix plastic package available 2Q82"),
  SN74LS362N (the TIM9904 sheet prints no code; neighbouring TIM990x sheets order
  SN74LSxxx in "J OR N PACKAGE"). MOS codes come from the catalog's cross reference.
- **Not generated:** MC6820 (no sheet in either Motorola book; the MC6821 replaced it),
  6532B and 6551B (in the key or feature list but with no B timing), MC6847T1 (not in
  either book), the MC2681/MC2682 (general-bus DUART variants), TMS9901-40/9902-40
  (DESIGN GOAL), 8224-4 and 8284A-1 (not in the 1981 catalog), the 1989 NMOS Zilog
  codes (Z0842004PSC etc., same parts as the 1982 A/B grades), CMOS DART (none
  exists), Z84C43/44 and Z84C90 (no DIP).
- **Technology:** the 8212/8216/8226/8224/8228/8238 sheets don't name the process;
  they are recorded as bipolar from their TTL characteristics. NMOS is assumed for the
  8255A, 8257 and 8279. The MC68901 and MC68681 manuals don't name it, so
  `technology` is NULL. RCA parts are -40 to 85 C (no 0-70 C grade), and the CMOS
  Z80 DMA is E temperature only (-40 to 100 C), as the CPU's Z84C0010PEC.
- **Footprints:** stock DIP, 0.6" except the 16/18/20-pin parts (8216/8226, 8224,
  8284A, 8288, CDP1853, TMS9902, TIM9904) at 0.3". The MOS book has no 28-pin outline;
  the 6551 is taken as 0.6" from the pin-compatible W65C51N.
- **Symbols:** stock where the pinout matches pin for pin, active-low bars included:
  `Interface:6821`, `Interface:MC6843`, `Interface:MC6844`, `GPU:MC6845`,
  `Interface:Z8420`, `Timer:8253`, `Interface:8255A`, `Interface:8259A`,
  `Timer:8284` (8284A) and `Interface:8288`. 37 custom symbols in
  `kicad_symbols/terra_symbols_ic_peripherals.kicad_sym` from
  `db/tables/ic_peripherals/_pinouts.py`, including MC6840 (stock types D0-D7 as
  inputs), MC6850 (stock drops the bar on ~{CS2}) and MC68230/MC68681 (stock drops
  every bar). The WDC parts get their own symbols with WDC's B-suffix names; the
  W65C22N and W65C22S differ in IRQB type (open drain vs totem pole). One symbol per
  SIO bonding option (Z8440/Z8441/Z8442).

Follow-ups:
- 6530 mask-ROM variants (e.g. the KIM-1's 6530-002/-003) are not generated; the row
  is the generic MPS6530.
- MC68230 and MC68681 sheets say nothing about plastic availability beyond the codes
  above; check a later Motorola book if exact plastic codes matter.
- PLCC versions and the military/industrial grades are out of scope (DIP only).

### Phase 6: crystals (done 2026-11-20)

New tables `crystals_th` and `crystals_smt` on one fragment
(`db/schema/types/crystals.sql`), registered in `table_map.json`, `PAIRS` and the
chooser as "Crystals (Through-Hole)" and "Crystals (SMT)". Shared row builder, value
formats and Abracon option decoder in `tools/crystal_rows.py`. 226 rows, all Active,
each code checked as stocked at Mouser on 2026-11-20 and decoded from the
manufacturer's part-numbering key:

| Table | Generator | Rows | Parts |
|---|---|---|---|
| `crystals_th` | `run_300_abracon_ab.py` | 32 | Abracon AB HC-49/U, 1.8432-50 MHz, -B2 grade (-20 to 70 C, ±20 ppm, 18 pF), plus AB-4.433619MHZ |
| | `run_310_ecs_hc49ux.py` | 43 | ECS HC-49UX: 30 series-resonant codes, 12 parallel codes at vintage frequencies AB lacks, ECS-10-13-1XH (1 MHz) |
| | `run_320_abracon_abl.py` | 30 | Abracon ABL HC-49/US, 3.579545-48 MHz, -B2 grade |
| | `run_330_abracon_ab26t.py` | 4 | Abracon AB26T 32.768 kHz cylinder |
| `crystals_smt` | `run_300_abracon_abls.py` | 26 | Abracon ABLS HC-49/US SMD, -B2-T grade |
| | `run_310_abracon_abm3.py` | 34 | Abracon ABM3 (5032 2-pad) and ABM3B (5032 4-pad), -B2-T grade |
| | `run_320_abracon_abm8g.py` | 18 | Abracon ABM8G 3225, -18-D2Y-T grade (18 pF, -40 to 85 C) |
| | `run_330_abracon_abm10.py` | 27 | Abracon ABM10 2520, -E20-T and -D30-T3 grades |
| | `run_340_abracon_32khz.py` | 12 | Abracon ABS25 (8038) and ABS07 (3215) 32.768 kHz |

Vintage frequencies, from the OSI SAMS Computerfacts parts lists (C1P, C2/C3, C4P in
`~/vsrc/osiweb`) and the machines' own manuals and schematics (S = secondary
source):

| MHz | Machine | Row |
|---|---|---|
| 1.000 | KIM-1, SYM-1 | ECS-10-13-1XH |
| 1.7971 | SWTPC MP-A (MC14411 and CPU) | none: not stocked |
| 1.8432 | MC14411 datasheet | AB, ECS series |
| 2.000 | Altair 8800 | AB, ECS series |
| 2.4576 | Altair 88-2SIO | ECS-24-32-1X |
| 3.52180 | COSMAC VIP | none: not stocked |
| 3.579545 | Netronics Elf II, OSI C4P 540, Atari (S) | AB, ABL, ABLS, ECS series |
| 3.93216 | OSI C1P 600 board | ECS-39-17-1X |
| 4.000 | AIM-65, OSI 470/505/550/555, North Star MDS | AB, ABLS, ECS series |
| 4.433618 | VIC-20 PAL (S) | ECS-44-20-1X, AB-4.433619MHZ |
| 8.000 | OSI 510, North Star ZPB-A, Cromemco ZPU | AB, ABL, ABLS, ABM3B, ECS series |
| 10.6445 | TRS-80 Model I | none: not stocked |
| 10.738635 | TI-99/4A TMS9918 (S) | ECS-107-S-1X |
| 12.000 | OSI C4P 540, TI-99/4A tank (S) | AB, ABL, ABLS, ABM3/3B/8G, ECS series |
| 14.31818 | Apple 1, Apple II, IBM PC, VIC-20/C64 NTSC (S) | every MHz family |
| 17.734475 | C64 PAL (S) | AB-17.734475-B4 |
| 18.000 | IMSAI MPU-A (8224), an OSI C2/C3 board | ECS-180-20-1X, ECS-180-S-1X |
| 18.432 | Heathkit H8 (8224) | AB, ABL, ABLS, ABM3/3B/8G/10, ECS series |
| 48.000 | TI-99/4A TIM9904 (S) | AB, ABL, ABLS, ABM3/3B/8G/10, ECS-480-S-1X |

Unconfirmed in any source found: Quest Super Elf, SWTPC MP-S, PET 2001, ZX80, H89.
The SWTPC MP-A crystal is 1.7971 MHz, not 1.8432 (that is the MSI CP-1).

- **Grades:** one standard grade per family, the one Mouser stocks most widely.
  AB/ABL/ABLS/ABM3/ABM3B use -B2 (and -B2F, fundamental above 24 MHz); ECS uses its
  standard grade. All 32.768 kHz load-capacitance and tolerance codes in stock are
  included, since the load matters to the RTC.
- **ECS selection:** series-resonant codes at the datasheet's developed frequencies,
  and parallel codes only where AB is not stocked. Mouser lists ECS-100-S-1X with a
  20 pF load; the key says series, and the row follows the key.
- **ECS-107-S-1X:** its abbreviation (107 = 10.738635 MHz) is not in the HC-49UX
  developed-frequency table; it is added as a listed exception.
- **Not generated:** 1.7971, 3.52180 and 10.6445 MHz (no stocked HC-49/U part);
  ABS07-32.768KHZ-1-T
  (its "1" may be the 0.65 mm height option or ±10 ppm); the odd-frequency ECS codes
  and the 32.000/100.000 kHz ABS25 parts.
- **MPN spellings:** Mouser prints AB-17.734475-B4 without "MHZ" (kept) and
  ABL4.194304MHZB2 without dashes (written as the key gives it, Mouser spelling in
  keywords).
- **Symbols:** stock `Device:Crystal` (2-pad and through-hole),
  `Device:Crystal_GND24` (ABM3B/ABM8G/ABM10: crystal on 1-3, lid on 2/4) and
  `Device:Crystal_GND23` (ABS25: crystal on 1-4; pads 2/3 float, so grounding them is
  harmless).
- **Footprints:** stock `Crystal:` footprints, Abracon-specific where KiCad has one.
  ABL uses `Crystal_HC49-4H_Vertical` (same land pattern, outline 0.5 mm taller);
  ABS07 uses the generic `Crystal_SMD_3215-2Pin_3.2x1.5mm`.

Follow-ups:
- A source for 10.6445 MHz (TRS-80), 1.7971 MHz (SWTPC) and 3.52180 MHz (VIP) would
  need a custom-crystal maker; leave as a note unless asked.
- HC-49/U-3pin, HC-18/U and HC-33/U holders are not seeded (no stocked parts at the
  vintage frequencies checked).

### Phase 7: through-hole trimpots (done 2026-11-21)

New table `potentiometers_th` on type `potentiometers` (fragment
`db/schema/types/potentiometers.sql`), registered in `table_map.json`, `PAIRS` and the
chooser as "Trimpots (Through-Hole)". Shared row builder and the Bourns standard
resistance table in `db/tables/potentiometers_th/_pot.py`. 152 rows, all Active:

| Generator | Rows | Parts |
|---|---|---|
| `run_300_bourns_3296.py` | 95 | Bourns 3296W/Y/P/X/Z-1-<code>LF, 25-turn, 3/8" square |
| `run_310_bourns_3362.py` | 57 | Bourns 3362P/H/U-1-<code>LF, single-turn, 1/4" square |

- **Specs** (both datasheets): ±10 %, 0.5 W at 70 °C (300 V max), ±100 ppm/°C, cermet,
  -55 to 125 °C. `value` is the end-to-end resistance (`10kΩ`), formatted by
  `passive_units`.
- **Codes:** every standard-table value (19) in each style, tube packaging, LF (tin)
  terminations, from the key "<model><style>-1-<code>LF". Mouser lists all 152 as
  Active (checked 2026-11-21); 78 were on order rather than in stock that day (e.g.
  3362P-1-102LF, 13,468 on order).
- **Symbol:** stock `Device:R_Potentiometer_Trim`: pins 1 and 3 the ends, 2 the wiper,
  matching Bourns' 1 CCW / 2 wiper / 3 CW.
- **Footprints:** stock `Potentiometer_THT:Potentiometer_Bourns_3296*` for the 3296.
  KiCad ships no 3362 footprint, so `run_310_bourns_3362.py` writes
  `Potentiometer_Bourns_3362{P,H,U}_Vertical` to
  `kicad_footprints/terra_footprints_potentiometers_th.pretty` from the datasheet
  pin-style drawings (pin 1 at the origin, 6.60 x 6.99 mm body, 1.44 mm pads on 0.8 mm
  drills as KiCad's 3296). The drawings are read as top views; the three styles are
  mirror-symmetric, so a mirrored reading would only swap pins 1 and 3.
- **Corrections to the original seed note:** 3296Y is top adjust (staggered pins), not
  side adjust; the 3296 has five pin styles and all are seeded. The standard table
  adds 25 kΩ and 250 kΩ to the 1-2-5 values.

Follow-ups:
- The 3362 side-adjust styles (M, S, W, X, Z) and top-adjust F and R are not seeded;
  each would need its own terra footprint.
- Carbon single-turn trimmers (Piher PT10/PT15 and the like), the round 3/8" Bourns
  3386 and SMT trimmers are not seeded.

