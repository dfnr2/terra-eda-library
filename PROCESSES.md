# Terra EDA Library — Processes

The detailed, operational "how." For the *why* behind these processes, see
[PLAN.md](PLAN.md); for the HTTP server contract, see
[specs/100-httplib-server-spec/server-spec.md](specs/100-httplib-server-spec/server-spec.md).

The environment is managed by [uv](https://docs.astral.sh/uv/); `make` syncs it
automatically (`make sync` to do it explicitly).

## Build and serve

The source of truth is the scripts and assets under `db/tables/<type>/`. The SQL
and the databases are generated from them.

```bash
make                 # build per-table DBs, db/terra.db, terra.kicad_dbl, lib-tables
make httplib         # write terra.kicad_httplib (the KiCad connection file)
make serve           # serve db/terra.db to KiCad at http://127.0.0.1:8361/
```

`make serve` runs in the foreground and reads a **snapshot** of the database at
launch — rebuild and restart it to pick up changes.

Per-table targets (replace `<type>` with `resistors_smt`, `capacitors_smt`, …):

```bash
make <type>-generate # run that table's run_*.py generators
make <type>-build    # build db/<type>.db
make <type>-dump     # dump db/<type>.db back to static SQL
make <type>-clean    # remove that table's generated files
make <type>-test     # run that table's pytest, if present
```

## Adding and changing parts

Parts are produced by **scripts** — generators and curation tools — not by
hand-editing the SQL or the database. **Every part has a script, even bespoke
one-offs**, so schema changes and convention switches (US vs. EU symbol styles)
are configuration changes followed by a rebuild. The scripts also enforce the
library's invariants — the canonical `part_locator` and complete metadata — that
a manual edit would bypass.

- **Generate a series:** run a table's generators, then rebuild — `make
  <type>-generate` then `make <type>-build` (or `make` for everything). The
  generators write `<type>_generated_*.sql` (gitignored, reproduced on every
  build).
- **Add a bespoke part:** write (or extend) a script for it in the table's
  directory, then rebuild as above.

Finish with `make`, then `make verify`, then review the diff of the scripts and
assets before committing.

**Legacy migration:** a few legacy parts still live as tracked static SQL
(`dump_priority > 0`). These are slated for migration to scripts; no new parts
should be added as static SQL. (`make dump` / `db_to_tables.py` is **legacy** —
used only to extract that remaining static SQL during migration, never in a normal
build; it rewrites tracked files, so don't run it casually.)

## Verifying

```bash
make verify          # clean rebuild from source + test suite (incl. schema drift guard)
make status          # state of all tables and databases
make schema          # regenerate _0_schema.sql files from db/schema/ sources
```

Run `make verify` after any significant change. Schemas are generated from the
canonical core + per-type fragments under `db/schema/`; edit those, not the
generated `_0_schema.sql` files, then `make schema`.

## Seeding parts from KiCad's shipped libraries

The go-forward way to grow the native library (see [PLAN.md](PLAN.md)). Iterate
KiCad's symbol library, classifying each symbol:

1. **Specific-part symbol** (carries an MPN-grade identity, a datasheet field,
   and usually a designated footprint):
   - Validate the datasheet link; harvest the **link** only (download the PDF
     only if validation needs it). If the part already exists and the datasheet
     changed, repoint it.
   - Pull parameters from Nexar (or extract from the datasheet).
   - Compute `part_locator` with the shared canonicalizer (below).
   - Upsert the row into the appropriate `db/tables/<type>/` SQL.
2. **Generic symbol** (`Device:*` and similar — no MPN, footprint by filter):
   - Hand to the datasheet-driven **value-space generator** for that type. The
     existing resistor/capacitor generators are the template: parametrics from
     the MPN, one series datasheet covering many values, KiCad-curated footprints.

Parameter harvest uses the Nexar free Evaluation tier (~1000 matched parts/month,
window closing ~Nov 2026). Run datasheet-first (cheap, ungated), Nexar-params
second (gated), prioritized against that window.

## `part_locator` canonicalization

`part_locator` is the substitutability/equivalence key. It **must** be a computed
canonical value, identical for interchangeable parts:

- Produce it from **one shared canonicalization function** used by *every*
  creation path — generators, the KiCad-seed pipeline, and CERN fold-ins. Never
  format the locator string per-generator, or equivalent parts from different
  sources land in different buckets.
- Derive it deterministically from **normalized** specs: canonical value
  magnitude (`100nF` ≡ `0.1µF`), canonical tolerance and ratings, and the
  **package** (so a 10k 0603 and a 10k 0805 never collide).
- Use a **per-component-type field set** — the fields that define
  interchangeability differ by type (dielectric for capacitors, temperature
  coefficient for precision resistors, etc.).

Alternates are then resolved on the cold path by a BOM/procurement tool reading
the database directly: `SELECT … WHERE part_locator = ? AND unique_id != ?`.

## Winding down CERN

CERN is a donor being retired (see [PLAN.md](PLAN.md)). Execute in order; do not
collapse steps 2 and 3.

1. **Fold in where helpful.** For a category, identify the CERN parts/footprints
   that fill a gap KiCad's shipped libraries don't already cover. Promote them
   into a curated native table following the `led_drivers` pattern, and durably
   exclude their MPNs from the CERN import via `tools/cern_promoted.py`.
2. **Exclude `cern_*` tables from the build** (reversible). Flip them out of the
   build, then confirm `make clean && make` and the full test suite stay green
   and that no native table references them.
3. **Delete the `cern_*` part-data tables.** Keep bespoke footprint/symbol assets
   still referenced by promoted native parts; remove only the SQL part-data.

## Footprint maintenance

`make normalize-footprints` runs a maintenance pass over copied CERN `.kicad_mod`
files: it sets the SMD/through-hole attribute and assigns KiCad 3D models with
alignment offsets. It **edits committed source files**, so it is a deliberate
target — *not* part of `make`/`make build`, which must never dirty the tree. It is
idempotent.

## Running the server as a service

`make serve` runs the server in the foreground (dev). To keep it running:

- **Login item (per-user, no sudo):** `make install-service MODE=user`
  (starts at login; `loginctl enable-linger $USER` to run without an active session).
- **Managed service (system-wide, boot):** `sudo make install-service MODE=system`.
- Status: `make service-status [MODE=user|system]`. Remove: `make uninstall-service MODE=…`.

`make install` does the lot: build + register terra into KiCad's global lib tables
(idempotent) + install the service in `MODE` (default `user`). Override port/tier with
`PORT=` / `TIER=`. Preview the unit without touching the system:
`uv run python tools/install_service.py install --mode user --dry-run`.
