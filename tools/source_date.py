#!/usr/bin/env python3
"""Print the 'Updated On' date (YYYY-MM-DD) for the parts a SQL file loads.

The date is stable across rebuilds, so a rebuild with no changes leaves every part's
symbol fields identical and KiCad's ERC does not report "symbol doesn't match library".

- Static SQL (tracked): the date of the last commit that touched the file.
- Generated SQL (`<table>_generated_NNN_<name>.sql`): the latest commit date among the
  generator `run_NNN_<name>.py` and the helper and data files beside it (`_*.py`,
  `*.json`, `*.csv`).
- A source with uncommitted changes gets today's date, so a part being edited shows as
  updated until the change is committed.
"""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _git(*args):
    try:
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def sources_for(sql_file):
    """Files whose content determines the rows in `sql_file`."""
    p = Path(sql_file).resolve()
    m = re.match(r"^(?P<table>.+?)_generated_(?P<num>\d+)_(?P<name>.+)\.sql$", p.name)
    if not m:
        return [p]
    gen = p.with_name(f"run_{m['num']}_{m['name']}.py")
    helpers = [*p.parent.glob("_*.py"), *p.parent.glob("*.json"), *p.parent.glob("*.csv")]
    return [gen, *helpers] if gen.exists() else helpers or [p]


def updated_on(sql_file):
    rels = [str(s.relative_to(ROOT)) for s in sources_for(sql_file) if s.exists()]
    today = date.today().isoformat()
    if not rels:
        return today
    if _git("status", "--porcelain", "--", *rels):
        return today
    return _git("log", "-1", "--format=%cs", "--", *rels) or today


if __name__ == "__main__":
    print(updated_on(sys.argv[1]))
