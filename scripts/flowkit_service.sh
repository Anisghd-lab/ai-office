#!/usr/bin/env bash
# FlowKit Service Management Script for AI Office
# Strict loopback binding (127.0.0.1:8100) with PID tracking and idempotency.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FLOWKIT_DIR="${ROOT_DIR}/flowkit"
PID_FILE="${FLOWKIT_DIR}/flowkit.pid"
LOG_FILE="${FLOWKIT_DIR}/flowkit.log"
BACKUP_DIR="${FLOWKIT_DIR}/backups"
VENV_PYTHON="${FLOWKIT_DIR}/.venv/bin/python3"
VENV_UVICORN="${FLOWKIT_DIR}/.venv/bin/uvicorn"

HOST="127.0.0.1"
PORT="8100"
WS_PORT="9222"

is_running() {
    if [ -f "${PID_FILE}" ]; then
        local pid
        pid="$(cat "${PID_FILE}")"
        if kill -0 "${pid}" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

cmd_start() {
    echo "=== Starting FlowKit Video Engine ==="
    if is_running; then
        local pid
        pid="$(cat "${PID_FILE}")"
        echo "FlowKit is already running (PID: ${pid})."
        return 0
    fi

    # Check port availability
    if python3 -c "import socket; s = socket.socket(); s.connect(('${HOST}', ${PORT})); s.close()" 2>/dev/null; then
        echo "ERROR: Port ${PORT} is already in use by another process!" >&2
        return 1
    fi

    echo "Launching FlowKit on ${HOST}:${PORT} (WebSocket: ${HOST}:${WS_PORT})..."
    cd "${FLOWKIT_DIR}"
    export API_HOST="${HOST}"
    export API_PORT="${PORT}"
    export WS_HOST="${HOST}"
    export WS_PORT="${WS_PORT}"
    export FLOW_AGENT_DIR="${FLOWKIT_DIR}"

    nohup "${VENV_UVICORN}" agent.main:app --host "${HOST}" --port "${PORT}" >> "${LOG_FILE}" 2>&1 &
    local new_pid=$!
    disown -h "${new_pid}" 2>/dev/null || true
    echo "${new_pid}" > "${PID_FILE}"
    echo "Spawned FlowKit process (PID: ${new_pid}). Waiting for health check..."

    # Wait for health check (up to 15 seconds)
    local retries=15
    local healthy=0
    while [ ${retries} -gt 0 ]; do
        sleep 1
        if curl -s "http://${HOST}:${PORT}/health" >/dev/null 2>&1; then
            healthy=1
            break
        fi
        if ! kill -0 "${new_pid}" 2>/dev/null; then
            echo "ERROR: FlowKit process exited prematurely! Check logs at ${LOG_FILE}" >&2
            rm -f "${PID_FILE}"
            return 1
        fi
        retries=$((retries - 1))
    done

    if [ ${healthy} -eq 1 ]; then
        echo "FlowKit started successfully! Health check passed on http://${HOST}:${PORT}/health."
    else
        echo "WARNING: FlowKit started (PID: ${new_pid}), but health check did not respond within 15s."
    fi
}

cmd_stop() {
    echo "=== Stopping FlowKit Video Engine ==="
    if [ ! -f "${PID_FILE}" ]; then
        echo "No PID file found at ${PID_FILE}. Checking if orphan process exists on port ${PORT}..."
        local port_pid
        port_pid="$(lsof -t -i ":${PORT}" 2>/dev/null || true)"
        if [ -n "${port_pid}" ]; then
            echo "Killing orphan process ${port_pid} on port ${PORT}..."
            kill -15 "${port_pid}" 2>/dev/null || true
            sleep 2
            kill -9 "${port_pid}" 2>/dev/null || true
        else
            echo "FlowKit is not running."
        fi
        return 0
    fi

    local pid
    pid="$(cat "${PID_FILE}")"
    echo "Stopping FlowKit (PID: ${pid})..."
    if kill -0 "${pid}" 2>/dev/null; then
        kill -15 "${pid}" 2>/dev/null || true
        local count=0
        while kill -0 "${pid}" 2>/dev/null && [ ${count} -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        if kill -0 "${pid}" 2>/dev/null; then
            echo "Force killing FlowKit (SIGKILL)..."
            kill -9 "${pid}" 2>/dev/null || true
        fi
    fi
    rm -f "${PID_FILE}"
    echo "FlowKit stopped."
}

cmd_restart() {
    cmd_stop
    sleep 1
    cmd_start
}

cmd_status() {
    echo "=== FlowKit Video Engine Status ==="
    if is_running; then
        local pid
        pid="$(cat "${PID_FILE}")"
        echo "Process: RUNNING (PID: ${pid})"
        if curl -s "http://${HOST}:${PORT}/health" >/dev/null 2>&1; then
            echo "API Health: OK (http://${HOST}:${PORT}/health)"
            curl -s "http://${HOST}:${PORT}/health"
            echo ""
        else
            echo "API Health: UNRESPONSIVE"
        fi
    else
        echo "Process: STOPPED"
    fi
}

cmd_health() {
    if curl -s "http://${HOST}:${PORT}/health"; then
        echo ""
    else
        echo "ERROR: Unable to reach FlowKit health endpoint at http://${HOST}:${PORT}/health" >&2
        return 1
    fi
}

cmd_logs() {
    if [ -f "${LOG_FILE}" ]; then
        tail -n 50 "${LOG_FILE}"
    else
        echo "Log file not found at ${LOG_FILE}"
    fi
}

cmd_check_deps() {
    echo "=== Checking FlowKit Dependencies ==="
    if [ -x "${VENV_PYTHON}" ]; then
        echo "Python venv: OK (${VENV_PYTHON})"
    else
        echo "ERROR: Python venv not found at ${VENV_PYTHON}" >&2
        return 1
    fi

    if which ffmpeg >/dev/null 2>&1; then
        echo "FFmpeg: OK ($(ffmpeg -version | head -n 1))"
    else
        echo "ERROR: FFmpeg binary not found!" >&2
        return 1
    fi

    if which ffprobe >/dev/null 2>&1; then
        echo "FFprobe: OK ($(ffprobe -version | head -n 1))"
    else
        echo "ERROR: FFprobe binary not found!" >&2
        return 1
    fi
    echo "All dependencies verified."
}

cmd_backup_db() {
    echo "=== Backing up FlowKit Database ==="
    mkdir -p "${BACKUP_DIR}"
    local db_file="${FLOWKIT_DIR}/flow_agent.db"
    if [ -f "${db_file}" ]; then
        local timestamp
        timestamp="$(date +%Y%m%d_%H%M%S)"
        local backup_file="${BACKUP_DIR}/flow_agent_${timestamp}.db"
        cp -p "${db_file}" "${backup_file}"
        echo "Database backup created: ${backup_file}"
    else
        echo "No FlowKit database found at ${db_file} (Will be created on first start)."
    fi
}

case "${1:-status}" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    health)
        cmd_health
        ;;
    logs)
        cmd_logs
        ;;
    check-deps)
        cmd_check_deps
        ;;
    backup-db)
        cmd_backup_db
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|health|logs|check-deps|backup-db}"
        exit 1
        ;;
esac
