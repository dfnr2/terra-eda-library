"""Locate and read the CERN KiCad library SQLite database (read-only)."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator, Dict, Any

# tools/cern_source.py -> parents[0]=tools, parents[1]=terra root, parents[2]=vsrc
_DEFAULT = Path(__file__).resolve().parents[2] / "cern-kicad-libs" / "CERN.sqlite"


def cern_db_path() -> Path:
    env = os.environ.get("CERN_SQLITE")
    return Path(env) if env else _DEFAULT


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
