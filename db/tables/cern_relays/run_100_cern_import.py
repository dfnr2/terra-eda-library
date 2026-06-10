#!/usr/bin/env python3
# db/tables/cern_relays/run_100_cern_import.py
"""Import CERN 'Relays' -> cern_relays_generated_100_cern_import.sql."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Make repo root importable (for tools.*) when run via Makefile (cwd = table dir)
_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))

from tools import cern_source, cern_libmap  # noqa: E402

CERN_TABLE = "Relays"
OUTPUT_FILE = "cern_relays_generated_100_cern_import.sql"

# The Relays table also carries 'Discontinued'/'Recommended'/'None' statuses not
# seen in earlier CERN tables; Discontinued maps to Obsolete, the rest to Active.
LIFECYCLE = {
    "": "Active", "none": "Active", "recommended": "Active",
    "obsolete": "Obsolete", "discontinued": "Obsolete",
    "not recommended": "NRND", "sourcing difficulty": "NRND",
}

DENY_PATTERNS = [
    re.compile(r"read me", re.I),
    re.compile(r"drill-drawing", re.I),
    re.compile(r"^CERN_OHL", re.I),
    re.compile(r"^Empty$", re.I),
    re.compile(r"copyright", re.I),
]

# Real parts whose LibSymbol AND LibFootprint were never created in the upstream
# CERN repo (no file/symbol anywhere in SchLib/PcbLib, and no same-geometry
# equivalent to fix up via cern_libmap.ITEM_FIXUP). Excluded rather than given a
# wrong footprint; keyed by Part Number Nocolon. See AUDIT.md.
EXCLUDE_MISSING_ASSETS = {
    "REL_FINDER_56.32.9.012.0040",  # FINDER 56.32 relay - no symbol/footprint upstream
    "RELS_FINDER_96.12",            # FINDER 96.12 socket - no symbol/footprint upstream
}

INSERT_COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "source", "dump_priority",
    "tier", "tags", "created_by", "pin_count", "component_height",
    "relay_kind", "coil_voltage",
]


def sqlstr(v) -> str:
    s = "" if v is None else str(v)
    return "'" + s.replace("'", "''") + "'"


def clean(v) -> str:
    return "" if v is None else str(v).strip()


def map_lifecycle(status) -> str:
    return LIFECYCLE.get(clean(status).lower(), "Active")


def relay_kind_from_symbol(libsymbol: str) -> str:
    """'Relay' | 'Socket' from the CERN symbol-name prefix.

    Relay symbols are 'REL_<MFR>_<SERIES>'; socket symbols are 'RELS_*',
    'RELS NoPin', or 'SOCKET NoPin' (the Sockets-lib generic). Deterministic for
    every row in the CERN Relays table.
    """
    name = libsymbol.split(":", 1)[1] if ":" in libsymbol else libsymbol
    if name.startswith(("RELS", "SOCKET")):
        return "Socket"
    if name.startswith("REL_"):
        return "Relay"
    return ""


def datasheet_hint(raw: str) -> str:
    return clean(raw).replace("\\", "/").split("/")[-1]


def http_or_blank(url) -> str:
    u = clean(url)
    return u if u.lower().startswith("http") else ""


def is_denylisted(row: dict) -> bool:
    blob = f"{clean(row.get('Part Number'))} {clean(row.get('Part Description'))}".strip()
    return any(p.search(blob) for p in DENY_PATTERNS)


def map_row(row: dict) -> dict:
    mfr = clean(row.get("Manufacturer"))
    mpn = clean(row.get("Manufacturer Part Number"))
    pnn = clean(row.get("Part Number Nocolon") or row.get("Part Number"))
    # CERN puts the coil voltage in Value (e.g. '24VDC', '230VAC'); the blank-
    # Value rows are sockets/accessories, which have no coil.
    coil = clean(row.get("Value"))
    return {
        "unique_id": f"{mfr}-{mpn}",
        "part_locator": pnn,
        "mpn": mpn,
        "manufacturer": mfr,
        "package": clean(row.get("Case")),
        "value": coil or clean(row.get("Part Description")),
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
        "tags": "relay",
        "created_by": "cern_import",
        "pin_count": clean(row.get("Pin Count")),
        "component_height": clean(row.get("ComponentHeight")),
        "relay_kind": relay_kind_from_symbol(clean(row.get("LibSymbol"))),
        "coil_voltage": coil,
    }


def finalize_unique_id(m: dict, row: dict, seen: set) -> str:
    uid = m["unique_id"]
    if uid in seen:
        pnn = clean(row.get("Part Number Nocolon") or row.get("Part Number"))
        return f'{m["manufacturer"]}-{pnn}'
    return uid


def render(mapped: list[dict]) -> str:
    lines = ["BEGIN TRANSACTION;"]
    cols_sql = ", ".join(INSERT_COLS)
    for m in mapped:
        vals = []
        for c in INSERT_COLS:
            v = m[c]
            vals.append(str(v) if c in ("dump_priority", "tier") else sqlstr(v))
        lines.append(
            f"INSERT INTO cern_relays ({cols_sql}) VALUES ({', '.join(vals)});")
    for m in mapped:
        lines.append(
            "INSERT INTO tags (unique_id, tag) VALUES "
            f"({sqlstr(m['unique_id'])}, 'relay');")
    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"


def main() -> None:
    mapped, seen = [], set()
    def _sort_key(r):
        pnn = clean(r.get("Part Number Nocolon") or r.get("Part Number"))
        mpn = clean(r.get("Manufacturer Part Number"))
        # Within an MPN collision group put the row whose PNN == MPN first so it
        # wins the bare mfr-mpn unique_id; variants (PNN != MPN) follow.
        return (mpn, pnn != mpn, pnn)

    rows = sorted(cern_source.rows(CERN_TABLE), key=_sort_key)
    for row in rows:
        if is_denylisted(row):
            continue
        pnn = clean(row.get("Part Number Nocolon") or row.get("Part Number"))
        if pnn in EXCLUDE_MISSING_ASSETS:
            continue
        m = map_row(row)
        m["unique_id"] = finalize_unique_id(m, row, seen)
        if m["unique_id"] in seen:
            raise SystemExit(f"duplicate unique_id after fallback: {m['unique_id']}")
        seen.add(m["unique_id"])
        mapped.append(m)
    Path(OUTPUT_FILE).write_text(render(mapped))
    print(f"+ Wrote {OUTPUT_FILE}: {len(mapped)} cern_relays parts")


if __name__ == "__main__":
    main()
