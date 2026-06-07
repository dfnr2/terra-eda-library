"""Exact reconciliation of CERN parts against existing terra unique_ids."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable, Tuple

Key = Tuple[str, str]


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def index_from_rows(rows: Iterable[dict]) -> Dict[Key, str]:
    idx: Dict[Key, str] = {}
    for r in rows:
        mfr, mpn, uid = r.get("manufacturer"), r.get("mpn"), r.get("unique_id")
        if mfr and mpn and uid:
            idx[(_norm(mfr), _norm(mpn))] = uid
    return idx


def build_existing_index(db_glob_dir: Path) -> Dict[Key, str]:
    """Scan db/*.db (excluding cern_*.db) for (manufacturer,mpn)->unique_id."""
    idx: Dict[Key, str] = {}
    for db in sorted(Path(db_glob_dir).glob("*.db")):
        if db.name.startswith("cern_") or db.name == "terra.db":
            continue
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        try:
            for (tbl,) in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ):
                cols = {c[1] for c in con.execute(f'PRAGMA table_info("{tbl}")')}
                if {"manufacturer", "mpn", "unique_id"} <= cols:
                    idx.update(index_from_rows(
                        dict(r) for r in con.execute(
                            f'SELECT manufacturer, mpn, unique_id FROM "{tbl}"'
                        )
                    ))
        finally:
            con.close()
    return idx


def resolve_unique_id(manufacturer: str, mpn: str, index: Dict[Key, str]) -> str:
    hit = index.get((_norm(manufacturer), _norm(mpn)))
    return hit if hit else f"{manufacturer.strip()}-{mpn.strip()}"
