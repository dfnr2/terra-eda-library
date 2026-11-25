# optocouplers: classic through-hole DIP optocouplers

**Date:** 2026-11-25
**Status:** Done. 29 rows; see Results.
**Scope:** a new `optocouplers` table holding the DIP optocouplers that show up on
most schematics: the 4N25..4N37 and CNY17 phototransistor parts, the 4N32/4N33
photodarlingtons, PC817, the 6N135..6N139 high-speed and split-Darlington parts,
the 6N137/HCPL-2601/HCPL-2630 logic-gate parts, H11L1, H11AA1 and the MOC30xx
triac drivers. Through-hole DIP only. MOSFET-output photorelays stay in
`relays_ssr`.

## Schema

The table uses the new type fragment `db/schema/types/optocouplers.sql`. In
`table_map.json` it has `tier_default` 2 and `dump_priority_default` 1, with no sim
fields. It has a `PAIRS` entry in `tests/test_schema_consolidation.py`. Column names
and units follow `relays_ssr.sql` where the meaning is the same (`channels`,
`isolation_voltage`, `led_forward_voltage`, `led_operate_current`, `turn_on_time`,
`turn_off_time`).

| Column | Holds |
|---|---|
| `output_type` | phototransistor, darlington, logic, transistor-high-speed, schmitt, triac-driver, or triac-driver-zc |
| `channels` | couplers per package |
| `isolation_voltage` | I/O withstand voltage, e.g. `5000Vrms` |
| `ctr` | CTR with its test condition. NULL for logic, Schmitt and triac outputs |
| `led_forward_voltage` | Vf typ/max, with condition |
| `led_operate_current` | the LED current needed to switch: IFT (triac), IF(on) (H11L1), ITH (6N137 family), or the minimum input ON current (6N138/6N139). NULL for phototransistors |
| `output_voltage_max` | VCEO (6-pin and 4-pin transistor outputs), VDRM (triac drivers), or VO/VCC max (8-pin parts and H11L1) |
| `output_current_max` | IC, IO or ITM. NULL where the sheet gives none |
| `turn_on_time`, `turn_off_time` | max unless marked `typ`. For the 8-pin parts these hold tPHL/tPLH (tPHL is turn-on: LED on, output low). For PC817 they hold tr/tf, the only times its sheet gives |

## Generator

| File | Role |
|---|---|
| `db/tables/optocouplers/run_310_th_optocouplers.py` | the 29 parts as `Part(...)` records transcribed from their sheets |
| `db/tables/optocouplers/_opto.py` | `Part` record, row builder, symbol and pinout check, writer |

Each row has `source=NULL`, `dump_priority=0` and `tier=2`. Each INSERT names its
columns. `unique_id` is `<Manufacturer>-<MPN>`, and a duplicate stops the build.
`value` is the bare type number (`4N35`, `PC817`, `MOC3021`).

## Sources

The vendor preference followed the brief: Vishay for the 4N/CNY17 line, onsemi as
the fallback, Broadcom for the 6N13x/HCPL parts, Sharp for PC817 and onsemi for the
MOC and H11L parts. CERN data was not used for anything.

| Maker | Parts | Data sheet |
|---|---|---|
| onsemi | 4N25M, 4N26M, 4N27M, 4N28M, 4N35M, 4N36M, 4N37M | `onsemi/4n37m-d.pdf` (Rev. 2, Sep 2021) |
| onsemi | 4N32M, 4N33M | `onsemi/h11b1m-d.pdf` (Rev. 2, Apr 2022) |
| onsemi | H11L1M | `onsemi/h11l3m-d.pdf` (Rev. 4, Sep 2024) |
| onsemi | MOC3021M, MOC3022M, MOC3023M | `onsemi/moc3023m-d.pdf` (Rev. 3, Jun 2023) |
| onsemi | MOC3041M, MOC3043M | `onsemi/moc3043m-d.pdf` (Rev. 4, Sep 2022) |
| onsemi | MOC3063M | `onsemi/moc3163m-d.pdf` (Rev. 3, Sep 2022) |
| Vishay | CNY17-1, CNY17-2, CNY17-3, CNY17-4 | `vishay/cny17.pdf` (doc 83606, Rev. 2.1, Jan 2014) |
| Vishay | H11AA1 | `vishay/h11aa1.pdf` (doc 83608, Rev. 2.0, Mar 2026) |
| Broadcom | 6N135-000E, 6N136-000E | `broadcom/6n135-6n136-hcpl-2502.pdf` (AV02-0171EN, Jan 2019) |
| Broadcom | 6N137-000E, HCPL-2601-000E, HCPL-2630-000E | `broadcom/6n137-hcpl-2601-2630.pdf` (AV02-0940EN, Mar 2021) |
| Broadcom | 6N138-000E, 6N139-000E | `broadcom/6n138-6n139-hcpl-0700.pdf` (AV02-1359EN, Feb 2025) |
| Sharp | PC817XNNSZ1B | `sharp/pc817xxnsz1b.pdf` (OP18002EN, Jan 2018); `datasheets/sharp/` is a new directory |

**Ordering codes.** Each part uses one MPN: the plain DIP tube or bulk code.

- **onsemi:** the bare `...M` code (DIP-6, tube or bulk bag). Not used: `S`
  (gull-wing), `SR2` (reel), `T` (0.4" leads) and `V` (VDE).
- **Vishay:** the bare code (`CNY17-1`, `H11AA1`). Not used: `X001` (VDE), `X006`
  (400 mil), `X007T`/`X009T` (SMD).
- **Broadcom:** `-000E`, the RoHS plain 300-mil DIP-8, 50 per tube.
- **Sharp:** `PC817XNNSZ1B`, the through-hole sleeve part with no CTR rank
  (IC 2.5-30mA at IF=5mA). Ranked codes `X1`..`X0` and the `NIP1B` gull-wing reels
  are not used.

**Why onsemi supplies the 4N parts.** The brief made Vishay the default, but
Vishay's own pages don't show the 4N parts as current:

- Vishay's phototransistor-output selector (`/en/optocouplers/opt-tran-output/`,
  85 rows) lists CNY17, CNY17F, H11D and the SFH6xx parts, but not 4N25..4N28 or
  4N35..4N37.
- The photodarlington selector (7 rows) has no 4N32/4N33, and Vishay has no
  4N32/4N33 product page at all.
- The 4N25 and 4N35 product pages are still online, but their datasheets date
  from 2010 (Rev. 1.8 and Rev. 1.2) and still cite RoHS 2002/95/EC.
- The product pages render their part tables client-side, so no per-part status
  could be read from them.

onsemi's product pages list every 4NxxM code as Active, so onsemi was used. The
Vishay 4N25/4N35 sheets were downloaded but not committed.

## Symbols and footprints

All footprints are stock: `Package_DIP:DIP-4_W7.62mm`, `DIP-6_W7.62mm` and
`DIP-8_W7.62mm`. No row needed DIP-16, because PC847 was left out (see Not added).

All symbols are stock, from `Isolator` and `Relay_SolidState`, except 4N32/4N33.
KiCad 10 has no 4N32 or 4N33 symbol and no DIP-6 photodarlington with a base pin,
and borrowing the single-transistor `4N25` drawing for a Darlington was ruled out.
So `kicad_symbols/terra_symbols_optocouplers.kicad_sym` (new, auto-registered by
`make lib-tables`) adds:

- `4N32`, drawn from `Isolator:4N25`, with the same LED and pins 1-5. A Darlington
  pair replaces the phototransistor, and the base pin (6) enters from below.
- `4N33`, which extends `4N32`.

### Pinout check

Most stock opto symbols leave their pins unnamed and show the function only in the
drawing, so `_opto.py` checks pinouts in two steps:

1. **The symbol.** `SYMBOL_PINS` records the function of every pin of each root
   symbol (the end of the `extends` chain), read off the drawing. At generation
   time `check_symbol()` re-parses the library and holds that record to everything
   the file states directly:
   - the pin-number set;
   - which pins are no-connect;
   - the pin names, where the symbol has any;
   - the side of the body each pin sits on: LED pins on the left; outputs on the
     right; VCC on the top or right; GND on the bottom or right.
2. **The data sheet.** Each `Part` carries its sheet's pin table, which must equal
   the recorded functions of its symbol pin for pin.

A failure at either step stops the build. These mismatches were tried, and each
was rejected:

- 4N35 with emitter and collector swapped;
- H11L1 on the `4N25` symbol;
- 6N138 on the `6N137` symbol;
- PC817 on the generic `Optocoupler_DC_PhotoNPN_AKEC` symbol;
- HCPL-2630 declared as single-channel;
- a duplicate row;
- a tampered `SYMBOL_PINS` entry.

| Pin table | Parts | Root symbol |
|---|---|---|
| 1 A, 2 K, 3 NC, 4 E, 5 C, 6 B | 4N25..4N37, CNY17-x, 4N32/4N33 | `Isolator:4N25`, `Isolator:CNY17-1`, `terra_symbols_optocouplers:4N32` |
| 1 A/K, 2 K/A, 3 NC, 4 E, 5 C, 6 B | H11AA1 | `Isolator:H11AA1` |
| 1 A, 2 K, 3 E, 4 C | PC817 | `Isolator:PC817` |
| 1 NC, 2 A, 3 K, 4 NC, 5 GND, 6 VO, 7 VB, 8 VCC | 6N135/6N136, 6N138/6N139 | `Isolator:6N135`, `Isolator:6N138` |
| 1 NC, 2 A, 3 K, 4 NC, 5 GND, 6 VO, 7 VE, 8 VCC | 6N137, HCPL-2601 | `Isolator:HCPL-261A` (6N137 extends it), `Isolator:HCPL-2601` |
| 1 A1, 2 K1, 3 K2, 4 A2, 5 GND, 6 VO2, 7 VO1, 8 VCC | HCPL-2630 | `Isolator:HCPL-263A` |
| 1 A, 2 K, 3 NC, 4 VO, 5 GND, 6 VCC | H11L1 | `Isolator:H11L1` |
| 1 A, 2 K, 3 NC, 4 MT, 5 NC (triac substrate), 6 MT | MOC302x, MOC304x, MOC306x | `Relay_SolidState:MOC3010M`, `MOC3031M` |

Every data sheet agreed with its stock symbol's drawing. Some symbols differ in
smaller ways:

- **`Isolator:6N138`/`6N139` pin names are wrong; its drawing is right.** The
  symbol names pins 2/3 `C1`/`C2` (they are the LED anode and cathode) and pins
  7/6 `VO1`/`VO2`. Its drawing makes pin 7 the first emitter / second base (VB) and
  pin 6 the output collector (VO), which matches Broadcom's sheet. `NAME_QUIRKS`
  lists these names exactly, so if the library renames them the check fails and
  someone reviews them. The pin names are labels only; the connections are
  correct.
- **`Isolator:6N137` extends `HCPL-261A`,** whose NC pins 1 and 4 are `passive`
  pins named `NC`, not `no_connect` pins. The check counts the name.
- **Stock `CNY17-x`, `6N138`, `H11L1` and the MOC30xxM symbols carry an empty
  Footprint property.** The
  row's `kicad_footprint` governs.
- **The stock symbols' Description text is out of date.** For example, `4N35` says
  "Vce 70V", while onsemi 4N35M is rated VCEO 30V. Descriptions come from the rows,
  not the symbols.

## Data notes

- **onsemi 4NxxM:** VCEO is 30V for every grade, including 4N35..4N37. The sheet
  gives no collector-current rating, only a detector PD of 150mW, so
  `output_current_max` is NULL. 4N25..4N28 give only typical switching times
  (2us typ); 4N35..4N37 give a 10us max.
- **Vishay CNY17:** the times are the typical non-saturated ones (IF=10mA, VCC=5V,
  RL=75R).
- **Vishay H11AA1:** the sheet has no IC rating and no switching table, so those
  fields are NULL. AC input is recorded in the description and keywords
  (`ac-input`, `bidirectional-input`).
- **Sharp PC817:** the cover text says "CTR 50% to 400%", but the
  characteristics table gives IC = 2.5-30mA at IF=5mA, which is 50-600%. The row
  follows the table.
- **Broadcom 6N135/6N136:** the sheet gives two sets of output ratings. Broadcom
  guarantees VCC 30V / VO 20V; the JEDEC registration is 15V for both. The row
  stores `20V (VO; JEDEC 15V)`.
- **Broadcom 6N138/6N139:** CTR and delays are at each part's own spec point:
  IF=1.6mA for 6N138, IF=0.5mA for 6N139.
- **MOC302xM:** the sheet gives no repetitive on-state current, only ITSM of 1A
  peak (100us, 120pps), so that is what the row stores. MOC304xM and MOC306xM give
  ITM of 100mA peak.
- **Not filled:** operating temperature and other core fields the bjt generators
  also leave empty.

## Lifecycle (2026-11-25)

All 29 rows are Active, taken from the makers' sites on 2026-11-25:

- **onsemi:** every `...M` product page (`product.do?id=<MPN>`) lists the bare DIP
  code as Active in its orderable-parts table.
- **Broadcom:** the product JSON behind each product page
  (`/api/getjson?url=products/optocouplers/...`) shows `lifecycle: Active` for
  6N135, 6N136, 6N137, 6N138, 6N139, HCPL-2601 and HCPL-2630.
- **Vishay:** the product pages show no per-part status to a scripted fetch. CNY17
  and H11AA1 are taken as Active because both are in Vishay's current selector
  tables, and the H11AA1 sheet was revised in March 2026.
- **Sharp:** PC817XxNSZ1B is on Sharp's current photocoupler lineup page (DIP 4-pin).

**A distributor check is still owed.** Digi-Key and Mouser refuse scripted fetches,
so nobody has checked these rows against distributor status or recent PDNs. The
Vishay rows need it most.

## Not added

| Part | Why |
|---|---|
| PC827, PC847 | Not on Sharp's current photocoupler lineup, which lists only 4-pin DIP parts (PC123, PC1231, PC817, PC8171, PC851, PC852). Stock `Isolator:PC827`/`PC847` symbols exist if another maker's part is wanted later |
| Vishay 4N25..4N28, 4N35..4N37 | Not in Vishay's current selector tables, and the sheets date from 2010; taken from onsemi instead |
| Vishay 4N32/4N33 | No Vishay product page or selector entry; taken from onsemi instead |

No part on the approved list was marked NRND, obsolete or EOL by the maker that
supplied it.

## Fetching

| Site | Result |
|---|---|
| onsemi | Product pages (`product.do?id=`) and `/download/data-sheet/pdf/<x>.pdf` work with curl and a browser User-Agent. The old `/pdf/datasheet/<x>.pdf` path now returns an HTML page |
| Broadcom | `docs.broadcom.com/docs/<id>` returns an HTML wrapper; `docs.broadcom.com/doc/<id>` returns the PDF. Product pages are a JS app; the data is at `/api/getjson?url=<path>&locale=en-us` |
| Vishay | `vishay.com/docs/<n>/<x>.pdf` and the category pages (server-rendered selector tables) work. Product pages build their part tables client-side, so they show no status |
| Sharp | `global.sharp/products/device/lineup/data/pdf/datasheet/<x>.pdf` and the lineup pages work. `sharp-world.com` did not respond |
| Claude in Chrome | Not connected, so it was not used to render the Vishay pages |

## Results

- **Rows:** 29 in the new `optocouplers` table.

  | Output type | Rows | Parts |
  |---|---|---|
  | phototransistor | 13 | 4N25..4N28, 4N35..4N37, CNY17-1..-4, H11AA1, PC817 |
  | darlington | 4 | 4N32, 4N33, 6N138, 6N139 |
  | transistor-high-speed | 2 | 6N135, 6N136 |
  | logic | 3 | 6N137, HCPL-2601, HCPL-2630 |
  | schmitt | 1 | H11L1 |
  | triac-driver | 3 | MOC3021, MOC3022, MOC3023 |
  | triac-driver-zc | 3 | MOC3041, MOC3043, MOC3063 |

- **By maker:** onsemi 16, Broadcom 7, Vishay 5, Sharp 1.
- **Checks at generation:**
  - every symbol passed the pinout check;
  - every footprint resolves in the stock KiCad 10 library;
  - every data sheet path exists.
- **Build and tests:** all pass:
  - `make schema`;
  - `make optocouplers-generate && make optocouplers-build`;
  - `make && make verify`;
  - `uv run pytest -q tests/` (220 passed).
- **Spot checks against the sheets:** MPN, value, symbol, footprint and every tail
  field match for 4N35M, 6N138-000E, MOC3043M, PC817XNNSZ1B and HCPL-2630-000E.

## Follow-ups

- **Distributor lifecycle check** at Digi-Key/Mouser from a browser, especially the
  Vishay rows.
- **Vishay 4N parts:** if a rendered Vishay product page or a distributor shows
  them still in production, Vishay rows can be added beside the onsemi ones.
- **PC827/PC847 equivalents:** Lite-On's LTV-827/LTV-847 are an option, and stock
  symbols exist for them. They were not on the approved list.
- **SPICE:** none of these rows has a model. Vendor opto models could be parked in
  `spice/<mfr>/`.
