# CERN → Terra Importer (cern_diodes pilot) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import all 962 real CERN `Diodes` parts into a new terra `cern_diodes` table — mirroring CERN 1:1 — with correct field mapping, exact `unique_id` reconciliation against existing terra parts, copied-and-registered CERN symbol/footprint libraries, and a decoupled datasheet acquisition/verification subsystem.

**Architecture:** Reuse terra's per-table generator machinery. A shared `tools/cern_source.py` reads `../cern-kicad-libs/CERN.sqlite` (read-only). A per-table generator emits `cern_diodes_generated_100_cern_import.sql` (`dump_priority=0`, gitignored); the Makefile auto-discovers `db/tables/cern_diodes/`, builds `db/cern_diodes.db`, the `cern_diodes_v` view, and the `.kicad_dbl` entry. Datasheets are a separate manifest-driven fetch+parse-verify subsystem that never blocks the import.

**Tech Stack:** Python 3 (stdlib `sqlite3`, `pathlib`, `json`), SQLite, GNU Make, pytest, Git LFS, KiCad `.kicad_sym`/`.pretty`/lib-tables. `uv` for env/deps.

**Spec:** `docs/superpowers/specs/2026-06-06-cern-diodes-importer-design.md`

**Conventions used throughout:**
- All `python`/`pytest` invocations go through `uv run` to use terra's venv.
- Table dir: `db/tables/cern_diodes/`. Generated SQL is gitignored by the existing `db/tables/*/*_generated_*.sql` rule.
- Known reference part for assertions: CERN `Diodes` row where `Manufacturer Part Number = '0402ESDA-MLP'`:
  `Manufacturer='EATON'`, `Voltage='8kV'`, `Power=None`, `Pin Count='2'`, `Case='0402'`, `ComponentHeight='0.44mm'`, `Status=None`, `LibSymbol='Diodes:Diode TVS Bi-Directional'`, `LibFootprint='ICs And Semiconductors SMD:EATON_0402ESDA-MLP'`, `Part Description='0.05pF 8kV Bidirectional ESD Voltage Suppressor'`, `Datasheet='${CERN_DATASHEET_DIR}\\0402ESDA-MLP.pdf'`.

---

## File Structure

| File | Responsibility |
|---|---|
| `tools/cern_source.py` | Locate + open `CERN.sqlite` read-only; yield table rows as dicts. |
| `tools/cern_libmap.py` | Canonical CERN→terra library-nickname map + `rewrite_ref()`. Shared by generator and lib registration. |
| `tools/cern_reconcile.py` | Build index of existing terra `(manufacturer,mpn)→unique_id`; `resolve_unique_id()`. |
| `tools/cern_datasheets/build_manifest.py` | Build `manifest.json` of required datasheets from a CERN table. |
| `tools/cern_datasheets/verify.py` | Parse a datasheet's text and confirm MPN + CERN params (exact). |
| `tools/cern_datasheets/fetch.py` | Resumable web fetch driven by the manifest (run-time tool). |
| `tools/cern_datasheets/rewrite_datasheets.py` | Rewrite `datasheet` column to local asset path for verified parts. |
| `db/tables/cern_diodes/cern_diodes_0_schema.sql` | `cern_diodes` schema (core + adopted + diode tail). |
| `db/tables/cern_diodes/run_100_cern_import.py` | The importer/generator. |
| `db/tables/cern_diodes/test_cern_diodes.py` | Automated exact mapping test (builds db, asserts). |
| `db/tables/cern_diodes/AUDIT.md` | Human audit checklist + sign-off. |
| `assets/symbols/cern/Diodes.kicad_sym` | Copied CERN diode symbols. |
| `assets/footprints/cern/ICs And Semiconductors {SMD,THD,BONDING}.pretty` | Copied CERN footprints. |
| `kicad_config_templates/{sym,fp}-lib-table` | Add `cern_`-prefixed library entries. |
| `tests/` (repo root) | Tests for shared `tools/*` modules. |
| `.gitattributes` | Add Git LFS rule for `*.pdf`. |

---

## Task 1: Dev tooling — pytest + package skeleton

**Files:**
- Modify: `pyproject.toml` (dev dependency)
- Create: `tests/__init__.py`, `tools/cern_datasheets/__init__.py`

- [ ] **Step 1: Add pytest to the dev environment**

Run:
```bash
cd /users/dave/vsrc/terra-eda-library
uv add --dev pytest
```
Expected: `pyproject.toml` gains a `[dependency-groups]`/dev `pytest` entry; `uv.lock` updates.

- [ ] **Step 2: Verify pytest runs**

Run: `uv run pytest --version`
Expected: prints `pytest 8.x` (a version string), exit 0.

- [ ] **Step 3: Create test/package dirs**

```bash
mkdir -p tests tools/cern_datasheets
touch tests/__init__.py tools/cern_datasheets/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock tests/__init__.py tools/cern_datasheets/__init__.py
git commit -m "add pytest dev dependency and test/package skeleton"
```

---

## Task 2: Shared CERN source helper

**Files:**
- Create: `tools/cern_source.py`
- Test: `tests/test_cern_source.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cern_source.py
import os
import pytest
from tools import cern_source


def test_default_path_points_at_sibling_repo():
    p = cern_source.cern_db_path()
    assert p.name == "CERN.sqlite"
    assert p.parent.name == "cern-kicad-libs"


def test_env_override(monkeypatch):
    monkeypatch.setenv("CERN_SQLITE", "/tmp/override/CERN.sqlite")
    assert str(cern_source.cern_db_path()) == "/tmp/override/CERN.sqlite"


def test_rows_reads_diodes():
    if not cern_source.cern_db_path().exists():
        pytest.skip("CERN.sqlite not present")
    rows = list(cern_source.rows("Diodes"))
    assert len(rows) == 962
    assert isinstance(rows[0], dict)
    assert "Manufacturer Part Number" in rows[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cern_source.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.cern_source'` (or import error).

- [ ] **Step 3: Write the implementation**

```python
# tools/cern_source.py
"""Locate and read the CERN KiCad library SQLite database (read-only)."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator, Dict, Any

# tools/cern_source.py -> parents[0]=tools, parents[1]=terra root, parents[2]=vsrc
_DEFAULT = Path(__file__).resolve().parents[2] / "cern-kicad-libs" / "CERN.sqlite"


def cern_db_path() -> Path:
    env = os.environ.get("CERN_SQLITE")
    return Path(env) if env else _DEFAULT


def connect() -> sqlite3.Connection:
    path = cern_db_path()
    if not path.exists():
        raise FileNotFoundError(
            f"CERN.sqlite not found at {path}; set CERN_SQLITE to override."
        )
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def rows(table: str) -> Iterator[Dict[str, Any]]:
    con = connect()
    try:
        for r in con.execute(f'SELECT * FROM "{table}"'):
            yield dict(r)
    finally:
        con.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cern_source.py -v`
Expected: 3 passed (or 2 passed + 1 skipped if CERN.sqlite absent).

- [ ] **Step 5: Commit**

```bash
git add tools/cern_source.py tests/test_cern_source.py
git commit -m "add tools.cern_source read-only CERN.sqlite accessor"
```

---

## Task 3: Library nickname map + reference rewrite

**Files:**
- Create: `tools/cern_libmap.py`
- Test: `tests/test_cern_libmap.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cern_libmap.py
from tools import cern_libmap as lm


def test_symbol_rewrite():
    assert lm.rewrite_ref("Diodes:Diode TVS Bi-Directional", lm.SYMBOL_LIB_NICK) \
        == "cern_Diodes:Diode TVS Bi-Directional"


def test_footprint_rewrite():
    assert lm.rewrite_ref("ICs And Semiconductors SMD:EATON_0402ESDA-MLP", lm.FOOTPRINT_LIB_NICK) \
        == "cern_ICs_SMD:EATON_0402ESDA-MLP"


def test_unknown_lib_passthrough():
    assert lm.rewrite_ref("Other:Thing", lm.FOOTPRINT_LIB_NICK) == "Other:Thing"


def test_empty_and_no_colon():
    assert lm.rewrite_ref("", lm.SYMBOL_LIB_NICK) == ""
    assert lm.rewrite_ref("NoColon", lm.SYMBOL_LIB_NICK) == "NoColon"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cern_libmap.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
# tools/cern_libmap.py
"""Canonical CERN -> terra library nickname mapping (diodes pilot scope)."""
from __future__ import annotations

SYMBOL_LIB_NICK = {
    "Diodes": "cern_Diodes",
}

FOOTPRINT_LIB_NICK = {
    "ICs And Semiconductors SMD": "cern_ICs_SMD",
    "ICs And Semiconductors THD": "cern_ICs_THD",
    "ICs And Semiconductors BONDING": "cern_ICs_BONDING",
}


def rewrite_ref(ref: str, nickmap: dict) -> str:
    """Rewrite the library-nickname portion of a 'Lib:Item' reference."""
    if not ref or ":" not in ref:
        return ref
    nick, name = ref.split(":", 1)
    return f"{nickmap.get(nick, nick)}:{name}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cern_libmap.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/cern_libmap.py tests/test_cern_libmap.py
git commit -m "add CERN->terra library nickname map and rewrite_ref"
```

---

## Task 4: Copy + register CERN diode libraries

**Files:**
- Create: `assets/symbols/cern/Diodes.kicad_sym`, `assets/footprints/cern/ICs And Semiconductors {SMD,THD,BONDING}.pretty`
- Modify: `kicad_config_templates/sym-lib-table`, `kicad_config_templates/fp-lib-table`
- Test: `tests/test_cern_libs_registered.py`

- [ ] **Step 1: Copy the CERN libraries into terra**

```bash
cd /users/dave/vsrc/terra-eda-library
mkdir -p assets/symbols/cern assets/footprints/cern
CERN=../cern-kicad-libs
cp "$CERN/SchLib/Diodes.kicad_sym" assets/symbols/cern/Diodes.kicad_sym
cp -r "$CERN/PcbLib/ICs And Semiconductors SMD.pretty" assets/footprints/cern/
cp -r "$CERN/PcbLib/ICs And Semiconductors THD.pretty" assets/footprints/cern/
cp -r "$CERN/PcbLib/ICs And Semiconductors BONDING.pretty" assets/footprints/cern/
```

- [ ] **Step 2: Register the symbol library**

In `kicad_config_templates/sym-lib-table`, add this line before the closing `)`:
```
  (lib (name "cern_Diodes")(type "KiCad")(uri "${TERRA_EDA_LIB}/assets/symbols/cern/Diodes.kicad_sym")(options "")(descr "CERN diode symbols"))
```

- [ ] **Step 3: Register the footprint libraries**

In `kicad_config_templates/fp-lib-table`, add before the closing `)`:
```
  (lib (name "cern_ICs_SMD")(type "KiCad")(uri "${TERRA_EDA_LIB}/assets/footprints/cern/ICs And Semiconductors SMD.pretty")(options "")(descr "CERN IC/semiconductor SMD footprints"))
  (lib (name "cern_ICs_THD")(type "KiCad")(uri "${TERRA_EDA_LIB}/assets/footprints/cern/ICs And Semiconductors THD.pretty")(options "")(descr "CERN IC/semiconductor THD footprints"))
  (lib (name "cern_ICs_BONDING")(type "KiCad")(uri "${TERRA_EDA_LIB}/assets/footprints/cern/ICs And Semiconductors BONDING.pretty")(options "")(descr "CERN IC/semiconductor bonding footprints"))
```

- [ ] **Step 4: Write the test (verifies files + registration nicknames match the libmap)**

```python
# tests/test_cern_libs_registered.py
from pathlib import Path
from tools import cern_libmap as lm

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_file_present():
    assert (ROOT / "assets/symbols/cern/Diodes.kicad_sym").is_file()


def test_footprint_dirs_present():
    for d in ["ICs And Semiconductors SMD.pretty",
              "ICs And Semiconductors THD.pretty",
              "ICs And Semiconductors BONDING.pretty"]:
        assert (ROOT / "assets/footprints/cern" / d).is_dir()


def test_every_nick_is_registered():
    sym = (ROOT / "kicad_config_templates/sym-lib-table").read_text()
    fp = (ROOT / "kicad_config_templates/fp-lib-table").read_text()
    for nick in lm.SYMBOL_LIB_NICK.values():
        assert f'(name "{nick}")' in sym
    for nick in lm.FOOTPRINT_LIB_NICK.values():
        assert f'(name "{nick}")' in fp
```

- [ ] **Step 5: Run the test**

Run: `uv run pytest tests/test_cern_libs_registered.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add assets/symbols/cern assets/footprints/cern kicad_config_templates/sym-lib-table kicad_config_templates/fp-lib-table tests/test_cern_libs_registered.py
git commit -m "copy and register CERN diode symbol/footprint libraries as cern_ nicks"
```

---

## Task 5: cern_diodes schema

**Files:**
- Create: `db/tables/cern_diodes/cern_diodes_0_schema.sql`
- Test: `tests/test_cern_diodes_schema.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cern_diodes_schema.py
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "db/tables/cern_diodes/cern_diodes_0_schema.sql"

EXPECTED = {
    "unique_id", "part_locator", "mpn", "manufacturer", "variant", "package",
    "value", "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status",
    "rohs", "rohs_document_link", "allow_substitution", "tracking",
    "standards_version", "bom_comment", "created_at", "updated_at", "created_by",
    "source", "dump_priority", "tier", "tags", "sim_model_type", "sim_device",
    "sim_pins", "sim_model_file", "sim_params",
    "pin_count", "component_height",
    "diode_type", "voltage_rating", "power_rating",
}


def test_schema_columns():
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA.read_text())
    cols = {r[1] for r in con.execute("PRAGMA table_info(cern_diodes)")}
    assert cols == EXPECTED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cern_diodes_schema.py -v`
Expected: FAIL — file does not exist / no such table.

- [ ] **Step 3: Write the schema**

```sql
-- db/tables/cern_diodes/cern_diodes_0_schema.sql
-- Terra EDA Library - cern_diodes table schema (CERN import, diodes pilot)
-- Core fields match the go-forward core; tier defaults to 5 per TIER_TAG_SPEC.org.

CREATE TABLE cern_diodes (
    -- Core fields (shared across all component types)
    unique_id TEXT PRIMARY KEY,
    part_locator TEXT,
    mpn TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    variant TEXT,
    package TEXT,
    value TEXT,
    description TEXT,
    datasheet TEXT,
    manufacturer_link TEXT,
    kicad_symbol TEXT,
    kicad_footprint TEXT,
    altium_symbol TEXT,
    altium_footprint TEXT,
    lifecycle_status TEXT DEFAULT 'Active',
    rohs TEXT DEFAULT 'no',
    rohs_document_link TEXT,
    allow_substitution TEXT DEFAULT 'no',
    tracking TEXT DEFAULT 'no',
    standards_version TEXT DEFAULT 'v1.0',
    bom_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    source TEXT DEFAULT 'static',
    dump_priority INTEGER DEFAULT 1,
    tier INTEGER DEFAULT 5,
    tags TEXT DEFAULT '',
    sim_model_type TEXT,
    sim_device TEXT,
    sim_pins TEXT,
    sim_model_file TEXT,
    sim_params TEXT,

    -- Adopted-from-CERN core additions
    pin_count TEXT,
    component_height TEXT,

    -- Diode-specific tail
    diode_type TEXT,
    voltage_rating TEXT,
    power_rating TEXT
);
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cern_diodes_schema.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add db/tables/cern_diodes/cern_diodes_0_schema.sql tests/test_cern_diodes_schema.py
git commit -m "add cern_diodes schema (core + pin_count/component_height + diode tail)"
```

---

## Task 6: unique_id reconciliation helper

**Files:**
- Create: `tools/cern_reconcile.py`
- Test: `tests/test_cern_reconcile.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cern_reconcile.py
from tools import cern_reconcile as rc


def test_reuses_existing_unique_id_case_insensitive():
    index = {("onsemi", "mbr0530t1g"): "OnSemi-MBR0530T1G"}
    assert rc.resolve_unique_id("OnSemi", "MBR0530T1G", index) == "OnSemi-MBR0530T1G"
    assert rc.resolve_unique_id("ONSEMI", " mbr0530t1g ", index) == "OnSemi-MBR0530T1G"


def test_mints_new_id_when_no_match():
    assert rc.resolve_unique_id("EATON", "0402ESDA-MLP", {}) == "EATON-0402ESDA-MLP"


def test_index_from_rows():
    rows = [
        {"manufacturer": "EATON", "mpn": "X1", "unique_id": "EATON-X1"},
        {"manufacturer": "Foo", "mpn": "Y2", "unique_id": "Foo-Y2"},
    ]
    idx = rc.index_from_rows(rows)
    assert idx[("eaton", "x1")] == "EATON-X1"
    assert len(idx) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cern_reconcile.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
# tools/cern_reconcile.py
"""Exact reconciliation of CERN parts against existing terra unique_ids."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Iterable, Tuple

Key = Tuple[str, str]


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def index_from_rows(rows: Iterable[dict]) -> Dict[Key, str]:
    idx: Dict[Key, str] = {}
    for r in rows:
        mfr, mpn, uid = r.get("manufacturer"), r.get("mpn"), r.get("unique_id")
        if mfr and mpn and uid:
            idx[(_norm(mfr), _norm(mpn))] = uid
    return idx


def build_existing_index(db_glob_dir: Path) -> Dict[Key, str]:
    """Scan db/*.db (excluding cern_*.db) for (manufacturer,mpn)->unique_id."""
    idx: Dict[Key, str] = {}
    for db in sorted(Path(db_glob_dir).glob("*.db")):
        if db.name.startswith("cern_") or db.name == "terra.db":
            continue
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        try:
            for (tbl,) in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ):
                cols = {c[1] for c in con.execute(f'PRAGMA table_info("{tbl}")')}
                if {"manufacturer", "mpn", "unique_id"} <= cols:
                    idx.update(index_from_rows(
                        dict(r) for r in con.execute(
                            f'SELECT manufacturer, mpn, unique_id FROM "{tbl}"'
                        )
                    ))
        finally:
            con.close()
    return idx


def resolve_unique_id(manufacturer: str, mpn: str, index: Dict[Key, str]) -> str:
    hit = index.get((_norm(manufacturer), _norm(mpn)))
    return hit if hit else f"{manufacturer.strip()}-{mpn.strip()}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cern_reconcile.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/cern_reconcile.py tests/test_cern_reconcile.py
git commit -m "add exact unique_id reconciliation against existing terra parts"
```

---

## Task 7: The importer generator

**Files:**
- Create: `db/tables/cern_diodes/run_100_cern_import.py`
- Test: `tests/test_cern_diodes_generator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cern_diodes_generator.py
import importlib.util
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "db/tables/cern_diodes/run_100_cern_import.py"


def _load():
    spec = importlib.util.spec_from_file_location("cern_diodes_gen", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sqlstr_escapes_quotes():
    mod = _load()
    assert mod.sqlstr("a'b") == "'a''b'"
    assert mod.sqlstr(None) == "''"


def test_diode_type_parsed():
    mod = _load()
    assert mod.diode_type_from_symbol("Diodes:Diode TVS Bi-Directional") == "TVS Bi-Directional"
    assert mod.diode_type_from_symbol("Diodes:Diode Schottky") == "Schottky"


def test_lifecycle_mapping():
    mod = _load()
    assert mod.map_lifecycle(None) == "Active"
    assert mod.map_lifecycle("") == "Active"
    assert mod.map_lifecycle("Obsolete") == "Obsolete"
    assert mod.map_lifecycle("Not Recommended") == "NRND"
    assert mod.map_lifecycle("Sourcing Difficulty") == "NRND"


def test_map_row_known_part():
    mod = _load()
    row = {
        "Part Number": "0402ESDA-MLP",
        "Manufacturer Part Number": "0402ESDA-MLP",
        "Manufacturer": "EATON",
        "Voltage": "8kV", "Power": None, "Pin Count": "2", "Case": "0402",
        "ComponentHeight": "0.44mm", "Status": None,
        "LibSymbol": "Diodes:Diode TVS Bi-Directional",
        "LibFootprint": "ICs And Semiconductors SMD:EATON_0402ESDA-MLP",
        "Part Description": "0.05pF 8kV Bidirectional ESD Voltage Suppressor",
        "Datasheet": "${CERN_DATASHEET_DIR}\\\\0402ESDA-MLP.pdf",
        "ComponentLink1URL": "",
    }
    m = mod.map_row(row, existing_index={})
    assert m["unique_id"] == "EATON-0402ESDA-MLP"
    assert m["mpn"] == "0402ESDA-MLP"
    assert m["manufacturer"] == "EATON"
    assert m["package"] == "0402"
    assert m["voltage_rating"] == "8kV"
    assert m["power_rating"] == ""
    assert m["pin_count"] == "2"
    assert m["component_height"] == "0.44mm"
    assert m["lifecycle_status"] == "Active"
    assert m["diode_type"] == "TVS Bi-Directional"
    assert m["kicad_symbol"] == "cern_Diodes:Diode TVS Bi-Directional"
    assert m["kicad_footprint"] == "cern_ICs_SMD:EATON_0402ESDA-MLP"
    assert m["datasheet"] == "0402ESDA-MLP.pdf"
    assert m["tags"] == "diode"


def test_denylist_filters_nonparts():
    mod = _load()
    assert mod.is_denylisted({"Part Number": "Empty", "Part Description": ""})
    assert mod.is_denylisted({"Part Number": "FOO Read Me", "Part Description": "x"})
    assert not mod.is_denylisted({"Part Number": "0402ESDA-MLP", "Part Description": "x"})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cern_diodes_generator.py -v`
Expected: FAIL — generator file missing.

- [ ] **Step 3: Write the generator**

```python
#!/usr/bin/env python3
# db/tables/cern_diodes/run_100_cern_import.py
"""Import CERN 'Diodes' -> cern_diodes_generated_100_cern_import.sql."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Make repo root importable (for tools.*) when run via Makefile (cwd = table dir)
_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))

from tools import cern_source, cern_libmap, cern_reconcile  # noqa: E402

CERN_TABLE = "Diodes"
OUTPUT_FILE = "cern_diodes_generated_100_cern_import.sql"

LIFECYCLE = {
    "": "Active", "obsolete": "Obsolete",
    "not recommended": "NRND", "sourcing difficulty": "NRND",
}

DENY_PATTERNS = [
    re.compile(r"read me", re.I),
    re.compile(r"drill-drawing", re.I),
    re.compile(r"^CERN_OHL", re.I),
    re.compile(r"^Empty$", re.I),
    re.compile(r"copyright", re.I),
]

INSERT_COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "source", "dump_priority",
    "tier", "tags", "created_by", "pin_count", "component_height",
    "diode_type", "voltage_rating", "power_rating",
]


def sqlstr(v) -> str:
    s = "" if v is None else str(v)
    return "'" + s.replace("'", "''") + "'"


def clean(v) -> str:
    return "" if v is None else str(v).strip()


def map_lifecycle(status) -> str:
    return LIFECYCLE.get(clean(status).lower(), "Active")


def diode_type_from_symbol(libsymbol: str) -> str:
    name = libsymbol.split(":", 1)[1] if ":" in libsymbol else libsymbol
    return re.sub(r"^Diode\s+", "", name).strip()


def datasheet_hint(raw: str) -> str:
    return clean(raw).replace("\\", "/").split("/")[-1]


def http_or_blank(url) -> str:
    u = clean(url)
    return u if u.lower().startswith("http") else ""


def is_denylisted(row: dict) -> bool:
    blob = f"{clean(row.get('Part Number'))} {clean(row.get('Part Description'))}"
    return any(p.search(blob) for p in DENY_PATTERNS)


def map_row(row: dict, existing_index: dict) -> dict:
    mfr = clean(row.get("Manufacturer"))
    mpn = clean(row.get("Manufacturer Part Number"))
    return {
        "unique_id": cern_reconcile.resolve_unique_id(mfr, mpn, existing_index),
        "part_locator": clean(row.get("Part Number")),
        "mpn": mpn,
        "manufacturer": mfr,
        "package": clean(row.get("Case")),
        "value": clean(row.get("Part Description")),
        "description": clean(row.get("Part Description")),
        "datasheet": datasheet_hint(row.get("Datasheet")),
        "manufacturer_link": http_or_blank(row.get("ComponentLink1URL")),
        "kicad_symbol": cern_libmap.rewrite_ref(
            clean(row.get("LibSymbol")), cern_libmap.SYMBOL_LIB_NICK),
        "kicad_footprint": cern_libmap.rewrite_ref(
            clean(row.get("LibFootprint")), cern_libmap.FOOTPRINT_LIB_NICK),
        "lifecycle_status": map_lifecycle(row.get("Status")),
        "rohs": "no",
        "source": "cern_import",
        "dump_priority": 0,
        "tier": 5,
        "tags": "diode",
        "created_by": "cern_import",
        "pin_count": clean(row.get("Pin Count")),
        "component_height": clean(row.get("ComponentHeight")),
        "diode_type": diode_type_from_symbol(clean(row.get("LibSymbol"))),
        "voltage_rating": clean(row.get("Voltage")),
        "power_rating": clean(row.get("Power")),
    }


def render(mapped: list[dict]) -> str:
    lines = ["BEGIN TRANSACTION;"]
    cols_sql = ", ".join(INSERT_COLS)
    for m in mapped:
        vals = []
        for c in INSERT_COLS:
            v = m[c]
            vals.append(str(v) if c in ("dump_priority", "tier") else sqlstr(v))
        lines.append(
            f"INSERT INTO cern_diodes ({cols_sql}) VALUES ({', '.join(vals)});")
    for m in mapped:
        lines.append(
            "INSERT INTO tags (unique_id, tag) VALUES "
            f"({sqlstr(m['unique_id'])}, 'diode');")
    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"


def main() -> None:
    index = cern_reconcile.build_existing_index(_ROOT / "db")
    mapped, seen = [], set()
    for row in cern_source.rows(CERN_TABLE):
        if is_denylisted(row):
            continue
        m = map_row(row, index)
        if m["unique_id"] in seen:
            continue
        seen.add(m["unique_id"])
        mapped.append(m)
    Path(OUTPUT_FILE).write_text(render(mapped))
    print(f"+ Wrote {OUTPUT_FILE}: {len(mapped)} cern_diodes parts")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run unit tests to verify they pass**

Run: `uv run pytest tests/test_cern_diodes_generator.py -v`
Expected: 6 passed.

- [ ] **Step 5: Generate the SQL and sanity-check the count**

Run:
```bash
cd db/tables/cern_diodes && uv run python run_100_cern_import.py && cd -
grep -c "INSERT INTO cern_diodes" db/tables/cern_diodes/cern_diodes_generated_100_cern_import.sql
```
Expected: prints `+ Wrote … 962 cern_diodes parts` and the grep prints `962`.

- [ ] **Step 6: Commit**

```bash
git add db/tables/cern_diodes/run_100_cern_import.py tests/test_cern_diodes_generator.py
git commit -m "add cern_diodes importer generator (CERN Diodes -> generated SQL)"
```
(The `*_generated_*.sql` output is gitignored — do not add it.)

---

## Task 8: End-to-end build + automated mapping test

**Files:**
- Create: `db/tables/cern_diodes/test_cern_diodes.py`

- [ ] **Step 1: Build the table database**

Run: `make cern_diodes-build`
Expected: `+ Built db/cern_diodes.db from N SQL file(s)`, exit 0.

- [ ] **Step 2: Write the end-to-end test**

```python
# db/tables/cern_diodes/test_cern_diodes.py
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "db/cern_diodes.db"


def _con():
    subprocess.run(["make", "cern_diodes-build"], cwd=ROOT, check=True,
                   capture_output=True)
    return sqlite3.connect(DB)


def test_row_count_is_962():
    con = _con()
    assert con.execute("SELECT COUNT(*) FROM cern_diodes").fetchone()[0] == 962


def test_no_duplicate_unique_ids():
    con = _con()
    n, d = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT unique_id) FROM cern_diodes").fetchone()
    assert n == d


def test_known_part_mapping():
    con = _con()
    con.row_factory = sqlite3.Row
    r = con.execute(
        "SELECT * FROM cern_diodes WHERE mpn='0402ESDA-MLP'").fetchone()
    assert r["manufacturer"] == "EATON"
    assert r["unique_id"] == "EATON-0402ESDA-MLP"
    assert r["package"] == "0402"
    assert r["voltage_rating"] == "8kV"
    assert r["pin_count"] == "2"
    assert r["component_height"] == "0.44mm"
    assert r["lifecycle_status"] == "Active"
    assert r["diode_type"] == "TVS Bi-Directional"
    assert r["kicad_symbol"] == "cern_Diodes:Diode TVS Bi-Directional"
    assert r["kicad_footprint"] == "cern_ICs_SMD:EATON_0402ESDA-MLP"


def test_all_symbol_nicks_registered():
    con = _con()
    sym = (ROOT / "kicad_config_templates/sym-lib-table").read_text()
    fp = (ROOT / "kicad_config_templates/fp-lib-table").read_text()
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_symbol FROM cern_diodes WHERE kicad_symbol != ''"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for (val,) in con.execute(
            "SELECT DISTINCT kicad_footprint FROM cern_diodes WHERE kicad_footprint LIKE '%:%'"):
        nick = val.split(":", 1)[0]
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"
```

- [ ] **Step 3: Run the end-to-end test**

Run: `make cern_diodes-test`
Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add db/tables/cern_diodes/test_cern_diodes.py
git commit -m "add cern_diodes end-to-end build + mapping test"
```

---

## Task 9: Datasheet manifest builder

**Files:**
- Create: `tools/cern_datasheets/build_manifest.py`
- Test: `tests/test_build_manifest.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_build_manifest.py
from tools.cern_datasheets import build_manifest as bm


def test_manifest_dedups_by_filename():
    rows = [
        {"Manufacturer Part Number": "A1", "Manufacturer": "M",
         "Datasheet": "${CERN_DATASHEET_DIR}\\\\1.5KE.pdf"},
        {"Manufacturer Part Number": "A2", "Manufacturer": "M",
         "Datasheet": "${CERN_DATASHEET_DIR}\\\\1.5KE.pdf"},
        {"Manufacturer Part Number": "B1", "Manufacturer": "N",
         "Datasheet": "${CERN_DATASHEET_DIR}\\\\OTHER.pdf"},
    ]
    man = bm.build(rows)
    assert set(man) == {"1.5KE.pdf", "OTHER.pdf"}
    assert sorted(man["1.5KE.pdf"]["mpns"]) == ["A1", "A2"]
    assert man["1.5KE.pdf"]["status"] == "pending"
    assert man["OTHER.pdf"]["verify"] == "unchecked"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_manifest.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
# tools/cern_datasheets/build_manifest.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_build_manifest.py -v`
Expected: 1 passed.

- [ ] **Step 5: Build the real diode manifest**

Run: `uv run python tools/cern_datasheets/build_manifest.py Diodes`
Expected: `+ …/manifest.json: N unique datasheets for Diodes` (N ≤ 962).

- [ ] **Step 6: Commit**

```bash
git add tools/cern_datasheets/build_manifest.py tests/test_build_manifest.py assets/datasheets/cern/manifest.json
git commit -m "add datasheet manifest builder (dedup by filename) and diode manifest"
```

---

## Task 10: Datasheet parse-verification

**Files:**
- Create: `tools/cern_datasheets/verify.py`
- Test: `tests/test_datasheet_verify.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_datasheet_verify.py
from tools.cern_datasheets import verify


def test_exact_mpn_required():
    text = "EATON 0402ESDA-MLP  Working Voltage 8kV  ESD Suppressor"
    assert verify.check_text(text, "0402ESDA-MLP", params=["8kV"]) == "ok"


def test_mpn_mismatch():
    text = "Some other part 1N4148  100V"
    assert verify.check_text(text, "0402ESDA-MLP", params=["8kV"]) == "mpn_mismatch"


def test_unparseable_empty_text():
    assert verify.check_text("", "0402ESDA-MLP", params=["8kV"]) == "unparseable"


def test_param_missing_is_review():
    text = "EATON 0402ESDA-MLP ESD Suppressor"
    assert verify.check_text(text, "0402ESDA-MLP", params=["8kV"]) == "param_missing"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_datasheet_verify.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
# tools/cern_datasheets/verify.py
"""Exact datasheet verification: confirm MPN + CERN params appear in PDF text."""
from __future__ import annotations

from pathlib import Path
from typing import List


def check_text(text: str, mpn: str, params: List[str]) -> str:
    """Return one of: ok | unparseable | mpn_mismatch | param_missing."""
    if not text or not text.strip():
        return "unparseable"
    norm = text.upper()
    if mpn.upper() not in norm:
        return "mpn_mismatch"
    for p in params:
        if p and p.upper() not in norm:
            return "param_missing"
    return "ok"


def extract_text(pdf_path: Path) -> str:
    """Extract text from a PDF. Returns '' if it cannot be parsed."""
    try:
        from pypdf import PdfReader  # lazy import; add as dep when fetching
    except ImportError:  # pragma: no cover
        raise RuntimeError("pypdf not installed; run: uv add --dev pypdf")
    try:
        reader = PdfReader(str(pdf_path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


def verify_pdf(pdf_path: Path, mpn: str, params: List[str]) -> str:
    return check_text(extract_text(pdf_path), mpn, params)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_datasheet_verify.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/cern_datasheets/verify.py tests/test_datasheet_verify.py
git commit -m "add exact datasheet parse-verification (MPN + CERN params)"
```

---

## Task 11: Git LFS for datasheet PDFs

**Files:**
- Modify: `.gitattributes`

- [ ] **Step 1: Add the LFS rule**

Append to `.gitattributes`:
```
# Datasheet PDFs are stored via Git LFS
*.pdf filter=lfs diff=lfs merge=lfs -text
```

- [ ] **Step 2: Initialize LFS and verify the pattern is tracked**

Run:
```bash
git lfs install --local
git check-attr filter -- assets/datasheets/cern/example.pdf
```
Expected: second command prints `assets/datasheets/cern/example.pdf: filter: lfs`.

> Note: existing committed PDFs (e.g. `db/tables/resistors_smt/panasonic-erj.pdf`) are not retroactively migrated here; that is out of scope for the pilot.

- [ ] **Step 3: Commit**

```bash
git add .gitattributes
git commit -m "track *.pdf via Git LFS for datasheet assets"
```

---

## Task 12: Datasheet path rewrite step

**Files:**
- Create: `tools/cern_datasheets/rewrite_datasheets.py`
- Test: `tests/test_rewrite_datasheets.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_rewrite_datasheets.py
import sqlite3
from tools.cern_datasheets import rewrite_datasheets as rw


def _db():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE cern_diodes (unique_id TEXT, datasheet TEXT)")
    con.execute("INSERT INTO cern_diodes VALUES ('A', '0402ESDA-MLP.pdf')")
    con.execute("INSERT INTO cern_diodes VALUES ('B', 'MISSING.pdf')")
    return con


def test_only_verified_are_rewritten():
    con = _db()
    manifest = {
        "0402ESDA-MLP.pdf": {"verify": "ok",
                              "local_path": "assets/datasheets/cern/0402ESDA-MLP.pdf"},
        "MISSING.pdf": {"verify": "mpn_mismatch", "local_path": ""},
    }
    n = rw.apply(con, "cern_diodes", manifest)
    assert n == 1
    rows = dict(con.execute("SELECT unique_id, datasheet FROM cern_diodes"))
    assert rows["A"] == "assets/datasheets/cern/0402ESDA-MLP.pdf"
    assert rows["B"] == "MISSING.pdf"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_rewrite_datasheets.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
# tools/cern_datasheets/rewrite_datasheets.py
"""Rewrite cern_<t>.datasheet to local asset paths for verified datasheets."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = _ROOT / "assets/datasheets/cern/manifest.json"


def apply(con: sqlite3.Connection, table: str, manifest: dict) -> int:
    count = 0
    for fn, entry in manifest.items():
        if entry.get("verify") == "ok" and entry.get("local_path"):
            cur = con.execute(
                f"UPDATE {table} SET datasheet = ? WHERE datasheet = ?",
                (entry["local_path"], fn))
            count += cur.rowcount
    con.commit()
    return count


def main(table: str = "cern_diodes") -> None:
    manifest = json.loads(MANIFEST.read_text())
    db = _ROOT / "db" / f"{table}.db"
    con = sqlite3.connect(db)
    try:
        n = apply(con, table, manifest)
    finally:
        con.close()
    print(f"+ rewrote {n} datasheet paths in {db}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cern_diodes")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_rewrite_datasheets.py -v`
Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/cern_datasheets/rewrite_datasheets.py tests/test_rewrite_datasheets.py
git commit -m "add datasheet path rewrite for verified parts"
```

---

## Task 13: Audit checklist

**Files:**
- Create: `db/tables/cern_diodes/AUDIT.md`

- [ ] **Step 1: Write the audit checklist**

```markdown
# cern_diodes — Human Audit

Source: CERN `Diodes` (962 parts). Generated by `run_100_cern_import.py`.

## Automated (must pass before audit)
- [ ] `make cern_diodes-test` green (row count 962, no dup ids, known-part mapping, nicks registered)
- [ ] `uv run pytest tests/ -q` green

## Sampling (audit ≥ 20 parts spanning diode_type values)
For each sampled part, open its verified datasheet and confirm:
- [ ] MPN matches the datasheet exactly
- [ ] `voltage_rating` / `power_rating` match the datasheet
- [ ] `package` / `pin_count` match
- [ ] `kicad_symbol` and `kicad_footprint` render in KiCad

## Datasheet verifier follow-ups
- [ ] List parts with `verify != ok` from `manifest.json` and resolve or accept:

| filename | mpns | verify | action |
|---|---|---|---|

## Known carve-outs (from spec)
- [ ] Secondary footprint variants (`…_bot`) intentionally deduped — confirm none needed.

## Sign-off
- Auditor: ______  Date: ______
```

- [ ] **Step 2: Commit**

```bash
git add db/tables/cern_diodes/AUDIT.md
git commit -m "add cern_diodes human audit checklist"
```

---

## Task 14: Master build + KiCad integration verification

**Files:** none created — verifies the full pipeline.

- [ ] **Step 1: Build the master database and dbl files**

Run: `make`
Expected: builds `db/cern_diodes.db`, `db/terra.db`, regenerates `terra.kicad_dbl`; exit 0.

- [ ] **Step 2: Verify the base table and the tier-gated view**

The base table must hold all parts; the `_v` view is tier-gated. Because `cern_diodes`
parts are `tier=5` and the Makefile `DEFAULT_TIER=2`, the view is **expected to be empty
at the default cutoff** — raising the cutoff proves the view plumbing works.

Run:
```bash
sqlite3 db/terra.db "SELECT COUNT(*) FROM cern_diodes;"                                   # base table
sqlite3 db/terra.db "SELECT COUNT(*) FROM cern_diodes_v;"                                  # default tier=2
sqlite3 db/terra.db "UPDATE terra_tier_config SET tier_level=5; SELECT COUNT(*) FROM cern_diodes_v;"
```
Expected: base table = `962`; view at default = `0` (tier-gated, correct); view after
raising cutoff to 5 = `962`. (The `UPDATE` mutates the generated master DB only — it is
rebuilt by `make`; do not commit it.)

> Behavior note: imported CERN catalog parts are intentionally `tier=5`, so they stay out
> of the default KiCad view until the user raises the tier cutoff or activates the `diode`
> tag. This is the lazy-loading-friendly default, not a bug.

- [ ] **Step 3: Verify the .kicad_dbl references the table**

Run: `grep -c "cern_diodes" terra.kicad_dbl`
Expected: ≥ 1 (a library entry for `cern_diodes` / `cern_diodes_v`).

- [ ] **Step 4: Full test sweep**

Run: `uv run pytest tests/ db/tables/cern_diodes -q`
Expected: all passed.

- [ ] **Step 5: Commit any regenerated tracked artifacts**

```bash
git add terra.kicad_dbl
git commit -m "regenerate terra.kicad_dbl with cern_diodes library"
```

---

## Out of scope (deferred per spec §8)
- The web fetcher (`tools/cern_datasheets/fetch.py`) — implemented/run as a separate, resumable, rate-limited tool after the pilot lands; not a unit-tested step here. It populates each manifest entry's `source_url`, `local_path`, `status`, and runs `verify.verify_pdf` to set `verify`.
- Generalizing to the other 54 CERN tables.
- Rolling `pin_count`/`component_height` into all terra tables; second-source MPN; Family→tags; Altium columns; `…_bot` footprint variants; migrating pre-existing committed PDFs to LFS.
