"""HTTP library server exposing the Terra parts database to KiCad.

KiCad's HTTP library plugin fetches a category list and per-part objects over a
small REST surface. This module reads the parts SQLite database (read-only) and
the ``terra.kicad_dbl`` description file, then serves the four endpoints KiCad
expects. Stable part ids are derived from each row's ``unique_id`` so that the
ids KiCad caches remain valid across regenerations of the database.
"""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def part_id(unique_id: str) -> str:
    """Return a stable, URL-safe id: the first 16 hex chars of sha1(unique_id)."""
    return hashlib.sha1(unique_id.encode("utf-8")).hexdigest()[:16]


def sanitize(s: str) -> str:
    """Replace every character outside [A-Za-z0-9._-] with '_'.

    The allow-list is a subset of KiCad-legal LIB_ID characters; KiCad rejects
    '/', ':', and whitespace, so they are mapped to '_'.
    """
    return "".join(c if (c.isalnum() and c.isascii()) or c in "._-" else "_" for c in s)


def part_name(unique_id: str) -> str:
    """The KiCad symbol name: the sanitized unique_id.

    unique_id is globally unique and sanitizes to a name that is unique within
    every category, so it needs no disambiguating suffix. It already carries the
    manufacturer and the real part/variant identifier.
    """
    return sanitize(unique_id)


def load_spec(dbl_path: str | Path) -> list[dict]:
    """Parse a terra.kicad_dbl JSON file into a list of per-library spec dicts."""
    with open(dbl_path, encoding="utf-8") as fh:
        data = json.load(fh)

    specs = []
    for lib in data["libraries"]:
        table = lib["table"]
        base = table[:-2] if table.endswith("_v") else table
        symbols = lib["symbols"]
        footprints = lib["footprints"]

        field_cols = [
            f["column"] for f in lib["fields"] if f["column"] not in (symbols, footprints)
        ]

        # Optional description column, surfaced in the category listing so KiCad
        # shows a meaningful description in the chooser.
        desc_col = "description" if "description" in field_cols else None

        specs.append(
            {
                "category_id": base,
                "name": lib["name"],
                "base_table": base,
                "key": lib["key"],
                "symbols": symbols,
                "footprints": footprints,
                "desc_col": desc_col,
                "fields": lib["fields"],
            }
        )
    return specs


def build_id_map(conn: sqlite3.Connection, specs: list[dict]) -> dict[str, tuple[str, str]]:
    """Map every part's stable id to its (base_table, unique_id) pair.

    Iterates every row of every base table with no tier filter, validating that
    keys are present and that ids are globally unique.
    """
    id_map: dict[str, tuple[str, str]] = {}
    seen_uids: set[str] = set()
    for spec in specs:
        table = spec["base_table"]
        key = spec["key"]
        for row in conn.execute(f"SELECT * FROM {table}"):
            uid = row[key]
            if uid is None:
                raise ValueError(f"null {key} in {table}")
            if uid in seen_uids:
                raise ValueError(f"duplicate unique_id across tables: {uid}")
            seen_uids.add(uid)

            pid = part_id(uid)
            if pid in id_map:
                raise ValueError(f"hash collision for unique_id {uid}")
            id_map[pid] = (table, uid)
    return id_map


def assert_unique_names(conn, specs) -> None:
    """Fail loudly if sanitize(unique_id) is not unique within a category.

    Names are the LIB_ID handle KiCad keys on; a collision would silently shadow
    a part. unique_id is globally unique, so this only trips if two unique_ids
    sanitize to the same string within one table.
    """
    for spec in specs:
        seen = {}
        for (uid,) in conn.execute(f'SELECT "{spec["key"]}" FROM "{spec["base_table"]}"'):
            nm = part_name(uid)
            if nm in seen:
                raise ValueError(
                    f"name collision in {spec['base_table']}: {uid!r} and {seen[nm]!r} -> {nm!r}"
                )
            seen[nm] = uid


def serialize_part(row, spec, pid: str) -> dict:
    """Build the KiCad HTTP part object for a single database row.

    All boolean-valued members are emitted as the strings "true"/"false"
    because KiCad's HTTP library parser expects string booleans, not JSON
    booleans.
    """
    fields: dict[str, dict] = {}

    # Footprint is a member of fields, never a top-level key. The fields loop
    # below skips the symbol and footprint columns so this canonical entry is
    # not clobbered by a re-emitted "Footprint" field.
    footprint = row[spec["footprints"]]
    if footprint:
        fields["footprint"] = {"value": str(footprint), "visible": "true"}

    for field in spec["fields"]:
        column = field["column"]
        if column in (spec["symbols"], spec["footprints"]):
            continue
        value = row[column]
        if value is None or value == "":
            continue
        fields[field["name"]] = {
            "value": str(value),
            "visible": "true" if field.get("visible_in_chooser") else "false",
        }

    return {
        "id": pid,
        "name": part_name(row[spec["key"]]),
        "symbolIdStr": str(row[spec["symbols"]] or ""),
        "exclude_from_bom": "false",
        "exclude_from_board": "false",
        "exclude_from_sim": "false",
        "fields": fields,
    }


def create_app(db_path: str, dbl_path: str, tier: int = 2):
    """Build and return the FastAPI app serving the KiCad HTTP library API."""
    from fastapi import FastAPI, HTTPException

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    specs = load_spec(dbl_path)
    id_map = build_id_map(conn, specs)
    assert_unique_names(conn, specs)
    specs_by_category = {spec["category_id"]: spec for spec in specs}

    app = FastAPI()

    @app.get("/v1/")
    def root():
        # Both values must be non-empty strings; KiCad checks !.empty().
        return {"categories": "v1/categories.json", "parts": "v1/parts"}

    @app.get("/v1/categories.json")
    def categories():
        return [
            {"id": spec["category_id"], "name": spec["name"], "description": ""}
            for spec in specs
        ]

    @app.get("/v1/parts/category/{category}.json")
    def parts_in_category(category: str):
        spec = specs_by_category.get(category)
        if spec is None:
            raise HTTPException(status_code=404, detail="category not found")
        # The tier cutoff applies only here, when listing a category's parts.
        rows = conn.execute(
            f"SELECT * FROM {spec['base_table']} WHERE tier <= ?", (tier,)
        )
        result = []
        for row in rows:
            uid = row[spec["key"]]
            pid = part_id(uid)
            entry = {"id": pid, "name": part_name(uid)}
            if spec["desc_col"]:
                desc = row[spec["desc_col"]]
                if desc:
                    entry["description"] = str(desc)
            result.append(entry)
        return result

    @app.get("/v1/parts/{pid}.json")
    def part_detail(pid: str):
        entry = id_map.get(pid)
        if entry is None:
            raise HTTPException(status_code=404, detail="part not found")
        table, uid = entry
        spec = specs_by_category[table]
        # Tier-agnostic: any known part id resolves regardless of tier.
        row = conn.execute(
            f"SELECT * FROM {table} WHERE {spec['key']} = ?", (uid,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="part not found")
        return serialize_part(row, spec, pid)

    return app


def main() -> None:
    """Parse command-line arguments and run the server with uvicorn."""
    parser = argparse.ArgumentParser(description="Serve the Terra parts DB to KiCad over HTTP.")
    parser.add_argument("--db", default="db/terra.db")
    parser.add_argument("--dbl", default="terra.kicad_dbl")
    parser.add_argument("--tier", type=int, default=2)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8361)
    args = parser.parse_args()

    import uvicorn

    app = create_app(args.db, args.dbl, tier=args.tier)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
