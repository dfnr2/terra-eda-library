# Datasheet storage — permanent internal library

**Problem.** Manufacturer datasheet URLs rot (links move, parts get deprecated, sites
reorganize). terra parts that cite a web URL for `datasheet` will silently lose their
documentation over time. terra must be self-contained.

**Principle.** Every *native / generated* terra part's `datasheet` resolves to a local
PDF stored in this repo. Web URLs are never the system of record. (CERN parts keep their
URLs — they are being wound down and not worth the bytes.)

## Layout

A central, manufacturer-organized library at the repo root:

```
datasheets/
  <manufacturer-slug>/<family-or-series-or-mpn-slug>.pdf
```

- One PDF per family/series where a single sheet covers many parts (e.g. a whole
  Murata BLM18…N1 family), else per MPN.
- Slugs are lowercase, hyphenated. Manufacturer slug is the maker (e.g. `murata`,
  `ti`, `bourns`, `panasonic`, `chemi-con`, `tt-electronics`).
- Central (not per-table) so a family sheet isn't duplicated across tables and
  survives table renames/splits (we already renamed `ferrites` → `ferrites_smt`).

Stored via Git LFS (`*.pdf` is already an LFS filter in `.gitattributes`).

## Referencing

Generators (the source of truth) set the `datasheet` column to:

```
${TERRA_EDA_LIB}/datasheets/<manufacturer>/<slug>.pdf
```

`${TERRA_EDA_LIB}` resolves to the repo root (same var used for footprints / 3D models).

## Current inventory (migrated 2026-06-14)

| File | Used by |
|------|---------|
| `datasheets/murata/blm18-n1.pdf` | ferrites_smt `run_500_murata_blm18.py` |
| `datasheets/bourns/mh-series.pdf` | ferrites_smt `run_510_bourns_mh.py` |
| `datasheets/ti/pca9306.pdf` | ic_analog `run_300_spiro_harvest.py` |
| `datasheets/panasonic/erj-series.pdf` | resistors_smt `run_220_panasonic_erj_current_sense.py` |
| `datasheets/chemi-con/kyc-series.pdf` | capacitors_electrolytic_th (new) |
| `datasheets/tt-electronics/opb733.pdf` | optoelectronics_sensors (new) |

## Backfill (tracked, deferred)

Native harvests that currently cite manufacturer URLs (TVS/connectors/op-amp/BJT from the
abc4-spiro mainboard + cartridge harvests) still need their PDFs pulled and parked, then
their generators repointed. Do this as part of the **Nexar harvest sweep** — Nexar (via
Altium creds) is our param *and* datasheet source and the creds **expire Nov 2026**, so
pull permanent datasheet copies during that sweep. See the Nexar note in memory.

CERN tables: out of scope (wind-down) — leave their web URLs.
