# ic_logic datasheet harvest — dynamic parameters

**Date:** 2026-06-28
**Status:** Done (2026-06-28) — all 259 devices have entries (28-part tail filled
manually from `ic_logic_with_good_urls.csv`); see Results below
**Scope:** the `ic_logic` table only (74xx TTL + CD4000 CMOS). Other tables and
the CERN sweep are out.

## Motivation

The 74xx and CD4000 harvests (`run_320`, `run_330`) derive every *functional*
parameter from the KiCad symbols, but three *dynamic* electrical parameters are
not in the symbols and were left `NULL` for a datasheet pass:

- `propagation_delay`
- `max_frequency`
- `supply_current`

(`bit_width` is also occasionally `NULL`; it is a functional value and is **not**
in scope here.) Supply voltages, I/O levels (`vih`/`vil`/`voh`/`vol`), and
`output_current` are already filled per-family by the generators and are left
untouched.

This round fills those three columns from the manufacturers' datasheets and
nothing more.

## Decisions

### Source: read the datasheets (not Nexar) for this table

The `2026-06-11` resolver design locked Nexar's structured `specs` as the param
source and rejected datasheet extraction. That decision stands library-wide, but
**ic_logic is harvested from the datasheets instead**, deliberately, because:

- **Quota.** ~259 logic devices would consume a quarter of the Nexar
  1000-matched-parts/month budget — better spent on parts where structured data
  is harder to get (MCUs, analog).
- **Reliability.** 7400/4000-series dynamics are highly standardized and clearly
  tabulated; a cheap model reads them reliably. A 3-device pilot (below)
  confirmed this.
- **Nexar coverage of these three attributes for logic was never confirmed**, so
  the datasheet is the surer source here.

### Interim datasheet handling

Per the user's call for this round (a fuller storage/link plan comes later, see
[datasheet-storage.md](datasheet-storage.md) and
[datasheet-harvest-pending.org](datasheet-harvest-pending.org)):

- Downloaded PDFs go to a **gitignored scratch dir**, not the repo
  `datasheets/<mfr>/` store. The repo is not loaded up with PDFs this round.
- The parts' existing `datasheet` URLs are **left as-is** — not repointed.
- The canonical manufacturer URL each agent actually used **is banked** in the
  data file (`datasheet_url`) so the later link-cleanup has a clean source.

### Fill-blanks-only, never guess

Governing principle is "sparse but high quality": a value is written only when an
agent confirms it from the actual datasheet PDF. Anything it cannot confirm is
left `NULL` and logged — never fabricated.

### DB stays read-only after build

No sidecar, no `apply_harvest.py`, no post-build `UPDATE` (the `2026-06-10`
design's `apply_harvest` is dead). Harvested values live in a committed data file
that the **generators** read at generate time, so `terra.db` remains a pure
artifact of its sources. Honors the `db-read-only-after-generation` rule.

## Architecture

### A. Committed data file

`db/tables/ic_logic/ic_logic_datasheet_params.json`, keyed by
`"<logic_family>/<base_number>"` — the join both generators already share
(`run_320` → `74LS`/`161`; `run_330` → `4000B`/`4017`):

```json
{
  "74HC/00": {
    "propagation_delay": "9 ns typ (Vcc=4.5V, CL=15pF)",
    "max_frequency": null,
    "supply_current": "20 µA (Icc max, Vcc=6V)",
    "datasheet_url": "https://www.ti.com/lit/gpn/sn74hc00",
    "_prov": { "src": "datasheet", "conf": "high", "date": "2026-06-28" }
  }
}
```

`null` is a deliberate, recorded "no such spec for this device" (e.g. a plain
gate has no `max_frequency`), distinct from a missing key (not yet harvested).

### B. Generator integration

`run_320` and `run_330` each load the JSON and, for the three target columns,
set the value **only where the generator currently produces `None`**
(fill-blanks-only). Family electrical levels and all functional fields are
untouched. IEEE-symbol clones inherit the values through the existing `{**r}`
spread. `run_310` (curated, already carries hand-checked dynamics) and `run_300`
(4 sparse one-offs) are left alone. Rebuilt with
`make ic_logic-generate && make ic_logic-build`.

### C. Harvest run + honesty guards

One cheap (haiku) agent per device:

1. Find the canonical manufacturer datasheet (TI `lit/gpn` for 74xx/CD4000B;
   Nexperia acceptable for 74HC equivalents).
2. Download it to the gitignored scratch dir and **open the PDF** (not from
   memory).
3. Extract the three params in a **pinned format**:
   - `propagation_delay`: `"<typ> ns typ (<path/conditions>)"`, at Vcc/Vdd = 5 V.
   - `max_frequency`: `"<value> MHz (<conditions>)"`, or `null` for a
     non-clocked part (combinational gates, buffers, decoders without a clock).
   - `supply_current`: quiescent `Icc/Idd` in µA for **CMOS** (74HC/HCT, 4000B);
     operating `Icc` in mA for **bipolar TTL** (74/74LS).
4. Return strict JSON under an enforced schema: device key, the three params,
   `datasheet_url`, `pdf_opened`, `source`, `confidence`, and a `notes` field
   citing the exact table/section.

Guards: `pdf_opened` must be true and the table must be cited; unconfirmable
values → `null` + logged; low-confidence or out-of-plausible-range entries
(family sanity bands for ns / MHz / current) get a **second-agent verify pass**.
Conflicts and low-confidence entries are written to a review file for a human
glance before the values are trusted.

### D. Execution: batched agent fan-out

Driven from the main session (no Workflow). The worklist is the distinct
`(logic_family, base_number)` set from `run_320` + `run_330`. Agents run in
capped-concurrency batches; results are merged into the data file. Resumable by
skipping device keys already present in the file.

## Scope / worklist

| source | family span | distinct devices |
|--------|-------------|------------------|
| `run_320` (TTL) | 74, 74LS, 74HC, 74HCT | 210 |
| `run_330` (CD4000) | 4000B | 49 |
| **total** | | **259** |

3 done in the pilot (74HC00, 74LS161, CD4017B); 256 remain. `run_310`'s 5
curated parts and `run_300`'s 4 one-offs are excluded.

## Pilot evidence (2026-06-28)

Three haiku agents each downloaded and read the real TI PDF:

| device | propagation_delay | max_frequency | supply_current |
|--------|-------------------|---------------|----------------|
| 74HC00 | 9 ns (Vcc=4.5V, CL=15pF) | `null` (gate — correct) | 20 µA (Icc max, Vcc=6V) |
| 74LS161 | 14 ns (clk→Q, Vcc=5V) | 32 MHz | 31 mA (Icc, outputs high) |
| CD4017B | 325 ns min / 850 ns max (Vdd=5V) | 5 MHz (Vdd=5V) | 5 µA (Idd max, Vdd=5V) |

All cited specific datasheet tables; current basis varied correctly by family
(µA quiescent for CMOS, mA operating for TTL); the gate correctly produced no
`max_frequency`. CD4017B returned min/max rather than the more useful typ —
hence the **pinned typ-format** in §C, applied uniformly in the production run.

## Out of scope (deferred)

- **Repo PDF storage** and **`datasheet`-link repointing** — a separate plan.
- **Nexar** — not used for this table this round.
- **`run_300`'s 4 one-offs** and any other table.
- `bit_width` and other functional gaps.

## Verification

- `make ic_logic-generate && make ic_logic-build && make verify` after
  integration.
- Spot-check a sample of filled rows against their datasheets.
- Confirm fill-blanks-only: the 5 `run_310` curated rows and all family
  electrical levels are byte-identical before/after.
- Review the low-confidence/conflict file before trusting flagged values.

## Results (2026-06-28)

Harvested with batched haiku agents reading the actual TI/Nexperia PDFs.
**231 / 259 devices filled (89%); 0 numeric sanity outliers.** `make verify`
clean (261 tests pass). Fill-blanks-only confirmed: the `run_310` curated rows
and the per-family electrical levels are unchanged.

| family | filled | null tail |
|--------|-------:|----------:|
| 4000B  | 46 | 3 |
| 74     | 3  | 0 |
| 74HC   | 27 | 5 |
| 74HCT  | 23 | 1 |
| 74LS   | 132 | 19 |
| **total** | **231** | **28** |

Field coverage among filled rows: `propagation_delay` 227, `supply_current` 212,
`max_frequency` 84 (combinational parts legitimately have no fmax → null).

**Operational lesson — TI rate-limits concurrent downloads.** The first sweep ran
25 agents at once; TI served HTML error pages under the load, spiking the 74LS
failure rate. A low-concurrency (≤5–6 agents) rescue pass with retry+backoff and a
fuller fallback chain (TI gpn → TI symlink → existing URL → Nexperia → web search)
recovered most of them. **Keep harvest concurrency ≤ ~6 against ti.com.**

**Null tail (28) — left honest-NULL, candidates for a later pass.** Obsolete/
delisted parts (TI serves no PDF) or image-only PDFs the model couldn't read:

```
4000B: 4009 4049 4069
74HC:  137 4024 590 596 7014
74HCT: 237
74LS:  01 13 15? 22 155 246 258 295 322 352 353 366 368 385 386 395 398 596 76 77
```
(74LS15 was recovered in the rescue pass; the rest remain.) These are obsolete
enough that NULL is the correct "sparse but high quality" outcome; revisit only if a
specific design needs one.

**Interim datasheet handling (as decided):** PDFs were downloaded to a gitignored
scratch dir, **not** committed to the repo; parts keep their existing `datasheet`
URLs; the canonical manufacturer URL each agent used is banked in
`ic_logic_datasheet_params.json` (`datasheet_url`) for the later storage/link plan.

### Tail filled manually (2026-06-28)

The 28 null-tail parts were completed by hand via `ic_logic_with_good_urls.csv`
and ingested into the params file — **all 259 devices now have an entry**
(780/788 rows carry `propagation_delay`). The 8 rows still `NULL` on
`propagation_delay` are honest: analog muxes (74HC/74HCT 4051) and a VCO
(74LS629) have no conventional logic tpd, and 74HCT193 is a partial (only
`supply_current` found). To re-check later: 74LS629's `supply_current` reads
`55 µA` — likely a mA/µA slip for a VCO.

### Build fix

Generated SQL now depends on the table dir's `*.json` (Makefile rule), so editing
`ic_logic_datasheet_params.json` and running `make` regenerates — the JSON was
previously not a tracked prerequisite.
