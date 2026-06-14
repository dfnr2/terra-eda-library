# Project conversion to terra — working plan

Converting existing KiCad projects to terra parts with `tools/terra_convert.py`.
First target: `abc4-spiro-hw/mainboard`. Working/disposable plan — visible in the
repo; commit only if it outlives the work.

## Pipeline status
- [x] **#1** quality-aware read-only converter (`tools/terra_convert.py`) — committed `f1960cb`
- [x] **#2** ferrite resolution — **library side DONE 2026-06-14**: full Murata BLM18…N1
      family generator built; rotten BLM18 rows replaced. Remaining piece is schematic-side
      (BD121 vs BD221 per rail) and belongs to #6. See *Ferrite generator* below.
- [x] **#3** substitution policy — decided; see *Approved substitutions*
- [x] **#4** harvest gap parts → native terra tables — **DONE 2026-06-14.** All 21 gap
      instances (12 distinct parts) now resolve to tier A; converter reports **0 gaps**
      (A=43, B=26, C=0). Footprints migrated into per-category libs (terra-diodes,
      terra-connectors, terra-test-points) with their 3D models; new `test_points` and
      `batteries` tables added. See *Harvest manifest* (done) below.
- [ ] **#5** `U2` PCA9306DCT: port `cern_analog_interface` → native, delete the CERN entry
- [ ] **#6** stage-4 write engine — **designed:** `specs/200-stage4-write-engine/write-engine-spec.md`
      (4a terra-side writes via `terra_harvest`; 4b pin-preserving schematic rewrite via
      `terra_rewrite`). Next: review the spec, then implement 4a first.

## mainboard.kicad_sch — current result (69 real parts)
- **22 drop-in** (exact MPN): ferrites (12, see conflict), ICs (5), LEDs (2), 2 already-terra
- **26 substitute** (safe / meet-or-exceed): 12 resistors (Yageo RT thin-film), 14 caps
  (KEMET X7R → Samsung CL X7R ≥16V)
- **21 gap** → ~13 native parts to harvest

## Harvest manifest (gaps → native terra; the curated project parts ARE the source)
All 12 distinct parts carry a datasheet + real description, so these are clean ports.
**Footprint note (#4):** the connectors, SM712, and the test point carry hand-curated `nema:`
footprints to migrate into terra's footprint assets; the 3 simple TVS use standard KiCad fps.

- → **`diodes`** (native): `VESD05A1-02VHG3-08` (4, std fp), `SMF18A` (2, std), `SMF6.0A`
  (1, std), `SM712-02HTG` (2, fp `nema:SM71202HTG`; near-match in `cern_diodes` → port + delete-CERN)
- → **`connectors`** (native; all custom `nema:` fps): Molex `15912240` (3) / `15912040` (1),
  Hirose `DF3A-8P-2DSA`, Kycon `STX-3500-3NTR`, Leader Tech `14-37FSV30-BD-16`, `RRC-MC20-90-10`
- → **`test_points`** (NEW native table — decided 2026-06-13): Keystone `5017` (3). New type:
  canonical core + small tail (style loop/pad, pad size, mount SMT/THT, color); add
  `db/schema/types/test_points.sql` + table_map entry + `db/tables/test_points/` + a generator,
  and migrate the `nema:` footprint.
- → **`batteries`** (NEW native table — decided 2026-06-13): `RRC2054` (1), 14.4V / 3.4Ah /
  49Wh Li-ion smart pack. New type: canonical core + tail (chemistry, nominal_voltage_v,
  capacity_ah, energy_wh, rechargeable, smart/interface); add `db/schema/types/batteries.sql`
  + table_map entry + `db/tables/batteries/` + a generator.

## Ferrite generator (#2 — LIBRARY SIDE DONE 2026-06-14)
Built `db/tables/ferrites_smt/run_500_murata_blm18.py`, a datasheet-driven generator for
the full Murata BLM18…N1 0603 family (74 parts) from the parked spec
`murata_blm18xxxxxxN1x_datasheet.pdf` (JENF243A_0003AN-01). Removed the two cut/paste-rotted
hand-migrated BLM18 rows (the generator supersedes them); kept the non-BLM18 parts
(Bourns MH2029, Murata BLM41) and fixed BLM41's rotted `value` field. Symbol
`Device:FerriteBead_Small`, footprint `Inductor_SMD:L_0603_1608Metric`.
- **"EG" myth busted:** no `BLM18EG…` series exists in the datasheet. The terra migrated
  row `BLM18EG121SN1D` was a typo for `BLM18PG121SN1D` (120Ω / 2A DC-power-line); now present.
- **The real schematic rot (open decision, drives #6, NOT a library task):** all 12 small
  `FB` symbols carry MPN `BLM18BD221SN1D` (220Ω / 250mA) but value text "120 ohm 300 mA"
  = `BLM18BD121SN1D`. `terra_convert` now surfaces this as a per-instance CONFLICT (it was
  masked before, when terra held matching rotten rows). terra carries BOTH parts, so the fix
  is purely schematic-side: decide 120Ω/300mA (BD121) vs 220Ω/250mA (BD221) per rail and
  rewrite the MPN. FB9 = `BLM41PG600SN1L` (60Ω/6A) is correct; only its value text is rot.
- **Bourns MH series:** also generated now — `run_510_bourns_mh.py` builds the full
  MH-series family (27 parts, 0603/0805/1206) from `bourns_mh_ferrites_datasheet.pdf`,
  superseding the hand-migrated MH2029-800Y row (which is a library part, not used on this
  board). Only the Murata BLM41 (1806) remains hand-migrated. ferrites_smt = 102 rows.
- **Rename prerequisite:** DONE earlier (`ferrites` → `ferrites_smt`).

## Approved substitutions (#3 — decided 2026-06-13)
Resistors accepted as-is (50 ppm RT is fine; nothing here needs a tighter tempco). Caps
derated to **25V** X7R (Dave: 25V derated parts OK) — produced automatically by
`terra_convert.py --derate` (default remains smallest-sufficient, i.e. 16V).

Resistors (12) — Yageo RT thin-film, same value / 1% / 1/10W / 0603:
```
RT0603FRE07120RL -> RT0603FKE07120RL   (R4, R5)
RT0603FRE07130RL -> RT0603FKE07130RL   (R11, R12, R13)
RT0603FRE07300RL -> RT0603FKE07300RL   (R1)
RT0603FRE072K2L  -> RT0603FKE072K2L    (R9, R10)
RT0603FRE0722KL  -> RT0603FKE0722KL    (R14)
RT0603FRE07200KL -> RT0603FKE07200KL   (R6)
RT0603FRE071ML   -> RT0603FKE071ML     (R2, R3)
```
Caps (14) — KEMET X7R 16V -> Samsung CL X7R **25V** 10% 0603:
```
C0603C104K4RACTU -> CL10B104KA8NNN   (0.1uF; C1,C3,C5,C7,C9,C11,C13)
C0603C105K4RACTU -> CL10B105KA8NNN   (1uF;  C2,C4,C6,C8,C10,C12,C14)
```

## Open decisions
- **#2 ferrites:** which bead is actually intended — resolved by the deferred generator above;
  confirm the rail current (≤300mA vs >300mA) and 120Ω vs 220Ω when we build it.
