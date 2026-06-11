#!/usr/bin/env python3
"""remigrate_native.py — rewrite legacy terra-native INSERT rows onto canonical schema.

Usage:
    python tools/remigrate_native.py <table> [<table> ...]

For each named table, reads db/tables/<table>/<table>_1_migrated.sql and rewrites it
in place so every INSERT references only columns present in the canonical schema
defined by db/tables/<table>/<table>_0_schema.sql.

Transforms applied per row:
  - number_of_pins  → pin_count
  - temp_operating  → temp_operating_min, temp_operating_max  (parsed from range string)
  - temp_storage    → temp_storage_min, temp_storage_max      (parsed from range string)
  - temp_soldering  → temp_soldering  (only if string parses as a single number)
  - All other legacy columns not in canonical schema are dropped
  - Placeholder junk values (empty, 'if applicable', 'na', 'n/a', 'tbd', 'none') are nulled
"""

import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Values that should be treated as absent (NULL) regardless of column
PLACEHOLDER_STRS = frozenset({"if applicable", "na", "n/a", "tbd", "none", ""})

# Legacy column name renames / splits
RENAME_MAP = {
    "number_of_pins": "pin_count",
}

# Legacy columns that split into two canonical columns
SPLIT_COLS = {
    "temp_operating": ("temp_operating_min", "temp_operating_max"),
    "temp_storage":   ("temp_storage_min",   "temp_storage_max"),
}


def parse_temp_range(s: str):
    """Extract (min, max) floats from a temperature range string.

    Handles formats:
        '-65C/150C', '-40C/+85C', '-55 to 125', '-55°C ~ 125°C', etc.

    Returns (min_float, max_float) if two numbers found; otherwise (None, None).
    """
    if not s or not s.strip():
        return (None, None)
    # Extract all signed numbers (integers or decimals), ignoring degree symbols
    nums = re.findall(r"[+-]?\d+(?:\.\d+)?", s)
    if len(nums) < 2:
        return (None, None)
    return (float(nums[0]), float(nums[1]))


def parse_single_temp(s: str):
    """Return a single float if s is a parseable number; else None."""
    if not s or not s.strip():
        return None
    nums = re.findall(r"[+-]?\d+(?:\.\d+)?", s.strip())
    if len(nums) == 1:
        return float(nums[0])
    return None


def is_placeholder(v) -> bool:
    """Return True if v is a None/NULL or a placeholder junk string."""
    if v is None:
        return True
    return str(v).strip().lower() in PLACEHOLDER_STRS


def canonical_cols(schema_path: Path) -> list:
    """Load schema SQL into in-memory sqlite and return ordered column names."""
    con = sqlite3.connect(":memory:")
    con.executescript(schema_path.read_text())
    table = schema_path.parent.name
    cols = [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]
    con.close()
    return cols


def canonical_not_null_no_default(schema_path: Path) -> set:
    """Return column names that are NOT NULL with no default (must be supplied)."""
    con = sqlite3.connect(":memory:")
    con.executescript(schema_path.read_text())
    table = schema_path.parent.name
    # PRAGMA table_info: cid|name|type|notnull|dflt_value|pk
    result = {
        r[1] for r in con.execute(f'PRAGMA table_info("{table}")')
        if r[3] == 1 and r[4] is None and r[5] == 0  # notnull, no default, not pk
    }
    con.close()
    return result


def parse_inserts(sql_text: str, table: str) -> list:
    """Parse each INSERT statement from sql_text into an ordered dict via sqlite.

    Uses sqlite itself to safely parse quoted/escaped values — no hand-rolled
    SQL value parser.

    Returns a list of dicts: [{col: value_or_None, ...}, ...] in statement order.
    """
    rows = []
    # Find all INSERT INTO <table> (...) VALUES (...); statements (possibly multiline)
    pattern = re.compile(
        rf"INSERT\s+INTO\s+(?:\"{re.escape(table)}\"|{re.escape(table)})\s*"
        r"\(([^)]+)\)\s*VALUES\s*\((.+?)\);",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(sql_text):
        col_str = m.group(1)
        # Parse column names (strip quotes)
        cols = [c.strip().strip('"').strip("'") for c in col_str.split(",")]
        full_stmt = m.group(0)

        # Create a temp table with all TEXT columns, load the row, read it back
        tmp_con = sqlite3.connect(":memory:")
        col_defs = ", ".join(f'"{c}" TEXT' for c in cols)
        tmp_con.execute(f'CREATE TABLE _legacy ({col_defs})')
        # Rewrite the INSERT to target _legacy
        rewritten = re.sub(
            rf"INSERT\s+INTO\s+(?:\"{re.escape(table)}\"|{re.escape(table)})",
            "INSERT INTO _legacy",
            full_stmt,
            count=1,
            flags=re.IGNORECASE,
        )
        tmp_con.executescript(rewritten)
        row_data = tmp_con.execute("SELECT * FROM _legacy").fetchone()
        tmp_con.close()

        row_dict = {col: val for col, val in zip(cols, row_data)}
        rows.append(row_dict)
    return rows


def _derive_from_unique_id(uid: str, col: str):
    """Attempt to derive mpn or manufacturer from unique_id (format: mfr-mpn[-variant]).

    Returns a string or None.  Only called as a last-resort fallback for NOT NULL columns
    that are genuinely absent from the legacy row.
    """
    if not uid:
        return None
    parts = uid.split("-", 1)
    if len(parts) < 2:
        return None
    if col == "manufacturer":
        return parts[0]
    if col == "mpn":
        return parts[1]
    return None


def build_canonical_row(legacy: dict, canon_set: set,
                        not_null_cols: set | None = None) -> dict:
    """Map a legacy row dict to a canonical row dict.

    canon_set: set of canonical column names (for quick lookup).
    Returns a dict with only non-null canonical columns.
    """
    result = {}

    # Process split columns first (temp_operating, temp_storage)
    for legacy_col, (min_col, max_col) in SPLIT_COLS.items():
        if legacy_col in legacy:
            v = legacy[legacy_col]
            if not is_placeholder(v):
                mn, mx = parse_temp_range(v)
                if mn is not None and min_col in canon_set:
                    result[min_col] = mn
                if mx is not None and max_col in canon_set:
                    result[max_col] = mx

    # temp_soldering: keep only if it's a single parseable number
    if "temp_soldering" in legacy:
        v = legacy["temp_soldering"]
        if not is_placeholder(v) and "temp_soldering" in canon_set:
            single = parse_single_temp(v)
            if single is not None:
                result["temp_soldering"] = single

    # Explicit renames
    for old, new in RENAME_MAP.items():
        if old in legacy and new in canon_set:
            v = legacy[old]
            if not is_placeholder(v):
                result[new] = v

    # All other columns: keep if in canonical schema, drop otherwise
    split_handled = set(SPLIT_COLS.keys()) | {"temp_soldering"}
    renamed_handled = set(RENAME_MAP.keys())
    skip = split_handled | renamed_handled

    for col, v in legacy.items():
        if col in skip:
            continue
        if col not in canon_set:
            continue  # drop legacy-only column
        if is_placeholder(v):
            continue  # null out placeholders
        result[col] = v

    # Last-resort fallback: NOT NULL columns with no default that ended up absent
    if not_null_cols:
        uid = result.get("unique_id") or legacy.get("unique_id")
        for col in not_null_cols:
            if col not in result:
                derived = _derive_from_unique_id(uid, col)
                if derived is not None:
                    print(f"  WARNING: {col!r} was NULL; derived {derived!r} from unique_id {uid!r}",
                          file=__import__("sys").stderr)
                    result[col] = derived

    return result


def quote_value(v) -> str:
    """Render a Python value as a SQL literal."""
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        # Render integers without decimal point
        if isinstance(v, float) and v == int(v):
            return str(int(v))
        return repr(v)
    # String: escape single quotes by doubling
    s = str(v)
    escaped = s.replace("'", "''")
    return f"'{escaped}'"


def emit_insert(table: str, row: dict, canon_cols: list) -> str:
    """Emit a canonical INSERT statement preserving column order."""
    # Use canonical column order (only those present in row)
    ordered_cols = [c for c in canon_cols if c in row]
    col_list = ", ".join(f'"{c}"' for c in ordered_cols)
    val_list = ", ".join(quote_value(row[c]) for c in ordered_cols)
    return f"INSERT INTO {table} ({col_list}) VALUES ({val_list});"


def rewrite_file(table: str) -> None:
    """Rewrite <table>_1_migrated.sql with canonical INSERT statements."""
    table_dir = ROOT / "db" / "tables" / table
    schema_path = table_dir / f"{table}_0_schema.sql"
    data_path = table_dir / f"{table}_1_migrated.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    canon_cols = canonical_cols(schema_path)
    canon_set = set(canon_cols)
    not_null_cols = canonical_not_null_no_default(schema_path)

    original = data_path.read_text()
    legacy_rows = parse_inserts(original, table)

    if not legacy_rows:
        print(f"[{table}] No INSERT statements found — nothing to rewrite.")
        return

    # Collect header lines (comment-only preamble before any DDL/DML)
    STOP_TOKENS = ("INSERT", "CREATE TABLE", "DROP TABLE", "BEGIN", "COMMIT", "ROLLBACK")
    header_lines = []
    in_header = True
    for line in original.splitlines():
        stripped = line.strip().upper()
        if in_header:
            if any(stripped.startswith(t) for t in STOP_TOKENS):
                in_header = False
            else:
                header_lines.append(line)
    # Remove trailing blank lines from header
    while header_lines and not header_lines[-1].strip():
        header_lines.pop()

    has_transaction = bool(re.search(r"^\s*BEGIN\s+TRANSACTION", original,
                                     re.IGNORECASE | re.MULTILINE))

    canonical_rows = [build_canonical_row(r, canon_set, not_null_cols) for r in legacy_rows]

    # Build output
    lines = []
    for h in header_lines:
        lines.append(h)
    lines.append("")

    if has_transaction:
        lines.append("BEGIN TRANSACTION;")
        lines.append("")

    for row in canonical_rows:
        lines.append(emit_insert(table, row, canon_cols))

    if has_transaction:
        lines.append("")
        lines.append("COMMIT;")

    lines.append("")
    output = "\n".join(lines)

    data_path.write_text(output)
    print(f"[{table}] Rewrote {len(canonical_rows)} row(s) → {data_path.relative_to(ROOT)}")


def main():
    if len(sys.argv) < 2:
        print("Usage: remigrate_native.py <table> [<table> ...]", file=sys.stderr)
        sys.exit(1)
    for table in sys.argv[1:]:
        try:
            rewrite_file(table)
        except Exception as exc:
            print(f"[{table}] ERROR: {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
