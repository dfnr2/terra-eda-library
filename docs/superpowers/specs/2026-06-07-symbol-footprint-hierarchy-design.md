# Symbol / Footprint Hierarchy + 3D Models — Design

**Date:** 2026-06-07
**Status:** Draft
**Supersedes:** the `cern_`-prefixed `assets/{symbols,footprints}/cern/` copies from the
cern_diodes pilot (`2026-06-06-cern-diodes-importer-design.md` §5.5).

## 1. Goal

Give terra a single, self-contained, terra-owned **symbol and footprint hierarchy** that
parts reference, with registration **generated** by the build (never hand-maintained). CERN
(and future vendor) libraries are **copied in** under normalized names so terra owns clean,
updatable copies. Then (phase 2) **3D models are auto-downloaded and embedded** into the
footprints, with final positioning left to a human.

## 2. Locked decisions

| # | Decision |
|---|---|
| Owned hierarchy | Two top-level dirs: **`kicad_symbols/`** (`.kicad_sym` libs) and **`kicad_footprints/`** (`.pretty` libs). |
| No translation | Do **not** map parts to KiCad's built-in `Device:`/`Diode_SMD:` libs. Parts always reference terra-owned libs under the hierarchy. |
| CERN copy granularity | **Mirror CERN PcbLib/SchLib 1:1** — one copied lib per source lib, normalized name. e.g. `PcbLib/MOLEX THD.pretty` → `kicad_footprints/cern-molex-thd.pretty`; `SchLib/Diodes.kicad_sym` → `kicad_symbols/cern-diodes.kicad_sym`. |
| Nickname rule | lowercase; non-alphanumerics → `-`; collapse repeats; CERN libs prefixed `cern-`. Nickname = the copied filename stem. e.g. `ICs And Semiconductors SMD` → `cern-ics-and-semiconductors-smd`. |
| Fold `terra_sym` | Move `terra_sym.kicad_sym` → `kicad_symbols/terra_sym.kicad_sym` and `assets/footprints/terra_sym.pretty` → `kicad_footprints/terra_sym.pretty`. One consistent hierarchy. |
| Registration | The build **generates** `kicad_symbols/sym-lib-table` and `kicad_footprints/fp-lib-table` listing every lib in each dir, with `${TERRA_EDA_LIB}`-relative URIs (KiCad **does** expand path vars in lib-table URIs). The user includes each with a single `(type "Table")` entry in their global table. |
| 3D models | Phase 2 (deferred): auto-download STEP/WRL, auto-embed into `.kicad_mod`, human positions. Source TBD. |

## 3. Phase 1 — hierarchy + rendering (diodes pilot)

**Layout**
```
kicad_symbols/
  sym-lib-table                      # GENERATED: registers every *.kicad_sym here
  terra_sym.kicad_sym                # moved from repo root
  cern-diodes.kicad_sym              # copied from CERN SchLib/Diodes.kicad_sym
kicad_footprints/
  fp-lib-table                       # GENERATED: registers every *.pretty here
  terra_sym.pretty/                  # moved from assets/footprints/
  cern-ics-and-semiconductors-smd.pretty/      # from PcbLib/ICs And Semiconductors SMD.pretty
  cern-ics-and-semiconductors-thd.pretty/
  cern-ics-and-semiconductors-bonding.pretty/
```

**Importer change (`tools/cern_libmap.py` + `run_100_cern_import.py`)**
- Replace the `cern_`/`assets/.../cern/` scheme. Map each CERN `LibSymbol`/`LibFootprint`
  nickname to its normalized terra nickname: `Diodes` → `cern-diodes`;
  `ICs And Semiconductors SMD` → `cern-ics-and-semiconductors-smd`; etc.
- `rewrite_ref` rewrites the nickname portion to the normalized name (item name unchanged).
- `kicad_symbol`/`kicad_footprint` in the DB then reference the terra-owned libs.

**Copy step** (a small tool, run by the importer or a make target): copy the needed CERN
libs into the hierarchy with normalized names. Idempotent; re-copy on update.

**Registration generator** (`tools/generate_lib_tables.py`, run by `make`): scan
`kicad_symbols/*.kicad_sym` and `kicad_footprints/*.pretty`, emit the two lib-table files
with entries:
```
(lib (name "<stem>")(type "KiCad")(uri "${TERRA_EDA_LIB}/kicad_symbols/<file>")(options "")(descr ""))
```
The user adds two one-line `(type "Table")` includes (global tables) pointing at
`${TERRA_EDA_LIB}/kicad_symbols/sym-lib-table` and `…/kicad_footprints/fp-lib-table`.

**Cleanup**: remove `assets/symbols/cern/`, `assets/footprints/cern/`, and the `cern_*`
entries in `kicad_config_templates/` (superseded).

**Verify**: rebuild; every `cern_diodes.kicad_symbol`/`kicad_footprint` nickname appears in
the generated lib-tables and resolves to a file/item that exists; KiCad renders diode
symbols + footprints.

## 4. Phase 2 — 3D models (deferred)

- **Download**: fetch STEP/WRL per footprint/part (source decided in phase 2 — manufacturer
  links vs KiCad/community packs). Resumable manifest, like the datasheet fetcher.
- **Embed**: write the model into the `.kicad_mod` (KiCad embedded files) so it travels with
  the footprint.
- **Position**: leave 3D offset/rotation/scale to a human pass (default at origin).

## 5. Out of scope (for now)
- Resistor subset re-inclusion (separate decision).
- Translating any parts to KiCad built-in libs.
- Scale-out to the other CERN tables (after diodes render correctly under this model).
