#!/usr/bin/env python3
"""Shared CERN import generator for tables with no type-specific tail.

Connector vendors (and other grab-bag tables) all map the CERN core the same way
and carry no derived tail, so their per-table `run_100_cern_import.py` is a thin
call to `generate(...)` instead of a near-duplicate script.
"""
from __future__ import annotations

import re
from pathlib import Path

from tools import cern_source, cern_libmap

LIFECYCLE = {
    "": "Active", "obsolete": "Obsolete",
    "not recommended": "NRND", "sourcing difficulty": "NRND",
}

DENY_PATTERNS = [
    re.compile(r"read me", re.I),
    re.compile(r"drill-drawing", re.I),
    re.compile(r"^CERN_OHL", re.I),
    re.compile(r"^Empty$", re.I),
    re.compile(r"copyright", re.I),
]

INSERT_COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "source", "dump_priority",
    "tier", "keywords", "created_by", "pin_count", "component_height",
]


def sqlstr(v) -> str:
    s = "" if v is None else str(v)
    return "'" + s.replace("'", "''") + "'"


def clean(v) -> str:
    return "" if v is None else str(v).strip()


def map_lifecycle(status) -> str:
    return LIFECYCLE.get(clean(status).lower(), "Active")


def datasheet_hint(raw: str) -> str:
    return clean(raw).replace("\\", "/").split("/")[-1]


def http_or_blank(url) -> str:
    u = clean(url)
    return u if u.lower().startswith("http") else ""


def is_denylisted(row: dict) -> bool:
    blob = f"{clean(row.get('Part Number'))} {clean(row.get('Part Description'))}".strip()
    return any(p.search(blob) for p in DENY_PATTERNS)


def map_row(row: dict, tag: str, extra=None) -> dict:
    mfr = clean(row.get("Manufacturer"))
    mpn = clean(row.get("Manufacturer Part Number"))
    pnn = clean(row.get("Part Number Nocolon") or row.get("Part Number"))
    return {
        "unique_id": f"{mfr}-{mpn}",
        "part_locator": pnn,
        "mpn": mpn,
        "manufacturer": mfr,
        "package": clean(row.get("Case")),
        "value": clean(row.get("Part Description")),
        "description": clean(row.get("Part Description")),
        "datasheet": datasheet_hint(row.get("Datasheet")),
        "manufacturer_link": http_or_blank(row.get("ComponentLink1URL")),
        "kicad_symbol": cern_libmap.rewrite_ref(
            clean(row.get("LibSymbol")), cern_libmap.SYMBOL_LIB_NICK),
        "kicad_footprint": cern_libmap.rewrite_ref(
            clean(row.get("LibFootprint")), cern_libmap.FOOTPRINT_LIB_NICK),
        "lifecycle_status": map_lifecycle(row.get("Status")),
        "rohs": "no",
        "source": "cern_import",
        "dump_priority": 0,
        "tier": 5,
        "keywords": tag,
        "created_by": "cern_import",
        "pin_count": clean(row.get("Pin Count")),
        "component_height": clean(row.get("ComponentHeight")),
    }


def _augment(m: dict, row: dict, extra) -> dict:
    if extra:
        m.update(extra(row))
    return m


def _finalize_unique_id(m: dict, row: dict, seen: set) -> str:
    uid = m["unique_id"]
    if uid in seen:
        pnn = clean(row.get("Part Number Nocolon") or row.get("Part Number"))
        return f'{m["manufacturer"]}-{pnn}'
    return uid


def _sort_key(r: dict):
    pnn = clean(r.get("Part Number Nocolon") or r.get("Part Number"))
    mpn = clean(r.get("Manufacturer Part Number"))
    # Within an MPN collision group put the row whose PNN == MPN first so it wins
    # the bare mfr-mpn unique_id; variants (PNN != MPN) follow.
    return (mpn, pnn != mpn, pnn)


def _render(out_table: str, tag: str, mapped: list[dict], cols: list[str]) -> str:
    lines = ["BEGIN TRANSACTION;"]
    cols_sql = ", ".join(cols)
    for m in mapped:
        vals = [str(m[c]) if c in ("dump_priority", "tier") else sqlstr(m[c])
                for c in cols]
        lines.append(f"INSERT INTO {out_table} ({cols_sql}) VALUES ({', '.join(vals)});")
    for m in mapped:
        lines.append("INSERT INTO tags (unique_id, tag) VALUES "
                     f"({sqlstr(m['unique_id'])}, {sqlstr(tag)});")
    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"


def generate(cern_table: str, out_table: str, output_file: str, tag: str,
             extra_cols=None, extra=None) -> None:
    """Generate `output_file` (relative to cwd) from a CERN table.

    `extra_cols` / `extra` add a type-specific tail: extra_cols lists the column
    names; extra(row) returns a dict of their values for each row.
    """
    cols = INSERT_COLS + list(extra_cols or [])
    mapped, seen = [], set()
    for row in sorted(cern_source.rows(cern_table), key=_sort_key):
        if is_denylisted(row):
            continue
        m = _augment(map_row(row, tag), row, extra)
        m["unique_id"] = _finalize_unique_id(m, row, seen)
        if m["unique_id"] in seen:
            raise SystemExit(f"duplicate unique_id after fallback: {m['unique_id']}")
        seen.add(m["unique_id"])
        mapped.append(m)
    Path(output_file).write_text(_render(out_table, tag, mapped, cols))
    print(f"+ Wrote {output_file}: {len(mapped)} {out_table} parts")
