# relays_ssr — MOSFET-output solid-state relays seeded from KiCad

**Started:** 2026-10-01
**Status:** Built — 74 parts; open items below

## Intent

Stand up a `relays_ssr` table by taking every MOSFET-output (DC-switching) part in
KiCad's stock `Relay_SolidState` symbol library and turning it into fully-qualified
terra rows: KiCad's own symbol and a verified footprint, plus the parametric tail,
lifecycle and datasheet that KiCad doesn't carry. This is the template for the
long-term approach: leverage KiCad's symbols and footprints, bring parameters.

The immediate driver is replacing the end-of-life IXYS LAA110 with the Panasonic
AQW210EHA, so the Panasonic GE 2 Form A family (AQW21xEH) comes in too, using the
stock `Relay_SolidState:LAA110` symbol (pinout verified against the Panasonic
catalog).

## Scope

- **In:** the 52 MOSFET/DC-output parts in `Relay_SolidState` (Littelfuse/IXYS 30,
  Panasonic 10, Toshiba 9, Finder 2, Broadcom 1) plus Panasonic AQW21xEH.
- **Out (future AC table):** the 68 triac/thyristor-output parts (AQH, MOC30xx,
  FOD4xx, FODM30xx, Sharp S-series, TLP14x/16x, Finder 34.81-8240, HHG1D-1).

## Decisions

- **One row per package variant** the datasheet lists (DIP, SMD DIP, SO, flatpack,
  alternate pinouts). **No rows for packing** (tube, tape and reel, cut tape).
  The `mpn` is the orderable number without a packing suffix.
- **End-of-life parts are included and marked** in `lifecycle_status`
  (`Active` | `NRND` | `EOL` | `Obsolete`), so `terra_convert` can still match them
  on old boards. `EOL` = end of life announced, last-time buy still open; `NRND` =
  still made but not recommended; `Obsolete` = no longer orderable.
- **Symbols:** the stock KiCad symbol for the part. A variant KiCad doesn't list
  uses its sibling's symbol only when the pinout is identical.
- **Footprints:** a stock KiCad footprint checked against the datasheet package
  drawing; mismatches are recorded, not silently accepted.
- **`load_type` follows the datasheet rating table strictly**: a part rated only in
  DC (e.g. CPC1020N, 1.2ADC) is `DC` even if its output is back-to-back MOSFETs.
- **Datasheets** are stored in `datasheets/<mfr>/` and referenced via
  `${TERRA_EDA_LIB}`.
- **Columns** (`db/schema/types/relays_ssr.sql`): contact form, channels, load type,
  voltage/current rating, on-resistance, off capacitance, LED operate current and
  forward voltage, control voltage (Finder modules only), isolation voltage,
  turn-on/off time. Values follow the existing unit style (`60V`, `500mA`,
  `2.5Ohm max @ <condition>`).

## Build

Per-manufacturer data catalogs (`db/tables/relays_ssr/<mfr>_catalog.json`) are
harvested from the datasheets; one generator per manufacturer
(`run_300_panasonic_photomos.py`, `run_310_littelfuse_optomos.py`,
`run_320_toshiba_photorelay.py`, `run_330_broadcom_assr.py`,
`run_340_finder_3481.py`) turns them into rows.

## Results

74 rows from 6 catalogs (Panasonic 18, Littelfuse 36, Toshiba 13, Finder 6,
Broadcom 1); 16 Active, 44 EOL, 1 NRND, 13 Obsolete. Every symbol and footprint resolves
to a stock KiCad library item. `make verify` clean.

**Findings that differ from KiCad or from expectations**

- **The whole Littelfuse OptoMOS line is EOL:** PDN EIC-1177 (2026-08-13) phases
  out the "PCB SSR product family", last-time buy 2026-11-11. The PDN's affected-part
  attachment wasn't obtained; coverage of all 36 rows rests on Mouser/Digi-Key
  marking them EOL. (The harvest first marked them Active from a Jan 2026 product
  page and PCN EIC-1159, both of which predate the PDN.) The LAA110 -> Panasonic
  AQW210EHA replacement is the reason this table exists.
- **LBB110 symbol:** KiCad's stock LBB110 (extends TLP222A-2) draws normally-open
  MOSFETs. LBB110/S/P use `Relay_SolidState:CPC2125N` instead (dual Form B, same
  pin split, checked against the LBB110 pin configuration).
- **KiCad descriptions out of date:** TLP3542 is 60V / 2.5A / 100mOhm (KiCad says
  20V / 4A / 50mOhm); Finder 34.81-9024 is rated 6A (KiCad says 2A); CPC2025N is
  30Ohm max (KiCad gives the 20Ohm typical).
- **Toshiba:** TLP222A/-2 obsolete; TLP3123 and TLP3542–3546 EOL announced
  (replacements TLP3122A, TLP3543A, TLP3545A, TLP3546A); TLP175A NRND.
- **Panasonic AQY28x EH/EHA/S marked Obsolete by inference** (product pages gone,
  not in current series lists); no EOL notice found. Their data comes from 2003
  datasheets.

**Footprints marked close** (stock footprint usable, pads differ from the
datasheet's recommended land pattern): Littelfuse SOP-4 (CPC10xx/CPC11xx, ~0.1mm
row spacing), Panasonic SMD DIP (`SMDIP-4/8_W7.62mm`, ~1.2mm wider than the
recommended pattern), Toshiba (LF1) lead-form variants (`SMDIP-*_W9.53mm`).

**Open**

- Toshiba (LF1) rows only where a distributor listing confirmed the number;
  TLP3542/3543/3546 (LF1) probably exist but are unconfirmed.
- Not included: current-limited LAA110L/LS/PL (separate datasheet), Broadcom
  ASSR-1219/1228, and the newer Toshiba replacements.
- Several datasheets came from Wayback captures of the manufacturer files
  (Littelfuse blocks scripted downloads); CPC2017N is revision R06 and may not be
  the newest.
