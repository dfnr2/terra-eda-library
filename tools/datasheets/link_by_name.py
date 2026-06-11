#!/usr/bin/env python3
"""Build a human-browsable view of the content-addressed datasheet store.

Storage is content-addressed (`files/<sha256>.pdf`) for dedup + integrity, which is
opaque to humans. This reads the acquisition log and (re)creates a `by-name/`
directory of symlinks named by the real datasheet filename, each pointing at its
content-addressed file. Browse `by-name/` to see datasheets by name; the symlinks are
gitignored and fully regenerable from the log.

  by-name/1.5KE.pdf -> ../files/<sha256>.pdf
  by-name/_quarantine/<name>.pdf -> ../../quarantine/<sha256>.pdf

Usage: python3 tools/datasheets/link_by_name.py
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "assets/datasheets/acquisition.jsonl"
BYNAME = ROOT / "assets/datasheets/by-name"
QDIR = BYNAME / "_quarantine"


def sanitize(name: str) -> str:
    return name.replace("/", "_").strip()


def rebuild() -> None:
    # wipe existing symlinks (rebuild from scratch — deterministic)
    for d in (BYNAME, QDIR):
        if d.exists():
            for f in d.glob("*"):
                if f.is_symlink():
                    f.unlink()
    BYNAME.mkdir(parents=True, exist_ok=True)
    QDIR.mkdir(parents=True, exist_ok=True)

    records = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()] if LOG.exists() else []
    ok = quar = 0
    for r in records:
        h, st = r.get("sha256"), r.get("status")
        if not h:
            continue
        name = sanitize(r["filename"])
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        if st == "ok":
            link = BYNAME / name
            target = Path("..") / "files" / f"{h}.pdf"
            ok += 1
        elif st == "quarantine":
            link = QDIR / name
            target = Path("..") / ".." / "quarantine" / f"{h}.pdf"
            quar += 1
        else:
            continue
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(target)
    print(f"by-name/: {ok} ok symlinks, {quar} quarantine symlinks "
          f"(browse {BYNAME.relative_to(ROOT)})")


if __name__ == "__main__":
    rebuild()
