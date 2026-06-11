# KiCad Symbol Library Database Makefile
#
# This Makefile automates the workflow for managing KiCad symbol libraries
# as SQL-based databases with git tracking support.
#
# Two-phase build:
#   Phase A: Master DB build (only when library changes)
#            db/terra.db - contains all part tables, tags, empty config, views
#   Phase B: Project DB build (per KiCad project, when config changes)
#            ${KIPRJMOD}/terra_local.db - clone of master + project config applied

# Configuration
PYTHON := uv run python
CONFIG := tools/field_mappings.yaml
VENV_MARKER := .venv/.synced

# Default tier cutoff when no terra_config.sql exists
DEFAULT_TIER := 2

# Tables with deliberately-assigned tiers; everything else is re-tiered to 0.
PARAMETRIC_TIER_TABLES := resistors_smt capacitors_smt

# Override via command line: make TIER=3 TAGS=analog,passive
TIER ?=
TAGS ?=

# ============================================================================
# Per-Table Database Architecture with Generator Support
# ============================================================================
# Directory structure:
#   db/{table}.db                              - Per-table database (generated)
#   db/tables/_global/                         - Infrastructure tables (tags, config)
#   db/tables/{table}/                         - Table source directory
#     +-- run_N_description.py                 - Generator scripts (tracked)
#     +-- {table}_N_source.sql                 - Static SQL (tracked, dump_priority=N)
#     +-- {table}_generated_N_source.sql       - Generated SQL (ignored, dump_priority=0)
#
# Dependency chain per table:
#   run_*.py -> {table}_generated_*.sql -> db/{table}.db
#     |              |                      |
#   change       rebuild                rebuild
#
# Metadata in SQL for round-trip:
#   - Static: dump_priority > 0, source = 'manual'|'vendor'|etc.
#   - Generated: dump_priority = 0, source = 'generator_name'
#   - Dump reconstructs: {table}_{priority}_{source}.sql
# ============================================================================

# Tables to exclude from the build (space-separated names), e.g.:
#   make EXCLUDE_TABLES="resistors_smt resistors_th"
# Excluded tables get no per-table DB, no rows/indexes/views in the master DB,
# and no entry in terra.kicad_dbl. Purely a build-time toggle; nothing on disk
# is moved or deleted, so omitting the flag restores the full build.
EXCLUDE_TABLES ?=

# Discover all table directories (exclude _global which is infrastructure)
TABLE_DIRS := $(filter-out db/tables/_global/,$(wildcard db/tables/*/))
TABLES := $(filter-out $(EXCLUDE_TABLES),$(patsubst db/tables/%/,%,$(TABLE_DIRS)))
DB_FILES := $(patsubst %,db/%.db,$(TABLES))

# Global infrastructure SQL (loaded before any part tables)
GLOBAL_SQL := $(sort $(wildcard db/tables/_global/*.sql))

# Part tables that get filtered views (exclude _global)
PART_TABLES := $(TABLES)

# ============================================================================
# Dynamic Per-Table Rules
# ============================================================================
# For each table, create variables and rules for:
#   - {table}-generate: run all run_*.py scripts -> {table}_generated_*.sql
#   - {table}-build: build db/{table}.db from all SQL
#   - {table}-dump: dump db/{table}.db back to static SQL files
#   - {table}-clean: remove generated SQL and database
#   - {table}-test: run pytest on test_*.py files
# ============================================================================

define TABLE_RULES
# Variables for table: $(1)
$(1)_DIR := db/tables/$(1)
$(1)_DB := db/$(1).db
$(1)_GEN_SCRIPTS := $$(sort $$(wildcard $$($(1)_DIR)/run_*.py))
$(1)_GEN_SQL := $$(patsubst $$($(1)_DIR)/run_%.py,$$($(1)_DIR)/$(1)_generated_%.sql,$$($(1)_GEN_SCRIPTS))
$(1)_STATIC_SQL := $$(filter-out %_generated_%.sql,$$(wildcard $$($(1)_DIR)/*.sql))
$(1)_ALL_SQL := $$($(1)_STATIC_SQL) $$($(1)_GEN_SQL)

# Target: generate SQL for table $(1)
.PHONY: $(1)-generate
$(1)-generate: $$($(1)_GEN_SQL)

# Rule: run_N_name.py -> {table}_generated_N_name.sql
# If ANY generator script changes, rebuild ALL generated SQL for this table
$$($(1)_DIR)/$(1)_generated_%.sql: $$($(1)_DIR)/run_%.py $$($(1)_GEN_SCRIPTS)
	@echo "Running generator: $$<"
	@cd $$($(1)_DIR) && $$(PYTHON) $$(notdir $$<)
	@echo "+ Generated: $$@"

# Target: build database for table $(1)
.PHONY: $(1)-build
$(1)-build: $$($(1)_DB)

# Rule: build db/{table}.db from all SQL files (global infra + static + generated)
$$($(1)_DB): $$(GLOBAL_SQL) $$($(1)_ALL_SQL)
	@echo "Building database: $$@"
	@mkdir -p db
	@rm -f $$@
	@if [ -z "$$($(1)_ALL_SQL)" ]; then \
		echo "Error: No SQL files found for $(1)"; \
		exit 1; \
	fi
	@cat $$(GLOBAL_SQL) $$(sort $$($(1)_ALL_SQL)) | sqlite3 $$@
	@echo "+ Built $$@ from $$(words $$($(1)_ALL_SQL)) SQL file(s)"

# Target: dump database for table $(1)
.PHONY: $(1)-dump
$(1)-dump: $$(VENV_MARKER) $$($(1)_DB)
	@echo "Dumping $(1) database to static SQL files..."
	@$$(PYTHON) tools/db_to_tables.py $$($(1)_DB) db/tables/
	@echo "Done"

# Target: clean generated files for table $(1)
.PHONY: $(1)-clean
$(1)-clean:
	@echo "Cleaning generated files for $(1)..."
	@rm -f $$($(1)_GEN_SQL)
	@rm -f $$($(1)_DB)
	@echo "Done"

# Target: test table $(1)
.PHONY: $(1)-test
$(1)-test:
	@if [ -n "$$(wildcard $$($(1)_DIR)/test_*.py)" ]; then \
		echo "Testing $(1)..."; \
		cd $$($(1)_DIR) && pytest -v; \
	else \
		echo "No tests found for $(1)"; \
	fi

endef

# ============================================================================
# Global Targets (must be before dynamic rule generation)
# ============================================================================

# Default target: build per-table DBs, master DB, kicad_dbl, and lib-tables
.PHONY: all build
all build: $(DB_FILES) db/terra.db terra.kicad_dbl lib-tables

# Generate the symbol/footprint lib-tables from the kicad_symbols/ and
# kicad_footprints/ hierarchy (registration is an output of the build).
.PHONY: lib-tables
lib-tables: $(VENV_MARKER)
	@$(PYTHON) tools/generate_lib_tables.py

# Serve the library over HTTP for KiCad's HTTP Library backend.
.PHONY: serve
serve: db/terra.db terra.kicad_dbl
	$(PYTHON) tools/terra_server.py --db db/terra.db --dbl terra.kicad_dbl --tier 2

# Generate the terra.kicad_httplib connection file (KiCad HTTP Library v1).
.PHONY: httplib
httplib terra.kicad_httplib:
	$(PYTHON) tools/generate_kicad_httplib.py terra.kicad_httplib

# Footprint maintenance pass over the copied cern-* .kicad_mod files. Two steps,
# same lifecycle moment (after a CERN PcbLib is copied / a table is built):
#   1. fix_footprint_attrs - set smd/through_hole type (per library, no DB)
#   2. apply_3d_models      - assign KiCad 3D models + alignment offsets (per
#                             table, reads db/terra.db)
# This EDITS committed source files, so it is a deliberate maintenance target,
# NOT part of all/build (which must not dirty the tree). Idempotent.
.PHONY: normalize-footprints
normalize-footprints: $(VENV_MARKER) db/terra.db
	@$(PYTHON) tools/fix_footprint_attrs.py
	@for t in $(filter cern_%,$(TABLES)); do \
		echo "3d models: $$t"; \
		$(PYTHON) tools/apply_3d_models.py --table $$t; \
	done

# Generate rules for all discovered tables
$(foreach table,$(TABLES),$(eval $(call TABLE_RULES,$(table))))

# Ensure uv environment is synced
$(VENV_MARKER): pyproject.toml
	@echo "Syncing uv environment..."
	@command -v uv >/dev/null 2>&1 || { echo "Error: uv is not installed. Install from https://docs.astral.sh/uv/"; exit 1; }
	@uv sync
	@mkdir -p .venv
	@touch $(VENV_MARKER)
	@echo "uv environment ready"

# Manual sync target
.PHONY: sync
sync: $(VENV_MARKER)

# Regenerate all _0_schema.sql files from db/schema/ sources
.PHONY: schema
schema: $(VENV_MARKER)
	@echo "Regenerating part-table schemas from db/schema/ ..."
	@$(PYTHON) tools/gen_schema.py

# Global generate target: run all table generators
.PHONY: generate
generate: $(foreach table,$(TABLES),$(table)-generate)

# ============================================================================
# Phase A: Master DB Build
# ============================================================================
# Build unified terra.db with all tables, tags, config schema, and views.
# This is the "master" database that project DBs are cloned from.

db/terra.db: $(GLOBAL_SQL) $(foreach table,$(TABLES),$($(table)_ALL_SQL))
	@echo "Building master database: $@"
	@mkdir -p db
	@rm -f $@
	@echo "  Loading global infrastructure tables..."
	@if [ -n "$(GLOBAL_SQL)" ]; then \
		cat $(GLOBAL_SQL) | sqlite3 $@; \
	fi
	@for table_dir in $$(ls -d db/tables/*/ 2>/dev/null | sort); do \
		table_name=$$(basename "$$table_dir"); \
		if [ "$$table_name" = "_global" ]; then continue; fi; \
		case " $(EXCLUDE_TABLES) " in *" $$table_name "*) echo "  - skipping $$table_name (excluded)"; continue;; esac; \
		sql_files=$$(find "$$table_dir" -name "*.sql" -type f | sort); \
		if [ -n "$$sql_files" ]; then \
			cat $$sql_files | sqlite3 $@; \
			if [ $$? -eq 0 ]; then \
				count=$$(sqlite3 $@ "SELECT COUNT(*) FROM $$table_name" 2>/dev/null || echo "0"); \
				echo "  + Added $$count rows to $$table_name"; \
			fi; \
		fi; \
	done
	@echo "  Re-tiering static/curated tables to tier 0..."
	@$(PYTHON) tools/retier_static.py $@ $(PARAMETRIC_TIER_TABLES)
	@echo "  Resolving cross-table duplicate unique_ids..."
	@$(PYTHON) tools/dedup_cross_table.py $@
	@echo "  Inserting default config (tier=$(DEFAULT_TIER), no active tags)..."
	@sqlite3 $@ "INSERT OR IGNORE INTO terra_tier_config VALUES ($(DEFAULT_TIER));"
	@echo "  Creating tier indexes..."
	@for table_name in $(PART_TABLES); do \
		sqlite3 $@ "CREATE INDEX IF NOT EXISTS idx_$${table_name}_tier_uid ON $$table_name(tier, unique_id);" 2>/dev/null || true; \
	done
	@echo "  Creating filtered views..."
	@for table_name in $(PART_TABLES); do \
		has_tier=$$(sqlite3 $@ "SELECT COUNT(*) FROM pragma_table_info('$$table_name') WHERE name='tier';"); \
		if [ "$$has_tier" = "1" ]; then \
			sqlite3 $@ "CREATE VIEW IF NOT EXISTS $${table_name}_v AS \
				SELECT p.* FROM $$table_name p \
				LEFT JOIN active_tagged_ids a ON a.unique_id = p.unique_id \
				WHERE p.tier <= (SELECT COALESCE(MAX(tier_level), $(DEFAULT_TIER)) FROM terra_tier_config) \
				   OR a.unique_id IS NOT NULL;"; \
		else \
			sqlite3 $@ "CREATE VIEW IF NOT EXISTS $${table_name}_v AS SELECT * FROM $$table_name;"; \
		fi; \
	done
	@echo "  Tier distribution:"
	@for table_name in $(PART_TABLES); do \
		dist=$$(sqlite3 $@ "SELECT tier, COUNT(*) FROM $$table_name GROUP BY tier ORDER BY tier" 2>/dev/null | tr '\n' ' ' || true); \
		if [ -n "$$dist" ]; then \
			echo "    $$table_name: $$dist"; \
		fi; \
	done
	@tag_count=$$(sqlite3 $@ "SELECT COUNT(*) FROM tags" 2>/dev/null || echo "0"); \
	echo "  Tags: $$tag_count entries"
	@echo "+ Built $@ with $(words $(TABLES)) tables"

# ============================================================================
# Phase B: Project DB Build
# ============================================================================
# Build a project-local DB by cloning the master and applying project config.
# Usage: make project-db KIPRJMOD=/path/to/kicad/project
#
# Inputs (optional, in ${KIPRJMOD}/):
#   terra_config.sql  - tier cutoff and active tags
#   terra_tags.sql    - user-specific part tags

.PHONY: project-db
project-db: db/terra.db
ifndef KIPRJMOD
	$(error KIPRJMOD is not set. Usage: make project-db KIPRJMOD=/path/to/project)
endif
	@echo "Building project database: $(KIPRJMOD)/terra_local.db"
	@echo "  Cloning master database..."
	@cp db/terra.db "$(KIPRJMOD)/terra_local.db.tmp"
	@if [ -f "$(KIPRJMOD)/terra_config.sql" ]; then \
		echo "  Applying project config: $(KIPRJMOD)/terra_config.sql"; \
		sqlite3 "$(KIPRJMOD)/terra_local.db.tmp" < "$(KIPRJMOD)/terra_config.sql"; \
	else \
		echo "  No terra_config.sql found, using defaults (tier=$(DEFAULT_TIER))"; \
	fi
	@if [ -f "$(KIPRJMOD)/terra_tags.sql" ]; then \
		echo "  Applying user tags: $(KIPRJMOD)/terra_tags.sql"; \
		sqlite3 "$(KIPRJMOD)/terra_local.db.tmp" < "$(KIPRJMOD)/terra_tags.sql"; \
	else \
		echo "  No terra_tags.sql found, no user tags"; \
	fi
ifneq ($(TIER),)
	@echo "  Overriding tier to $(TIER)"
	@sqlite3 "$(KIPRJMOD)/terra_local.db.tmp" "DELETE FROM terra_tier_config; INSERT INTO terra_tier_config VALUES ($(TIER));"
endif
ifneq ($(TAGS),)
	@echo "  Overriding active tags to $(TAGS)"
	@sqlite3 "$(KIPRJMOD)/terra_local.db.tmp" "DELETE FROM terra_tag_config; $(foreach tag,$(subst $(comma), ,$(TAGS)),INSERT INTO terra_tag_config VALUES ('$(tag)');)"
endif
	@sqlite3 "$(KIPRJMOD)/terra_local.db.tmp" "PRAGMA journal_mode=WAL;" > /dev/null
	@mv "$(KIPRJMOD)/terra_local.db.tmp" "$(KIPRJMOD)/terra_local.db"
	@tier_val=$$(sqlite3 "$(KIPRJMOD)/terra_local.db" "SELECT tier_level FROM terra_tier_config LIMIT 1" 2>/dev/null || echo "$(DEFAULT_TIER)"); \
	tag_count=$$(sqlite3 "$(KIPRJMOD)/terra_local.db" "SELECT COUNT(*) FROM terra_tag_config" 2>/dev/null || echo "0"); \
	tagged_ids=$$(sqlite3 "$(KIPRJMOD)/terra_local.db" "SELECT COUNT(*) FROM active_tagged_ids" 2>/dev/null || echo "0"); \
	echo "  Config: tier<=$$tier_val, $$tag_count active tags, $$tagged_ids tagged IDs"
	@echo "+ Built $(KIPRJMOD)/terra_local.db"

# Comma helper for $(subst)
comma := ,

# Generate unified terra.kicad_dbl file
terra.kicad_dbl: $(VENV_MARKER) db/terra.db
	@echo "Generating terra.kicad_dbl..."
	@$(PYTHON) tools/generate_kicad_dbl_files.py db/terra.db
	@echo "Done"

# Convert KiCad symbol library to SQL (initial import)
# Pattern: terra_sym.kicad_sym -> db/terra.sql
db/%.sql: %_sym.kicad_sym $(CONFIG)
	@echo "Converting symbol library to SQL: $< -> $@"
	@mkdir -p db
	@$(PYTHON) tools/kicad_sym_to_db.py $< $@ --config $(CONFIG)
	@echo "Done: $@"

# Dump all databases back to static SQL files
.PHONY: dump
dump: $(foreach table,$(TABLES),$(table)-dump)
	@echo "All tables dumped. Review changes with 'git diff db/tables/' before committing."

# Verify round-trip consistency
# Process: Static SQL -> [Generate] -> DB -> Dump -> Compare Static SQL
# Generated SQL (source=''|NULL) should NOT appear in dump
.PHONY: verify
verify: $(VENV_MARKER)
	@echo "Verifying round-trip consistency..."
	@echo "  Step 1: Save checksums of current static SQL files (excluding *_generated_*)"
	@rm -f /tmp/terra_checksums_before.txt
	@for table_dir in $(TABLE_DIRS); do \
		for sql in $$table_dir/*.sql; do \
			if [ -f "$$sql" ] && [[ "$$(basename $$sql)" != *_generated_* ]]; then \
				md5sum "$$sql" >> /tmp/terra_checksums_before.txt; \
			fi; \
		done; \
	done
	@echo "  Step 2: Clean and rebuild (run generators, build DBs)"
	@$(MAKE) clean
	@$(MAKE) all
	@echo "  Step 3: Dump databases back to static SQL"
	@$(MAKE) dump
	@echo "  Step 4: Compare checksums of dumped static SQL files"
	@rm -f /tmp/terra_checksums_after.txt
	@for table_dir in $(TABLE_DIRS); do \
		for sql in $$table_dir/*.sql; do \
			if [ -f "$$sql" ] && [[ "$$(basename $$sql)" != *_generated_* ]]; then \
				md5sum "$$sql" >> /tmp/terra_checksums_after.txt; \
			fi; \
		done; \
	done
	@if diff /tmp/terra_checksums_before.txt /tmp/terra_checksums_after.txt > /dev/null 2>&1; then \
		echo "Round-trip verification passed."; \
		rm -f /tmp/terra_checksums_before.txt /tmp/terra_checksums_after.txt; \
	else \
		echo "X Round-trip verification failed!"; \
		echo "Static SQL files changed after dump:"; \
		diff /tmp/terra_checksums_before.txt /tmp/terra_checksums_after.txt || true; \
		rm -f /tmp/terra_checksums_before.txt /tmp/terra_checksums_after.txt; \
		exit 1; \
	fi

# Clean generated files (per-table generated SQL + databases)
.PHONY: clean
clean: $(foreach table,$(TABLES),$(table)-clean)
	@echo "Cleaning temporary files..."
	@rm -f db/*_test.sql db/*_test.db
	@rm -f db/terra.db
	@rm -f terra_*.kicad_dbl
	@rm -f *.kicad_dbl
	@echo "Done. Static SQL files and venv preserved."

# Clean everything including venv (use with caution!)
.PHONY: distclean
distclean: clean
	@echo "Cleaning all generated files including venv..."
	@rm -rf .venv
	@echo "Done."

# Show status
.PHONY: status
status:
	@echo "Terra EDA Library Status"
	@echo "========================"
	@echo ""
	@echo "Discovered Tables: $(TABLES)"
	@echo ""
	@echo "Per-Table Status:"
	@for table in $(TABLES); do \
		echo ""; \
		echo "  Table: $$table"; \
		table_dir="db/tables/$$table"; \
		gen_scripts=$$(ls $$table_dir/run_*.py 2>/dev/null | wc -l | tr -d ' '); \
		static_sql=$$(ls $$table_dir/$${table}_[0-9]*.sql 2>/dev/null | grep -v generated | wc -l | tr -d ' '); \
		gen_sql=$$(ls $$table_dir/$${table}_generated_*.sql 2>/dev/null | wc -l | tr -d ' '); \
		echo "    Generator scripts: $$gen_scripts"; \
		echo "    Static SQL files:  $$static_sql"; \
		echo "    Generated SQL:     $$gen_sql"; \
		db_file="db/$$table.db"; \
		if [ -f "$$db_file" ]; then \
			size=$$(du -h "$$db_file" | cut -f1); \
			count=$$(sqlite3 "$$db_file" "SELECT COUNT(*) FROM $$table" 2>/dev/null || echo "?"); \
			echo "    Database:          $$db_file ($$count rows, $$size)"; \
		else \
			echo "    Database:          not built"; \
		fi; \
	done
	@echo ""
	@if [ -f "db/terra.db" ]; then \
		echo "Master DB: db/terra.db"; \
		tier_val=$$(sqlite3 db/terra.db "SELECT tier_level FROM terra_tier_config LIMIT 1" 2>/dev/null || echo "?"); \
		tag_count=$$(sqlite3 db/terra.db "SELECT COUNT(*) FROM tags" 2>/dev/null || echo "?"); \
		echo "  Default tier: $$tier_val"; \
		echo "  Tag entries: $$tag_count"; \
		echo "  Tag distribution:"; \
		sqlite3 db/terra.db "SELECT tag, COUNT(*) FROM tags GROUP BY tag ORDER BY tag" 2>/dev/null | while read line; do \
			echo "    $$line"; \
		done; \
	fi
	@echo ""

# Help target
help:
	@echo "Terra EDA Library - Multi-Table Database Makefile"
	@echo "=================================================="
	@echo ""
	@echo "Two-Phase Build Architecture:"
	@echo "  Phase A: Master DB    db/terra.db (all tables + tags + views)"
	@echo "  Phase B: Project DB   \$${KIPRJMOD}/terra_local.db (master + config)"
	@echo ""
	@echo "Targets:"
	@echo "  make                  Build per-table DBs, master DB, and .kicad_dbl"
	@echo "  make project-db KIPRJMOD=/path  Build project-local DB from master"
	@echo "  make generate         Run all generator scripts"
	@echo "  make normalize-footprints  Set footprint types + assign 3D models (edits cern-* .kicad_mod)"
	@echo "  make sync             Ensure uv environment is set up"
	@echo "  make dump             Dump databases back to db/tables/ structure"
	@echo "  make verify           Verify round-trip consistency (SQL->DB->SQL->DB)"
	@echo "  make status           Show status of all tables and database"
	@echo "  make clean            Remove generated files (keep SQL and venv)"
	@echo "  make distclean        Remove all generated files including venv"
	@echo "  make help             Show this help"
	@echo ""
	@echo "Override tier/tags for project-db:"
	@echo "  make project-db KIPRJMOD=/path TIER=3 TAGS=analog,passive"
	@echo ""
	@echo "Workflow:"
	@echo "  1. Build master:  make"
	@echo "  2. Build project: make project-db KIPRJMOD=\$$KIPRJMOD"
	@echo "  3. Edit DB:       sqlite3 db/terra.db"
	@echo "  4. Dump:          make dump"
	@echo "  5. Commit:        git diff db/tables/ && git add ..."

.PHONY: all sync schema dump verify clean distclean status help project-db normalize-footprints
