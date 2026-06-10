# Terra Datasheet & Parameter Resolver — Design

**Date:** 2026-06-10
**Status:** Design — approved in brainstorming, pending spec review
**Scope note:** terra-wide (CERN imports **and** terra-native tables), not CERN-only.
**Depends on:** Phase 0 (part-type schema consolidation) — a blocking gate inside this spec.
**Reuses:** the existing `tools/cern_datasheets/` trio (`build_manifest.py`,
`rewrite_datasheets.py`, `verify.py`) and `assets/datasheets/cern/manifest.json`,
generalized from CERN-only to terra-wide.

## Motivation

The ported CERN parts carry a `datasheet` field that is 99% filled but holds a bare
PDF **filename** (`0402ESDA-MLP.pdf`), not a resolvable URL — the CERN source only ever
had an internal fileshare path (`\\cern.ch\dfs\…`) we don't possess. Clicking
"datasheet" in KiCad opens nothing. Separately, the import left real gaps:
`manufacturer_link` ~0%, `rohs_document_link` 0%, `package` 54%, and many type-specific
parametric columns blank.

Both problems share one fix: a maintainer-run lookup keyed by `mpn`+`manufacturer`
that returns a datasheet URL **and** structured parameters. We mirror the PDF to durable
storage we control, and harvest the parameters into the library — filling blanks only,
because the CERN data is curated.

Neither manufacturer nor distributor datasheet URLs are durable (site re-orgs, M&A
namespace death, obsolescence purges). The only stable reference is a copy **we**
archive and address by content. This design treats every upstream URL as a one-time
*fetch source*, never the stored reference.

## Scope

### Phase 0 (blocking gate) — part-type schema consolidation

The harvest writes into the **type-specific parametric columns**. Those columns must be
canonical *before* any harvest runs, and canonical **for the whole library**: the same
parametric tail serves both a CERN table and its terra-native counterpart.

- For each part type, define the type-specific column set as a **shared SQL schema
  fragment** under `db/schema/types/<type>.sql` (e.g. `diodes.sql`, `transistors.sql`,
  `op_amps.sql`, `connectors.sql`).
- Both the CERN table schema (`cern_diodes_0_schema.sql`) and the terra-native table
  schema (`diodes_0_schema.sql`) include that fragment, so the parametric tail is
  defined once.
- Part types with a CERN table but no terra-native counterpart yet (regulators,
  optocouplers, dc-dc, crystals, relays, fuses, sensors, transformers, power supplies,
  thermistors, batteries) still get a reviewed fragment — it becomes *the* terra schema
  for that type.
- **Nothing in Phases 1–4 runs until Phase 0 is committed.** The fragment column set is
  the contract that bounds what the harvest may populate.

Mechanism note: the build concatenates SQL per table. The schema fragment is included by
literal `cat`/`.read` composition in the table's `_0_schema.sql` build step (no SQL
`INCLUDE` exists in SQLite). The exact composition is a Phase-0 implementation detail;
the invariant is **one fragment, two includers, identical columns**.

### In

- Generalize `build_manifest` to scan **all** part tables (CERN + native) into one
  terra-wide datasheet manifest.
- `tools/cern_datasheets/harvest.py` — maintainer/online. Per part, query Nexar/Octopart
  by `mpn`+`manufacturer`; write the upstream datasheet URL into the manifest and the
  harvested parameters into a per-table **params sidecar**.
- `tools/cern_datasheets/mirror.py` — maintainer. Download each PDF from its upstream
  URL, content-address it (`<sha256>.pdf`), `gh release upload --clobber` into the
  rolling collection, record `download_url`+`sha256` in the manifest.
- `tools/cern_datasheets/prune.py` — maintainer. Delete release assets whose `sha256` is
  no longer referenced by the current manifest (anti-staleness).
- `tools/cern_datasheets/download.py` — consumer/online, once. Read the manifest, fetch
  each `download_url` into a **gitignored** local dir, verify `sha256`. Lazy, resumable.
- Generator integration — each table's `run_*` generator merges its params sidecar
  **fill-blanks-only**; CERN/native curated values win on conflict; conflicts logged.
- `rewrite_datasheets.py` — offline build step; repoint the DB `datasheet` field at the
  local file path for verified entries.
- A **GitHub Pages catalog index** — a small static site listing part types / parts with
  links to the Release-hosted datasheets (and, later, a browse front-end for the terra
  HTTP library). Generated from the DB + manifest; well under the Pages 1 GB limit
  because it holds HTML/JSON only, never PDFs.
- Make targets wiring the consumer-facing and offline steps.

### Out (deferred)

- Lazy single-datasheet fetch *by the terra HTTP server* at request time (the per-file
  manifest makes this possible later; not built here).
- PDF text/parameter extraction (we harvest Nexar's *structured* params only; no PDF
  parsing).
- Non-Nexar data providers (the harvest provider is a thin seam, but only the Nexar
  backend ships).
- Automated/CI re-mirroring (Phase 2 is local `gh`; CI is optional and unbuilt).

## Decisions (authoritative)

1. **Storage:** repo commits only text (manifest + sidecars). PDFs are **gitignored**
   locally and hosted on **GitHub Release assets** (free, unmetered bandwidth on public
   repos, outside git history, no LFS). Manifest stays host-agnostic (IA/Dropbox remain
   drop-in via a configurable base).
2. **Granularity:** **per-file** assets + per-file `sha256` in the manifest; lazy,
   resumable fetch.
3. **Content addressing:** asset name = `<sha256>.pdf` → automatic dedup (many MPNs share
   one datasheet), clean revisions (new content = new hash), trivial prune.
4. **One rolling collection:** a fixed release tag (sharded only if asset counts get
   unwieldy), updated in place with `--clobber`. No versioned snapshot accumulation.
5. **Data source:** Nexar/Octopart API, keyed by `mpn`+`manufacturer`, returns datasheet
   URL + structured params in one call.
6. **Reconciliation:** **fill-blanks-only.** Harvest never overwrites a non-empty curated
   value; disagreements go to a conflicts report for human review.
7. **Regenerable:** harvested data is a committed **sidecar** merged by the generator at
   generate-time. No live-DB edits; the DB rebuilds from `CERN.sqlite`/generators +
   sidecars.
8. **Offline build:** `make` never touches the network. Nexar lookups and `gh` uploads
   happen only in maintainer-run phases.
9. **Phase-0 gate:** schema consolidation precedes any harvest.

## Pipeline (5 phases; 2 online, 1 consumer-facing)

```
Phase 0  schema consolidation        maintainer, offline, blocking gate
Phase 1  harvest   (Nexar)           maintainer, ONLINE   -> manifest source_url + params sidecar
Phase 2  mirror    (gh release)      maintainer, ONLINE   -> manifest download_url + sha256
         prune     (gh release)      maintainer, ONLINE   -> delete unreferenced assets
Phase 3  download  (make datasheets) consumer,   ONLINE   -> gitignored local PDFs, sha256-verified
Phase 4  build     (make)            anyone,     OFFLINE  -> generators merge sidecar; rewrite_datasheets
```

The periodic refresh ("update the collection along with the native terra collection") is
the maintainer routine **harvest → mirror → prune**, run across all tables. Because it is
incremental (sha256 dedup skips unchanged content) and pruned (unreferenced assets
deleted), the collection stays single and current — never a graveyard of stale sets.

## Components

### 1. Manifest — `assets/datasheets/manifest.json` (terra-wide)

Keyed by datasheet **filename** (a datasheet is shared by many MPNs). Generalizes the
existing CERN manifest; the CERN-scoped path is migrated.

```json
{
  "0402ESDA-MLP.pdf": {
    "filename": "0402ESDA-MLP.pdf",
    "mpns": ["0402ESDA-MLP"],
    "manufacturer": "STMicroelectronics",
    "source_url": "https://www.st.com/resource/.../0402esda.pdf",   // upstream, fetch-only
    "sha256": "ab12…",                                              // of the archived PDF
    "download_url": "https://github.com/dfnr2/terra-eda-library/releases/download/terra-datasheets/ab12….pdf",
    "license_note": "",                                             // redistribution caveat if known
    "status": "mirrored",        // pending | sourced | mirrored | missing
    "verify": "ok"               // unchecked | ok | mismatch
  }
}
```

### 2. Params sidecar — `db/tables/<table>/<table>_harvest.json`

Keyed by `unique_id` (params are per-part). Lives next to its table so the generator
reads it locally and the diff is reviewable.

```json
{
  "STMicroelectronics-0402ESDA-MLP": {
    "package": "SOT-23",
    "manufacturer_link": "https://www.st.com/en/...",
    "<type-specific column>": "<value>",
    "_provenance": { "source": "nexar", "harvested_at": "2026-06-10", "match": "exact" }
  }
}
```

Only columns present in the part type's Phase-0 schema fragment are written. `_provenance`
records the match quality so a low-confidence match is auditable.

### 3. `harvest.py` (online)

For each part across all tables: query Nexar by `mpn`+`manufacturer`. On a high-confidence
match, write `source_url` to the manifest entry and the mapped params to the table's
sidecar. A Nexar→terra **field map** (per part type) translates Nexar attribute names to
the schema-fragment columns; unmapped attributes are dropped. Rate-limited, checkpointed
(resume mid-sweep), and incremental (skip parts already resolved unless `--refresh`).

### 4. `mirror.py` + `prune.py` (online, `gh`)

`mirror`: for each manifest entry with a `source_url` but no verified `download_url`,
download the PDF, compute `sha256`, `gh release upload --clobber <tag> <sha256>.pdf`,
write `download_url`+`sha256`+`status=mirrored`. Skip if the `sha256` asset already exists.
`prune`: list release assets, delete any whose `sha256` is absent from the current
manifest.

### 5. `download.py` / `make datasheets` (consumer, online, once)

Read the manifest, fetch each `download_url` into a gitignored
`assets/datasheets/files/` (or `${TERRA_EDA_LIB}`-served) dir, verify `sha256` (`verify=ok`).
Resumable; re-running fetches only missing/changed files.

### 6. Generator integration (offline)

Each `run_*` generator, after building its rows from the source, merges its
`<table>_harvest.json`: for each row, set any **blank** schema-fragment column from the
sidecar; never overwrite a non-blank curated value; append disagreements to a per-table
`*_conflicts.log`. Keeps `dump_priority`/regenerability intact.

### 7. `rewrite_datasheets.py` (offline)

Unchanged in spirit: for entries with `verify=ok`, `UPDATE <table> SET datasheet =
<local_path> WHERE datasheet = <filename>`. Now terra-wide.

### 8. GitHub Pages catalog index

A static-site generator (`tools/cern_datasheets/build_catalog.py` → `docs/` or a
`gh-pages` artifact) that renders, from `db/terra.db` + manifest, a browsable index of
part types → parts → datasheet links (Release URLs) and key parameters. HTML/JSON only;
no PDFs, so it stays far under the Pages 1 GB limit. Optional future front-end for the
terra HTTP library.

## Anti-staleness / lifecycle

- **Single source of truth = manifest.** An asset exists iff its `sha256` is referenced.
- **Dedup by content** collapses shared/identical datasheets to one asset.
- **`prune` is the GC**: removes superseded/orphaned assets every refresh.
- **In-place `--clobber`** on a fixed tag — no `-v1/-v2` accumulation.
- A `verify`/audit target re-checks that every manifest `download_url` resolves and every
  local file matches its `sha256`, and reports manifest entries with no asset (`missing`).

## Reconciliation

Fill-blanks-only, enforced in the generator merge (§6), not in the DB. Curated CERN/native
values always win; harvested values fill only `NULL`/empty columns. Every overwrite that
*would* have happened is logged to `*_conflicts.log` for human review — turning the
harvest into a passive data-quality probe as a side effect.

## Error handling & rate limits

- **Nexar:** OAuth token refresh; exponential backoff on 429; checkpoint after each part
  so a quota stop resumes cleanly; `no-match` and `low-confidence` recorded (not guessed).
- **mirror:** a `source_url` that 404s → `status=missing`, no asset; surfaced by audit.
- **download:** `sha256` mismatch → re-fetch once, then `verify=mismatch` and skip (never
  installs an unverified PDF).
- **Offline guarantee:** `make` targets that build the DB depend only on committed files;
  the online phases are separate targets that are never prerequisites of `all`.

## Testing

- Phase 0: a test that each `<type>.sql` fragment is included by both the CERN and native
  schemas, and that the resulting tables expose an identical type-column set.
- `harvest`: fixture Nexar responses → asserts field-map output and that only
  schema-fragment columns are written; low-confidence handling.
- merge: fixture sidecar → asserts blanks filled, non-blanks preserved, conflicts logged.
- `mirror`/`prune`: fake release-asset listing → asserts content-addressed upload, clobber,
  and that exactly the unreferenced hashes are pruned.
- `download`: sha256 verify pass/mismatch paths.
- manifest round-trip / schema validation; catalog builds from a fixture DB.

## Open questions

- **License flag policy:** what populates `license_note`, and whether any manufacturer's
  terms require excluding its PDFs from the public mirror (handled per-entry, default
  empty). To settle during implementation.
- **Sharding threshold:** single `terra-datasheets` tag vs per-type tags — decide once the
  real asset count is known after the first full harvest.
- **Catalog hosting branch:** `/docs` on `main` vs a `gh-pages` branch — Phase-implementation
  detail.
