# Terra Datasheet & Parameter Resolver — Design

**Date:** 2026-06-10
**Status:** Design — approved in brainstorming, pending spec review
**Scope note:** terra-wide (CERN imports **and** terra-native tables), not CERN-only.
**Depends on:** Phase 0 (part-type schema consolidation) — a blocking gate inside this spec.
**Reuses/generalizes:** the existing `tools/cern_datasheets/` (`build_manifest.py`,
`verify.py`) and `assets/datasheets/cern/manifest.json`, broadened from CERN-only to
terra-wide. `rewrite_datasheets.py`'s filename-match is **superseded** by the row-keyed
`apply_harvest.py` (see §6), because native rows store full URLs, not filenames.

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
- `tools/cern_datasheets/apply_harvest.py` — offline post-load build step, keyed by
  `unique_id` (like `retier_static.py`/`dedup_cross_table.py`), applied to the built DB so
  it works for **static** native tables *and* generator-backed tables alike. Fills blank
  allowlist columns **fill-blanks-only** (curated values win; conflicts logged) and
  repoints `datasheet` to the local file **only when present-and-verified in the local
  cache**. Supersedes the CERN-only filename-match in `rewrite_datasheets.py`.
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
7. **Regenerable:** harvested data is a committed **sidecar** applied by the offline
   post-load step `apply_harvest.py` (keyed by `unique_id`), not by per-table generators —
   so it covers the many static native tables too. No manual live-DB edits; the DB rebuilds
   deterministically from `CERN.sqlite`/generators/static SQL + committed sidecars.
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
Phase 4  build     (make)            anyone,     OFFLINE  -> apply_harvest (by unique_id): fill blanks + datasheet rewrite
```

The periodic refresh ("update the collection along with the native terra collection") is
the maintainer routine **harvest → mirror → prune**, run across all tables. Because it is
incremental (sha256 dedup skips unchanged content) and pruned (unreferenced assets
deleted), the collection stays single and current — never a graveyard of stale sets.

## Components

Two committed artifacts, with **distinct keys**, and one **gitignored** local-cache index:
the collection manifest is content-addressed (the asset set), and the per-table sidecar is
row-addressed (what each part resolved to). They are deliberately separate because a single
datasheet is shared by many parts, and because native rows do not store filenames.

### 1. Collection manifest — `assets/datasheets/manifest.json` (terra-wide)

Keyed by **`sha256`** of the archived PDF (content-addressed → automatic dedup, clean
revisions, trivial prune). `filenames`/`mpns` are descriptive aliases, not the key.
`archive_ok` is **host-side** state (the asset exists on the Release and its hash matches),
set by the maintainer in Phase 2 — it says nothing about any consumer's local cache.

```json
{
  "ab12…": {                              // sha256 of the PDF = the key
    "filenames": ["0402ESDA-MLP.pdf"],    // upstream name(s) this content was known by
    "mpns": ["0402ESDA-MLP"],
    "manufacturer": "STMicroelectronics",
    "source_url": "https://www.st.com/resource/.../0402esda.pdf",   // upstream, fetch-only
    "download_url": "https://github.com/dfnr2/terra-eda-library/releases/download/terra-datasheets/ab12….pdf",
    "size": 184213,
    "license_note": "",                   // redistribution caveat if known
    "archive_ok": true                    // host asset present + hash verified (maintainer-set)
  }
}
```

### 2. Per-table sidecar — `db/tables/<table>/<table>_harvest.json`

Keyed by **`unique_id`** (per-part). Carries the harvested params *and* the resolved
datasheet reference, so every later step is row-addressed (fixes the native-rows-store-URLs
and filename-collision problems). `original_datasheet` records the pre-existing value
(a CERN filename **or** a native http URL) for audit and safe rewrite-by-`unique_id`.

```json
{
  "STMicroelectronics-0402ESDA-MLP": {
    "datasheet_sha256": "ab12…",                       // -> collection manifest
    "original_datasheet": "0402ESDA-MLP.pdf",          // pre-existing row value (filename or URL)
    "package": "SOT-23",
    "manufacturer_link": "https://www.st.com/en/...",
    "rohs_document_link": "https://www.st.com/...rohs.pdf",
    "<type-fragment column>": "<value>",
    "_provenance": { "source": "nexar", "harvested_at": "2026-06-10", "match": "exact" }
  }
}
```

**Writable-column allowlist (resolves the contradiction).** The harvest may write exactly:
- **`CORE_HARVEST_COLUMNS`** — a fixed set of core columns this design exists to repair:
  `manufacturer_link`, `rohs_document_link`, `package`, plus the `datasheet` reference.
- **the part type's Phase-0 type-fragment columns** — the parametric tail.

Any Nexar attribute mapping outside that union is dropped. (Curated columns like
`description`/`value`/`mpn` are never harvest targets.)

### 3. `harvest.py` (online)

For each part across all tables: query Nexar by `mpn`+`manufacturer`. On a high-confidence
match, (a) ensure a collection-manifest entry keyed by the datasheet's eventual `sha256`
carrying its `source_url`; (b) write the row's `datasheet_sha256`, `original_datasheet`,
and the allowlisted params to that table's sidecar. A per-type Nexar→terra **field map**
translates attribute names to allowlist columns; unmapped attributes are dropped.
Rate-limited, checkpointed (resume mid-sweep), incremental (skip already-resolved rows
unless `--refresh`), and records `no-match`/`low-confidence` rather than guessing.

(Note: `source_url`'s `sha256` isn't known until the PDF is fetched in Phase 2; harvest
keys the manifest entry provisionally by `source_url` and Phase 2 re-keys to the real
`sha256` once computed.)

### 4. `mirror.py` + `prune.py` (online, `gh`)

`mirror`: for each manifest entry not yet `archive_ok`, download from `source_url`, compute
`sha256`, re-key the entry to that hash, `gh release upload --clobber <tag> <sha256>.pdf`,
set `download_url`+`size`+`archive_ok=true`. Skip upload if a `<sha256>.pdf` asset already
exists. `prune`: list release assets, delete any whose `sha256` is absent from the current
manifest. A `source_url` that 404s → entry left without `download_url` (surfaced by audit).

### 5. `download.py` / `make datasheets` (consumer, online, once) + local-cache index

Read the manifest, fetch each `download_url` into a **gitignored** `assets/datasheets/files/`
(served via `${TERRA_EDA_LIB}`), verify each against its `sha256`. Writes a **gitignored**
`assets/datasheets/.cache-state.json` recording which `sha256`s are present-and-verified
**locally**. This local-cache state is what the build trusts — never the committed
`archive_ok`. Resumable; re-running fetches only missing/changed files. On a `sha256`
mismatch: re-fetch once, then mark that hash unavailable and skip (never install an
unverified PDF).

### 6. `apply_harvest.py` (offline post-load build step) — replaces generator-merge + filename rewrite

Runs in `make project-db` as a post-load pass over the built DB, **keyed by `unique_id`**,
exactly like the existing `retier_static.py`/`dedup_cross_table.py` steps — so it works
uniformly for **both** generator-backed tables (`resistors_smt`, CERN imports) **and** the
many **static** native tables (`diodes`, `bjt`, `ic_*`, `leds`, …) that have no generator
to hook. For each sidecar row, by `unique_id`:
- **Params:** set any **blank** allowlist column from the sidecar; never overwrite a
  non-blank curated value; append disagreements to `<table>_conflicts.log`.
- **Datasheet:** if `datasheet_sha256` is present-and-verified in the **local-cache index**,
  `UPDATE <table> SET datasheet = <local_path> WHERE unique_id = ?`. Otherwise leave the
  row's existing `datasheet` (CERN filename or native URL) untouched — so a consumer who
  skipped Phase 3 never gets a DB pointing at absent local PDFs.

Reading a committed sidecar in a deterministic build step keeps the DB **regenerable** (no
manual live-DB edits); this supersedes the old `rewrite_datasheets.py` filename-match,
which only worked for CERN rows.

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
- An **audit** target re-checks two independent things: (a) *archive* — every manifest
  `download_url` resolves and the host asset's hash matches its key (`archive_ok`);
  (b) *local cache* — every present file in `assets/datasheets/files/` matches its `sha256`.
  Reports manifest entries with no resolvable asset.

## Reconciliation

Fill-blanks-only, enforced in `apply_harvest.py` (§6) over the built DB. Curated
CERN/native values always win; harvested values fill only `NULL`/empty allowlist columns.
Every overwrite that *would* have happened is logged to `<table>_conflicts.log` for human
review — turning the harvest into a passive data-quality probe as a side effect.

## Error handling & rate limits

- **Nexar:** OAuth token refresh; exponential backoff on 429; checkpoint after each part
  so a quota stop resumes cleanly; `no-match` and `low-confidence` recorded (not guessed).
- **mirror:** a `source_url` that 404s → entry left without `download_url`/`archive_ok`;
  surfaced by audit.
- **download:** `sha256` mismatch → re-fetch once, then mark that hash absent in the
  local-cache index and skip (never installs an unverified PDF). `apply_harvest` then leaves
  those rows' original `datasheet` untouched.
- **Offline guarantee:** `make` targets that build the DB depend only on committed files;
  the online phases are separate targets that are never prerequisites of `all`.

## Testing

- Phase 0: a test that each `<type>.sql` fragment is included by both the CERN and native
  schemas, and that the resulting tables expose an identical type-column set.
- `harvest`: fixture Nexar responses → asserts field-map output respects the
  `CORE_HARVEST_COLUMNS` + type-fragment allowlist (and drops everything else);
  low-confidence handling; sidecar carries `datasheet_sha256` + `original_datasheet`.
- `apply_harvest`: fixture sidecar + built DB → asserts blanks filled, non-blanks
  preserved, conflicts logged, and rewrite-by-`unique_id` hits a **static** native table
  (URL-valued `datasheet`) as well as a generator/CERN table.
- local-cache gating: `apply_harvest` rewrites datasheet only when the hash is in the
  local-cache index; with an empty cache, original `datasheet` values are left intact.
- `mirror`/`prune`: fake release-asset listing → asserts content-addressed upload, clobber,
  and that exactly the unreferenced hashes are pruned.
- `download`: sha256 verify pass/mismatch paths update the local-cache index correctly.
- manifest round-trip / schema validation; catalog builds from a fixture DB.

## Open questions

- **License flag policy:** what populates `license_note`, and whether any manufacturer's
  terms require excluding its PDFs from the public mirror (handled per-entry, default
  empty). To settle during implementation.
- **Sharding threshold:** single `terra-datasheets` tag vs per-type tags — decide once the
  real asset count is known after the first full harvest.
- **Catalog hosting branch:** `/docs` on `main` vs a `gh-pages` branch — Phase-implementation
  detail.
