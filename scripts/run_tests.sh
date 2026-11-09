#!/usr/bin/env bash
set -euo pipefail

# AI Office Unified Test Suite Execution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================="
echo "AI OFFICE — FULL TEST SUITE VERIFICATION"
echo "=========================================="

echo "[1/2] Running Backend Python 3.12 Test Suite..."
cd "${ROOT_DIR}/backend"
if [ -f ".venv/bin/pytest" ]; then
    .venv/bin/pytest tests/ -v
else
    pytest tests/ -v
fi

echo "[2/2] Running Android Native Kotlin Unit Tests..."
cd "${ROOT_DIR}/android"
./gradlew testDebugUnitTest --no-daemon

echo "=========================================="
echo "ALL TEST SUITES PASSED CLEANLY (100%)"
echo "=========================================="
