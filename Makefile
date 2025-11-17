# KiCad Symbol Library Database Makefile
#
# This Makefile automates the workflow for managing KiCad symbol libraries
# as SQL-based databases with git tracking support.

# Configuration
PYTHON := uv run python
CONFIG := tools/field_mappings.yaml
VENV_MARKER := .venv/.synced

# ============================================================================
# Per-Table Database Architecture with Generator Support
# ============================================================================
# Directory structure:
#   db/{table}.db                              - Per-table database (generated)
#   db/tables/{table}/                         - Table source directory
#     ├── run_N_description.py                 - Generator scripts (tracked)
#     ├── {table}_N_source.sql                 - Static SQL (tracked, dump_priority=N)
#     └── {table}_generated_N_source.sql       - Generated SQL (ignored, dump_priority=0)
#
# Dependency chain per table:
#   run_*.py → {table}_generated_*.sql → db/{table}.db
#     ↓              ↓                      ↓
#   change       rebuild                rebuild
#
# Metadata in SQL for round-trip:
#   - Static: dump_priority > 0, source = 'manual'|'vendor'|etc.
#   - Generated: dump_priority = 0, source = 'generator_name'
#   - Dump reconstructs: {table}_{priority}_{source}.sql
# ============================================================================

# Discover all table directories
TABLE_DIRS := $(wildcard db/tables/*/)
TABLES := $(patsubst db/tables/%/,%,$(TABLE_DIRS))
DB_FILES := $(patsubst %,db/%.db,$(TABLES))

# ============================================================================
# Dynamic Per-Table Rules
# ============================================================================
# For each table, create variables and rules for:
#   - {table}-generate: run all run_*.py scripts → {table}_generated_*.sql
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

# Rule: run_N_name.py → {table}_generated_N_name.sql
# If ANY generator script changes, rebuild ALL generated SQL for this table
$$($(1)_DIR)/$(1)_generated_%.sql: $$($(1)_DIR)/run_%.py $$($(1)_GEN_SCRIPTS)
	@echo "Running generator: $$<"
	@cd $$($(1)_DIR) && $$(PYTHON) $$(notdir $$<)
	@echo "✓ Generated: $$@"

# Target: build database for table $(1)
.PHONY: $(1)-build
$(1)-build: $$($(1)_DB)

# Rule: build db/{table}.db from all SQL files (static + generated)
$$($(1)_DB): $$($(1)_ALL_SQL)
	@echo "Building database: $$@"
	@mkdir -p db
	@rm -f $$@
	@if [ -z "$$($(1)_ALL_SQL)" ]; then \
		echo "Error: No SQL files found for $(1)"; \
		exit 1; \
	fi
	@cat $$(sort $$($(1)_ALL_SQL)) | sqlite3 $$@
	@echo "✓ Built $$@ from $$(words $$($(1)_ALL_SQL)) SQL file(s)"

# Target: dump database for table $(1)
.PHONY: $(1)-dump
$(1)-dump: $$(VENV_MARKER) $$($(1)_DB)
	@echo "Dumping $(1) database to static SQL files..."
	@$$(PYTHON) tools/db_to_tables.py $$($(1)_DB) db/tables/
	@echo "✓ Done"

# Target: clean generated files for table $(1)
.PHONY: $(1)-clean
$(1)-clean:
	@echo "Cleaning generated files for $(1)..."
	@rm -f $$($(1)_GEN_SQL)
	@rm -f $$($(1)_DB)
	@echo "✓ Done"

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

# Generate rules for all discovered tables
$(foreach table,$(TABLES),$(eval $(call TABLE_RULES,$(table))))

# ============================================================================
# Global Targets
# ============================================================================

# Default target: build all table databases and unified terra.db
.PHONY: all build
all build: $(DB_FILES) db/terra.db terra.kicad_dbl

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

# Global generate target: run all table generators
.PHONY: generate
generate: $(foreach table,$(TABLES),$(table)-generate)

# Build unified terra.db with all tables
db/terra.db: $(foreach table,$(TABLES),$($(table)_ALL_SQL))
	@echo "Building unified database: $@"
	@mkdir -p db
	@rm -f $@
	@for table_dir in $$(ls -d db/tables/*/ | sort); do \
		table_name=$$(basename "$$table_dir"); \
		sql_files=$$(find "$$table_dir" -name "*.sql" -type f | sort); \
		if [ -n "$$sql_files" ]; then \
			cat $$sql_files | sqlite3 $@; \
			if [ $$? -eq 0 ]; then \
				count=$$(sqlite3 $@ "SELECT COUNT(*) FROM $$table_name" 2>/dev/null || echo "0"); \
				echo "  ✓ Added $$count rows to $$table_name"; \
			fi; \
		fi; \
	done
	@echo "✓ Built $@ with $(words $(TABLES)) tables"

# Generate unified terra.kicad_dbl file
terra.kicad_dbl: $(VENV_MARKER) db/terra.db
	@echo "Generating terra.kicad_dbl..."
	@$(PYTHON) tools/generate_kicad_dbl_files.py db/terra.db
	@echo "✓ Done"

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
	@echo "✓ All tables dumped. Review changes with 'git diff db/tables/' before committing."

# Verify round-trip consistency
# Process: Static SQL → [Generate] → DB → Dump → Compare Static SQL
# Generated SQL (source=''|NULL) should NOT appear in dump
.PHONY: verify
verify: $(VENV_MARKER)
	@echo "Verifying round-trip consistency..."
	@echo "  Step 1: Save checksums of current static SQL files (excluding *_generated_*)"
	@rm -f /tmp/terra_checksums_before.txt
	@for table_dir in $(TABLE_DIRS); do \
		for sql in $$table_dir/*.sql; do \
			if [ -f "$$sql" ] && [[ "$$(basename $$sql)" != *_generated_* ]]; then \
				md5 -q "$$sql" >> /tmp/terra_checksums_before.txt; \
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
				md5 -q "$$sql" >> /tmp/terra_checksums_after.txt; \
			fi; \
		done; \
	done
	@if diff /tmp/terra_checksums_before.txt /tmp/terra_checksums_after.txt > /dev/null 2>&1; then \
		echo "✓ Round-trip verification passed!"; \
		rm -f /tmp/terra_checksums_before.txt /tmp/terra_checksums_after.txt; \
	else \
		echo "✗ Round-trip verification failed!"; \
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
	@rm -f terra_*.kicad_dbl
	@rm -f *.kicad_dbl
	@echo "✓ Done. Static SQL files and venv preserved."

# Clean everything including venv (use with caution!)
.PHONY: distclean
distclean: clean
	@echo "Cleaning all generated files including venv..."
	@rm -rf .venv
	@echo "✓ Done."

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

# Help target
help:
	@echo "Terra EDA Library - Multi-Table Database Makefile"
	@echo "=================================================="
	@echo ""
	@echo "Multi-Table Architecture:"
	@echo "  SQL files:  db/tables/{component_type}/{component_type}.sql (source of truth)"
	@echo "  Database:   db/terra.db (generated from all table SQL files)"
	@echo ""
	@echo "Targets:"
	@echo "  make              Build terra.db from all db/tables/*/*.sql files"
	@echo "  make sync         Ensure uv environment is set up"
	@echo "  make dump         Dump terra.db back to db/tables/ structure"
	@echo "  make verify       Verify round-trip consistency (SQL→DB→SQL→DB)"
	@echo "  make status       Show status of all tables and database"
	@echo "  make clean        Remove generated .db file (keep SQL and venv)"
	@echo "  make distclean    Remove all generated files including SQL"
	@echo "  make help         Show this help"
	@echo ""
	@echo "Workflow:"
	@echo "  1. Build: Create database from table SQL files"
	@echo "     make"
	@echo ""
	@echo "  2. Edit: Modify database directly"
	@echo "     sqlite3 db/terra.db"
	@echo "     > UPDATE resistors SET tolerance='1%' WHERE part_id='RES-001';"
	@echo ""
	@echo "  3. Dump: Export changes back to SQL files"
	@echo "     make dump"
	@echo ""
	@echo "  4. Commit: Review and commit changes"
	@echo "     git diff db/tables/"
	@echo "     git add db/tables/resistors/resistors.sql"
	@echo "     git commit -m 'Update resistor tolerance'"
	@echo ""
	@echo "Migration from Legacy:"
	@echo "  python tools/migrate_to_tables.py db/terra.db db/terra_new.db --dump-sql db/tables/"
	@echo ""
	@echo "See MIGRATION_PLAN.md for details."

.PHONY: all sync dump verify clean distclean status help kicad-dbl-files
