# KiCad Symbol Library Database Makefile
#
# This Makefile automates the workflow for managing KiCad symbol libraries
# as SQL-based databases with git tracking support.

# Configuration
PYTHON := uv run python
CONFIG := tools/field_mappings.yaml
VENV_MARKER := .venv/.synced

# Multi-table architecture
# SQL files are in db/tables/*/*.sql, DB is generated at db/terra.db
TABLE_SQL_FILES := $(wildcard db/tables/*/*.sql)
DB_FILE := db/terra.db

# Default target: build database from all table SQL files
all: $(DB_FILE) kicad-dbl-files

# Ensure uv environment is synced
$(VENV_MARKER): pyproject.toml
	@echo "Syncing uv environment..."
	@command -v uv >/dev/null 2>&1 || { echo "Error: uv is not installed. Install from https://docs.astral.sh/uv/"; exit 1; }
	@uv sync
	@mkdir -p .venv
	@touch $(VENV_MARKER)
	@echo "uv environment ready"

# Manual sync target
sync: $(VENV_MARKER)

# Build database from all table SQL files
$(DB_FILE): $(TABLE_SQL_FILES)
	@echo "Building database from table SQL files..."
	@mkdir -p db
	@rm -f $@
	@if [ -z "$(TABLE_SQL_FILES)" ]; then \
		echo "Warning: No SQL files found in db/tables/*/"; \
		echo "Run 'make migrate' to migrate from legacy structure"; \
		exit 1; \
	fi
	@echo "Found $(words $(TABLE_SQL_FILES)) SQL file(s)"
	@cat $(shell ls db/tables/*/*.sql | sort) | sqlite3 $@
	@echo "✓ Database built: $@"

# Generate .kicad_dbl files for all component type tables
kicad-dbl-files: $(VENV_MARKER) $(DB_FILE)
	@echo "Generating .kicad_dbl files for all tables..."
	@$(PYTHON) tools/generate_kicad_dbl_files.py $(DB_FILE)
	@echo "✓ Done"

# Convert KiCad symbol library to SQL (initial import)
# Pattern: terra_sym.kicad_sym -> db/terra.sql
db/%.sql: %_sym.kicad_sym $(CONFIG)
	@echo "Converting symbol library to SQL: $< -> $@"
	@mkdir -p db
	@$(PYTHON) tools/kicad_sym_to_db.py $< $@ --config $(CONFIG)
	@echo "Done: $@"

# Dump database back to table structure (for committing changes after editing)
dump: $(VENV_MARKER) $(DB_FILE)
	@echo "Dumping database to table structure..."
	@$(PYTHON) tools/db_to_tables.py $(DB_FILE) db/tables/
	@echo "✓ Done. Review changes with 'git diff db/tables/' before committing."

# Verify round-trip consistency (SQL -> DB -> SQL -> DB)
verify: $(VENV_MARKER) $(DB_FILE)
	@echo "Verifying round-trip consistency..."
	@echo "  Step 1: Dump current database to temp tables/"
	@rm -rf db/tables_test/
	@$(PYTHON) tools/db_to_tables.py $(DB_FILE) db/tables_test/
	@echo "  Step 2: Rebuild database from dumped SQL"
	@rm -f db/terra_test.db
	@cat $$(ls db/tables_test/*/*.sql | sort) | sqlite3 db/terra_test.db
	@echo "  Step 3: Compare original and rebuilt databases"
	@tables=$$(sqlite3 $(DB_FILE) "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"); \
	all_match=true; \
	for table in $$tables; do \
		checksum1=$$(sqlite3 $(DB_FILE) "SELECT * FROM $$table ORDER BY part_id" | md5); \
		checksum2=$$(sqlite3 db/terra_test.db "SELECT * FROM $$table ORDER BY part_id" | md5); \
		if [ "$$checksum1" = "$$checksum2" ]; then \
			echo "    ✓ $$table: checksums match"; \
		else \
			echo "    ✗ $$table: checksums differ!"; \
			echo "      Original:  $$checksum1"; \
			echo "      Rebuilt:   $$checksum2"; \
			all_match=false; \
		fi; \
	done; \
	rm -rf db/tables_test/ db/terra_test.db; \
	if [ "$$all_match" = "true" ]; then \
		echo "\n✓ All tables verified successfully!"; \
	else \
		echo "\n✗ Verification failed!"; \
		exit 1; \
	fi

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f $(DB_FILES)
	rm -f db/*_test.sql db/*_test.db
	rm -f terra_*.kicad_dbl
	@echo "Done. SQL files and venv preserved."

# Clean everything including SQL and venv (use with caution!)
distclean: clean
	@echo "Cleaning all generated files including SQL and venv..."
	rm -f $(SQL_FILES)
	rm -rf .venv
	@echo "Done."

# Show status
status:
	@echo "Terra EDA Library Status"
	@echo "========================"
	@echo ""
	@echo "Component Type Tables (db/tables/):"
	@if [ -d "db/tables" ]; then \
		for dir in db/tables/*/; do \
			if [ -d "$$dir" ]; then \
				table=$$(basename $$dir); \
				sql_file="$$dir$$table.sql"; \
				if [ -f "$$sql_file" ]; then \
					count=$$(grep -c "^INSERT INTO $$table" "$$sql_file" 2>/dev/null || echo 0); \
					size=$$(du -h "$$sql_file" | cut -f1); \
					echo "  $$table: $$count components ($$size)"; \
				fi; \
			fi; \
		done; \
	else \
		echo "  No tables found in db/tables/"; \
		echo "  Run migration script to create initial structure"; \
	fi
	@echo ""
	@echo "Database (generated):"
	@if [ -f "$(DB_FILE)" ]; then \
		size=$$(du -h "$(DB_FILE)" | cut -f1); \
		tables=$$(sqlite3 $(DB_FILE) "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'" 2>/dev/null || echo 0); \
		total=$$(sqlite3 $(DB_FILE) "SELECT SUM(cnt) FROM (SELECT COUNT(*) as cnt FROM resistors UNION ALL SELECT COUNT(*) FROM capacitors)" 2>/dev/null || echo "?"); \
		echo "  $(DB_FILE) ($$tables tables, $$size)"; \
	else \
		echo "  $(DB_FILE) (not built - run 'make' to build)"; \
	fi

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
