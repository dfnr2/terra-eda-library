# Terra EDA Library Specification

## 1. Overview
The **Terra EDA Library** is a database-driven component library supporting multiple EDA tools (KiCad, Altium). It provides a reproducible SQLite backend, automated part ingestion from YAML sources, and consistent linking to symbols, footprints, and 3D models.

**Note:** This project was originally called "Ether KiCad Library" but has been renamed to "Terra EDA Library" to reflect its multi-EDA nature and use of the "terra" prefix in file names.

**Goals**
- Build the DB from version-controlled YAML + SQL sources.
- Auto-generate SQL per part using a schema with defaults.
- Validate referenced assets (symbols, footprints, 3D models).
- Support multiple EDA tools (KiCad via `.kicad_dbl`, Altium integration TBD).
- Keep assets portable under a single `assets/` root.

---

## 2. Repository Layout

```
terra-eda-library/
├─ Makefile
├─ README.md
│
├─ db/
│  ├─ schema.sql            # tables, views, pragmas (WAL optional)
│  ├─ *.sql                 # category or auto-generated inserts
│  └─ terra_lib.db          # build artifact (not committed)
│
├─ kicad/
│  ├─ terra_resistors.kicad_dbl
│  ├─ terra_capacitors.kicad_dbl
│  ├─ terra_connectors.kicad_dbl
│  └─ terra_diodes.kicad_dbl
│
├─ assets/
│  ├─ symbols/
│  │   ├─ Standard/*.kicad_sym
│  │   └─ Custom/*.kicad_sym
│  ├─ footprints/
│  │   ├─ Standard.pretty/*.kicad_mod
│  │   └─ Custom.pretty/*.kicad_mod
│  └─ 3dmodels/
│      ├─ Standard.3dshapes/*.step
│      └─ Custom.3dshapes/*.step
│
├─ parts/
│  └─ <PartID>/
│      ├─ part.yml                     # per-part overrides/metadata
│      ├─ *.kicad_sym / *.kicad_mod    # only if bespoke
│      ├─ *.step                       # only if bespoke
│      └─ doc/                         # optional datasheets/notes
│
└─ tools/
   ├─ gen_part_sql.py
   ├─ validate_assets.py
   └─ schema.yml
```

---

## 3. Data Model

### 3.1 SQLite Schema (`db/schema.sql`)
```sql
PRAGMA foreign_keys = ON;
-- Optional: PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS part (
  part_id     TEXT PRIMARY KEY,
  class       TEXT,
  value       TEXT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS symbol_map (
  part_id  TEXT,
  symbol   TEXT,
  FOREIGN KEY(part_id) REFERENCES part(part_id)
);

CREATE TABLE IF NOT EXISTS footprint_map (
  part_id   TEXT,
  footprint TEXT,
  FOREIGN KEY(part_id) REFERENCES part(part_id)
);

CREATE TABLE IF NOT EXISTS mpn (
  part_id       TEXT,
  manufacturer  TEXT,
  mpn           TEXT,
  preferred     INTEGER DEFAULT 1,
  PRIMARY KEY(part_id, manufacturer, mpn),
  FOREIGN KEY(part_id) REFERENCES part(part_id)
);

-- runtime/config values (not usually dumped)
CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT
);

-- Example category views (extend as needed)
CREATE VIEW IF NOT EXISTS resistors_v AS
SELECT p.part_id AS Symbol_Name, s.symbol AS Symbol, f.footprint AS Footprint,
       p.value AS Value,
       (SELECT mpn FROM mpn m WHERE m.part_id=p.part_id AND preferred=1 LIMIT 1) AS MPN,
       (SELECT manufacturer FROM mpn m WHERE m.part_id=p.part_id AND preferred=1 LIMIT 1) AS Manufacturer,
       p.description AS Description
FROM part p
JOIN symbol_map s ON s.part_id=p.part_id
JOIN footprint_map f ON f.part_id=p.part_id
WHERE p.class='Resistor';

CREATE VIEW IF NOT EXISTS capacitors_v AS
SELECT p.part_id AS Symbol_Name, s.symbol AS Symbol, f.footprint AS Footprint,
       p.value AS Value,
       (SELECT mpn FROM mpn m WHERE m.part_id=p.part_id AND preferred=1 LIMIT 1) AS MPN,
       (SELECT manufacturer FROM mpn m WHERE m.part_id=p.part_id AND preferred=1 LIMIT 1) AS Manufacturer,
       p.description AS Description
FROM part p
JOIN symbol_map s ON s.part_id=p.part_id
JOIN footprint_map f ON f.part_id=p.part_id
WHERE p.class='Capacitor';
```

**Notes**
- No `model_map`: 3D models are referenced inside `.kicad_mod` `(model "...")`.
- Views create category-specific slices for nicer KiCad browsing.

### 3.2 YAML Schema (`tools/schema.yml`)
```yaml
version: 1.0

defaults:
  class: Generic
  value: N/A
  description: Auto-generated part
  symbol: "Device:R"                                 # example default
  footprint: "@@ASSET_ROOT@@/footprints/Standard.pretty/R_0603"
  manufacturer: ""
  mpn: ""

fields:
  part:
    - part_id
    - class
    - value
    - description
  symbol_map:
    - part_id
    - symbol
  footprint_map:
    - part_id
    - footprint
  mpn:
    - part_id
    - manufacturer
    - mpn
```

---

## 4. Build System (Makefile)

### Targets
- `make db` — rebuild the database from `schema.sql` + `db/*.sql` (after running generator).
- `make scan` — generate `db/auto_parts.sql` (or per-category SQLs) from `parts/` and YAML.
- `make validate` — verify assets and footprint model references.
- `make dumps` — export tables/views as `.sql` (excluding `settings`).
- `make clean` — remove build artifacts.

### Behavior
- Replace `@@ASSET_ROOT@@` with `${ASSET_ROOT}` (default `assets`) when importing SQL.
- Recreate `settings` each build (e.g., `INSERT INTO settings VALUES('asset_root','assets');`).
- Order: `scan → db → validate`.

**Environment variables**
| Var           | Purpose                       | Default             |
|---------------|-------------------------------|---------------------|
| `ASSET_ROOT`  | prefix for asset paths        | `assets`            |
| `TERRA_DB`    | database file path            | `db/terra_lib.db`   |
| `SCHEMA_FILE` | YAML schema path              | `tools/schema.yml`  |

---

## 5. Tools

### 5.1 gen_part_sql.py
Generates SQL from per-part YAML (`parts/<PartID>/part.yml`) merged with defaults in `schema.yml`.

**Inputs**
- YAML schema and part definitions
- Asset tree under `assets/` for internal references (external references like `Device:R` are allowed).

**Outputs**
- SQL insert statements under `db/auto_parts.sql` or category files.

**Rules**
- Fill missing fields from schema defaults.
- Internal refs start with `@@ASSET_ROOT@@/` or `assets/`.
- External refs like `Device:R` are preserved as-is.

**Example emitted SQL**
```sql
INSERT OR REPLACE INTO part(part_id,class,value,description)
VALUES ('R0603_10K_1PCT','Resistor','10k','0603 resistor 1% 1/10W');
INSERT OR REPLACE INTO symbol_map VALUES ('R0603_10K_1PCT','Device:R');
INSERT OR REPLACE INTO footprint_map VALUES ('R0603_10K_1PCT','@@ASSET_ROOT@@/footprints/Standard.pretty/R_0603');
```

### 5.2 validate_assets.py
Verifies internal asset existence and footprint→model consistency.

**Checks**
1. Internal symbols and footprints exist.
2. Footprint `(model "...")` paths exist under `assets/3dmodels/`, unless external (`${KICAD6_3DMODEL_DIR}`). 
3. Reports orphaned assets not referenced by DB.
4. Exits nonzero on failure.

---

## 6. KiCad Integration
Each `.kicad_dbl` maps to a database view.

Example `kicad/terra_resistors.kicad_dbl`:
```json
{
  "meta": { "version": 0, "filename": "terra_resistors.kicad_dbl" },
  "name": "Ether Resistors",
  "description": "Resistor library backed by Ether DB",
  "source": {
    "type": "odbc",
    "dsn": "terra_parts",
    "connection_string": "DSN=terra_parts"
  },
  "libraries": [
    {
      "name": "Resistors",
      "table": "resistors_v",
      "key": "Symbol_Name",
      "symbols": "Symbol",
      "footprints": "Footprint",
      "fields": [
        { "column": "Value", "name": "Value", "visible_on_add": true },
        { "column": "MPN", "name": "MPN", "visible_on_add": true },
        { "column": "Manufacturer", "name": "Manufacturer", "visible_on_add": true },
        { "column": "Description", "name": "Description", "visible_on_add": false }
      ]
    }
  ]
}
```

---

## 7. Example Part Folder

`parts/R0603_10K_1PCT/part.yml`
```yaml
class: Resistor
value: 10k
tolerance: 1%
power: 0.1W
symbol: Device:R
footprint: "@@ASSET_ROOT@@/footprints/Standard.pretty/R_0603"
description: "0603 resistor 1% 1/10W"
```

---

## 8. Development Plan (Incremental)

| Step | Component        | Deliverable |
|-----:|------------------|-------------|
| 1    | Skeleton         | Layout, Makefile stub, empty schema |
| 2    | Core DB schema   | `schema.sql`, views, `settings` bootstrap |
| 3    | YAML schema      | `tools/schema.yml` with defaults |
| 4    | Generator        | `gen_part_sql.py` basic merge + SQL emit |
| 5    | Build flow       | Makefile: `scan → db → validate` |
| 6    | Validator        | `validate_assets.py` (internal/external + model scan) |
| 7    | Category dblibs  | `.kicad_dbl` files linked to views |
| 8    | Seeds            | Standard parts, custom samples |
| 9    | CI (optional)    | Run `make validate` on PRs |

---

## 9. Principles
- Declarative metadata → deterministic builds.
- Database built, never manually edited.
- Portability via `assets/` + `@@ASSET_ROOT@@`.
- KiCad-native 3D model handling.
- Modular growth (shared vs. bespoke assets).
- Automated validation.

---

## 10. Stretch Goals
- Schema versioning + migration.
- Class-specific attribute tables.
- JSON export for web catalog.
- Submodule for large 3D libraries (`terra-assets`).
