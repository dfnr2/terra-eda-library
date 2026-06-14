# tests/test_terra_convert_hierarchy.py
# Locks in terra_convert's hierarchical-sheet parsing: per-instance references
# (incl. multi-instantiated sub-sheets) and transitive Sheetfile discovery.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import terra_convert as tc  # noqa: E402


def test_instance_refs_reads_every_path():
    # A sub-sheet symbol instantiated twice -> two (path ... (reference)) entries.
    chunk = '''Device:R")
        (property "Reference" "R?")
        (instances
            (project "x"
                (path "/aaaa/bbbb" (reference "R6") (unit 1))
                (path "/aaaa/cccc" (reference "R12") (unit 1))))'''
    assert tc._instance_refs(chunk) == ["R6", "R12"]


def test_instance_refs_falls_back_to_property():
    # Older file with no instances block: use the Reference property.
    chunk = 'Device:C")\n        (property "Reference" "C3")\n'
    assert tc._instance_refs(chunk) == ["C3"]


def test_parse_one_drops_power_and_hash_refs():
    text = '''
    (symbol (lib_id "power:GND") (property "Reference" "#PWR01")
        (instances (project "x" (path "/a" (reference "#PWR01") (unit 1)))))
    (symbol (lib_id "Device:R") (property "Reference" "R1")
        (property "Value" "10k")
        (instances (project "x" (path "/a" (reference "R1") (unit 1)))))
    '''
    parts = tc._parse_one(text)
    assert [p.ref for p in parts] == ["R1"]
    assert parts[0].lib_id == "Device:R" and parts[0].value == "10k"


def test_subsheet_paths_resolve_relative_to_source(tmp_path):
    root = tmp_path / "board.kicad_sch"
    text = '(property "Sheetfile" "sub/valve.kicad_sch")'
    assert tc._subsheet_paths(text, root) == [tmp_path / "sub" / "valve.kicad_sch"]


def test_parse_schematic_follows_hierarchy(tmp_path):
    sub = tmp_path / "valve.kicad_sch"
    sub.write_text('(symbol (lib_id "Device:R") (property "Reference" "R6")'
                   ' (instances (project "x" (path "/a/b" (reference "R6") (unit 1)))))')
    root = tmp_path / "board.kicad_sch"
    root.write_text(
        '(symbol (lib_id "Device:C") (property "Reference" "C1")'
        ' (instances (project "x" (path "/a" (reference "C1") (unit 1)))))'
        '(sheet (property "Sheetname" "Valve") (property "Sheetfile" "valve.kicad_sch"))')
    refs = {p.ref for p in tc.parse_schematic(root)}
    assert refs == {"C1", "R6"}  # root symbol + sub-sheet symbol


def test_parse_schematic_visits_each_file_once(tmp_path):
    # Same Sheetfile referenced by two sheet blocks must not double-parse the file;
    # the sub-sheet's own (instances) paths are what multiply its parts.
    sub = tmp_path / "valve.kicad_sch"
    sub.write_text('(symbol (lib_id "Device:R") (property "Reference" "R?")'
                   ' (instances (project "x"'
                   ' (path "/a/b" (reference "R6") (unit 1))'
                   ' (path "/a/c" (reference "R7") (unit 1)))))')
    root = tmp_path / "board.kicad_sch"
    root.write_text(
        '(sheet (property "Sheetfile" "valve.kicad_sch"))'
        '(sheet (property "Sheetfile" "valve.kicad_sch"))')
    refs = sorted(p.ref for p in tc.parse_schematic(root))
    assert refs == ["R6", "R7"]  # both instances, file parsed once
