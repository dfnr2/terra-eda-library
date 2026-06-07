-- KiCad Symbol Library SQL Script
-- Generated from: terra_sym.kicad_sym
-- Number of symbols: 3
--
-- To create the database, run:
--   sqlite3 output.db < inductors_1_migrated.sql
--

-- Create symbols table
CREATE TABLE IF NOT EXISTS inductors (
  "unique_id" TEXT PRIMARY KEY,
  "part_locator" TEXT,
  "allow_substitution" TEXT,
  "bom_comment" TEXT,
  "class" TEXT,
  "component_type" TEXT,
  "component_value" TEXT,
  "current_rating" TEXT,
  "datasheet" TEXT,
  "description" TEXT,
  "kicad_footprint" TEXT,
  "manufacturer" TEXT,
  "manufacturer_link" TEXT,
  "mpn" TEXT,
  "composition" TEXT,
  "number_of_pins" TEXT,
  "package" TEXT,
  "reference" TEXT,
  "rohs" TEXT,
  "rohs_document_link" TEXT,
  "sim_device" TEXT,
  "sim_library" TEXT,
  "sim_pins" TEXT,
  "sim_type" TEXT,
  "standards_version" TEXT,
  "kicad_symbol" TEXT,
  "temp_operating" TEXT,
  "temp_soldering" TEXT,
  "temp_storage" TEXT,
  "temp_coeff" TEXT,
  "tolerance" TEXT,
  "tracking" TEXT,
  "value" TEXT,
  "altium_footprint" TEXT,
  "altium_symbol" TEXT,
  "variant" TEXT,
  "source" TEXT,
  "dump_priority" INTEGER,
    "tier" INTEGER DEFAULT 5,
    "tags" TEXT DEFAULT '',
    "lifecycle_status" TEXT DEFAULT 'Active',
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "created_by" TEXT,
    "sim_model_type" TEXT,
    "sim_model_file" TEXT,
    "sim_params" TEXT
);

-- Insert symbols
BEGIN TRANSACTION;

INSERT INTO inductors ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Bourns-SRR6603-100ML q q', 'IND Bourns 10uH 1.1A rms SRR6603-100ML', 'No', NULL, NULL, 'Inductor', '10 uH', '1.1A rms, 40C rise, 1.5ADC, 10% drop', 'https://www.bourns.com/pdfs/SRR6603.pdf', 'Power inductor, 10 mH, 75 mOhm, 1A rms,  20% SMT 6.8x4.4mm', 'terra_sym:Coilcraft MSS7341 Shileded power inductor', 'Bourns', 'https://www.bourns.com/resources/rohs/magnetics/power-inductors-smd-shielded', 'SRR6603-100ML q q', NULL, '2', 'SMT', 'L', 'Yes', 'https://www.bourns.com/docs/rohs-cofc/cofc_srr.pdf?sfvrsn=7557d913_18', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:IND Bourns 10uH 1.1A rms SRR6603-100ML', '-40C/+125C', 'Max: 260 °C for 5 sec, Reflow: 230 °C, 50 sec.', '-40C/+125C', NULL, '30%', 'No', 'IND Bourns 10uH 1.1A rms SRR6603-100ML', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO inductors ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('Bourns-SRR1210-680M', 'IND Bourns 68uH 3A rms  SRR1210-680M ', 'No', NULL, 'shielded', 'Inductor', '68 uH', '3A rms, 40C rise, 10% drop', 'https://www.bourns.com/docs/Product-Datasheets/SRR1210.pdf', 'Power inductor, 68 mH, 102 mOhm, 3A rms,  20% SMT 12mm x 12mm', 'terra_sym:Bourns SRR1210', 'Bourns', 'https://www.bourns.com/resources/rohs/magnetics/power-inductors-smd-shielded', 'SRR1210-680M', NULL, '2', 'SMT', 'L', 'Yes', 'https://www.bourns.com/docs/rohs-cofc/cofc_srr.pdf?sfvrsn=7557d913_18', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:IND Bourns 68uH 3A rms  SRR1210-680M ', '-40C/+125C', 'Max: 260 °C for 5 sec, Reflow: 230 °C, 50 sec.', '-40C/+125C', NULL, '20%', 'No', 'IND Bourns 68uH 3A rms  SRR1210-680M', NULL, NULL, NULL, 'terra_sym', 100);
INSERT INTO inductors ("unique_id", "part_locator", "allow_substitution", "bom_comment", "class", "component_type", "component_value", "current_rating", "datasheet", "description", "kicad_footprint", "manufacturer", "manufacturer_link", "mpn", "composition", "number_of_pins", "package", "reference", "rohs", "rohs_document_link", "sim_device", "sim_library", "sim_pins", "sim_type", "standards_version", "kicad_symbol", "temp_operating", "temp_soldering", "temp_storage", "temp_coeff", "tolerance", "tracking", "value", "altium_footprint", "altium_symbol", "variant", "source", "dump_priority") VALUES ('CoilCraft-MSS7341-103ML', 'IND CoilCraft 10uH 2.8A MSS7341-103ML', 'No', NULL, NULL, 'Inductor', '10 uH', '2.8A rms, 20C rise, 1.64ADC, 10% ind. drop', 'https://www.coilcraft.com/getmedia/7b464459-a4d6-47b0-83ca-9d96d4410863/MSS7341.pdf', 'Power inductor, 10 mH, 38 mOhm, 2.8A, 20% SMT 7.1x7.1 mm', 'terra_sym:Coilcraft MSS7341 Shileded power inductor', 'CoilCraft', 'https://www.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum/mss-mos/mss7341/mss7341-103/', 'MSS7341-103ML', NULL, '2', 'SMT', 'L', 'Yes', 'https://4donline.ihs.com/images/VipMasterIC/IC/COLC/COLC-E-A0007342590/COLC-E-A0007342584-1.pdf?hkey=6D0214268300F1406B835FE51CB13195', 'L', NULL, '1=+ 2=-', NULL, '1.1', 'terra_sym:IND CoilCraft 10uH 2.8A MSS7341-103ML', '-40C/+85C', 'reflow 40 sec at max 260C', '-40C/+125C', NULL, '30%', 'No', 'IND CoilCraft 10uH 2.8A MSS7341-103ML', NULL, NULL, NULL, 'terra_sym', 100);

COMMIT;
