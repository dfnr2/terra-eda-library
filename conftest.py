"""Repo-wide pytest configuration."""

# The cern_* tables are retired from the build (see RETIRED_TABLES in the
# Makefile), so their per-table tests have nothing to build or query. The
# directories stay on disk as source material until they are deleted.
collect_ignore_glob = [
    "db/tables/cern_*/*",
    "tests/test_cern_connectors.py",
]
