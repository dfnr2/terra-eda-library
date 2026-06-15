"""Render + install the terra-eda systemd unit (user login-item or system service)."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "deploy/terra-eda.service.in"
UNIT_NAME = "terra-eda.service"


def render_unit(mode: str, repo, uv, port: int = 8361, tier: int = 2, user: str | None = None) -> str:
    """Fill the unit template for ``mode`` in {'user','system'}. Pure (only reads the template)."""
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
