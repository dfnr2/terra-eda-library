# Registering terra libraries in KiCad (one-time, global)

Make the terra database library and every terra/cern symbol & footprint library
available in KiCad **once, globally**, so all projects see them and future
`cern_<table>` ports appear automatically with no further KiCad edits.

## Why global + includes (not per-project, not per-library)

Three registrations do everything:

1. **`terra` (Database)** → `${TERRA_EDA_LIB}/terra.kicad_dbl`. Supplies the
   parts, their fields, and which symbol/footprint each part uses.
2. **`terra-symbols` (Table)** → `${TERRA_EDA_LIB}/kicad_symbols/sym-lib-table`.
   A `(type "Table")` *include* of the generated symbol lib-table, which lists
   every `cern-*` symbol lib plus `terra_sym`.
3. **`terra-footprints` (Table)** → `${TERRA_EDA_LIB}/kicad_footprints/fp-lib-table`.
   Same idea for footprints.

The parts reference terra nicknames (`cern-diodes`, `cern-ics-and-semiconductors-smd`,
`terra_sym`, …). The two generated includes define those nicknames, so a single
include exposes **all current and future** libs — no edit per ported table.
Registering globally (not per-project) is what prevents the drift that causes
"no fields / no footprints": projects had partial, hand-added, sometimes broken
or self-duplicating entries.

## Preconditions

- **Fully quit KiCad** (all windows). KiCad rewrites the lib-tables on exit and
  caches database libraries at load — editing while it runs loses your edits and
  keeps stale data. Verify it is closed:
  ```
  pgrep -af '/usr/bin/kicad|eeschema|pcbnew'
  ```
- Config dir: `~/.config/kicad/<version>/` (e.g. `10.0`).
- `TERRA_EDA_LIB` is set under `vars` in `~/.config/kicad/<version>/kicad_common.json`.

## Step 1 — Back up the global tables
```
cd ~/.config/kicad/<version>
cp sym-lib-table sym-lib-table.bak
cp fp-lib-table  fp-lib-table.bak
```

## Step 2 — Global `sym-lib-table`
Add these two lines inside `(sym_lib_table … )`:
```
(lib (name "terra")(type "Database")(uri "${TERRA_EDA_LIB}/terra.kicad_dbl")(options "")(descr "terra parts database"))
(lib (name "terra-symbols")(type "Table")(uri "${TERRA_EDA_LIB}/kicad_symbols/sym-lib-table")(options "")(descr "terra + cern symbols"))
```

## Step 3 — Global `fp-lib-table`
Add inside `(fp_lib_table … )`:
```
(lib (name "terra-footprints")(type "Table")(uri "${TERRA_EDA_LIB}/kicad_footprints/fp-lib-table")(options "")(descr "terra + cern footprints"))
```
**Remove** any standalone `(lib (name "terra_sym") …)` — the include already
provides a working `terra_sym` (`kicad_footprints/terra_sym.pretty`); old
standalone entries often point at the dead `assets/footprints/terra_sym.pretty`
path and would also duplicate the include's nickname.

Optional: the raw `${CERN_LIB_DIR}/PcbLib/*` entries use the *original* CERN
nicknames (e.g. `ICs And Semiconductors SMD`), which do **not** collide with the
`cern-*` terra copies. They are redundant; leave them unless you want a clean
table, but the database parts never use them.

## Step 4 — De-duplicate project tables
KiCad errors on a nickname defined both globally and in a project. Remove every
terra/cern entry from each project's `sym-lib-table` **and** `fp-lib-table` so the
global ones are authoritative. Find them:
```
grep -lE 'terra|cern-|Database' <project>/sym-lib-table <project>/fp-lib-table
```
Delete lines whose `name` is any of: `terra`, `terra-symbols`, `terra-footprints`,
`terra_sym`, `terra_footprints`, or `cern-*`.

## Step 5 — Verify the backend (KiCad still closed)
```
echo "SELECT count(*) FROM cern_diodes_v;" | \
  isql -k "DRIVER=<driver.so>;Database=<ABSOLUTE path to db/terra.db>;Timeout=2000;"
```
Expect a non-zero count. The `.kicad_dbl` `connection_string` **must** use the
absolute DB path — KiCad does not expand `${…}` vars inside it.

## Step 6 — Launch & confirm
Open KiCad → Symbol Chooser → `terra` database → `cern_diodes`: parts appear with
fields; place one and confirm its symbol and footprint resolve. Repeat for
`cern_transistors`, `cern_regulators`.

## Rollback
Restore the `.bak` files and relaunch KiCad.

## Maintenance notes / gotchas
- **One-time.** After porting a new `cern_<table>`, just rebuild (`make`) — the
  generated includes pick up the new libs; KiCad needs no changes.
- **Always fully quit + relaunch KiCad after rebuilding `db/terra.db`** — database
  libraries are cached at load, so a rebuild looks like "no data" until restart.
- Absolute path in the `.kicad_dbl` connection string (emitted by
  `tools/generate_kicad_dbl_files.py`); vars are expanded in lib-table URIs but
  not in the connection string.
