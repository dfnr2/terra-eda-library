#!/usr/bin/env python3
# db/tables/cern_diodes/run_100_cern_import.py
"""Import CERN 'Diodes' -> cern_diodes_generated_100_cern_import.sql."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Make repo root importable (for tools.*) when run via Makefile (cwd = table dir)
_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))

from tools import cern_source, cern_libmap, cern_reconcile  # noqa: E402

CERN_TABLE = "Diodes"
OUTPUT_FILE = "cern_diodes_generated_100_cern_import.sql"

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
    "tier", "tags", "created_by", "pin_count", "component_height",
    "diode_type", "voltage_rating", "power_rating",
]


def sqlstr(v) -> str:
    s = "" if v is None else str(v)
    return "'" + s.replace("'", "''") + "'"


def clean(v) -> str:
    return "" if v is None else str(v).strip()


def map_lifecycle(status) -> str:
    return LIFECYCLE.get(clean(status).lower(), "Active")


def diode_type_from_symbol(libsymbol: str) -> str:
    name = libsymbol.split(":", 1)[1] if ":" in libsymbol else libsymbol
    return re.sub(r"^Diode\s+", "", name).strip()


def datasheet_hint(raw: str) -> str:
    return clean(raw).replace("\\", "/").split("/")[-1]


def http_or_blank(url) -> str:
    u = clean(url)
    return u if u.lower().startswith("http") else ""


def is_denylisted(row: dict) -> bool:
    blob = f"{clean(row.get('Part Number'))} {clean(row.get('Part Description'))}".strip()
    return any(p.search(blob) for p in DENY_PATTERNS)


def map_row(row: dict, existing_index: dict) -> dict:
    mfr = clean(row.get("Manufacturer"))
    mpn = clean(row.get("Manufacturer Part Number"))
    # Use Part Number Nocolon as the uniqueness key so [alt] entries are distinct;
    # fall back to Part Number when the field is absent (e.g. unit-test fixtures).
    uid_key = clean(row.get("Part Number Nocolon") or row.get("Part Number"))
    return {
        "unique_id": cern_reconcile.resolve_unique_id(mfr, uid_key, existing_index),
        "part_locator": clean(row.get("Part Number")),
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
        "tags": "diode",
        "created_by": "cern_import",
        "pin_count": clean(row.get("Pin Count")),
        "component_height": clean(row.get("ComponentHeight")),
        "diode_type": diode_type_from_symbol(clean(row.get("LibSymbol"))),
        "voltage_rating": clean(row.get("Voltage")),
        "power_rating": clean(row.get("Power")),
    }


def render(mapped: list[dict]) -> str:
    lines = ["BEGIN TRANSACTION;"]
    cols_sql = ", ".join(INSERT_COLS)
    for m in mapped:
        vals = []
        for c in INSERT_COLS:
            v = m[c]
            vals.append(str(v) if c in ("dump_priority", "tier") else sqlstr(v))
        lines.append(
            f"INSERT INTO cern_diodes ({cols_sql}) VALUES ({', '.join(vals)});")
    for m in mapped:
        lines.append(
            "INSERT INTO tags (unique_id, tag) VALUES "
            f"({sqlstr(m['unique_id'])}, 'diode');")
    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"


def main() -> None:
    index = cern_reconcile.build_existing_index(_ROOT / "db")
    mapped = []
    for row in cern_source.rows(CERN_TABLE):
        if is_denylisted(row):
            continue
        mapped.append(map_row(row, index))
    Path(OUTPUT_FILE).write_text(render(mapped))
    print(f"+ Wrote {OUTPUT_FILE}: {len(mapped)} cern_diodes parts")


if __name__ == "__main__":
    main()
