#!/usr/bin/env python3
"""Generate each part table's _0_schema.sql from the shared core + per-type fragment.

Reads db/schema/core.sql, db/schema/types/<type>.sql, db/schema/table_map.json.
Emits `CREATE TABLE <table> ( <core>, <type-fragment> );` to
db/tables/<table>/<table>_0_schema.sql (or stdout with --print <table>).
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "db/schema/core.sql"
TYPES = ROOT / "db/schema/types"
MAP = ROOT / "db/schema/table_map.json"


def _lines(text: str) -> list[str]:
    return [l.rstrip() for l in text.splitlines()
            if l.strip() and not l.strip().startswith("--")]


def render(table: str, cfg: dict) -> str:
    # Output is identical for --print and file writes so the drift guard
    # (tools/gen_schema.py --print <t> == committed _0_schema.sql) holds. No
    # header/footer — the drift test itself is what enforces "do not hand-edit".
    out = []
    for l in _lines(CORE.read_text()):
        s = l.strip().rstrip(",")
        if s.startswith("tier INTEGER"):
            l = f"    tier INTEGER DEFAULT {cfg['tier_default']}"
        elif s.startswith("dump_priority INTEGER"):
            l = f"    dump_priority INTEGER DEFAULT {cfg['dump_priority_default']}"
        elif s.startswith("sim_device TEXT") and cfg.get("sim_device"):
            l = f"    sim_device TEXT DEFAULT '{cfg['sim_device']}'"
        elif s.startswith("sim_pins TEXT") and cfg.get("sim_pins"):
            l = f"    sim_pins TEXT DEFAULT '{cfg['sim_pins']}'"
        out.append(l.rstrip(","))
    frag = _lines((TYPES / f"{cfg['type']}.sql").read_text())
    cols = [c.rstrip(",") for c in out + frag]
    body = ",\n".join(cols)
    return f"CREATE TABLE {table} (\n{body}\n);\n"


def main() -> None:
    table_map = json.loads(MAP.read_text())
    args = sys.argv[1:]
    if args and args[0] == "--print":
        sys.stdout.write(render(args[1], table_map[args[1]]))
        return
    for table in (args or list(table_map)):
        cfg = table_map[table]
        dest = ROOT / f"db/tables/{table}/{table}_0_schema.sql"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(table, cfg))
        print(f"  wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
