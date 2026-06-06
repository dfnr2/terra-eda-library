"""Build a required-datasheets manifest from CERN rows (keyed by filename)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from tools import cern_source  # noqa: E402

MANIFEST = _ROOT / "assets/datasheets/cern/manifest.json"


def _filename(raw) -> str:
    return ("" if raw is None else str(raw)).replace("\\", "/").split("/")[-1].strip()


def build(rows) -> dict:
    man: dict = {}
    for r in rows:
        fn = _filename(r.get("Datasheet"))
        if not fn or fn.lower() == "none":
            continue
        entry = man.setdefault(fn, {
            "filename": fn, "mpns": [], "manufacturer": r.get("Manufacturer"),
            "status": "pending", "source_url": "", "local_path": "",
            "verify": "unchecked",
        })
        mpn = r.get("Manufacturer Part Number")
        if mpn and mpn not in entry["mpns"]:
            entry["mpns"].append(mpn)
    return man


def main(table: str = "Diodes") -> None:
    man = build(cern_source.rows(table))
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(man, indent=2, sort_keys=True))
    print(f"+ {MANIFEST}: {len(man)} unique datasheets for {table}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Diodes")
