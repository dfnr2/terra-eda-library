#!/usr/bin/env python3
# db/tables/cern_phoenix/run_100_cern_import.py
"""Import CERN 'PHOENIX' -> cern_phoenix_generated_100_cern_import.sql (shared generator)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cern_import import generate  # noqa: E402

generate("PHOENIX", "cern_phoenix", "cern_phoenix_generated_100_cern_import.sql", "connector")
