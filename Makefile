# KiCad Symbol Library Database Makefile
#
# This Makefile automates the workflow for managing KiCad symbol libraries
# as SQL-based databases with git tracking support.

# Configuration
PYTHON := python3
CONFIG := tools/field_mappings.yaml

# Source files - add new *_sym.kicad_sym files here
# Pattern: terra_sym.kicad_sym -> db/terra.{sql,db}
#          terra_resistors_sym.kicad_sym -> db/terra_resistors.{sql,db}
KICAD_LIBS := terra_sym.kicad_sym

# Generate db/ paths for SQL and DB files (strip _sym suffix)
SQL_FILES := $(addprefix db/,$(KICAD_LIBS:_sym.kicad_sym=.sql))
DB_FILES := $(addprefix db/,$(KICAD_LIBS:_sym.kicad_sym=.db))

# Default target: build all databases from SQL
all: $(DB_FILES)

# Build database from SQL script
db/%.db: db/%.sql
	@echo "Building database: $@"
	@mkdir -p db
	@rm -f $@
	@sqlite3 $@ < $<
	@echo "Done: $@"

# Convert KiCad symbol library to SQL (initial import)
# Pattern: terra_sym.kicad_sym -> db/terra.sql
db/%.sql: %_sym.kicad_sym $(CONFIG)
	@echo "Converting symbol library to SQL: $< -> $@"
	@mkdir -p db
	@$(PYTHON) tools/kicad_sym_to_db.py $< $@ --config $(CONFIG)
	@echo "Done: $@"

# Dump database to SQL (for committing changes after editing)
dump: $(DB_FILES)
	@echo "Dumping databases to SQL..."
	@for db in $(DB_FILES); do \
		sql=$${db%.db}.sql; \
		echo "  $$db -> $$sql"; \
		$(PYTHON) tools/db_to_sql.py $$db $$sql; \
	done
	@echo "Done. Review changes with 'git diff' before committing."

# Verify round-trip consistency (database -> SQL -> database)
verify: $(DB_FILES)
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
	@echo "Done. SQL files preserved."

# Clean everything including SQL (use with caution!)
distclean: clean
	@echo "Cleaning all generated files including SQL..."
	rm -f $(SQL_FILES)
	@echo "Done."

# Show status
status:
	@echo "KiCad Symbol Library Status"
	@echo "============================"
	@echo ""
	@echo "Source libraries (.kicad_sym):"
	@for lib in $(KICAD_LIBS); do \
		if [ -f $$lib ]; then \
			count=$$(grep -c "^  (symbol " $$lib || echo 0); \
			echo "  $$lib ($$count symbols)"; \
		else \
			echo "  $$lib (missing)"; \
		fi; \
	done
	@echo ""
	@echo "SQL scripts (.sql):"
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
	@echo "  make dump         Dump .db files back to .sql (after editing)"
	@echo "  make verify       Verify round-trip consistency"
	@echo "  make status       Show status of all files"
	@echo "  make clean        Remove .db files (keep .sql)"
	@echo "  make distclean    Remove all generated files"
	@echo "  make help         Show this help"
	@echo ""
	@echo "Workflow:"
	@echo "  1. Initial: Convert .kicad_sym to .sql"
	@echo "     make db/terra.sql"
	@echo ""
	@echo "  2. Build: Create .db from .sql"
	@echo "     make"
	@echo ""
	@echo "  3. Edit: Modify database using SQLite tools or KiCad"
	@echo "     sqlite3 db/terra.db"
	@echo ""
	@echo "  4. Commit: Dump changes back to .sql and commit"
	@echo "     make dump"
	@echo "     git diff db/terra.sql"
	@echo "     git add db/terra.sql"
	@echo "     git commit -m 'Update library'"
	@echo ""
	@echo "Files:"
	@echo "  .kicad_sym  KiCad symbol library (source)"
	@echo "  .sql        SQL script (tracked in git)"
	@echo "  .db         SQLite database (generated, not tracked)"

.PHONY: all dump verify clean distclean status help
