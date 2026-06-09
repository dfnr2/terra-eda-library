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

- A local FastAPI server implementing KiCad's three HTTP Library v1 endpoints.
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

Source: KiCad developer docs, "HTTP Libraries".

| Endpoint | Returns |
|---|---|
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
    "footprint": { "value": "Library:FootprintName", "visible": "false" },
    "Value":     { "value": "10k", "visible": "true" },
    "Datasheet": { "value": "http://...", "visible": "false" }
  }
}
```

Contract details that drive the serializer:

- **All booleans are strings** — `"true"`/`"false"` (KiCad also accepts
  `"1"/"0"/"yes"/"no"/"y"/"n"`, case-insensitive). Never emit JSON booleans.
- **Footprint is not a top-level key.** It is `fields.footprint`, value
  `"Library:FootprintName"`.
- **`id` is global** across the whole library (the `/v1/parts/{id}` lookup is not
  category-scoped). Terra's `unique_id` (mfr-mpn) is globally unique and is the id.
- **Auth:** KiCad sends `Authorization: Token <token>`. v1 binds `127.0.0.1` and
  ignores the header.

`.kicad_httplib` config:

```json
{
  "meta": { "version": 1.0 },
  "name": "Terra EDA Library",
  "source": {
    "type": "REST_API",
    "api_version": "v1",
    "root_url": "http://127.0.0.1:8361/",
    "token": "",
    "timeout_seconds": 5
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
  `_v` suffix (or maps view→base via a known rule) to read all parts. Document the
  exact rule in the plan; verify every dbl table has a resolvable base table.
- **Global id index:** at startup, build `unique_id → table` from every base
  table's key column so `/v1/parts/{id}` resolves in one lookup. Detect and fail
  loudly on cross-table id collisions (should not happen given the mfr-mpn scheme).
- **Endpoints:**
  - `categories.json`: one entry per dbl library — `id` = base table name,
    `name` = library `name`, `description` = `""` (or library description if present).
  - `parts/category/{id}.json`: `SELECT <key> AS id, <name col> AS name FROM <table>`.
    **Name column:** the library's designated display field, defaulting to the
    first `fields[]` entry (typically `Manufacturer PN`), falling back to the key.
  - `parts/{id}.json`: look up table via the id index, fetch the row, then:
    - `symbolIdStr` ← row[symbols column]
    - `fields.footprint` ← `{value: row[footprints column], visible: "false"}`
      (omit if null/empty)
    - one `fields[name]` per dbl field def ← `{value: str(row[column]),
      visible: "true" if visible_in_chooser else "false"}` (skip null values)
    - `exclude_from_bom/board/sim` ← `"false"` in v1 (no column drives these yet)
- **Bind:** `127.0.0.1:8361`. Token ignored.

### 2. `tools/generate_kicad_httplib.py`

Emits `terra.kicad_httplib` (above), sibling to the existing
`tools/generate_kicad_dbl_files.py`. Port and root_url from a constant / CLI arg.

### 3. Makefile `serve` target

```
serve:
	uv run terra-server --db db/terra.db
```

Manual launch; KiCad must find the server already running. Auto-start deferred.
Expose the server as a `terra-server` console script via `pyproject.toml`.

### 4. Tests (`tests/`)

Pytest against a small fixture DB (a few rows across 2-3 tables) using FastAPI's
`TestClient`:

- `categories.json` returns the expected set, correct shape.
- `parts/category/{id}.json` returns id/name pairs for a known table.
- `parts/{id}.json` for a known part:
  - `symbolIdStr` matches the symbols-column value,
  - `fields.footprint.value` matches the footprints-column value,
  - every boolean is a JSON string, not a JSON boolean,
  - a `visible_in_chooser: false` field serializes `visible: "false"`.
- Unknown id → 404; unknown category → 404 or empty list (match KiCad's tolerance).

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
- Cross-table `unique_id` collision at index build → fail loudly at startup.
- Unknown part id → HTTP 404. Unknown category id → HTTP 404.
- Null/empty cell values → omit that field rather than emitting `"None"`.
- Server not running → KiCad shows empty libraries; acceptable for v1 (an offline
  `.kicad_dbl` fallback is a deferred consideration noted in `fastload.org`).

## Open items for the implementation plan

- Exact view→base-table resolution rule, verified across all 44 dbl libraries.
- Per-library "name column" choice (default-to-first-field may be wrong for some
  tables; confirm during the port).
- Whether `db/terra.db` already contains base tables alongside `*_v` views, or
  whether a make target must ensure they exist.
