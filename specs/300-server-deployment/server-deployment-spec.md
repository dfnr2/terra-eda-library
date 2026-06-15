# Stage — Server deployment & stable asset storage

**Status:** Design for implementation. Today `make serve` runs `terra_server.py`
in the foreground from the repo working dir (port 8361). This spec adds: (1)
running the server as a systemd service or login item, (2) an install/register
step, and (3+4) a stable-asset story for datasheets and 3D STEP models.
Maintainer-on-Linux scope; a no-toolchain Windows distributable is explicitly
out of scope (see end).

## Goal

Make the terra library usable without babysitting `make serve`, and give its big
binary assets (datasheet PDFs, STEP models) stable references that don't depend
on the local server and don't bloat the git clone.

Driving constraint: **a schematic shared on GitHub is self-sufficient**. A
part's `datasheet` URL must resolve for anyone, with no terra server running and
no local install.

---

## 1. Server as a service  *(build now)*

A generated systemd unit plus an install target with two modes:

- **Login item** — `systemd --user` unit at
  `~/.config/systemd/user/terra-eda.service`, enabled with `systemctl --user
  enable --now terra-eda`. Runs as the user, no sudo. Use `loginctl
  enable-linger <user>` to keep it up without an active login session.
- **Managed service** — system unit at `/etc/systemd/system/terra-eda.service` (sudo),
  with `User=<you>`. Starts at boot regardless of login.

The unit is **generated** (absolute repo path, port, and tier baked in at
install time), not committed as-is. For now `ExecStart` is `uv run python
tools/terra_server.py --db db/terra.db --dbl terra.kicad_dbl --tier 2` with
`WorkingDirectory=<repo>`; this is the one place a future frozen binary swaps
in. Restart policy `Restart=on-failure`.

Targets:
- `make install-service MODE=user|system` — render the unit from a template, install it,
  daemon-reload, enable + start.
- `make uninstall-service MODE=user|system` — stop, disable, remove the unit.
- `make service-status` — `systemctl [--user] status terra-eda`.

A template `deploy/terra-eda.service.in` holds the unit with `@PLACEHOLDERS@`; a small
`tools/install_service.py` (or shell) renders + installs it. Pure systemd; the rendered unit
does not depend on `make`.

## 2. Install / register with KiCad  *(build now)*

`make install`:
1. Ensure the library is built (`make all`) — generates `terra.kicad_dbl`,
   `terra.kicad_httplib`, and the lib-tables.
2. **Idempotently register** terra into KiCad's *global* tables if absent: the HTTP library
   (`terra` → `terra.kicad_httplib`) in `sym-lib-table`, and `terra-symbols` /
   the footprint table. (These are already wired globally; this formalizes/repairs it and
   makes a fresh machine one command.) Detect the KiCad config dir
   (`~/.config/kicad/<ver>/`), back up the table, insert the entry only if missing.
3. Install the service (section 1) in the chosen mode.

`${TERRA_EDA_LIB}` continues to point at the repo (maintainer / #3 use case). Implemented in
Python/shell so nothing the *installed* server needs requires `make` at runtime.

---

## 3. Datasheet stable URLs  *(spec)*

**System of record: a canonical public URL we control** — because shared schematics must
resolve datasheets without the local server. Manufacturer URLs rot (the reason we cache);
the local server URL isn't portable; so parts reference our hosted copy.

- A single **`ASSET_BASE`** config value (one place, e.g. `db/schema/asset_config.json` or a
  Makefile var threaded into generators). Default now = the GitHub Releases download base for
  a pinned tag:
  `https://github.com/<owner>/terra-eda-library/releases/download/<assets-tag>`. Later = CDN
  — migration is changing `ASSET_BASE` + re-publishing + regenerating.
- Generators set `datasheet = {ASSET_BASE}/datasheets/<mfr>/<slug>.pdf`.
- `make publish-datasheets` uploads `datasheets/**` as release assets via the `gh` CLI to the
  assets tag (flattening `<mfr>/<slug>.pdf` → an asset name, since release assets are a flat
  namespace — e.g. `datasheets__<mfr>__<slug>.pdf`; the URL scheme above accounts for this).
- The repo keeps `datasheets/` (LFS) as **source of truth**; the release is the published,
  referenced copy. A check target verifies every part's `datasheet` URL has a matching asset.

Open sub-decision deferred to the plan: exact asset-name flattening + the `<assets-tag>`
lifecycle (one rolling `assets-latest` tag vs. per-release immutable tags). Recommendation:
an immutable `assets-vN` tag bumped when assets change, so old schematics keep resolving.

## 4. STEP 3D bundle  *(spec)*

STEP models leave the default git clone (they bloat it for everyone, including non-LFS users):

- `assets/3dmodels/**` becomes **gitignored** (removed from tracking; `git rm --cached`).
  Footprints keep referencing the local `${TERRA_EDA_LIB}/assets/3dmodels/<lib>.3dshapes/…`
  path the bundle populates.
- `make bundle-3d` packs `assets/3dmodels/` into `terra-3dmodels-<assets-tag>.tar.zst` and
  `make publish-3d` uploads it as a release asset.
- `make fetch-3d` (also invoked by `make install`) downloads + unpacks the bundle into
  `assets/3dmodels/`. Idempotent; verifies against a manifest/checksum.
- Source of truth for the STEP files themselves is the bundle (built from whatever produced
  them); the repo holds only the generators/footprints that reference them.

---

## Sequencing & scope

- **Build now:** sections 1 (service/login item) and 2 (install/register).
- **Spec, implement next:** sections 3 (datasheet URLs) and 4 (STEP bundle) — they touch the
  generators' `datasheet` field and the asset-tracking model, and depend on a published
  release existing, so they land as a deliberate pass (likely after a first assets release).
- **Reversibility:** every target is idempotent; service install/uninstall is symmetric;
  asset moves are reviewable git changes + reversible release operations.

## Future — full distributable (roadmap, not this build)

Sections 1–2 serve the maintainer (Linux + toolchain). The destination is a no-toolchain
distributable for colleagues on Windows. The seams above (service `ExecStart`, `ASSET_BASE`)
are deliberately the only places this roadmap changes. Target pieces, all CI-driven:

1. **Cross-platform executable** — freeze `terra_server` into a standalone binary
   (PyInstaller/Nuitka) per OS, built in **CI** (a Windows runner; or Linux + wine for the
   Windows target). This replaces `uv run python` in the service `ExecStart` (section 1) and
   removes the python/uv/make dependency for end users.
2. **Database in CI** — generate `terra.db` in CI from the scripts, zip it, and publish as a
   **release asset** (so users get the built DB without running `make`). The build is already
   deterministic from the generator scripts.
3. **PDFs as independently-managed release assets** — datasheets published separately from the
   code/DB. **Source-of-truth ladder:** maintainer's machine → GitHub Release (the §3
   `ASSET_BASE`) → CDN once stable. Same `ASSET_BASE` indirection carries through.
4. **3D models, same pattern — only if they grow.** Bundle + publish like §4, but **lower
   priority/urgency than PDFs**: most parts use standard KiCad footprints (which reference
   KiCad's *shipped* 3D models), so terra only bundles STEP for its *custom* footprints. The
   custom-footprint count grows far slower than the part/PDF count, so the 3D bundle stays
   small for a long time.

**Asset SoT ladder (general):** local machine → GitHub Release → CDN — applied independently
to the DB, PDFs, and 3D bundle as each stabilizes.

## Out of scope (this build)

- Everything in the roadmap above (executable freeze, CI DB/PDF/3D publishing, CDN).
- **macOS launchd** — the login-item/service equivalents are launchd LaunchAgent/LaunchDaemon;
  the install logic generalizes but isn't built now (this box is Linux/systemd).
