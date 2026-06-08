# Porting a CERN library/table into terra

This procedure now lives as a skill: **`skills/port-cern-library/SKILL.md`**.

It's the repeatable runbook for importing a CERN table into terra as a `cern_<name>` table
(inspect/exclude rule → schema → import generator + `unique_id` strategy → terra-owned
symbol/footprint copy → build → 3D model map → tests/audit → one-time KiCad registration),
with the hard-won gotchas. See that skill for the full steps.
