# Phase 2 — 3D Models (hybrid source) Design

**Date:** 2026-06-07
**Status:** Draft
**Builds on:** `2026-06-07-symbol-footprint-hierarchy-design.md` (Phase 1, done).

## 1. Problem

CERN footprints reference 3D models via `(model "${CERN_3DMODEL_DIR}/<name>.stp")`, but the
models are **not available** (not in the CERN repo, var undefined — like the datasheets,
they live on a CERN share). 1716/1724 SMD diode footprints have a `(model …)` line pointing
at a missing file. We have only a filename hint + each part's MPN/manufacturer/package.

## 2. Source strategy — Hybrid (decided)

1. **Package → KiCad bundled model (primary).** KiCad ships 105 model libs covering the
   diode packages CERN uses (SOD-123, SOT-23, DO-214AC=SMA, etc.). A curated map
   `CERN package → ${KICAD10_3DMODEL_DIR}/<lib>.3dshapes/<file>.step` rewrites the
   footprint's `(model …)` line. Free, local, reliable, high coverage for standard packages.
2. **Web download per MPN (tail).** For unmapped/blank-package parts, best-effort download
   the exact STEP, stored in terra (see §4). Resumable manifest like the datasheet fetcher;
   misses flagged for human review. Expect partial coverage — automated per-MPN STEP
   fetching is fragile (account-walled sources).
3. **Human review/positioning** for the rest.

## 3. Model reference / placement

- **Bundled models: reference, don't embed.** Rewrite `(model …)` to
  `${KICAD10_3DMODEL_DIR}/<lib>.3dshapes/<file>.step` — always available, lightweight.
- **Downloaded models: terra-owned + reference** (consistent with the sym/fp hierarchy):
  store under `kicad_3dmodels/` and reference `${TERRA_EDA_LIB}/kicad_3dmodels/<file>`.
  (Embedding into `.kicad_mod` is possible — KiCad 9/10 `embedded_files` — but reference
  keeps footprints small and matches how we handle symbols/footprints. **Open question:**
  embed vs terra-reference for downloaded models — default to reference unless portability
  of individual `.kicad_mod` files is required.)
- **Positioning:** a KiCad package-generic model dropped into a CERN footprint may be
  mis-aligned (different origin/pad layout). Default offset/rotation/scale = 0; a **human
  positions** per the user's plan. Optionally seed a per-package default offset later.

## 4. Mechanism

- `tools/model_map.py` — curated `CERN package → (kicad_lib, model_file)` table for diode
  packages (DO-214AC→D_SMA, SOT23-3→SOT-23, SOD-123→D_SOD-123, …). Grows per part type.
- `tools/apply_3d_models.py` — for each `.kicad_mod` in the terra footprint libs, look up
  the package; if mapped, rewrite the `(model …)` path to the KiCad bundled ref; else leave
  the placeholder and record it for the download tail. Idempotent; re-runnable; run by `make`.
- `tools/cern_3dmodels/` (tail) — manifest of unmatched parts (keyed by model filename),
  resumable downloader, `verify`, and a rewrite step pointing `(model …)` at the stored
  terra model. Mirrors the datasheet subsystem.

The footprint `.kicad_mod` files are terra-owned (in `kicad_footprints/`), so rewriting
their `(model …)` lines in place is fine and committed.

## 5. Phasing

- **2a (reliable win):** package→bundled map + `apply_3d_models.py`; rewrite matched diode
  footprints; report coverage + the unmatched list. No network.
- **2b (tail) — REVISED:** Investigation showed the tail clusters by *body type*, not
  random MPNs, and **KiCad already ships models for almost all of it** (bridge rectifiers
  `Diode_Bridge_Vishay_*`, wide axials `D_DO-201*_P15.24mm`, `D_PowerDI-123`, MELF family,
  `D_SOD-123F`). So the per-MPN web downloader is unnecessary. Instead 2b *extends the
  codified map*: a bridge body-code map, an SMD body-code layer (SODFL→SOD-123F/128,
  DIOMELF→MELF family, PowerDI/PowerMite), and a footprint-name fallback
  (`resolve_from_footprint`) for blank-package parts whose body is in the footprint name.
  Wide axials take a capped best-effort to the largest bundled model. This raised diode
  coverage to **82%** with no network/accounts. The genuine residual (~18%: power modules
  SOT-227B/SEMITOP/IXBOD, exotic SMD SOD57/DFN2/SON10, horizontal TO-247 which KiCad lacks,
  one-off cans) goes to a **human drop-folder** under `kicad_3dmodels/` — sized small and
  body-clustered. The web-download subsystem is deferred indefinitely (kept on file).

## 6. Out of scope
- Exact-geometry guarantee (bundled models are package-generic).
- Auto-positioning (human pass).
