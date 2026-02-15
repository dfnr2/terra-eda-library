-- Terra EDA Library - Global Infrastructure Tables
-- Tags (many-to-many), config tables, and filtered views
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

-- User tags table: project-specific tags (populated by terra_tags.sql)
DROP TABLE IF EXISTS user_tags;
CREATE TABLE user_tags (
    unique_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (unique_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_user_tags_tag_uid ON user_tags(tag, unique_id);

-- Tier config: single row, sets the active tier cutoff
DROP TABLE IF EXISTS terra_tier_config;
CREATE TABLE terra_tier_config (
    tier_level INTEGER NOT NULL
);

-- Tag config: one row per active tag name
DROP TABLE IF EXISTS terra_tag_config;
CREATE TABLE terra_tag_config (
    tag TEXT NOT NULL PRIMARY KEY
);

-- Helper view: pre-compute IDs that match any active tag
CREATE VIEW IF NOT EXISTS active_tagged_ids AS
SELECT DISTINCT t.unique_id
FROM tags t
JOIN terra_tag_config c ON t.tag = c.tag
UNION
SELECT DISTINCT u.unique_id
FROM user_tags u
JOIN terra_tag_config c ON u.tag = c.tag;
