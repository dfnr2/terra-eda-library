-- Terra EDA Library - ferrites_smt Table Data (priority 100, source terra_sym)
-- Number of components: 2
-- Dump priority: 100
-- Source: terra_sym
-- Sorted by: unique_id
--
-- This file is auto-generated and suitable for git tracking.
-- Rows are sorted deterministically to ensure consistent diffs.
-- Table schema is in ferrites_smt_0_schema.sql
--
-- NOTE: the Murata BLM18...N1 family (incl. BLM18BD121/BD221/PG121) is now
-- produced by run_500_murata_blm18.py from the datasheet; only the non-BLM18
-- parts (Bourns MH2029, Murata BLM41) remain hand-migrated here.
--

BEGIN TRANSACTION;

INSERT INTO ferrites_smt ("unique_id", "part_locator", "mpn", "manufacturer", "variant", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "source", "dump_priority", "tier", "tags", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "pin_count", "component_height", "exclude_from_bom", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max", "temp_soldering", "impedance_at_freq", "dc_resistance", "current_rating", "power_rating", "tolerance") VALUES ('Bourns- MH2029-800Y', 'FERRITE Bourns  MH2029-800Y 80 ohm 3A', ' MH2029-800Y', 'Bourns', NULL, '0805', 'FB Bourns  MH2029-800Y 80 ohm 3A', 'Ferrite Bead, 80 ohm@100MHz, 3A', 'https://www.bourns.com/data/global/pdfs/mh.pdf', 'https://www.bourns.com', 'terra_sym:FERRITE Bourns  MH2029-800Y 80 ohm 3A', 'Inductor_SMD:L_0805_2012Metric', NULL, NULL, 'Active', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/BOUR/BOUR-E-A0004886223/BOUR-E-A0004886223-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'No', 'No', '1.1', NULL, '2026-06-13 21:56:05', '2026-06-13 21:56:05', NULL, 'terra_sym', 100, 2, NULL, NULL, NULL, NULL, NULL, NULL, '2', NULL, 0, -55.0, 150.0, -55.0, 150.0, NULL, NULL, NULL, NULL, NULL, '25%');
INSERT INTO ferrites_smt ("unique_id", "part_locator", "mpn", "manufacturer", "variant", "package", "value", "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint", "altium_symbol", "altium_footprint", "lifecycle_status", "rohs", "rohs_document_link", "allow_substitution", "tracking", "standards_version", "bom_comment", "created_at", "updated_at", "created_by", "source", "dump_priority", "tier", "tags", "sim_model_type", "sim_device", "sim_pins", "sim_model_file", "sim_params", "pin_count", "component_height", "exclude_from_bom", "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max", "temp_soldering", "impedance_at_freq", "dc_resistance", "current_rating", "power_rating", "tolerance") VALUES ('Murata- BLM41PG600SN1L', 'FERRITE Murata Ferrite Bead 60 ohm 6A 1806 BLM41PG600SN1L', ' BLM41PG600SN1L', 'Murata', NULL, '1806', 'FB Murata BLM41PG600SN1L 60 ohm 6A', 'Ferrite Bead 60ohm@100 MHz, Imax=6A', 'https://www.murata.com/en-us/products/productdata/8796739862558/ENFA0007.pdf', 'https://pim.murata.com/en-us/pim/details/?partNum=BLM41PG600SN1%23', 'terra_sym:FERRITE Murata Ferrite Bead 60 ohm 6A 1806 BLM41PG600SN1L', 'Inductor_SMD:L_1806_4516Metric_Pad1.45x1.90mm_HandSolder', NULL, NULL, 'Active', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/MURE/MURE-E-A0026527192/MURE-E-A0026527192-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'No', 'No', '1.1', NULL, '2026-06-13 21:56:05', '2026-06-13 21:56:05', NULL, 'terra_sym', 100, 2, NULL, NULL, NULL, NULL, NULL, NULL, '2', NULL, 0, -55.0, 125.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '25%');

COMMIT;
