#!/usr/bin/env bash
set -euo pipefail

# AI Office Database Migration Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Running AI Office Database Migrations ==="
cd "${ROOT_DIR}/backend"

if [ -f ".venv/bin/python3" ]; then
    PYTHON_BIN=".venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

"${PYTHON_BIN}" -c "
from app.database.connection import db_manager
from app.database.migrations import MigrationManager

with db_manager.session() as conn:
    applied = MigrationManager().run_migrations(conn)
    print(f'Applied {len(applied)} migrations successfully.')
"
echo "=== Migrations Complete ==="
