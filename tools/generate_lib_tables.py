#!/usr/bin/env python3
"""Generate terra's symbol and footprint lib-tables from the owned hierarchy.

Registration is an OUTPUT of the build, never hand-maintained: this scans
``kicad_symbols/*.kicad_sym`` and ``kicad_footprints/*.pretty`` and writes a
standard KiCad lib-table into each directory. Each entry's nickname is the lib
filename stem; URIs are ``${TERRA_EDA_LIB}``-relative (KiCad expands path vars in
lib-table URIs).

Include them from a global/project table with one ``(type "Table")`` entry, e.g.::

    (lib (name "terra_symbols")(type "Table")
         (uri "${TERRA_EDA_LIB}/kicad_symbols/sym-lib-table")(options "")(descr ""))
    (lib (name "terra_footprints")(type "Table")
         (uri "${TERRA_EDA_LIB}/kicad_footprints/fp-lib-table")(options "")(descr ""))
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate(dir_rel: str, pattern: str, table_tag: str, out_name: str) -> None:
    d = ROOT / dir_rel
    libs = sorted(p for p in d.glob(pattern))
    lines = [f"({table_tag}", "  (version 7)"]
    for p in libs:
        nick = p.name[: -len(p.suffix)] if p.suffix else p.name  # strip .kicad_sym/.pretty
        uri = f"${{TERRA_EDA_LIB}}/{dir_rel}/{p.name}"
        lines.append(
            f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr ""))'
        )
    lines.append(")")
    (d / out_name).write_text("\n".join(lines) + "\n")
    print(f"+ {dir_rel}/{out_name}: {len(libs)} libraries")


def main() -> None:
    generate("kicad_symbols", "*.kicad_sym", "sym_lib_table", "sym-lib-table")
    generate("kicad_footprints", "*.pretty", "fp_lib_table", "fp-lib-table")


if __name__ == "__main__":
    main()
