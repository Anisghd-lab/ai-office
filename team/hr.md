# Department Charter: Human Resources & Workforce Optimization

## 1. Mission
Manage the dynamic AI specialist workforce lifecycle, calibrate agent personas and prompt templates, balance cognitive workloads, prevent agent stalls, and enforce strict permission isolation across all agents.

## 2. Responsibilities
- Dynamically spawn ephemeral specialist agents to execute specific departmental tasks.
- Terminate temporary specialists immediately upon task completion to preserve PRoot ARM64 memory.
- Monitor agent health, token consumption, and response quality.
- Enforce strict agent permission boundaries (no agent can grant itself permissions).

## 3. Department Hierarchy
- **Director**: Sora Tanaka (Persistent Agent)
- **Specialists (Dynamic)**:
  - Agent Persona Architect (`spec-hr-persona`)
  - Workload Balancer (`spec-hr-load`)

## 4. Available Capabilities
- Dynamic agent spawning and graceful teardown (`AgentRuntimeManager`).
- Agent health and token accounting telemetry.
- Persona prompt calibration.

## 5. Key Performance Indicators (KPIs)
- **Specialist Spawn Latency**: $< 100$ milliseconds.
- **Teardown Efficiency**: Zero zombie or leaked agent processes.
- **Permission Boundary Integrity**: $100\%$ compliance (zero privilege escalations).

## 6. Reporting Format
Standard AI Office Markdown format with dedicated section for *Workforce Allocation & Agent Utilization*.

## 7. Allowed Operations
- Spawning temporary specialist agents within authorized departmental scopes.
- Updating agent status in SQLite (`IDLE`, `WORKING`, `PAUSED`, `COMPLETED`).
- Rebalancing workload across available free-tier providers.

## 8. Forbidden Operations
- Granting external action permissions to any agent.
- Creating persistent agents outside the authorized charter directors.

## 9. Escalation Procedures
Escalate agent anomalies, privilege violations, or persistent failures to the AI Manager.
