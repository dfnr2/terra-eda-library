from tools.generate_kicad_httplib import build_httplib


def test_httplib_config_shape():
    cfg = build_httplib()
    src = cfg["source"]
    assert src["type"] == "REST_API"
    assert src["api_version"] == "v1"
    assert src["root_url"].startswith("http://127.0.0.1:8361")
    assert src["token"] == ""
    # timeout keys must be the part/categories pair, NOT timeout_seconds
    assert "timeout_parts_seconds" in src and "timeout_categories_seconds" in src
    assert "timeout_seconds" not in src
