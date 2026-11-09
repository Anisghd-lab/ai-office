# AI Office Backend API Contract

Base URL: `http://127.0.0.1:8000/api/v1`

---

## 1. System & Health

### `GET /health`
Returns system status, active provider connectivity, and database health.
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "active_providers": ["groq", "gemini"],
  "timestamp": "2026-11-09T22:00:00Z"
}
```

### `GET /metrics`
Returns real-time Office Board telemetry: active agents, pending approvals, task counts, and provider latency.

---

## 2. CEO Governance & Approval Center

### `GET /governance/approvals`
List pending or historical approval requests.
Query params: `status` (`pending` | `approved` | `rejected` | `executed`)

### `GET /governance/approvals/{request_id}`
Get full details and canonical payload hash for an approval request.

### `POST /governance/approvals/{request_id}/approve`
CEO decision to approve.
```json
{
  "decision": "approved",
  "comment": "Approved for publication on TikTok"
}
```

### `POST /governance/approvals/{request_id}/reject`
CEO decision to reject.
```json
{
  "decision": "rejected",
  "reason": "Revise hashtags and video thumbnail first"
}
```

### `POST /governance/approvals/{request_id}/execute`
Execute an approved request. Validates payload hash and single-use constraint.

---

## 3. Agents & Departments

### `GET /departments`
List all 8 departments and their directors.

### `GET /departments/{dept_id}`
Get department detail, active dynamic specialists, and current tasks.

### `GET /agents`
List all agents (directors and dynamic specialists).

### `GET /agents/{agent_id}`
Detailed agent profile: status, model, tokens used, task history.

### `POST /agents/{agent_id}/instruction`
CEO direct instruction to an agent.
```json
{
  "instruction": "Accelerate competitor benchmark for Q4",
  "priority": "high"
}
```

### `POST /agents/{agent_id}/pause`
Pause agent execution.

### `POST /agents/{agent_id}/resume`
Resume agent execution.

---

## 4. Tasks & Planning

### `GET /tasks`
List all tasks with filtering by department, status, or assignee.

### `POST /tasks`
Create a new objective / task assigned to the AI Manager.

### `GET /tasks/{task_id}`
Get task progress, subtasks, and agent execution trace.

---

## 5. Social Media & Publications

### `GET /social/accounts`
Status of linked accounts (TikTok, Facebook, Instagram).

### `GET /social/{platform}/auth-url`
Initiates PKCE OAuth URL generation.

### `POST /social/publish`
Propose a publication. Enforces automatic redirection into CEO Approval Gateway!

---

## 6. Real-Time Telemetry (SSE)

### `GET /events/stream`
Server-Sent Events endpoint emitting live organizational updates:
- `agent.started`
- `agent.progress`
- `task.updated`
- `approval.created`
- `approval.decided`
- `social.published`
