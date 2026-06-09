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
part data only on selection — and caches by `max_age`. Moving to a local HTTP
server over the *same* SQLite gets that lazy behavior at localhost latency.

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
  (e.g. `bjt`, not the `bjt_v` view) — i.e. **all parts, no tier filter**.
- Reuses `terra.kicad_dbl` as the **library/field spec** (single source of truth
  for table names, key column, symbol/footprint columns, field name + visibility).
  No new config format.
- A generator `tools/generate_kicad_httplib.py` emitting `terra.kicad_httplib`.
- A `make serve` target for manual launch.
- Pytest coverage of the three endpoints against a small fixture DB.

### Out (deferred — tracked in `fastload.org`)

- Dynamic subcategories / category splitter.
- Web UI for browsing/tagging.
- Tier / tag filtering and `${KIPRJMOD}/terra.json` project config.
- Auto-start (systemd/launchd) service.
- Authentication / non-localhost hosting (the Cloudflare-worker option B).

### Deferred decision, validated empirically after v1

Ship flat, then benchmark the largest categories — **Regulators (~1056)**,
**SAMTEC (~1363)** — to measure KiCad's per-part fetch (N+1) behavior on category
expand/selection. Build the subcategory splitter only if the numbers require it.
This answers the `fastload.org` open question with real data.

## KiCad HTTP Library v1 contract (authoritative)

Source: KiCad developer docs, "HTTP Libraries"; verified against a known-good
`.kicad_httplib` example and the collision/URL-safety realities of `db/terra.db`.

| Endpoint | Returns |
|---|---|
| `GET /v1/` (root) | `{ "categories": "...", "parts": "..." }` — **only keys are validated**; values may be blank. KiCad hits this first to validate the connection before syncing. |
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
- **`id` is an opaque, URL-safe surrogate — NOT `unique_id`.** Two reasons,
  both verified against `db/terra.db`:
  - `unique_id` (mfr-mpn) is **not globally unique**: 5 cross-table collisions
    exist (e.g. `SAMTEC-CES-110-01-T-S` in both `cern_samtec` and `cern_sockets`).
    A global `unique_id → table` index would be ambiguous.
  - `unique_id` values contain spaces, dots, and slashes (e.g.
    `MURATA POWER SOLUTIONS-OKI-78SR-3.3/1.5-W36H-C`) — unusable as a URL path
    segment in `/v1/parts/{id}.json`.

  v1 id = **`{table}:{rowid}`** (SQLite integer `rowid`): table-namespaced so it is
  globally unique, integer-tailed so it is URL- and route-safe (no spaces, dots, or
  slashes). The server resolves `{table}:{rowid}` directly — no global index, no
  collision. The real MPN/`unique_id` still appears in the part's `fields`.
  `rowid` is not stable across DB rebuilds, which is acceptable: KiCad copies a
  placed part's symbol+fields into the schematic, so browse-time ids need not
  survive a regenerate.
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
  `_v` suffix (or maps view→base via a known rule) to read all parts. Verified: all
  44 dbl libraries have a resolvable base table in `db/terra.db`. Document the exact
  rule in the plan.
- **Part id = `{table}:{rowid}`** (see contract). No global index, no collision
  handling — the table is embedded in the id, so `/v1/parts/{id}.json` resolves with
  one `SELECT ... WHERE rowid = ?` against the named table.
- **Endpoints:**
  - `/v1/` (root): return `{"categories": "v1/categories.json", "parts": "v1/parts"}`
    (KiCad validates only that the keys exist).
  - `categories.json`: one entry per dbl library — `id` = base table name,
    `name` = library `name`, `description` = `""` (or library description if present).
  - `parts/category/{id}.json`: `SELECT rowid, <name col> FROM <table>`, emit
    `{id: f"{table}:{rowid}", name: <name col>}`.
    **Name column:** the library's designated display field, defaulting to the
    first non-reserved `fields[]` entry (typically `Manufacturer PN`), falling back
    to `unique_id`.
  - `parts/{id}.json`: split `{table}:{rowid}`, fetch the row by `rowid`, then:
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
	uv run terra-server --db db/terra.db
```

Manual launch; KiCad must find the server already running. Auto-start deferred.
Expose the server as a `terra-server` console script via `pyproject.toml`.

### 4. Tests (`tests/`)

Pytest against a small fixture DB (a few rows across 2-3 tables, **including a
deliberate cross-table `unique_id` duplicate** to lock in the surrogate-id fix)
using FastAPI's `TestClient`:

- `/v1/` root returns a dict containing both `categories` and `parts` keys.
- `categories.json` returns the expected set, correct shape.
- `parts/category/{id}.json` returns `{id, name}` pairs; every `id` matches the
  `{table}:{rowid}` form.
- `parts/{id}.json` for a known part:
  - `symbolIdStr` matches the symbols-column value,
  - `fields.footprint.value` matches the footprints-column value,
  - **no second `footprint`/`Footprint` field** is emitted from the generic loop,
    and **no `Symbol` field** (symbol/footprint columns are skipped),
  - every boolean is a JSON string, not a JSON boolean,
  - a `visible_in_chooser: false` field serializes `visible: "false"`.
- A part whose `unique_id` collides across two tables resolves to the correct row
  via its `{table}:{rowid}` id (no ambiguity).
- Unknown id → 404; unknown category → 404 or empty list (match KiCad's tolerance).
- **Generated `terra.kicad_httplib` schema:** asserts `source.type == "REST_API"`,
  `api_version == "v1"`, and that `timeout_parts_seconds` /
  `timeout_categories_seconds` are present (not `timeout_seconds`).

## Data flow

```
terra.kicad_dbl (library + field spec, read at startup)
        +
db/terra.db base tables (read-only, all parts)
        ↓
tools/terra_server.py  (FastAPI, 127.0.0.1:8361)
        ↓  GET /v1/...  (lazy: categories → category parts → part on select)
KiCad  ← terra.kicad_httplib (generated)
```

## Error handling

- DB missing / unreadable at startup → exit non-zero with a clear message.
- Malformed part id (not `{table}:{rowid}`, unknown table, or non-integer rowid)
  → HTTP 404. (The surrogate-id scheme removes the cross-table collision failure
  mode entirely — no global index to collide.)
- Unknown part id → HTTP 404. Unknown category id → HTTP 404.
- Null/empty cell values → omit that field rather than emitting `"None"`.
- Server not running → KiCad shows empty libraries; acceptable for v1 (an offline
  `.kicad_dbl` fallback is a deferred consideration noted in `fastload.org`).

## Open items for the implementation plan

- Exact view→base-table resolution rule (the `_v` strip is verified to cover all 44
  libraries; confirm no edge cases where the base name differs).
- Per-library "name column" choice (default-to-first-non-reserved-field may be wrong
  for some tables; confirm during the port).
- Confirm KiCad tolerates a `{table}:{rowid}` id containing a colon in the
  `/v1/parts/{id}.json` path (expected fine — colon is a valid path char; rowid is
  integer so no dot/slash ambiguity with the `.json` suffix). Validate end-to-end in
  a real KiCad before declaring v1 done.
