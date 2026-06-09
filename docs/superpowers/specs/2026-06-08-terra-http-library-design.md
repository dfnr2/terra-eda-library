# Terra HTTP Library — v1 Design

**Date:** 2026-06-08
**Status:** Approved, ready for implementation plan
**Supersedes for KiCad integration:** the ODBC `.kicad_dbl` path (kept only as the
field/library spec source — see below)
**Parent vision:** `fastload.org` § "HTTP Library Architecture". This spec is the
**scoped first goal** carved out of that doc.

## Motivation

KiCad loads the terra database library slowly. The `.kicad_dbl`/ODBC path
materializes the whole catalog up front. KiCad's HTTP library (KiCad 8+) loads
lazily — enumerate categories, fetch a category's part list on expand, fetch full
part data only on selection — and caches per the `timeout_parts_seconds` /
`timeout_categories_seconds` TTLs. Moving to a local HTTP server over the *same*
SQLite gets that lazy behavior at localhost latency.

The symbol and footprint **graphics do not move**. HTTP libraries, like database
libraries, only supply part *metadata* and reference symbols/footprints by
`lib:name` resolved through `sym-lib-table` / `fp-lib-table`. The big `.kicad_sym`
/ `.kicad_mod` files load on demand per symbol either way.

## Scope

### In (v1)

- A local FastAPI server implementing KiCad's HTTP Library v1 endpoints (the root
  validation endpoint plus the three data endpoints).
- **44 categories mapped 1:1** to the libraries currently defined in
  `terra.kicad_dbl` — no dynamic subcategory engine.
- Reads the existing master `db/terra.db` **read-only**, from the **base tables**
  (e.g. `bjt`, not the `bjt_v` view), with a **default tier cutoff applied
  server-side** (`WHERE tier <= 2`, the `fastload` `DEFAULT_TIER`). All 44 base
  tables have a populated `tier` column. The cutoff is a server flag (`--tier N`),
  not per-project config. This keeps the big generated tables manageable
  (`resistors_smt` 22,539 → 4,805 visible; `capacitors_smt` 4,863 → 706) without the
  subcategory splitter. The cutoff filters the **category listings**; `parts/{id}`
  still resolves any valid id regardless of tier (so a previously-placed
  higher-tier part keeps re-resolving even if the cutoff later tightens).
- Reuses `terra.kicad_dbl` as the **library/field spec** (single source of truth
  for table names, key column, symbol/footprint columns, field name + visibility).
  No new config format.
- A generator `tools/generate_kicad_httplib.py` emitting `terra.kicad_httplib`.
- A `make serve` target for manual launch.
- Pytest coverage of all four endpoints (root + the three data endpoints) against a
  small fixture DB.
- The packaging to support the above: new runtime/dev dependencies and a console
  script in `pyproject.toml` (see Component 3).

### Out (deferred — tracked in `fastload.org`)

- Dynamic subcategories / category splitter.
- Web UI for browsing/tagging.
- **Per-project, user-adjustable** tier/tag config (`${KIPRJMOD}/terra.json`
  overrides, tag filtering). A *fixed default tier cutoff* is in v1 (above); only the
  per-project override and tag filtering are deferred.
- Auto-start (systemd/launchd) service.
- Authentication / non-localhost hosting (the Cloudflare-worker option B).

### Deferred decision, validated empirically after v1

With the default `tier <= 2` cutoff, the largest **visible** categories are
`resistors_smt` (**4,805**) and `capacitors_smt` (**706**) — verified in
`db/terra.db` (raw row / `tier<=2` counts):

| table | rows | visible (`tier<=2`) |
|---|---|---|
| `resistors_smt` | 22,539 | **4,805** |
| `capacitors_smt` | 4,863 | 706 |
| `cern_analog_interface` | 2,199 | 2,199 |
| `cern_op_amps` | 1,569 | 1,569 |
| `cern_samtec` | 1,363 | 1,363 |
| `cern_regulators` | 1,056 | 1,056 |

(The CERN tables are mostly tier 0, so the cutoff barely changes them.) Benchmark
`resistors_smt` at ~4.8k **first** — it remains the stress case, but is now ~5×
smaller than the unfiltered 22.5k, and well short of needing the splitter on day one.

**What the benchmark decides:** `fastload`'s target is 50–200 parts/category, which a
4.8k category still exceeds. If KiCad's per-category enumeration is sluggish at 4.8k,
the next step is the **subcategory splitter** (by package, etc.) for the generated
tables — which is also what would eventually let the tier cutoff be raised or
dropped. Until measured, keep the flat-with-cutoff shape.

## KiCad HTTP Library v1 contract (authoritative)

Source: KiCad developer docs, "HTTP Libraries"; verified against a known-good
`.kicad_httplib` example and the collision/URL-safety realities of `db/terra.db`.

| Endpoint | Returns |
|---|---|
| `GET /v1/` (root) | `{ "categories": "...", "parts": "..." }` — both keys required **with non-empty values** (KiCad checks `!.empty()` on each). KiCad hits this first to validate the connection before syncing. |
| `GET /v1/categories.json` | `[{ "id", "name", "description" }]` |
| `GET /v1/parts/category/{id}.json` | `[{ "id", "name"?, "description"? }]` (cheap: id/name only) |
| `GET /v1/parts/{id}.json` | full part object (below) |

Part object:

```json
{
  "id": "string",
  "name": "string",
  "symbolIdStr": "Library:SymbolName",
  "exclude_from_bom": "false",
  "exclude_from_board": "false",
  "exclude_from_sim": "false",
  "fields": {
    "footprint": { "value": "Library:FootprintName", "visible": "true" },
    "Value":     { "value": "10k", "visible": "true" },
    "Datasheet": { "value": "http://...", "visible": "false" }
  }
}
```

Contract details that drive the serializer:

- **All booleans are strings** — `"true"`/`"false"` (KiCad also accepts
  `"1"/"0"/"yes"/"no"/"y"/"n"`, case-insensitive). Never emit JSON booleans.
- **Footprint is not a top-level key.** It is `fields.footprint`, value
  `"Library:FootprintName"`. KiCad lower-cases field names when applying built-ins,
  so any generic field also named `Footprint` collides with this canonical key
  (see "footprint/symbol columns" below).
- **`id` is KiCad's fetch/cache key, not the durable schematic handle.** For HTTP
  libraries KiCad does **not** store `id` in the schematic — the placed symbol's
  `LIB_ID` is `nickname:category:name` (see the `name` bullet below). `id` is only
  the key KiCad uses to fetch a part (`/v1/parts/{id}.json`) and to organize its
  in-memory cache, so it must be **globally unique** and **URL-safe**.
  - **`id` must nonetheless be stable across rebuilds — transitively.** The durable
    handle is `name`, and v1 constructs `name` to embed `id` (for uniqueness; see
    below). So an `id` that changed on `make` regenerate would change every `name`
    and orphan placed parts at the next *Update from Library*. The stability burden
    lives on `name`; embedding `id` propagates it to `id`. Either way, both must be
    a **pure function of stable source identity**, never of storage position.
  - This rules out `rowid` (insertion-order; renumbers when parts are added/removed
    or generator order changes).
  - It also rules out raw `unique_id` directly: not globally unique (5 cross-table
    collisions, e.g. `SAMTEC-CES-110-01-T-S` in both `cern_samtec` and
    `cern_sockets`) and not URL-safe (values contain spaces, dots, slashes, e.g.
    `MURATA POWER SOLUTIONS-OKI-78SR-3.3/1.5-W36H-C`).

  **v1 id = a deterministic hash of `unique_id`** (e.g. first 16 hex chars of
  `sha1(unique_id)`). Stable (pure function of the part's MPN identity), globally
  unique (given the build invariant below), and URL-safe (hex). The id is opaque
  plumbing; the real MPN stays in the part's `fields`. The server builds a
  `hash → (table, rowid)` map once at startup to resolve `/v1/parts/{id}.json`.

  **Build invariant (the actual stability guarantee):** the regenerate asserts that
  `unique_id` is non-null and **globally unique across all base tables**, failing
  loudly otherwise — so ids can never silently shift or merge. The 5 current
  cross-table duplicates must be resolved to satisfy this (they are the *same*
  physical part cross-listed; collapsing each to a single canonical row/category is
  the correct model, not a workaround). Exact resolution of the 5 is a plan item.

- **`name` is NOT a display label — it is the symbol's identity, and the durable
  schematic handle.** Verified in KiCad source (`sch_io_http_lib.cpp`):
  `wxString libIDString( part.name ); … symbol->SetName(...)` — `part.name` becomes
  the LIB_SYMBOL name and the placed symbol's `LIB_ID` is
  `nickname:category:name`. Consequences:
  - **Duplicate names overwrite each other** during category enumeration — the
    shadowed parts become unplaceable. Using the obvious display field (MPN) as
    `name` is unsafe: across base tables there are **~3,200 within-table duplicate
    values** in the would-be name column, and legacy generated tables whose first
    field is `Allow Substitution` would name every row `"Yes"`/`"No"`. So `name`
    must be **globally unique**.
  - It is the handle KiCad stores in the schematic and re-resolves on *Update from
    Library*, so it must also be **stable across rebuilds** and survive KiCad's
    illegal-LIB_ID-character sanitization (which replaces `/`, spaces, etc. with
    `_` — itself a collision source).

  v1 `name = sanitize(mpn-or-key) + "_" + id`, where:
  - **`sanitize(s)`** maps every character outside the allow-list `[A-Za-z0-9._-]`
    to `_`. That allow-list is a strict subset of KiCad's legal LIB_ID symbol-name
    characters (KiCad rejects `/`, `:`, and whitespace and replaces them with `_`;
    `_` `-` `.` and alphanumerics are legal). Because our output already contains
    only legal characters, **KiCad's own `FixIllegalChars` is a no-op on it** — so
    the name KiCad stores byte-matches the name we serve. No second normalization
    pass, no surprise rename.
  - **Uniqueness survives sanitization** because it is carried entirely by the
    `_<id>` suffix (`id` is a unique, already-legal hex hash), not by the sanitized
    prefix. Two different MPNs that sanitize to the same prefix still differ in the
    suffix, so names stay globally unique even after any normalization.
  - The leading sanitized MPN is only for human-recognizability; fall back to `id`
    alone when no MPN/key is present.

  The **pretty MPN, manufacturer, and description go in `fields`**
  (`Manufacturer PN`, `Value`, `Description`), which is what the chooser shows in
  columns.
- **Auth:** KiCad sends `Authorization: Token <token>`. v1 binds `127.0.0.1` and
  ignores the header.

`.kicad_httplib` config (timeout keys verified — KiCad uses
`timeout_parts_seconds` / `timeout_categories_seconds`, **not** `timeout_seconds`;
larger values are exactly what speeds up chooser open for static data):

```json
{
  "meta": { "version": 1.0 },
  "name": "Terra EDA Library",
  "source": {
    "type": "REST_API",
    "api_version": "v1",
    "root_url": "http://127.0.0.1:8361/",
    "token": "",
    "timeout_parts_seconds": 3600,
    "timeout_categories_seconds": 86400
  }
}
```

## Components

### 1. `tools/terra_server.py` — FastAPI app

- **DB access:** one read-only SQLite connection to `db/terra.db`
  (`file:...?mode=ro`, `check_same_thread=False`).
- **Spec source:** load `terra.kicad_dbl` at startup. Each library entry gives:
  `table`, `name`, `key` (`unique_id`), `symbols` (column holding `lib:symbol`),
  `footprints` (column holding `lib:fp`), and `fields[]`
  (`column`, `name`, `visible_in_chooser`).
- **Base-table mapping:** the dbl `table` points at the `*_v` view; v1 strips the
  `_v` suffix (or maps view→base via a known rule) to read the base table directly
  (the tier cutoff is applied per-query, below — not via the view). Verified: all
  44 dbl libraries have a resolvable base table in `db/terra.db`. Document the exact
  rule in the plan.
- **Part id = `hash(unique_id)`** (see contract). At startup the server scans every
  base table's `unique_id` column and builds a `hash → (table, rowid)` map; the
  build invariant guarantees this map is 1:1. A duplicate hash discovered at startup
  is a hard error (means the invariant was bypassed). The map covers **all** rows
  regardless of tier (so any placed part re-resolves even after the cutoff tightens).
- **Tier cutoff:** a server flag `--tier N` (default **2**). Applied as
  `WHERE tier <= N` in the **category listing** query only. All 44 base tables have a
  `tier` column. Per-project override is out of scope (see Deferred).
- **Endpoints:**
  - `/v1/` (root): return `{"categories": "v1/categories.json", "parts": "v1/parts"}`
    — both values **non-empty** (KiCad checks `!.empty()` on each, not just key
    presence).
  - `categories.json`: one entry per dbl library — `id` = base table name,
    `name` = library `name`, `description` = `""` (or library description if present).
  - `parts/category/{id}.json`:
    `SELECT unique_id, <display col> FROM <table> WHERE tier <= <cutoff>`, emit
    `{id: hash(unique_id), name: sanitize(<display col>) + "_" + id}` (see the `name`
    contract bullet — `name` must be globally unique, not the raw display field).
  - `parts/{id}.json`: resolve `id → (table, rowid)` via the startup map, fetch the
    row, then:
    - `name` ← `sanitize(mpn-or-key) + "_" + id` — **must byte-match** the `name`
      returned by the category listing for the same part (KiCad keys on it).
    - `symbolIdStr` ← row[symbols column]
    - `fields.footprint` ← `{value: row[footprints column],
      visible: <Footprint field's visible_in_chooser>}` (omit if null/empty)
    - one `fields[name]` per dbl field def — **but skip any field whose `column` is
      the library's `symbols` or `footprints` column** (in terra these are surfaced
      as fields named `Symbol` and `Footprint`; re-emitting `Footprint` would clobber
      the canonical `fields.footprint`, and `Symbol` is redundant with `symbolIdStr`).
      Value `str(row[column])`, `visible: "true"/"false"` from `visible_in_chooser`;
      skip null values.
    - `exclude_from_bom/board/sim` ← `"false"` in v1 (no column drives these yet)
- **Bind:** `127.0.0.1:8361`. Token ignored.

### 2. `tools/generate_kicad_httplib.py`

Emits `terra.kicad_httplib` (above), sibling to the existing
`tools/generate_kicad_dbl_files.py`. Port and root_url from a constant / CLI arg.
Must emit `timeout_parts_seconds` / `timeout_categories_seconds` (large defaults for
static data) — **not** `timeout_seconds`.

### 3. Makefile `serve` target

```
serve:
	uv run terra-server --db db/terra.db --tier 2
```

Manual launch; KiCad must find the server already running. Auto-start deferred.
`--tier` defaults to 2, so the flag is shown for discoverability, not necessity.

**Packaging (`pyproject.toml`) — currently absent, must be added by the plan:**

- Add runtime deps: `fastapi`, `uvicorn` (the existing deps are only `pyyaml`,
  `sexpdata`).
- Add dev dep: `httpx` (required by FastAPI's `TestClient`); `pytest` already
  present.
- Add `[project.scripts]` `terra-server = "tools.terra_server:main"` (or equivalent)
  so `uv run terra-server` and the `make serve` target resolve.

### 4. Tests (`tests/`)

Pytest against a small fixture DB (a few rows across 2-3 tables) using FastAPI's
`TestClient`:

- `/v1/` root returns a dict with `categories` and `parts` keys whose values are
  **non-empty** strings.
- `categories.json` returns the expected set, correct shape.
- `parts/category/{id}.json` returns `{id, name}` pairs; every `id` equals
  `hash(unique_id)` for its row.
- **tier cutoff:** with a fixture containing `tier` 0–3 rows, the default
  (`tier<=2`) category listing **excludes** the tier-3 rows; `--tier 3` includes
  them; and `parts/{id}` resolves a tier-3 part's id **regardless** of the cutoff
  (placed-part re-resolution must not depend on the current cutoff).
- **id stability:** the id for a fixture row equals the hash of its `unique_id` and
  does **not** change if the row is re-inserted at a different position (guards
  against any rowid/order dependence creeping back in).
- **name uniqueness:** a fixture with two rows sharing the same MPN (and a legacy
  row whose first field is `Allow Substitution`) still yields **distinct, non-empty
  `name`s**, and the `name` from `parts/category` byte-matches the `name` from
  `parts/{id}` for the same part.
- **name normalization-safety:** every generated `name` contains only
  `[A-Za-z0-9._-]`, and applying a KiCad-style `FixIllegalChars` (replace `/`, `:`,
  whitespace, and any non-allow-list char with `_`) leaves it **unchanged**
  (idempotent) — and the set of names is still fully unique after that pass. Include
  a fixture MPN containing `/`, space, and `:` to exercise this.
- `parts/{id}.json` for a known part:
  - `symbolIdStr` matches the symbols-column value,
  - `fields.footprint.value` matches the footprints-column value,
  - **no second `footprint`/`Footprint` field** is emitted from the generic loop,
    and **no `Symbol` field** (symbol/footprint columns are skipped),
  - every boolean is a JSON string, not a JSON boolean,
  - a `visible_in_chooser: false` field serializes `visible: "false"`.
- **Build invariant:** a fixture with a duplicate/null `unique_id` makes the
  uniqueness check fail loudly (and the server's startup map build raises on a
  duplicate hash).
- Unknown part id → 404; **unknown category → 404** (the server validates the
  category id before querying — single, consistent behavior).
- **Generated `terra.kicad_httplib` schema:** asserts `source.type == "REST_API"`,
  `api_version == "v1"`, and that `timeout_parts_seconds` /
  `timeout_categories_seconds` are present (not `timeout_seconds`).

## Data flow

```
terra.kicad_dbl (library + field spec, read at startup)
        +
db/terra.db base tables (read-only; default tier<=2 cutoff on listings)
        ↓
tools/terra_server.py  (FastAPI, 127.0.0.1:8361)
        ↓  GET /v1/...  (lazy: categories → category parts → part on select)
KiCad  ← terra.kicad_httplib (generated)
```

## Error handling

- DB missing / unreadable at startup → exit non-zero with a clear message.
- Duplicate `unique_id` hash while building the startup map → exit non-zero (the
  build invariant should have prevented this; fail rather than serve ambiguous ids).
- Unknown part id (hash not in the map) → HTTP 404. Unknown category id → HTTP 404.
- Null/empty cell values → omit that field rather than emitting `"None"`.
- Server not running → KiCad shows empty libraries; acceptable for v1 (an offline
  `.kicad_dbl` fallback is a deferred consideration noted in `fastload.org`).

## Open items for the implementation plan

- Exact view→base-table resolution rule (the `_v` strip is verified to cover all 44
  libraries; confirm no edge cases where the base name differs).
- Which display column leads the human-readable prefix of `name` (the MPN is the
  obvious choice, but legacy generated tables whose first field is
  `Allow Substitution` need a real MPN/key column picked instead). Uniqueness is
  already guaranteed by the `id` suffix regardless; this is only about readability.
- Exact resolution of the 5 cross-table `unique_id` duplicates (assign each to one
  canonical category, vs. list one id under multiple categories). v1 leans toward
  single canonical category for a clean 1:1 map; confirm none of the 5 must remain
  visible in both categories.
- Hash choice (algorithm + truncation length) — verify no collisions across the full
  `unique_id` set (**41,050 distinct** of 41,055 rows; the 5-row gap is the
  cross-table dups) at the chosen length; `sha1`-16-hex has ample headroom.
- Validate end-to-end in a real KiCad: place a part, regenerate the DB, then run
  *Update Symbols from Library* and confirm the placed part still re-resolves by its
  generated `name` (the LIB_ID handle, which embeds the stable `id`) — the whole
  point of the stable-name/id design.

## Future direction (v2) — part-locator normalization

Planned data-model change, **out of scope for v1** but recorded here because it
determines the long-term id story:

- The **part** becomes an abstract entity keyed by an internal `part_locator` UID.
  The primary part tables **drop the manufacturer/MPN columns**.
- A separate mapping table holds `(manufacturer, mpn, FK → part_locator)`, so one
  `part_locator` can have **many** manufacturer/MPN rows (alternates / second
  sources).

Id consequence: in v2 the HTTP part `id` becomes `part_locator` directly — opaque,
stable, and MPN-independent by construction (no hashing needed, and recategorization
or MPN edits no longer touch identity).

**Migration cost, accepted:** v1→v2 changes every generated `name`, because the
embedded `id` changes (from `hash(unique_id)` to `part_locator`). Since `name` is the
durable LIB_ID handle, parts placed under v1 orphan once at that major-version
boundary. This is a deliberate trade — it's the reason v1 keeps the id scheme
minimal (a hash) rather than over-investing. After v2, `part_locator` is the durable
id and never changes again. The v1 build invariant (global `unique_id` uniqueness)
is also a natural stepping stone: it's exactly the precondition for assigning one
`part_locator` per distinct part during the v2 migration.
