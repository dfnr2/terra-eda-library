# tests/test_keyword_import_mapping.py
# A KiCad symbol's `ki_keywords` (part-search terms) must survive import and land
# in the `keywords` column, while all other ki_* internals are still dropped.
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("k2db", ROOT / "tools/kicad_sym_to_db.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_ki_keywords_routes_to_keywords_column():
    m = _load()
    fm, patterns, edits = m.load_config(ROOT / "tools/field_mappings.yaml")
    fields = {"ki_keywords", "ki_description", "ki_locked", "MPN", "Value"}

    kept = m.apply_column_edits(fields, edits)
    assert "ki_keywords" in kept, "ki_keywords must be kept (it is part-search metadata)"
    assert "ki_description" not in kept and "ki_locked" not in kept, "other ki_* stay removed"

    mapping = m.create_field_mapping(kept, fm, patterns)
    assert mapping["ki_keywords"] == "keywords", \
        f"ki_keywords should map to the keywords column, got {mapping['ki_keywords']!r}"
