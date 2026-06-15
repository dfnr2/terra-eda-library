"""Idempotently register terra's libraries into KiCad's global lib tables."""
from __future__ import annotations

from pathlib import Path


def ensure_lib_entry(table_text: str, name: str, line: str) -> tuple[str, bool]:
    """Insert ``line`` before the table's final ')' if no lib named ``name`` exists.

    Returns (new_text, changed). Idempotent: a second call with the same name is a no-op.
    """
    if f'(name "{name}")' in table_text:
        return table_text, False
    close = table_text.rstrip().rfind(")")
    if close < 0:
        raise ValueError("not a lib table (no closing paren)")
    return table_text[:close] + "  " + line + "\n" + table_text[close:], True
