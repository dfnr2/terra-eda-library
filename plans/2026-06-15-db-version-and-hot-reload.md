# DB version stamp + server hot reload

**Goal:** Encode a build version in the DB and make the server pick up rebuilds
without a restart (dev hot reload).

## Why
- The DB carried no build/library version (`PRAGMA user_version` = 0, no meta
  table; `standards_version` is a per-row data field, not a build stamp).
- `make serve` read a one-time snapshot — a rebuild needed a manual restart.

## Pieces
1. **`tools/stamp_meta.py`** — writes a `terra_meta(key, value)` table into
   `db/terra.db` at the end of the master build: `version` (`git describe
   --tags --always --dirty`), `git_commit`, `built_at` (UTC ISO). Explicit
   values overridable for reproducible/test builds.
2. **Makefile** — stamp step at the tail of the `db/terra.db` recipe;
   `terra_meta` added to `generate_kicad_dbl_files.py` skip-list so it is not
   surfaced as a KiCad library.
3. **`terra_server.py` hot reload** — `create_app` still builds initial state
   eagerly (fail-fast on a bad DB/spec). Each request goes through a
   lock-guarded `session()` that re-stats `db`+`dbl` mtime and, on change,
   reconnects + rebuilds the id-map and re-reads `terra_meta`. Portable (no
   systemd/inotify), works on Windows. New `/v1/meta.json` exposes `terra_meta`.

## Tests
- `tests/test_stamp_meta.py` — stamp creates/overwrites; `git_version` non-empty.
- `tests/test_terra_server.py` — hot reload picks up an appended row after an
  mtime bump; `/v1/meta.json` returns `terra_meta`; empty dict when absent.
