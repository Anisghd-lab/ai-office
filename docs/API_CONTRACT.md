# AI Office Backend API Contract

Base URL: `http://127.0.0.1:8000/api/v1`

Authentication Header: `X-Owner-Key: <owner_secret_token>`

---

## 1. AI CEO Executive Interface

### `POST /ceo/chat`
Conversational dialogue between the Human Owner and the AI CEO.
```json
{
  "message": "We need to analyze our social growth on TikTok for Q4."
}
```
Response:
```json
{
  "reply": "I have directed Research to analyze trending formats and Marketing to prepare a 3-part campaign. I will review their deliverables and present the strategy for your approval.",
  "decisions": [
    {"action": "DELEGATE_RESEARCH", "dept": "research"},
    {"action": "DELEGATE_MARKETING", "dept": "marketing"}
  ],
  "timestamp": "2026-11-09T22:00:00Z"
}
```

### `GET /ceo/profile`
Returns AI CEO identity, executive status, active strategic priorities, and token consumption metrics.

### `GET /ceo/decisions`
List autonomous internal executive decisions made by the AI CEO.

### `GET /ceo/strategy`
Returns the current organizational strategy and active departmental initiatives.

---

## 2. User Governance & Approval Center

### `GET /governance/approvals`
List pending or historical external action requests requiring User Approval.
Query params: `status` (`PENDING`, `APPROVED`, `REJECTED`, `EXECUTED`)

### `POST /governance/approvals/{request_id}/approve`
Human Owner decision to approve external execution.

### `POST /governance/approvals/{request_id}/reject`
Human Owner decision to reject external execution.

### `POST /governance/approvals/{request_id}/execute`
Execute approved request. Cryptographically verifies canonical SHA-256 payload hash and single-use constraint.

---

## 3. Departments & Agents

### `GET /departments`
List all 8 departments and their directors.

### `GET /departments/{dept_id}`
Get department detail, active dynamic specialists, and current tasks.

### `GET /agents`
List all agents (AI CEO, 8 Directors, dynamic specialists).

### `GET /agents/{agent_id}`
Detailed agent profile.

---

## 4. Tasks & Planning

### `GET /tasks`
List all tasks with filtering by department, status, or priority.

### `POST /tasks`
Create or schedule a task.

---

## 5. Social Media & Accounts

### `GET /social/accounts`
Status of linked accounts (TikTok, Facebook, Instagram).

### `GET /social/{platform}/auth-url`
Initiate official OAuth 2.0 PKCE authorization flow.

### `POST /social/publish`
AI CEO proposes social publication -> automatically routes into User Approval Gateway.

---

## 6. Real-Time Telemetry (SSE)

### `GET /events/stream`
Server-Sent Events streaming live updates to Android Control Center.
