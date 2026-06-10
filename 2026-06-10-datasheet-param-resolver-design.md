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
- `tools/cern_datasheets/apply_harvest.py` — **deterministic** post-load step in the
  master `db/terra.db` recipe, keyed by `unique_id` (like
  `retier_static.py`/`dedup_cross_table.py`), so it covers **static** native tables *and*
  generator-backed tables alike. From committed inputs only (manifest + sidecars): fills
  blank allowlist columns **fill-blanks-only** (curated values win; conflicts logged) and
  sets `datasheet` to the manifest `download_url` (our durable Release copy). Supersedes
  the CERN-only filename-match in `rewrite_datasheets.py`.
- `tools/cern_datasheets/download.py` (`make datasheets`) + `localize_datasheets.py`
  (`make localize-datasheets`) — **optional, per-user** offline-convenience layer. Download
  fetches PDFs into a **gitignored** local dir and records a local-cache index; localize
  repoints `datasheet` from the Release URL to the local file for cached hashes. Neither is
  a prerequisite of `make all`, so gitignored local state never forks the canonical DB.
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
6. **Reconciliation:** **fill-blanks-only for params** — harvest never overwrites a
   non-empty curated param value; disagreements go to a conflicts report. **`datasheet` is
   the sole exception:** it is always repointed to the durable Release `download_url` when
   one exists (the goal is to replace rotting/internal links), never blanked otherwise.
7. **Regenerable:** harvested data is a committed **sidecar** applied by the offline
   post-load step `apply_harvest.py` (keyed by `unique_id`), not by per-table generators —
   so it covers the many static native tables too. No manual live-DB edits; the DB rebuilds
   deterministically from `CERN.sqlite`/generators/static SQL + committed sidecars.
8. **Offline + deterministic build:** `make` never touches the network, and `make all`
   builds an identical `db/terra.db` for everyone from committed inputs only (manifest +
   sidecars) — `datasheet` points at the Release `download_url`. The gitignored local-cache
   and the local-only `localize-datasheets` step are never prerequisites of `all`, so they
   cannot fork the canonical DB. Nexar lookups and `gh` uploads happen only in
   maintainer-run phases.
9. **Phase-0 gate:** schema consolidation precedes any harvest.

## Pipeline (5 phases; 2 online, 1 consumer-facing)

```
Phase 0  schema consolidation        maintainer, offline, blocking gate
Phase 1  harvest   (Nexar)           maintainer, ONLINE   -> manifest source_urls + params sidecar (datasheet_source_url)
Phase 2  mirror    (gh release)      maintainer, ONLINE   -> manifest re-keyed to sha256 + download_url
         prune     (gh release)      maintainer, ONLINE   -> delete unreferenced assets
Phase 4  build     (make)            anyone,     OFFLINE  -> apply_harvest: fill blank params + datasheet = download_url
                                                              (DETERMINISTIC: committed manifest + sidecars only)
-- optional, per-user, NOT part of the canonical build: --
Phase 3  download  (make datasheets) consumer,   ONLINE   -> gitignored local PDFs, sha256-verified -> local-cache index
Phase 5  localize  (make localize-datasheets) consumer, OFFLINE -> repoint datasheet to local file for cached hashes
```

Phases 0/1/2/4 produce a **deterministic** `db/terra.db` from committed inputs only —
every consumer who runs plain `make` gets the identical DB, with `datasheet` pointing at
the stable Release `download_url`. Phases 3/5 are an **optional offline-convenience layer**:
a user who wants datasheets served from local files runs `make datasheets` then
`make localize-datasheets`. Neither is a prerequisite of `make all`, so the gitignored
local-cache state can never fork the canonical build (resolves the determinism hazard).
`db/terra.db` depends on the committed manifest + sidecars, so harvested-data edits do
trigger a rebuild; the local cache state, deliberately, does not.

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
    "source_urls": ["https://www.st.com/resource/.../0402esda.pdf"], // upstream(s), fetch-only; the sidecar join key
    "download_url": "https://github.com/dfnr2/terra-eda-library/releases/download/terra-datasheets/ab12….pdf",
    "size": 184213,
    "license_note": "",                   // redistribution caveat if known
    "archive_ok": true                    // host asset present + hash verified (maintainer-set)
  }
}
```

`source_urls` is a list because content-dedup can merge several upstream URLs onto one
`sha256`. `apply_harvest` builds a reverse index `source_url → entry` from it, which is how
a sidecar's `datasheet_source_url` (known at harvest, before any hash) resolves to the
final `download_url` — **no sidecar ever needs patching when Phase 2 re-keys to `sha256`.**

### 2. Per-table sidecar — `db/tables/<table>/<table>_harvest.json`

Keyed by **`unique_id`** (per-part). Carries the harvested params *and* the resolved
datasheet reference, so every later step is row-addressed (fixes the native-rows-store-URLs
and filename-collision problems). `original_datasheet` records the pre-existing value
(a CERN filename **or** a native http URL) for audit and safe rewrite-by-`unique_id`.

```json
{
  "STMicroelectronics-0402ESDA-MLP": {
    "datasheet_source_url": "https://www.st.com/resource/.../0402esda.pdf",  // join key into manifest; known at harvest
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
match, (a) ensure a collection-manifest entry carrying this datasheet's `source_url` in its
`source_urls` list (provisionally keyed by `source_url` until Phase 2 computes the hash);
(b) write the row's `datasheet_source_url`, `original_datasheet`, and the allowlisted params
to that table's sidecar. The sidecar's join key is the **`source_url`** — known now, stable
across the later re-key — so harvest output is final and never rewritten by Phase 2. A
per-type Nexar→terra **field map** translates attribute names to allowlist columns; unmapped
attributes are dropped. Rate-limited, checkpointed (resume mid-sweep), incremental (skip
already-resolved rows unless `--refresh`), records `no-match`/`low-confidence` not guesses.

### 4. `mirror.py` + `prune.py` (online, `gh`)

`mirror`: for each manifest entry not yet `archive_ok`, download from a `source_url`,
compute `sha256`, **re-key the entry from its provisional `source_url` key to `sha256`**
(keeping the full `source_urls` list intact so the sidecar join still resolves),
`gh release upload --clobber <tag> <sha256>.pdf`, set `download_url`+`size`+`archive_ok=true`.
Skip upload if a `<sha256>.pdf` asset already exists. **No sidecar is touched.** `prune`:
list release assets, delete any whose `sha256` is absent from the current manifest. A
`source_url` that 404s → entry left without `download_url` (surfaced by audit).

### 5. `download.py` / `make datasheets` (consumer, **optional**, online, once) + local-cache index

Read the manifest, fetch each `download_url` into a **gitignored** `assets/datasheets/files/`
(served via `${TERRA_EDA_LIB}`), verify each against its `sha256`. Writes a **gitignored**
`assets/datasheets/.cache-state.json` recording which `sha256`s are present-and-verified
locally. **Not a prerequisite of `make all`** — purely to enable the optional local
localization in §6b. Resumable; on a `sha256` mismatch, re-fetch once, then mark the hash
unavailable and skip (never installs an unverified PDF).

### 6. `apply_harvest.py` (deterministic, in the `db/terra.db` recipe) — replaces generator-merge + filename rewrite

Runs in the **master `db/terra.db` build recipe** (the step `make project-db` triggers),
as a post-load pass **keyed by `unique_id`**, exactly like the adjacent
`retier_static.py`/`dedup_cross_table.py` steps — operating on the master only (per-table
`db/<table>.db` are build intermediates and are not harvested). Because it works on the
built DB rather than per-table generators, it covers **both** generator-backed tables
(`resistors_smt`, CERN imports) **and** the many **static** native tables (`diodes`, `bjt`,
`ic_*`, `leds`, …) uniformly. Inputs are **committed only** (manifest + sidecars), so the
result is deterministic — every plain `make` produces the same `db/terra.db`. For each
sidecar row, by `unique_id`:
- **Params (fill-blanks-only):** set any **blank** allowlist column from the sidecar;
  never overwrite a non-blank curated value; record disagreements (see conflicts report).
- **Datasheet (deliberate exception to fill-blanks-only — always repoint):** resolve
  `datasheet_source_url` → manifest entry (via the `source_urls` reverse index). **Only if**
  that entry exists and is `archive_ok` with a `download_url`, `UPDATE <table> SET datasheet
  = <download_url> WHERE unique_id = ?` — overwriting the row's prior value **even when it
  was a non-blank curated URL** (the whole point: repoint to our durable, content-addressed
  Release copy; native rows' rotting manufacturer URLs are exactly what this fixes). **If the
  sidecar has no entry, or it doesn't resolve, or the entry is unmirrored (no `archive_ok`/
  `download_url`), leave the existing `datasheet` untouched** — never write an empty/dangling
  value. (Curation note: harvest prefers to mirror the row's *existing* URL when it already
  has one, so repointing preserves the curated document, just served from our durable host.)

`db/terra.db` lists the manifest + sidecars as prerequisites, so harvested-data edits
trigger a rebuild. This supersedes the CERN-only `rewrite_datasheets.py` filename-match.

### 6b. `localize_datasheets.py` / `make localize-datasheets` (optional, local, offline)

A **separate opt-in** target for users who want datasheets served from local files instead
of the Release URL. It works **purely from the built DB + the local-cache index** — no
sidecars: each datasheet that `apply_harvest` set is a `download_url` of the form
`…/<sha256>.pdf`, so localize parses the `sha256` from the URL, and **iff** that hash is
present-and-verified in the local-cache index (§5), rewrites `datasheet` to the local
`${TERRA_EDA_LIB}` file path. Rows whose datasheet is not a Release `download_url` (left
untouched by `apply_harvest`), or whose hash isn't cached, stay as-is. This is the **only**
step that reads the gitignored local-cache state, and is never a prerequisite of `make all`
— so non-deterministic local state cannot fork the canonical DB (it only swaps a stable URL
for a local path on the user's own machine).

### 7. GitHub Pages catalog index

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

Fill-blanks-only for every allowlist column **except `datasheet`**, enforced in
`apply_harvest.py` (§6) over the built DB. For params, curated CERN/native values always
win; harvested values fill only `NULL`/empty columns. **`datasheet` is the deliberate
exception:** it is always repointed to the Release `download_url` when one is available
(§6), because repointing rotting/internal links to our durable mirror is the goal — but
it is never blanked when no mirror exists.

Every param overwrite that *would* have happened (non-blank curated value disagreeing with
a harvested one) is written to a conflicts report — turning the harvest into a passive
data-quality probe. The report is a **single gitignored file** (`build/harvest_conflicts.tsv`,
in `.gitignore`) **truncated and rewritten deterministically each build** — never appended,
so repeated builds neither duplicate entries nor dirty the tree.

## Error handling & rate limits

- **Nexar:** OAuth token refresh; exponential backoff on 429; checkpoint after each part
  so a quota stop resumes cleanly; `no-match` and `low-confidence` recorded (not guessed).
- **mirror:** a `source_url` that 404s → entry left without `download_url`/`archive_ok`;
  surfaced by audit.
- **download:** `sha256` mismatch → re-fetch once, then mark that hash absent in the
  local-cache index and skip (never installs an unverified PDF). `localize_datasheets` then
  leaves those rows at the Release `download_url`.
- **Offline + determinism guarantee:** `db/terra.db` depends only on committed files
  (manifest + sidecars); the online phases and the local-cache-dependent `localize` step are
  separate targets, never prerequisites of `all`.

## Testing

- Phase 0: a test that each `<type>.sql` fragment is included by both the CERN and native
  schemas, and that the resulting tables expose an identical type-column set.
- `harvest`: fixture Nexar responses → asserts field-map output respects the
  `CORE_HARVEST_COLUMNS` + type-fragment allowlist (and drops everything else);
  low-confidence handling; sidecar carries `datasheet_source_url` + `original_datasheet`.
- `apply_harvest` (deterministic): fixture sidecar + manifest + built DB → asserts blanks
  filled, non-blanks preserved, conflicts logged, and `datasheet` set to the resolved
  `download_url` by `unique_id` on a **static** native table (URL-valued `datasheet`) as
  well as a generator/CERN table. Resolution survives a Phase-2 re-key (sidecar
  `source_url` still joins to the now-`sha256`-keyed entry).
- **determinism:** `apply_harvest` produces an identical DB with an empty vs populated
  local cache (it never reads the cache).
- `mirror`/`prune`: fake release-asset listing → asserts content-addressed upload, clobber,
  re-key keeps `source_urls`, and exactly the unreferenced hashes are pruned.
- `download`/`localize`: sha256 pass/mismatch updates the local-cache index correctly;
  `localize` rewrites to a local path only for cached hashes and leaves the rest at
  `download_url`.
- manifest round-trip / schema validation; catalog builds from a fixture DB.

## Open questions

- **License flag policy:** what populates `license_note`, and whether any manufacturer's
  terms require excluding its PDFs from the public mirror (handled per-entry, default
  empty). To settle during implementation.
- **Sharding threshold:** single `terra-datasheets` tag vs per-type tags — decide once the
  real asset count is known after the first full harvest.
- **Catalog hosting branch:** `/docs` on `main` vs a `gh-pages` branch — Phase-implementation
  detail.
