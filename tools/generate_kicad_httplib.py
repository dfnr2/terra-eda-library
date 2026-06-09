#!/usr/bin/env python3
"""Write the terra.kicad_httplib connection file (KiCad HTTP Library v1)."""
import json
import sys
from pathlib import Path


def build_httplib(root_url: str = "http://127.0.0.1:8361/") -> dict:
    return {
        "meta": {"version": 1.0},
        "name": "Terra EDA Library",
        "source": {
            "type": "REST_API",
            "api_version": "v1",
            "root_url": root_url,
            "token": "",
            "timeout_parts_seconds": 3600,
            "timeout_categories_seconds": 86400,
        },
    }


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("terra.kicad_httplib")
    out.write_text(json.dumps(build_httplib(), indent=2) + "\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
