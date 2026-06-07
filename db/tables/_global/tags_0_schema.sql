-- Terra EDA Library - Global Infrastructure Tables
-- Tags table for part metadata/discoverability
--
-- This file is loaded BEFORE any part tables.
-- Generators populate the tags table alongside part INSERTs.

-- Tags table: many-to-many relationship between parts and tags
DROP TABLE IF EXISTS tags;
CREATE TABLE tags (
    unique_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (unique_id, tag)
);

-- Selection-direction index: given tag → unique_ids
CREATE INDEX IF NOT EXISTS idx_tags_tag_uid ON tags(tag, unique_id);
