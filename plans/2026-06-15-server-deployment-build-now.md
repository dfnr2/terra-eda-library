# Terra Server Deployment (build-now) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run `terra_server.py` as a systemd service (system/managed) or login item (systemd --user), and add `make install` that idempotently registers terra into KiCad's global library tables.

**Architecture:** A committed unit *template* (`deploy/terra-eda.service.in`) is rendered with the repo path / uv path / port / tier and installed by `tools/install_service.py` in `user` or `system` mode. A separate `tools/register_kicad.py` idempotently inserts terra's HTTP + nested sym/fp lib entries into KiCad's global tables. Makefile targets wire both. Pure logic (unit rendering, lib-table insertion, config-dir detection) is unit-tested; the `systemctl`/file side effects are thin wrappers exercised via a `--dry-run`.

**Tech Stack:** Python 3 (stdlib only), pytest (existing suite, run via `uv run pytest`), systemd, GNU Make.

**Scope:** Spec §1 (service/login item) + §2 (install/register) of `specs/300-server-deployment/server-deployment-spec.md`. §3 (datasheet URLs) and §4 (STEP bundle) are a later plan.

---

### Task 1: systemd unit template

**Files:**
- Create: `deploy/terra-eda.service.in`

- [ ] **Step 1: Create the template**

```ini
[Unit]
Description=Terra EDA Library HTTP server
After=network.target

[Service]
Type=simple
@USER_LINE@WorkingDirectory=@REPO@
ExecStart=@UV@ run python tools/terra_server.py --db db/terra.db --dbl terra.kicad_dbl --tier @TIER@ --host 127.0.0.1 --port @PORT@
Restart=on-failure
RestartSec=2

[Install]
WantedBy=@WANTEDBY@
```

- [ ] **Step 2: Commit**

```bash
git add deploy/terra-eda.service.in
git commit -m "add systemd unit template for terra server"
```

---

### Task 2: render the unit (pure)

**Files:**
- Create: `tools/install_service.py`
- Test: `tests/test_install_service.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_install_service.py
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import install_service as svc  # noqa: E402


def test_render_user_unit_has_no_user_line_and_default_target():
    u = svc.render_unit("user", repo="/home/dave/terra", uv="/usr/bin/uv", port=8361, tier=2)
    assert "User=" not in u
    assert "WantedBy=default.target" in u
    assert "WorkingDirectory=/home/dave/terra" in u
    assert "/usr/bin/uv run python tools/terra_server.py" in u
    assert "--port 8361" in u and "--tier 2" in u


def test_render_system_unit_has_user_line_and_multiuser_target():
    u = svc.render_unit("system", repo="/opt/terra", uv="/usr/bin/uv", port=9000, tier=3, user="dave")
    assert "User=dave" in u
    assert "WantedBy=multi-user.target" in u
    assert "--port 9000" in u and "--tier 3" in u
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_install_service.py -q`
Expected: FAIL (`ModuleNotFoundError: install_service` or `AttributeError: render_unit`)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/install_service.py
"""Render + install the terra-eda systemd unit (user login-item or system service)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "deploy/terra-eda.service.in"
UNIT_NAME = "terra-eda.service"


def render_unit(mode: str, repo, uv, port: int = 8361, tier: int = 2, user: str | None = None) -> str:
    """Fill the unit template for ``mode`` in {'user','system'}. Pure (no I/O beyond the template read)."""
    if mode not in ("user", "system"):
        raise ValueError(f"mode must be 'user' or 'system', got {mode!r}")
    text = TEMPLATE.read_text()
    if mode == "system":
        user_line, wantedby = f"User={user}\n", "multi-user.target"
    else:
        user_line, wantedby = "", "default.target"
    return (text.replace("@USER_LINE@", user_line)
                .replace("@REPO@", str(repo))
                .replace("@UV@", str(uv))
                .replace("@PORT@", str(port))
                .replace("@TIER@", str(tier))
                .replace("@WANTEDBY@", wantedby))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_install_service.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/install_service.py tests/test_install_service.py
git commit -m "install_service: render systemd unit (user/system)"
```

---

### Task 3: unit path + install/uninstall/status CLI

**Files:**
- Modify: `tools/install_service.py`
- Test: `tests/test_install_service.py`

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_install_service.py
def test_unit_path_user_vs_system():
    up = svc.unit_path("user")
    assert up.name == "terra-eda.service" and ".config/systemd/user" in str(up)
    sp = svc.unit_path("system")
    assert str(sp) == "/etc/systemd/system/terra-eda.service"


def test_dry_run_prints_unit_without_writing(capsys, monkeypatch, tmp_path):
    # dry-run must not touch the filesystem or call systemctl
    monkeypatch.setattr(svc, "_systemctl", lambda *a, **k: (_ for _ in ()).throw(AssertionError("called")))
    svc.install("user", port=8361, tier=2, dry_run=True)
    out = capsys.readouterr().out
    assert "WorkingDirectory=" in out and "terra-eda.service" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_install_service.py -q`
Expected: FAIL (`AttributeError: unit_path` / `install`)

- [ ] **Step 3: Write minimal implementation**

Append to `tools/install_service.py`:

```python
import argparse
import os
import shutil
import subprocess
import sys


def unit_path(mode: str) -> Path:
    if mode == "system":
        return Path("/etc/systemd/system") / UNIT_NAME
    return Path.home() / ".config" / "systemd" / "user" / UNIT_NAME


def _systemctl(mode: str, *args: str) -> int:
    cmd = ["systemctl"] + (["--user"] if mode == "user" else []) + list(args)
    return subprocess.run(cmd, check=False).returncode


def install(mode: str, port: int = 8361, tier: int = 2, dry_run: bool = False) -> None:
    uv = shutil.which("uv") or "uv"
    user = os.environ.get("SUDO_USER") or os.environ.get("USER") or os.environ.get("LOGNAME")
    unit = render_unit(mode, ROOT, uv, port, tier, user)
    dest = unit_path(mode)
    if dry_run:
        print(f"# would write {dest}\n{unit}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(unit)
    print(f"wrote {dest}")
    _systemctl(mode, "daemon-reload")
    _systemctl(mode, "enable", "--now", UNIT_NAME)
    print(f"enabled + started terra-eda ({mode} mode)")


def uninstall(mode: str) -> None:
    _systemctl(mode, "disable", "--now", UNIT_NAME)
    dest = unit_path(mode)
    if dest.exists():
        dest.unlink()
        print(f"removed {dest}")
    _systemctl(mode, "daemon-reload")


def status(mode: str) -> None:
    _systemctl(mode, "status", UNIT_NAME)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Install the terra-eda systemd service / login item.")
    ap.add_argument("action", choices=["install", "uninstall", "status"])
    ap.add_argument("--mode", choices=["user", "system"], default="user")
    ap.add_argument("--port", type=int, default=8361)
    ap.add_argument("--tier", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if a.action == "install":
        install(a.mode, a.port, a.tier, a.dry_run)
    elif a.action == "uninstall":
        uninstall(a.mode)
    else:
        status(a.mode)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_install_service.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Verify the dry-run end-to-end**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run python tools/install_service.py install --mode user --dry-run`
Expected: prints `# would write …/terra-eda.service` followed by the rendered unit (no files written, no systemctl call).

- [ ] **Step 6: Commit**

```bash
git add tools/install_service.py tests/test_install_service.py
git commit -m "install_service: unit path, install/uninstall/status, dry-run CLI"
```

---

### Task 4: idempotent KiCad lib-table insert (pure)

**Files:**
- Create: `tools/register_kicad.py`
- Test: `tests/test_register_kicad.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_register_kicad.py
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import register_kicad as rk  # noqa: E402

TABLE = '(sym_lib_table\n  (version 7)\n  (lib (name "Device")(type "KiCad")(uri "x")(options "")(descr ""))\n)\n'
LINE = '(lib (name "terra")(type "HTTP")(uri "${TERRA_EDA_LIB}/terra.kicad_httplib")(options "")(descr ""))'


def test_insert_when_missing():
    new, changed = rk.ensure_lib_entry(TABLE, "terra", LINE)
    assert changed is True
    assert '(name "terra")' in new
    assert new.count("(lib (name") == 2          # original + inserted
    assert new.rstrip().endswith(")")             # still closed


def test_noop_when_present():
    once, _ = rk.ensure_lib_entry(TABLE, "terra", LINE)
    twice, changed = rk.ensure_lib_entry(once, "terra", LINE)
    assert changed is False
    assert twice == once
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_register_kicad.py -q`
Expected: FAIL (`ModuleNotFoundError` / `AttributeError: ensure_lib_entry`)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/register_kicad.py
"""Idempotently register terra's libraries into KiCad's global lib tables."""
from __future__ import annotations

from pathlib import Path


def ensure_lib_entry(table_text: str, name: str, line: str) -> tuple[str, bool]:
    """Insert ``line`` before the table's final ')' if no lib named ``name`` exists.

    Returns (new_text, changed). Idempotent: a second call with the same name is a no-op.
    """
    if f'(name "{name}")' in table_text:
        return table_text, False
    close = table_text.rstrip().rfind(")")
    if close < 0:
        raise ValueError("not a lib table (no closing paren)")
    return table_text[:close] + "  " + line + "\n" + table_text[close:], True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_register_kicad.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/register_kicad.py tests/test_register_kicad.py
git commit -m "register_kicad: idempotent lib-table insert"
```

---

### Task 5: KiCad config detection + register orchestration

**Files:**
- Modify: `tools/register_kicad.py`
- Test: `tests/test_register_kicad.py`

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_register_kicad.py
def test_kicad_config_dir_picks_highest_version(tmp_path):
    base = tmp_path / "kicad"
    for v in ("8.0", "9.0", "10.0"):
        (base / v).mkdir(parents=True)
    assert rk.kicad_config_dir(base).name == "10.0"


def test_register_inserts_into_both_tables(tmp_path):
    cfg = tmp_path / "kicad" / "10.0"
    cfg.mkdir(parents=True)
    (cfg / "sym-lib-table").write_text('(sym_lib_table\n  (version 7)\n)\n')
    (cfg / "fp-lib-table").write_text('(fp_lib_table\n  (version 7)\n)\n')
    changed = rk.register(cfg)
    assert changed
    sym = (cfg / "sym-lib-table").read_text()
    assert '(name "terra")' in sym and '(name "terra-symbols")' in sym
    assert (cfg / "fp-lib-table").read_text().count('(name "terra-footprints")') == 1
    # backups written
    assert (cfg / "sym-lib-table.terra.bak").exists()
    # idempotent: second run makes no changes
    assert rk.register(cfg) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_register_kicad.py -q`
Expected: FAIL (`AttributeError: kicad_config_dir` / `register`)

- [ ] **Step 3: Write minimal implementation**

Append to `tools/register_kicad.py`:

```python
import sys

# (name, target table filename, lib line) — uri uses ${TERRA_EDA_LIB}, resolved by KiCad.
ENTRIES = [
    ("terra", "sym-lib-table",
     '(lib (name "terra")(type "HTTP")(uri "${TERRA_EDA_LIB}/terra.kicad_httplib")(options "")(descr "terra HTTP library"))'),
    ("terra-symbols", "sym-lib-table",
     '(lib (name "terra-symbols")(type "Table")(uri "${TERRA_EDA_LIB}/kicad_symbols/sym-lib-table")(options "")(descr "terra + cern symbols"))'),
    ("terra-footprints", "fp-lib-table",
     '(lib (name "terra-footprints")(type "Table")(uri "${TERRA_EDA_LIB}/kicad_footprints/fp-lib-table")(options "")(descr "terra + cern footprints"))'),
]


def kicad_config_dir(base: Path | None = None) -> Path:
    """Highest-versioned KiCad config dir under ``base`` (default ~/.config/kicad)."""
    base = base or (Path.home() / ".config" / "kicad")
    versions = [d for d in base.iterdir() if d.is_dir() and d.name[0].isdigit()]
    if not versions:
        raise FileNotFoundError(f"no KiCad config dir under {base}")
    return max(versions, key=lambda d: tuple(int(x) for x in d.name.split(".") if x.isdigit()))


def register(cfg: Path) -> list[str]:
    """Ensure terra entries in cfg's sym/fp tables. Returns names added (empty = no-op)."""
    added: list[str] = []
    for table in {e[1] for e in ENTRIES}:
        path = cfg / table
        if not path.exists():
            continue
        text = path.read_text()
        new = text
        table_added = []
        for name, tbl, line in ENTRIES:
            if tbl != table:
                continue
            new, changed = ensure_lib_entry(new, name, line)
            if changed:
                table_added.append(name)
        if table_added:
            path.with_suffix(path.suffix + ".terra.bak").write_text(text)
            path.write_text(new)
            added += table_added
    return added


def main(argv=None) -> None:
    cfg = kicad_config_dir()
    added = register(cfg)
    print(f"registered into {cfg}: {added or 'nothing (already present)'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/test_register_kicad.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/register_kicad.py tests/test_register_kicad.py
git commit -m "register_kicad: config detection + idempotent register into sym/fp tables"
```

---

### Task 6: Makefile targets

**Files:**
- Modify: `Makefile` (append targets; add to `.PHONY`)

- [ ] **Step 1: Add the targets**

Append to `Makefile`:

```makefile
# --- Deployment: service / login item + KiCad registration ---
MODE ?= user
PORT ?= 8361
TIER ?= 2

.PHONY: install install-service uninstall-service service-status register-kicad
install: all register-kicad install-service
	@echo "Installed: KiCad registered + terra-eda service ($(MODE) mode)."

register-kicad: $(VENV_MARKER)
	@$(PYTHON) tools/register_kicad.py

install-service: $(VENV_MARKER)
	@$(PYTHON) tools/install_service.py install --mode $(MODE) --port $(PORT) --tier $(TIER)

uninstall-service: $(VENV_MARKER)
	@$(PYTHON) tools/install_service.py uninstall --mode $(MODE)

service-status:
	@$(PYTHON) tools/install_service.py status --mode $(MODE)
```

- [ ] **Step 2: Verify the dry path resolves (no install yet)**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run python tools/install_service.py install --mode user --dry-run | head -5`
Expected: prints the rendered unit header (`[Unit] … Description=Terra EDA Library HTTP server`).

- [ ] **Step 3: Confirm the help lists the new targets (if help enumerates them)**

Run: `cd /users/dave/vsrc/terra-eda-library && grep -nE "install-service|register-kicad" Makefile`
Expected: shows the new targets.

- [ ] **Step 4: Commit**

```bash
git add Makefile
git commit -m "make: install / install-service / uninstall-service / service-status targets"
```

---

### Task 7: docs + full verification

**Files:**
- Modify: `PROCESSES.md` (add a "Running as a service" section)

- [ ] **Step 1: Document the workflow**

Add to `PROCESSES.md` under a new `## Running the server as a service` heading:

```markdown
## Running the server as a service

`make serve` runs the server in the foreground (dev). To keep it running:

- **Login item (per-user, no sudo):** `make install-service MODE=user`
  (starts at login; `loginctl enable-linger $USER` to run without an active session).
- **Managed service (system-wide, boot):** `sudo make install-service MODE=system`.
- Status: `make service-status [MODE=user|system]`. Remove: `make uninstall-service MODE=…`.

`make install` does the lot: build + register terra into KiCad's global lib tables
(idempotent) + install the service in `MODE` (default `user`). Override port/tier with
`PORT=` / `TIER=`. Preview the unit without touching the system:
`uv run python tools/install_service.py install --mode user --dry-run`.
```

- [ ] **Step 2: Run the full test suite**

Run: `cd /users/dave/vsrc/terra-eda-library && uv run pytest tests/ -q`
Expected: PASS (previous count + 8 new: 4 install_service + 4 register_kicad).

- [ ] **Step 3: Smoke-test the real user-mode install (if a user systemd bus is available)**

Run: `cd /users/dave/vsrc/terra-eda-library && make install-service MODE=user && make service-status MODE=user`
Expected: unit written to `~/.config/systemd/user/terra-eda.service`, enabled+started, status shows `active (running)`. If `systemctl --user` reports "Failed to connect to bus" (no user session bus in this environment), note it and rely on the dry-run + unit tests instead — do NOT mark this step blocking.

- [ ] **Step 4: Commit**

```bash
git add PROCESSES.md
git commit -m "docs: running the terra server as a service / login item"
```

---

## Notes for the implementer

- **System mode needs root:** writing `/etc/systemd/system/` and `systemctl` (no `--user`) require `sudo` — run `sudo make install-service MODE=system`. User mode needs no sudo.
- **`$(PYTHON)` / `$(VENV_MARKER)`** are existing Makefile vars (`uv run python` and the uv-sync marker) — reuse them, don't redefine.
- **`${TERRA_EDA_LIB}`** stays pointing at the repo (maintainer use case); registration only touches KiCad's lib tables, not that env var.
- Keep stdlib-only in both tools (no new deps).
