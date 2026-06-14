-- db/schema/types/test_points.sql
-- Canonical parametric tail for test points (test_points).
    tp_style TEXT,          -- 'loop' | 'pad' | 'smt-pad' | 'thru-hole' | 'miniature'
    pad_diameter_mm REAL,   -- pad / loop diameter (mm)
    mount TEXT,             -- 'SMT' | 'THT'
    color TEXT              -- insulation / keying color if functionally relevant
