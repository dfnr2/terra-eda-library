# mosfet — through-hole classics (TO-92 small-signal, TO-220 power)

**Date:** 2026-11-25
**Status:** Done — 19 parts (3 TO-92 + 16 TO-220AB); see Results
**Scope:** add the common through-hole MOSFETs to the existing `mosfet` table, which
held only SMD parts. Two generators share a small helper:
`db/tables/mosfet/run_330_th_small_signal.py`, `run_340_th_power.py`, `_th_fets.py`.

## Motivation

The `mosfet` table had SOT-23 / DSO parts only. Hobby, repair and legacy-style designs
reach first for 2N7000 / BS170 / BS250 and the IRF/IRL TO-220 parts, so those should be
fully qualified parts in terra: real orderable MPN, local datasheet, verified pinout.

## Decisions

- **Table:** existing `mosfet` (type `transistors`). No schema change.
- **Orderable MPNs only.** Infineon "Orderable Part Number" (`IRF540NPBF` …); Vishay
  lead (Pb)-free code (`IRF540PbF`, recorded `IRF540PBF` as distributors list it; the
  halogen-free `-BE3` option is not recorded); onsemi straight-lead bulk codes
  (`2N7000`, `BS170`, `FQP27P06`); Diodes `BS250P`. Reel/ammo/formed-lead codes
  (`-D26Z`, `-D74Z`, `RLRAG` …) are packaging options and are not recorded.
- **Vishay originals are separate rows.** IRF520 / IRF540 / IRF9540 (Vishay) are
  different dies from Infineon's IRF520N / IRF540N / IRF9540N.
- **`value`** is the schematic label without packaging suffix (`IRF540N`, `IRF540`,
  `IRLB8721`, `BS250P`).
- **Logic-level** appears in description and keywords only where the datasheet specifies
  RDS(on) at Vgs = 4.5 V / 5 V: 2N7000 (4.5 V), IRLZ44N (5 V and 4 V), IRLB8721 (4.5 V).
- **P-channel magnitudes.** `v_ce_ds_max` / `i_c_d_max` hold magnitudes, as the table's
  existing BSS84AK / DMP rows do; descriptions, `rds_on` and `vgs_th` keep the sign.
- **`part_locator`** follows the table's existing form: `mosfet-nch-100v-33a-to220`.
- **Datasheets** parked in the local store and referenced through `${TERRA_EDA_LIB}`:
  `datasheets/infineon/<opn>.pdf` (new directory), `datasheets/vishay/irf*.pdf`,
  `datasheets/onsemi/{nds7002a-d,mmbf170-d,fqp27p06-d}.pdf`,
  `datasheets/diodes-inc/bs250p.pdf`.

## Symbols and pinouts

Every datasheet pinout was read (text or rendered drawing) and compared with the stock
`Transistor_FET` symbol's pin numbers (resolving `extends`). `_th_fets.check()` holds
that pin map and refuses any row whose symbol pin order or polarity differs from the
row's recorded datasheet pinout.

| Part(s) | Datasheet pins 1-2-3 | Symbol |
|---|---|---|
| 2N7000 | S-G-D | `Transistor_FET:2N7000` (S-G-D) |
| BS170 | D-G-S ("Pin Array DGS") | `Transistor_FET:BS170` (extends BS107, D-G-S) |
| BS250P | D, G, S lead labels on the E-Line drawing (no numbers) | `Transistor_FET:BS250` (D-G-S) |
| IRF540N, IRF9540N, IRLZ44N, IRF3205, IRF4905, IRLB8721, IRF740, FQP27P06 | G-D-S | the per-part stock symbol (all G-D-S) |
| IRFZ44N, IRF520N, IRF530N, Vishay IRF520 / IRF540 / IRF840 | G-D-S | `Q_NMOS_GDS` (no per-part stock symbol) |
| Vishay IRF9530 / IRF9540 | G-D-S | `Q_PMOS_GDS` |

No mismatches were found. Two near-misses were avoided: the stock `VN10LF` symbol is a
SOT-23 G-S-D part, and `IRF840A` is a different part from IRF840, so neither was borrowed.

Footprints: `Package_TO_SOT_THT:TO-92_Inline` and `Package_TO_SOT_THT:TO-220-3_Vertical`.
The BS250P E-Line body is "TO92 compatible" per its datasheet, which has no outline, so
`TO-92_Inline` is the nearest stock match, not a dimensioned one.

## Dropped

- **FQP30N06L** — onsemi product page: Obsolete.
- **VN10LF** — the only current datasheet (Diodes/Zetex, 1996) is SOT-23, not TO-92;
  out of scope for a through-hole round.
- **2N7000G / BS170G** (Motorola-lineage onsemi codes) — Obsolete; the active Fairchild
  lineage `2N7000` / `BS170` are used instead.
- **JFETs** (J310, 2N5457, 2N3819, MPF102, J111/J112, 2N5460) — not added; see below.

## JFETs: not in `mosfet`

The `transistors` fragment comment lists `jfet` as a `transistor_type`, but there is no
JFET table. The `mosfet` table is a poor home: a JFET's key parameters, IDSS and
VGS(off), have no columns (`vgs_th` would be misused for VGS(off)), and a table called
`mosfet` would mislabel them in the KiCad chooser. The clean route is a `jfet` table:
either `transistors` type plus two new columns (`idss`, `vgs_off`) or a small new
`jfet` fragment. Per the add-terra-table skill, column review comes first.

## Lifecycle sources (checked 2026-11-25)

Digi-Key and Mouser refused scripted fetches, so manufacturer pages were used:

- **Infineon** (`infineon.com/part/<base>` "Product Status"): all Active except IRF520N
  "not for new design" → `NRND`, and IRLB8721 "discontinued" → `Obsolete`. Both are
  kept because they are very common classics. Drop them if new designs should never see
  them.
- **onsemi** (product-page schema `itemCondition` per OPN): 2N7000, BS170, FQP27P06
  Active; FQP30N06L Obsolete.
- **Vishay**: the product pages give no status. Recorded Active from Future Electronics
  listings and Vishay process PCNs (2025–2026) naming IRF740PBF / IRF840PBF / IRF9530PBF
  as current production. **Recheck at a distributor.**
- **Diodes BS250P**: diodes.com returned 403. Recorded Active from Octopart ("in
  production") and a distributor listing. **Recheck at a distributor.**

## Build & verify

1. `make mosfet-generate && make mosfet-build`
2. Spot-check rows against the datasheets (MPN, Vds, Id, Pd, RDS(on) condition, Vgs(th),
   Tj, symbol pinout).
3. `uv run python -m pytest -q tests/`

## Results

- `run_330_th_small_signal.py`: 3 rows (onsemi 2N7000, BS170; Diodes BS250P).
- `run_340_th_power.py`: 16 rows. Infineon 9 (IRF540N, IRF9540N, IRLZ44N, IRFZ44N,
  IRF3205, IRF4905, IRLB8721, IRF520N, IRF530N), Vishay 6 (IRF520, IRF540, IRF740,
  IRF840, IRF9530, IRF9540), onsemi 1 (FQP27P06).
- `db/mosfet.db` builds with 25 rows: 6 existing plus 19 new.
- Tests: 218 passed. 1 failure is unrelated, from another table's symbol lib
  registration (`terra_symbols_voltage_regulator`).
- Spot-checked against the datasheets: IRLZ44N (22/25/35 mΩ at 10/5/4 V, Vth 1–2 V),
  IRLB8721 (8.7 mΩ at 10 V, 16 mΩ at 4.5 V), IRF3205 (110 A with a 75 A package limit),
  Vishay IRF840 (500 V, 8 A, 0.85 Ω, Tj 150 °C), 2N7000 (400 mW, 5 Ω / 5.3 Ω).

## Follow-ups

- Recheck Vishay and BS250P lifecycle at Digi-Key/Mouser.
- Decide on a `jfet` table (columns: `idss`, `vgs_off`) and add J310 / 2N5457 / 2N3819 /
  J111 / J112 / 2N5460 from current sources (InterFET / Central / onsemi).
- Possibly add Diodes E-Line ZVN2106A / ZVP2106A as active TO-92-compatible companions.
