"""Render + install the terra-eda systemd unit (user login-item or system service)."""
from __future__ import annotations

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
