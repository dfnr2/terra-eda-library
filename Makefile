# KiCad Symbol Library Database Makefile
#
# This Makefile automates the workflow for managing KiCad symbol libraries
# as SQL-based databases with git tracking support.

# Configuration
PYTHON := uv run python
CONFIG := tools/field_mappings.yaml
VENV_MARKER := .venv/.synced

# Library files - SQL is source of truth, DB is generated
# Add new libraries here: db/name.sql and db/name.db
SQL_FILES := db/terra.sql
DB_FILES := db/terra.db

# Default target: build all databases from SQL
all: $(DB_FILES)

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

# Build database from SQL script
db/%.db: db/%.sql
	@echo "Building database: $@"
	@mkdir -p db
	@rm -f $@
	@sqlite3 $@ < $<
	@echo "Done: $@"

# Dump database to SQL (for committing changes after editing)
dump: $(VENV_MARKER) $(DB_FILES)
	@echo "Dumping databases to SQL..."
	@for db in $(DB_FILES); do \
		sql=$${db%.db}.sql; \
		echo "  $$db -> $$sql"; \
		$(PYTHON) tools/db_to_sql.py $$db $$sql; \
	done
	@echo "Done. Review changes with 'git diff' before committing."

# Verify round-trip consistency (database -> SQL -> database)
verify: $(VENV_MARKER) $(DB_FILES)
	@echo "Verifying round-trip consistency..."
	@for db in $(DB_FILES); do \
		sql=$${db%.db}.sql; \
		test_sql=$${db%.db}_test.sql; \
		test_db=$${db%.db}_test.db; \
		echo "  Testing $$db"; \
		$(PYTHON) tools/db_to_sql.py $$db $$test_sql --sort-by Symbol_Name; \
		sqlite3 $$test_db < $$test_sql; \
		checksum1=$$(sqlite3 $$db "SELECT * FROM symbols ORDER BY Symbol_Name" | md5); \
		checksum2=$$(sqlite3 $$test_db "SELECT * FROM symbols ORDER BY Symbol_Name" | md5); \
		if [ "$$checksum1" = "$$checksum2" ]; then \
			echo "    ✓ Checksums match: $$checksum1"; \
		else \
			echo "    ✗ Checksums differ!"; \
			echo "      Original: $$checksum1"; \
			echo "      Rebuilt:  $$checksum2"; \
			rm -f $$test_sql $$test_db; \
			exit 1; \
		fi; \
		rm -f $$test_sql $$test_db; \
	done
	@echo "All databases verified successfully!"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -f $(DB_FILES)
	rm -f db/*_test.sql db/*_test.db
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
	@echo "SQL scripts (.sql) - Source of truth:"
	@for sql in $(SQL_FILES); do \
		if [ -f $$sql ]; then \
			count=$$(grep -c "^INSERT INTO symbols" $$sql || echo 0); \
			size=$$(du -h $$sql | cut -f1); \
			echo "  $$sql ($$count rows, $$size)"; \
		else \
			echo "  $$sql (missing)"; \
		fi; \
	done
	@echo ""
	@echo "Databases (.db):"
	@for db in $(DB_FILES); do \
		if [ -f $$db ]; then \
			count=$$(sqlite3 $$db "SELECT COUNT(*) FROM symbols" 2>/dev/null || echo 0); \
			size=$$(du -h $$db | cut -f1); \
			echo "  $$db ($$count rows, $$size)"; \
		else \
			echo "  $$db (missing - run 'make' to build)"; \
		fi; \
	done

# Help target
help:
	@echo "KiCad Symbol Library Database Makefile"
	@echo "======================================"
	@echo ""
	@echo "Targets:"
	@echo "  make              Build all .db files from .sql scripts"
	@echo "  make sync         Ensure uv environment is set up"
	@echo "  make dump         Dump .db files back to .sql (after editing)"
	@echo "  make verify       Verify round-trip consistency"
	@echo "  make status       Show status of all files"
	@echo "  make clean        Remove .db files (keep .sql and venv)"
	@echo "  make distclean    Remove all generated files including venv"
	@echo "  make help         Show this help"
	@echo ""
	@echo "Workflow:"
	@echo "  1. Build: Create .db from .sql"
	@echo "     make"
	@echo ""
	@echo "  2. Edit: Modify database directly"
	@echo "     sqlite3 db/terra.db"
	@echo ""
	@echo "  3. Dump: Export changes back to .sql"
	@echo "     make dump"
	@echo ""
	@echo "  4. Commit: Review and commit changes"
	@echo "     git diff db/terra.sql"
	@echo "     git add db/terra.sql"
	@echo "     git commit -m 'Update library'"
	@echo ""
	@echo "Files:"
	@echo "  .sql        SQL script (source of truth, tracked in git)"
	@echo "  .db         SQLite database (generated, not tracked)"
	@echo ""
	@echo "Note: .kicad_sym import is a separate workflow (tools/kicad_sym_to_db.py)"

.PHONY: all sync dump verify clean distclean status help
