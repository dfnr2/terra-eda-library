"""Build STEP models for terra-generated connector footprints, under FreeCAD.

Connector generators in db/tables/connectors that write their own footprints also
define ``model_specs()``: ``{footprint_name: [primitive, ...]}`` in footprint
coordinates (see db/tables/connectors/_connkit.py for the primitive list). This tool
turns each spec into a coloured STEP in assets/3dmodels/terra-connectors.3dshapes,
named after the footprint, which the footprint's ``(model ...)`` block references.

A manifest (``generated.json`` beside the models) records each spec's hash, so only
new or changed specs are rebuilt; tests/test_connector_models.py fails when a spec
and its model drift apart. Run it after changing a generator's geometry:

    make connector-models
    # i.e. QT_QPA_PLATFORM=offscreen freecad tools/make_connector_models.py

FreeCAD's GUI module is needed (headless, offscreen) because STEP colours come from
the view objects. Set TERRA_MODELS_FORCE=1 to rebuild everything, or
TERRA_MODELS_ONLY=<substring> to limit to matching footprint names.
"""
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("TERRA_EDA_LIB_ROOT", Path(__file__).resolve().parents[1]))
GEN_DIR = ROOT / "db" / "tables" / "connectors"
sys.path.insert(0, str(GEN_DIR))

import _connkit  # noqa: E402

MANIFEST = _connkit.MODEL_DIR / "generated.json"


def spec_hash(spec):
    return hashlib.sha1(json.dumps(spec, sort_keys=True).encode()).hexdigest()


def all_specs():
    """{footprint: spec} from every generator defining model_specs()."""
    specs = {}
    for path in sorted(GEN_DIR.glob("run_*.py")):
        if "model_specs" not in path.read_text():
            continue
        mod_spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(mod_spec)
        mod_spec.loader.exec_module(mod)
        for name, spec in mod.model_specs().items():
            if name in specs:
                raise SystemExit(f"{name}: model spec defined twice")
            specs[name] = [list(p) for p in spec]
    return specs


def shape_of(p):
    import FreeCAD
    import Part
    V = FreeCAD.Vector
    kind = p[0]
    if kind in ("box", "cut"):
        _, _, x0, y0, z0, x1, y1, z1 = p
        xa, xb = sorted((x0, x1))
        ya, yb = sorted((-y0, -y1))           # footprint y is down, model y is up
        za, zb = sorted((z0, z1))
        return Part.makeBox(xb - xa, yb - ya, zb - za, V(xa, ya, za))
    if kind == "cyl":
        _, _, x, y, z0, z1, d = p
        return Part.makeCylinder(d / 2, z1 - z0, V(x, -y, z0))
    if kind == "pin":
        _, _, x, y, z0, z1, w = p
        return Part.makeBox(w, w, z1 - z0, V(x - w / 2, -y - w / 2, z0))
    if kind == "hpin":
        _, _, x, y0, y1, z, w = p
        ya, yb = sorted((-y0, -y1))
        return Part.makeBox(w, yb - ya, w, V(x - w / 2, ya, z - w / 2))
    if kind == "hcyl":
        _, _, x, y0, y1, z, d = p
        ya, yb = sorted((-y0, -y1))
        return Part.makeCylinder(d / 2, yb - ya, V(x, ya, z), V(0, 1, 0))
    raise ValueError(f"unknown primitive {kind}")


def build(name, spec, out_path):
    import FreeCAD
    import ImportGui
    import Part
    doc = FreeCAD.newDocument("m")
    objs = []
    for colour in sorted({p[1] for p in spec if p[0] != "cut"}):
        shapes = [shape_of(p) for p in spec if p[1] == colour and p[0] != "cut"]
        cuts = [shape_of(p) for p in spec if p[1] == colour and p[0] == "cut"]
        if cuts:            # fuse the solids so a cut opens one clean cavity
            shape = shapes[0].fuse(shapes[1:]).removeSplitter() if len(shapes) > 1 else shapes[0]
            shape = shape.cut(Part.makeCompound(cuts))
        else:
            shape = Part.makeCompound(shapes)
        obj = doc.addObject("Part::Feature", f"{name}_{colour}".replace("-", "_")[:60])
        obj.Shape = shape
        obj.ViewObject.ShapeAppearance = (
            FreeCAD.Material(DiffuseColor=_connkit.COLOURS[colour]),)
        objs.append(obj)
    ImportGui.export(objs, str(out_path))
    FreeCAD.closeDocument(doc.Name)


def main():
    force = os.environ.get("TERRA_MODELS_FORCE") == "1"
    only = os.environ.get("TERRA_MODELS_ONLY", "")
    specs = all_specs()
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    _connkit.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    built = 0
    for name, spec in sorted(specs.items()):
        if only and only not in name:
            continue
        h = spec_hash(spec)
        out = _connkit.MODEL_DIR / f"{name}.step"
        if not force and manifest.get(name) == h and out.exists():
            continue
        build(name, spec, out)
        manifest[name] = h
        built += 1
    for stale in sorted(set(manifest) - set(specs)):
        del manifest[stale]
        (_connkit.MODEL_DIR / f"{stale}.step").unlink(missing_ok=True)
        print(f"removed {stale}")
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), indent=1) + "\n")
    print(f"connector models: {built} built, {len(specs)} specs")


try:
    main()
finally:
    try:
        import FreeCADGui
        FreeCADGui.getMainWindow().close()
    except Exception:
        pass
