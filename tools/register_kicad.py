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


# (name, target table filename, lib line) — uri uses ${TERRA_EDA_LIB}, resolved by KiCad.
ENTRIES = [
    ("terra", "sym-lib-table",
     '(lib (name "terra")(type "HTTP")(uri "${TERRA_EDA_LIB}/terra.kicad_httplib")(options "")(descr "terra HTTP library"))'),
    ("terra-symbols", "sym-lib-table",
     '(lib (name "terra-symbols")(type "Table")(uri "${TERRA_EDA_LIB}/kicad_symbols/sym-lib-table")(options "")(descr "terra + cern symbols"))'),
    ("terra-footprints", "fp-lib-table",
     '(lib (name "terra-footprints")(type "Table")(uri "${TERRA_EDA_LIB}/kicad_footprints/fp-lib-table")(options "")(descr "terra + cern footprints"))'),
]


def kicad_config_dir(base: Path | None = None) -> Path:
    """Highest-versioned KiCad config dir under ``base`` (default ~/.config/kicad)."""
    base = base or (Path.home() / ".config" / "kicad")
    versions = [d for d in base.iterdir() if d.is_dir() and d.name[0].isdigit()]
    if not versions:
        raise FileNotFoundError(f"no KiCad config dir under {base}")
    return max(versions, key=lambda d: tuple(int(x) for x in d.name.split(".") if x.isdigit()))


def register(cfg: Path) -> list[str]:
    """Ensure terra entries in cfg's sym/fp tables. Returns names added (empty = no-op)."""
    added: list[str] = []
    for table in {e[1] for e in ENTRIES}:
        path = cfg / table
        if not path.exists():
            continue
        text = path.read_text()
        new = text
        table_added: list[str] = []
        for name, tbl, line in ENTRIES:
            if tbl != table:
                continue
            new, changed = ensure_lib_entry(new, name, line)
            if changed:
                table_added.append(name)
        if table_added:
            path.with_suffix(path.suffix + ".terra.bak").write_text(text)
            path.write_text(new)
            added += table_added
    return added


def main(argv=None) -> None:
    cfg = kicad_config_dir()
    added = register(cfg)
    print(f"registered into {cfg}: {added or 'nothing (already present)'}")


if __name__ == "__main__":
    main()
