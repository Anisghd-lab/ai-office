# AI OFFICE — OPERATING RULES & WORKFLOW PROTOCOLS

## 1. Single Report Structure
All departments and specialist agents must generate operational reports using the standardized format:
- **DONE**: Clear bulleted list of completed work items and artifacts.
- **FILES / LINKS**: File paths, database IDs, and media asset URLs.
- **NEEDS YOUR DECISION**: Consequential actions requiring Human Owner authorization.
- **BLOCKERS**: Environmental limitations, missing dependencies, or quota exhaustion.
- **NEXT STEP**: Precise upcoming execution milestone.

## 2. Session Lifecycle & Telemetry
Every autonomous work session MUST trigger real-time state updates:
- **Session Start**:
  - Register new session ID and link to task/project.
  - Set employee status to `WORKING`.
  - Broadcast status event over Server-Sent Events (SSE).
- **Session Finish**:
  - Persist outputs, metrics, and logs.
  - Set employee status to `FREE`, `WAITING_FOR_OWNER`, or `STUCK`.
  - Broadcast status completion event.

## 3. Failure Handling & Recovery
1. Detect failures immediately via deterministic health checks and try-catch boundaries.
2. In case of transient network failure: apply exponential backoff with jitter (max 3 retries).
3. In case of unrecoverable service error: quarantine task, log root cause, notify Nova Prime for reassignment.
4. Never simulate success or invent output references.
