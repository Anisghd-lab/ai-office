#!/usr/bin/env bash
set -euo pipefail

# AI Office Backend Startup Script
# Optimized for Linux ARM64 / Ubuntu PRoot / Termux
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=== Starting AI Office Backend ==="
cd "${ROOT_DIR}/backend"

if [ -f ".venv/bin/activate" ]; then
    echo "Activating Python virtual environment..."
    # shellcheck source=/dev/null
    source .venv/bin/activate
fi

# Run preflight database migrations
echo "Running database schema migrations..."
python3 -c "
from app.database.connection import db_manager
from app.database.migrations import MigrationManager

with db_manager.session() as conn:
    MigrationManager().run_migrations(conn)
"

# Set default host and port (strict 127.0.0.1 loopback security default)
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

echo "Starting Uvicorn ASGI server on ${HOST}:${PORT}..."
exec uvicorn app.main:app --host "${HOST}" --port "${PORT}" --workers 1 --log-level info
