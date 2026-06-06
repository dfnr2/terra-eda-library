# CERN → Terra Importer — Design (Pilot: `cern_diodes`)

**Date:** 2026-06-06
**Status:** Draft for review
**Scope of this doc:** The overall importer architecture, plus a fully-specified pilot
(`cern_diodes`) that exercises every subsystem end-to-end. The remaining 54 CERN tables
follow the same pattern once the pilot is validated.

---

## 1. Goal & motivation

CERN's KiCad library (`../cern-kicad-libs/CERN.sqlite`, ~23.9k parts) is a curated,
real-manufacturer catalog covering categories terra is thin on (connectors, ICs,
diodes, transistors, etc.). We want those real parts in terra, mirroring CERN's table
structure 1:1 for now and folding/consolidating later.

CERN loads slowly in KiCad for the same reason terra does (eager loading of large
DB-libs); the long-term fix is terra's planned HTTP/lazy-load library. **Importing into
terra first, then doing the HTTP-lib work, is the agreed sequence** — the import is
independent of, and unblocked by, the lazy-load effort.

Because terra is fully regenerable (SQL is the source of truth; generated tables are
`*_generated_*.sql` at `dump_priority=0`; `make` rebuilds everything), mapping decisions
are cheap to revise: edit schema + generator, re-run. No live-DB migration. This lets us
land a first mapping and iterate.

---

## 2. Locked decisions

| # | Decision |
|---|---|
| Scope | Import **all real parts** across **all 55 CERN tables**. Pilot first: `cern_diodes`. |
| Structure | **Mirror CERN 1:1**: one terra table+dir per CERN table, `cern_`-prefixed (e.g. `cern_diodes`, `cern_samtec`). Consolidation deferred. |
| Exclude rule (refined) | Drop only true non-parts: (a) GENERIC/Undefined/blank-manufacturer rows **in passive tables only** (resistors/caps); (b) a small **denylist** of doc/graphical entries everywhere (`%Read Me%`, `%Drill-Drawing%`, `CERN_OHL%`, `Empty`, copyright markers). Keep real mechanical/generic parts (bonding pads, epoxy, PCB modules). |
| Symbols/footprints | **Copy CERN libs into terra** and reference as-is; no remapping now. |
| Core field adoption | Add **`pin_count`** and **`component_height`** to the terra core for `cern_` tables. **Not** adopting second-source MPN or a `family` column. |
| Family taxonomy | **Deferred.** It belongs to the existing `tags` subsystem, not a new column. Ingest CERN `Family`/type as tags later if the HTTP-lib work needs the granularity. |
| `unique_id` / reconciliation | **Reconcile-and-merge, not blind insert.** Reuse the existing terra part's `unique_id` when an exact equivalent already exists; else mint `"<manufacturer>-<mpn>"`. |
| Matching | **Exact, never statistical** — for both terra equivalence and datasheet↔part matching. |
| Datasheets | **Decoupled subsystem.** Build a required-datasheets manifest; fetch by exact MPN; **parse the PDF to confirm the MPN and the parameters CERN already records**; unparseable/unconfirmed → human review. Import is never blocked on datasheets. |
| Test/audit | Per-table automated mapping check (exact) **plus** a human audit pass against datasheets. |

---

## 3. Architecture — five subsystems

1. **Discovery & mapping** (this doc) — per-table field map, adopted core fields, the
   equivalence-match keys.
2. **Library copy + registration** — CERN `SchLib/*.kicad_sym` and `PcbLib/*.pretty`
   copied into terra and registered in the lib-tables.
3. **Import + reconciliation** — `run_*.py` reads `CERN.sqlite`, applies the mapping and
   exclude rule, resolves `unique_id` against existing terra parts, emits generated SQL.
4. **Datasheet acquisition + parse-verification** — standalone, resumable, manifest-driven.
5. **Test + audit** — automated exact checks + human audit.

### Shared helper: `tools/cern_source.py`
Single module that locates `CERN.sqlite` (default `../cern-kicad-libs/CERN.sqlite`,
overridable via `CERN_SQLITE` env var) and exposes typed row access. Every
`run_*_cern_import.py` imports from it, so the source path lives in one place.

---

## 4. Per-table layout (mirrors terra convention)

For each CERN table, create `db/tables/cern_<sanitized>/`:

```
cern_diodes_0_schema.sql                       # core + type-specific tail (tracked)
run_100_cern_import.py                          # CERN.sqlite -> generated SQL (tracked)
cern_diodes_generated_100_cern_import.sql       # generated, dump_priority=0 (gitignored)
test_cern_diodes.py                             # automated exact mapping check (tracked)
AUDIT.md                                        # human audit checklist + sign-off (tracked)
```

Table-name sanitization: lowercase, non-alphanumerics → `_`, collapse repeats.
`Diodes`→`cern_diodes`; `Analog & Interface`→`cern_analog_interface`;
`DC-DC Converters`→`cern_dc_dc_converters`; `SAMTEC`→`cern_samtec`.

The Makefile already auto-discovers `db/tables/*/`, builds `db/cern_<t>.db`, the master
`db/terra.db`, the `cern_<t>_v` filtered views, and the `.kicad_dbl` entries — **no
Makefile edits required**. `.gitignore` already covers `db/tables/*/*_generated_*.sql`
and `*.db`.

---

## 5. Pilot: `cern_diodes`

### 5.1 Source profile (CERN `Diodes`, 962 rows)

- 962/962 have `Manufacturer Part Number`, `Manufacturer`, `Datasheet` ref, `Pin Count`.
- `Voltage` 922/962, `Power` 905/962, `Case` 824/962, `ComponentHeight` 961/962.
- `Status` 52/962 (`Obsolete`, `Not Recommended`, `Sourcing Difficulty`).
- `LibSymbol`: 149 distinct, all in the `Diodes` symbol lib.
- `LibFootprint` libs: `ICs And Semiconductors {SMD,THD,BONDING}`.
- Exclude rule: diodes is **not** a passive table → no GENERIC filter; apply only the
  doc/graphical denylist (expected to drop 0 here). All 962 import.

### 5.2 Schema — `cern_diodes_0_schema.sql`

**Canonical core** (the current go-forward core fields as in
`resistors_smt_0_schema.sql` — *not* the legacy `diodes` schema), **plus two adopted
fields**, **plus a diode-specific tail**. Note: `tier` defaults to `5` per
`TIER_TAG_SPEC.org` (the existing `resistors_smt` schema currently has `DEFAULT 0` — a
pre-existing repo inconsistency; we follow the spec).

```sql
CREATE TABLE cern_diodes (
    -- === Canonical core (same as resistors_smt) ===
    unique_id TEXT PRIMARY KEY,
    part_locator TEXT,
    mpn TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    variant TEXT,
    package TEXT,
    value TEXT,
    description TEXT,
    datasheet TEXT,
    manufacturer_link TEXT,
    kicad_symbol TEXT,
    kicad_footprint TEXT,
    altium_symbol TEXT,
    altium_footprint TEXT,
    lifecycle_status TEXT DEFAULT 'Active',
    rohs TEXT DEFAULT 'no',
    rohs_document_link TEXT,
    allow_substitution TEXT DEFAULT 'no',
    tracking TEXT DEFAULT 'no',
    standards_version TEXT DEFAULT 'v1.0',
    bom_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    source TEXT DEFAULT 'static',
    dump_priority INTEGER DEFAULT 1,
    tier INTEGER DEFAULT 5,
    tags TEXT DEFAULT '',
    sim_model_type TEXT,
    sim_device TEXT,
    sim_pins TEXT,
    sim_model_file TEXT,
    sim_params TEXT,

    -- === Adopted-from-CERN core additions (cern_ tables) ===
    pin_count TEXT,
    component_height TEXT,

    -- === Diode-specific tail ===
    diode_type TEXT,        -- parsed from CERN LibSymbol (TVS/Schottky/Zener/…)
    voltage_rating TEXT,    -- CERN Voltage
    power_rating TEXT       -- CERN Power
);
```

> Note: `pin_count`/`component_height` are added to `cern_` tables now. Rolling them into
> *all* terra tables is a separate, trivial, regenerable change — out of scope for the pilot.

### 5.3 Field mapping (CERN `Diodes` → `cern_diodes`)

| terra column | CERN source | Transform / default |
|---|---|---|
| `unique_id` | `Manufacturer` + `Manufacturer Part Number` | `"<manufacturer>-<mpn>"`; on intra-CERN MPN collision, disambiguate via `Part Number Nocolon` (§5.4) |
| `mpn` | `Manufacturer Part Number` | trim (real MPN; may repeat across variants) |
| `manufacturer` | `Manufacturer` | trim |
| `part_locator` | `Part Number Nocolon` | unique CERN id; carries variant suffix (`_h`/`_v`) |
| `package` | `Case` | fallback `''` |
| `value` | `Part Description` | CERN has no clean "value"; use description text |
| `description` | `Part Description` | trim |
| `datasheet` | `Datasheet` filename | placeholder hint until datasheet subsystem rewrites to local asset path (§5.6) |
| `manufacturer_link` | `ComponentLink1URL` if http | else `''` (CERN links are mostly internal shares) |
| `kicad_symbol` | `LibSymbol` | rewrite lib prefix → copied `cern_`-namespaced lib (§5.5) |
| `kicad_footprint` | `LibFootprint` | rewrite lib prefix → copied `cern_`-namespaced lib (§5.5) |
| `lifecycle_status` | `Status` | map: ``''→Active``, `Obsolete→Obsolete`, `Not Recommended→NRND`, `Sourcing Difficulty→NRND` |
| `pin_count` | `Pin Count` | trim |
| `component_height` | `ComponentHeight` | trim |
| `diode_type` | `LibSymbol` (after `:`) | e.g. `Diode TVS Bi-Directional` → `TVS Bidirectional` |
| `voltage_rating` | `Voltage` | trim |
| `power_rating` | `Power` | trim |
| `rohs` | — | default `'no'` (CERN has no RoHS field) |
| `source` | — | `'cern_import'` |
| `dump_priority` | — | `0` (generated) |
| `tier` | — | `5` (default; CERN parts are catalog-tier) |
| `tags` | constant | `'diode'` (+ functional tags later) |
| `altium_symbol`/`altium_footprint` | — | `''` (KiCad-first; Altium later) |

Unmapped CERN columns (`SCEM`, `Author`, `CreateDate`, `Sense*`, `Mounted`, `Socket`,
`SMD`, `PressFit`, `Bonding`, `Database Name/Table`, `Component Kind/Type`) are **dropped**
for the pilot — recorded here so the decision is explicit and revisitable.

### 5.4 `unique_id` and part identity

terra's standard `unique_id` convention is `"<manufacturer>-<mpn>"` (e.g.
`OnSemi-MBR0530T1G`). The pilot uses that directly and does **not** reconcile against
existing terra parts — the `diodes` category is effectively new, so there is nothing to
merge. Cross-catalog dedup/merge by MPN is deferred to the later fold-in/consolidation
phase; the shared `tools/cern_reconcile.py` helper (built and tested) is reserved for the
passive tables where pre-existing terra parts genuinely overlap.

**Intra-CERN MPN collisions (discovered during implementation).** CERN `Diodes` has 962
rows but only **887 distinct** `(manufacturer, Manufacturer Part Number)` pairs: **60
groups** where one MPN appears as several distinct library entries (footprint/mounting/reel
variants such as `_h`/`_v`). `Manufacturer Part Number` is therefore **not** a unique key;
`Part Number Nocolon` is (962/962). So:

- `unique_id` = `"<manufacturer>-<mpn>"` for the 887 unambiguous parts.
- On collision, disambiguate with the unique CERN id:
  `"<manufacturer>-<Part Number Nocolon>"`. A safety gate raises if any duplicate survives,
  so the build can never silently drop the 75 variant rows.
- `mpn` column always holds the real `Manufacturer Part Number` (variants included).
- `part_locator` = `Part Number Nocolon` — the unique CERN identity carrying the variant
  suffix. (`part_locator` will need reconciliation for tables that overlap existing terra
  parts; diodes is new, so not a concern here.)

### 5.5 Symbol & footprint libraries

- Copy CERN `SchLib/Diodes.kicad_sym` → `assets/symbols/cern/Diodes.kicad_sym`.
- Copy CERN `PcbLib/ICs And Semiconductors {SMD,THD,BONDING}.pretty` →
  `assets/footprints/cern/…`.
- Register in `kicad_config_templates/{sym,fp}-lib-table` under `cern_`-prefixed nicknames
  using the `${TERRA_EDA_LIB}` scheme.
- Rewrite the lib **nickname** portion of `kicad_symbol`/`kicad_footprint` to the
  registered `cern_` nickname; keep the item name unchanged. (Full set of referenced libs
  is small: 1 symbol lib + 3 footprint libs for diodes.)

### 5.6 Datasheet subsystem (decoupled)

CERN stores **no PDFs and no web URLs** — only a filename hint (`1.5KE.pdf`) and an
inaccessible internal share path. So acquisition = resolve from `(mpn, manufacturer,
description)` to a real PDF on the web, then verify.

- **Manifest:** `assets/datasheets/cern/manifest.json`, keyed by CERN datasheet filename
  (dedups parts sharing a sheet). Each entry: `{filename, mpns[], manufacturer,
  status, source_url, local_path, verify}` where `status ∈ {pending, fetched,
  not_found, ambiguous}` and `verify ∈ {ok, mpn_mismatch, unparseable, unchecked}`.
- **Fetcher** (`tools/cern_datasheets/fetch.py`): resumable; skips already-resolved
  entries; rate-limited web search + download into `assets/datasheets/cern/`.
- **Parse-verification:** open each fetched PDF, extract text, and **require an exact
  match on the MPN**; additionally confirm the parameters CERN records (e.g. `Voltage`,
  `Power`) appear. Pass → `verify=ok`. Fail/unparseable → flag for **human review**
  (no statistical acceptance).
- **Rewrite step:** a `make`-able task updates `datasheet` for verified parts to the local
  asset path; unverified parts keep the hint and are listed in `AUDIT.md`.
- **PDF tracking:** add `*.pdf filter=lfs diff=lfs merge=lfs -text` to `.gitattributes`
  (Git LFS) — 14k sheets across the full import would be hundreds of MB.

### 5.7 Test + audit

- **`test_cern_diodes.py` (automated, exact):** rebuilds `db/cern_diodes.db` and asserts,
  per row, that each mapped column equals the deterministic transform of its CERN source
  (round-trip of the mapping). Asserts row count = 962 − denylisted. Asserts every
  `kicad_symbol`/`kicad_footprint` nickname resolves to a registered, copied lib. Asserts
  no duplicate `unique_id` and that reconciled ids point at real existing terra parts.
- **Human audit (`AUDIT.md`):** a sampled set of parts checked against their (verified)
  datasheet — confirm value/voltage/power/package match the PDF. Records sign-off and any
  parts kicked to review by the datasheet verifier.

---

## 6. Build / run flow (pilot)

```
1. tools/cern_source.py                      # add shared source helper
2. copy + register CERN diode sym/footprint libs   (§5.5)
3. db/tables/cern_diodes/cern_diodes_0_schema.sql   (§5.2)
4. db/tables/cern_diodes/run_100_cern_import.py     (§5.3–5.4)
5. make cern_diodes-build                     # -> db/cern_diodes.db
6. pytest db/tables/cern_diodes/test_cern_diodes.py # §5.7 automated
7. make                                       # master db + views + .kicad_dbl
8. (decoupled) tools/cern_datasheets/fetch.py # manifest -> PDFs -> verify
9. make <rewrite-datasheets>                  # local asset paths for verified parts
10. human audit -> AUDIT.md sign-off
```

---

## 7. Generalization (after pilot)

The pilot fixes the reusable shape: shared source helper, the core+tail schema pattern,
the mapping/reconciliation/lib-rewrite logic, the datasheet manifest/verify, and the
test+audit templates. Remaining tables differ only in: type-specific tail columns, the
exclude rule (GENERIC filter on passive tables), and per-table field nuances. Each is a
new `db/tables/cern_<t>/` directory following this template.

---

## 8. Open items / deferred

- Consolidation of mirrored tables (e.g. per-manufacturer connectors → one `connectors`).
- Rolling `pin_count`/`component_height` into **all** terra tables.
- Second-source MPN, CERN `Family`→tags ingestion.
- Altium symbol/footprint columns.
- Secondary footprint variants (`…_bot`).
- Bulk datasheet source better than per-part web search, if one exists.
```
