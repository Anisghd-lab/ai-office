# FlowKit Video Production Engine Integration

## 1. Overview & Architecture

FlowKit (`crisng95/flowkit`) is an open-source, automated video production engine that coordinates Google Flow generative video workflows with local FFmpeg media timeline assembly.

AI Office integrates FlowKit inside the local Ubuntu 24.04 PRoot ARM64 environment, keeping it fully isolated in its own virtual environment (`flowkit/.venv`) and communicating via REST and WebSocket loopback protocols.

---

## 2. Ports and Communication Interfaces

| Service | Port / Protocol | Purpose |
| :--- | :--- | :--- |
| **AI Office Backend** | `http://127.0.0.1:8000` | Main organization API, Employee registry, Approvals gateway |
| **FlowKit FastAPI Engine** | `http://127.0.0.1:8100` | Project management, scene generation, result handling |
| **FlowKit WebSocket Bridge**| `ws://127.0.0.1:9222` | Real-time communication with the browser extension |
| **Android Control Center** | Native App IPC | Monitors engine status, restarts daemons, visualizes queue |

---

## 3. Service Daemon Management (`scripts/flowkit_service.sh`)

A production-grade daemon management script manages the lifecycle of FlowKit:
```bash
# Start daemon in background with disown -h protection against SIGHUP
bash scripts/flowkit_service.sh start

# Check service status, process PID, and HTTP health
bash scripts/flowkit_service.sh status
bash scripts/flowkit_service.sh health

# Inspect rolling process logs
bash scripts/flowkit_service.sh logs

# Stop or restart daemon
bash scripts/flowkit_service.sh stop
bash scripts/flowkit_service.sh restart
```

### Safety Features
- **Loopback Binding**: Forces `127.0.0.1` binding to avoid exposing endpoints over local Wi-Fi.
- **PID Tracking**: Writes background process ID to `flowkit.pid` with stale PID cleanup.
- **Port Collision Prevention**: Checks port 8100 availability before spawning.
- **Automated Database Backup**: Backs up `flow_agent.db` before migrations or restart.

---

## 4. Backend Adapter (`app.flowkit.adapter`)

The AI Office backend communicates with FlowKit through `FlowKitAdapter`:
- `get_health()`: Polls `GET http://127.0.0.1:8100/health`.
- `get_queue_status()`: Polls `GET http://127.0.0.1:8100/api/queue`.
- `create_project()`: Posts new project definitions to FlowKit.
- `trigger_generation()`: Submits scene generation batches.
- `check_job_status()`: Observes rendering progress.

---

## 5. Local Timeline Assembly & Quality Control

When individual video scenes are generated, FlowKit uses local FFmpeg to concatenate scenes, burn subtitles, and mix background audio:
```bash
ffmpeg -f concat -safe 0 -i scenes_list.txt -c copy output_stitched.mp4
```
Automated QC checks then verify that the output adheres to 1080x1920 (9:16 vertical), contains zero audio clipping, and has no consecutive black frames.
