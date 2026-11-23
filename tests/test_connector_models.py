"""Generated connector 3D models stay in step with their generators' geometry.

tools/make_connector_models.py builds a STEP per footprint from each generator's
``model_specs()`` and records the spec hash in generated.json. These tests fail when a
spec changes without the models being rebuilt (run ``make connector-models``), when a
model is missing, or when a terra connector footprint references a model that does not
exist.
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN_DIR = ROOT / "db" / "tables" / "connectors"
MODEL_DIR = ROOT / "assets" / "3dmodels" / "terra-connectors.3dshapes"
FP_DIR = ROOT / "kicad_footprints" / "terra_footprints_connectors.pretty"
sys.path.insert(0, str(GEN_DIR))


def _specs():
    specs = {}
    for path in sorted(GEN_DIR.glob("run_*.py")):
        if "model_specs" not in path.read_text():
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name, s in mod.model_specs().items():
            specs[name] = [list(p) for p in s]
    return specs


def _hash(spec):
    return hashlib.sha1(json.dumps(spec, sort_keys=True).encode()).hexdigest()


@pytest.fixture(scope="module")
def specs():
    return _specs()


def test_every_spec_has_a_current_model(specs):
    manifest = json.loads((MODEL_DIR / "generated.json").read_text())
    stale = [n for n, s in specs.items() if manifest.get(n) != _hash(s)]
    missing = [n for n in specs if not (MODEL_DIR / f"{n}.step").exists()]
    assert not stale, f"rebuild with `make connector-models`: {stale[:5]}"
    assert not missing, f"missing models: {missing[:5]}"


def test_footprint_model_refs_resolve():
    ref = re.compile(r'\(model "\$\{TERRA_EDA_LIB\}/assets/3dmodels/'
                     r'terra-connectors\.3dshapes/([^"]+)"')
    broken = []
    for fp in sorted(FP_DIR.glob("*.kicad_mod")):
        for m in ref.finditer(fp.read_text()):
            if not (MODEL_DIR / m.group(1)).exists():
                broken.append(f"{fp.stem} -> {m.group(1)}")
    assert not broken, broken[:5]


def test_specs_use_known_colours(specs):
    import _connkit
    bad = {p[1] for s in specs.values() for p in s} - set(_connkit.COLOURS)
    assert not bad, bad
