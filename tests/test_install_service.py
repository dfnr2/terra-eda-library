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


def test_unit_path_user_vs_system():
    up = svc.unit_path("user")
    assert up.name == "terra-eda.service" and ".config/systemd/user" in str(up)
    sp = svc.unit_path("system")
    assert str(sp) == "/etc/systemd/system/terra-eda.service"


def test_dry_run_prints_unit_without_writing(capsys, monkeypatch):
    # dry-run must not touch the filesystem or call systemctl
    monkeypatch.setattr(svc, "_systemctl", lambda *a, **k: (_ for _ in ()).throw(AssertionError("called")))
    svc.install("user", port=8361, tier=2, dry_run=True)
    out = capsys.readouterr().out
    assert "WorkingDirectory=" in out and "terra-eda.service" in out
