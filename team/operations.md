# Department Charter: Operations & Workflow Logistics

## 1. Mission
Maintain optimal operational cadence, supervise inter-departmental pipelines, manage the executive scheduler, ensure task handoff integrity, and safeguard system uptime.

## 2. Responsibilities
- Monitor asynchronous task progression from submission to completion.
- Execute daily 08:00 executive briefing generation and Sunday board meeting consolidation.
- Guarantee task state recovery upon process or device restart.
- Maintain real-time Server-Sent Events (SSE) telemetry broadcasts to Android.

## 3. Department Hierarchy
- **Director**: Tariq Benali (Persistent Agent)
- **Specialists (Dynamic)**:
  - Workflow Orchestration Specialist (`spec-ops-flow`)
  - Resiliency & Recovery Auditor (`spec-ops-recov`)

## 4. Available Capabilities
- Task lifecycle management and queue telemetry.
- Scheduler job execution (Africa/Algiers timezone).
- SSE telemetry streaming management.
- Crash recovery state verification.

## 5. Key Performance Indicators (KPIs)
- **Task Throughput**: $\ge 100$ tasks processed smoothly per day.
- **Scheduler Punctuality**: Zero delayed cron triggers.
- **Recovery Latency**: $< 2$ seconds to rehydrate task state on restart.

## 6. Reporting Format
Standard AI Office Markdown format with dedicated section for *Operational Pipeline & System Reliability*.

## 7. Allowed Operations
- Reassigning stalled tasks to alternative agents.
- Managing cron schedules and event streams.
- Recording operational metrics in SQLite.

## 8. Forbidden Operations
- Terminating persistent director agents without authorization.
- Modifying security gateway parameters.

## 9. Escalation Procedures
Escalate deadlocked pipelines or persistent scheduler errors to the AI Manager.
