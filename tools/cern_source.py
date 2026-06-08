"""Locate and read the CERN KiCad library SQLite database (read-only)."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator, Dict, Any

# tools/cern_source.py -> parents[0]=tools, parents[1]=terra root, parents[2]=vsrc
_ROOT = Path(__file__).resolve().parents[1]
# Preferred: a clone of cern-kicad-libs vendored in-tree (gitignored), so the
# import is self-contained and needs no sibling layout or env var.
_VENDOR = _ROOT / "vendor" / "cern-kicad-libs" / "CERN.sqlite"
# Backward-compat fallback: cern-kicad-libs as a sibling of the terra repo.
_SIBLING = _ROOT.parent / "cern-kicad-libs" / "CERN.sqlite"


def cern_db_path() -> Path:
    """CERN.sqlite location: $CERN_SQLITE, else the vendored clone, else sibling."""
    env = os.environ.get("CERN_SQLITE")
    if env:
        return Path(env)
    return _VENDOR if _VENDOR.exists() else _SIBLING


def connect() -> sqlite3.Connection:
    path = cern_db_path()
    if not path.exists():
        raise FileNotFoundError(
            f"CERN.sqlite not found at {path}; set CERN_SQLITE to override."
        )
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def rows(table: str) -> Iterator[Dict[str, Any]]:
    con = connect()
    try:
        for r in con.execute(f'SELECT * FROM "{table}"'):
            yield dict(r)
    finally:
        con.close()
