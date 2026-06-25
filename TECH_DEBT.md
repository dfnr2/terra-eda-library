# Tech Debt & Deferred Work

Running backlog of known gaps, deferred scope, and follow-ups — the stuff we
consciously postponed while building, so it doesn't get lost when context
switches. Distinct from `plans/` (forward-looking design/worklists): this tracks
debt against work already landed.

**Format:** group by area. Each item is a checkbox with enough context to act on
cold — what, where (file/table), and why it was deferred. Check off and date when
resolved; delete stale items.

---

## ic_logic (74xx TTL/CMOS-TTL)

Landed 2026-06-25: 264 devices — 210 TTL harvested (`run_320_ttl_harvest.py`,
families 74/74LS/74HC/74HCT) + 5 curated (`run_310_ttl_canonical.py`) + 49
CD4000-series CMOS (`run_330_cd4000.py`, logic_family='4000B'). Each generator
also emits IEEE rectangular-symbol rows (`variant='IEEE'`) where KiCad's
`*_IEEE` libs cover the device — only a subset (67/164 TTL bases, 44/49 CD4000),
so most MSI parts have no IEEE alternative. 788 rows total.

- [ ] **Per-part dynamics are NULL** across all harvested parts (210 TTL + 49 CD4000):
  `propagation_delay`, `max_frequency`, `supply_current`. Not present in KiCad
  symbols — needs datasheet extraction. Only the curated 5 have them. Backfill
  the high-use parts first (counters, '245/'244 buffers, '74/'374 flip-flops).
- [ ] **Heuristic fields need a spot-check** (derived from symbol Description
  wording, not authoritative): `function_category`, `channels`,
  `inputs_per_gate`, `bit_width`, `logic_polarity`. ~115 MSI parts have NULL
  `channels` by design (a single counter/decoder has no channel count — leave).
- [ ] **74HC thresholds are @Vcc=4.5V representative values** (`vih_min` 3.15 /
  `vil_max` 1.35 in `FAMILY_EE`). Real HC inputs are Vcc-ratiometric (0.7/0.3·Vcc).
  Fine for parametric search; revisit if we want per-Vcc accuracy.
- [ ] **74LS629** (dual VCO) and **CD4046B** (PLL/VCO) are categorized `other` —
  legitimately not standard logic functions. Leave unless we add a category.
- [ ] **CD4000B levels are @Vcc=5V representative** (`vih_min` 3.5 / `vil_max` 1.5
  in `run_330` FAMILY_EE); real 4000B inputs are Vcc-ratiometric over a 3-18V
  supply, and the ~0.5mA drive scales strongly with Vcc. Fine for search.
- [ ] **CD4000 mfr/MPN/datasheet normalized to the TI CD4000B line** (CD<base>BE/BM,
  ti.com datasheet) for a coherent orderable part. A few devices only second-sourced
  elsewhere (some MC14xxx / HEF parts) may want a correction or 404-check on the URL.
- [ ] **Datasheets are TI URLs**, pulled from each symbol's Datasheet property
  (per agreement 2026-06-25). Only the curated 5 are local PDFs under
  `datasheets/ti/`. Optional: localize the most-used parts.

### Deferred logic scope (not yet harvested)
- [ ] **Modern specialty 74xx families** (~92 parts in `74xx.kicad_sym`): 74CBT
  bus switches, 74LCX / 74ALVC / 74LVC / 74AHCV translators. Not really "TTL";
  excluded from the retro harvest. Same `run_320` pattern extends to them if wanted.
- [x] **CD4000-series CMOS** (done 2026-06-25, `run_330_cd4000.py`) — 49 parts
  folded into `ic_logic` as logic_family='4000B'. The alternate IEEE-symbol lib
  `4xxx_IEEE.kicad_sym` was not harvested (same devices, different symbol style).

---

## ic_microcontrollers (Microchip ATmega)

Landed 2026-06-22: 29 active megaAVR devices (`db/tables/ic_microcontrollers/run_310_atmega.py`).

- [ ] **Datasheet download list** — 9 family datasheets still referenced by URL;
  only the 48/88/168/328 and 640/1280/2560 families are local. Download and
  repoint (drop in `staging/`, file into `datasheets/microchip/`):
  - 328PB → `ATmega328PB-Data-Sheet-DS40001984B.pdf`
  - 48PB/88PB/168PB → `ATmega48PB-88PB-168PB-Data-Sheet-40001906C.pdf`
  - 164PA/324PA/644PA/1284P → `ATmega164A_PA-324A_PA-644A_PA-1284_P_Data-Sheet-40002070B.pdf`
  - 324PB → `ATmega324PB-Data-Sheet-DS40001908A.pdf`
  - 16U2/32U2 → `doc7799.pdf`
  - 32U4 → `atmel-7766-8-bit-avr-atmega16u4-32u4_datasheet.pdf`
  - 16M1/32M1/64M1 → `doc8209.pdf`
  - 3208/3209/4808/4809 → `ATmega4808-4809-Data-Sheet-DS40002173A.pdf`
  - 406 → `doc2548.pdf`
  (all under `https://ww1.microchip.com/downloads/en/DeviceDoc/`)
- [ ] **Verify less-common peripheral counts** against datasheets — PWM/timer/ADC
  channel counts on the M1 (16M1/32M1/64M1) and megaAVR 0-series were set from
  general AVR data; the common parts (328P/2560/32U4) are solid.

---

## Cross-cutting

- [ ] **Lifecycle vocabulary** — `lifecycle_status` is free text (DEFAULT
  'Active'). Settle a controlled set: Active / Preview / NRND / Last Time Buy /
  Obsolete. Currently only Active and NRND are used.
- [ ] **`terra_sym.pretty` footprint catch-all** — ~64 orphan footprints, no part
  references them. Policy: leave, fix lazily (move to `terra_footprints_<table>`
  when a part is wired to one). The symbol catch-all is already depleted/removed.
