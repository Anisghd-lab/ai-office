# AI Office Architecture Documentation

## 1. Executive Summary

AI Office is an autonomous, localized, zero-cost multi-agent organization designed to run in a lightweight footprint on Android 16 ARM64 + Termux / Ubuntu 24.04 PRoot.

### The Human User ↔ AI CEO Governance Relationship
- **The Human Operating AI Office is NOT the CEO.**
- The human is the **OWNER / PRINCIPAL / USER**.
- The central autonomous executive intelligence running the company is the **AI CEO (Nova Prime)**.
- The User communicates directly and exclusively with the **AI CEO**.
- The **AI CEO** establishes strategy, directs 8 department directors, creates dynamic specialist agents, resolves task conflicts, and manages day-to-day operations.
- For consequential external actions (social publishing, spending, messaging, connecting/disconnecting accounts), the AI CEO proposes the action, but **MANDATORY USER APPROVAL** is required before execution.

---

## 2. System Hierarchy & Topology

```
                       [ HUMAN OWNER / PRINCIPAL ]
                                    │
                         Objectives & Guidance
                                    ▼
                         [ AI CEO: NOVA PRIME ]
                       (Executive Intelligence)
                                    │
          ┌─────────────┬───────────┼───────────┬─────────────┐
          ▼             ▼           ▼           ▼             ▼
       Research    Technology   Marketing    Finance     Operations ...
          │             │           │           │             │
          └─────────────┴───────────┴───────────┴─────────────┘
                                    │
                               Proposals
                                    ▼
                     [ USER APPROVAL GATEWAY ]
                                    │
                          [ OWNER APPROVAL ]
                                    │
                            Secure Execution
                       (TikTok / Meta Graph APIs)
```

### Communication Flow:
$$\text{USER} \longrightarrow \text{AI CEO} \longrightarrow \text{DEPARTMENTS} \longrightarrow \text{AI CEO} \longrightarrow \text{USER}$$

---

## 3. Subsystems

### 3.1 AI CEO (Executive Intelligence)
- Proactive, strategic executive partner for the Human Owner.
- Conversational interface: receives high-level user visions, formulates strategic plans, coordinates 8 departments, evaluates performance, and briefs the user.
- Autonomous internal authority: assign tasks, reorder priorities, spawn specialist agents, schedule meetings, approve internal research and drafts without bothering the user for trivial operations.

### 3.2 Human Owner Reserved Powers & User Approval Gateway
- **Default-Deny External Boundary**:
  - Content publication (TikTok, Facebook, Instagram)
  - Outbound messaging & emails
  - Any expenditure (strictly enforced $\$0.00$ zero-cost invariant)
  - External account linking / unlinking
  - Credential & sensitive settings updates
- **Cryptographic Binding**: All approval grants are bound to SHA-256 canonical payload digests. Any alteration invalidates approval.
- **Single-Use & TTL**: Execution tokens expire after 30 minutes and are strictly single-use.

### 3.3 The 8 AI Departments (Led by Persistent Directors)
1. **Research & Intelligence** (Dr. Aris Vance)
2. **Technology & Engineering** (Marcus Sterling)
3. **Marketing & Communications** (Elena Rostova)
4. **Finance & Economic Guardrails** (Cassian Drake)
5. **Operations & Workflow Logistics** (Tariq Benali)
6. **Creative & Visual Studio** (Lyra Silvers)
7. **Strategy & Growth Governance** (Kaelen Thorne)
8. **Human Resources & Workforce Optimization** (Sora Tanaka)

### 3.4 Dynamic Specialist Pool
Temporary sub-agents spawned on demand for isolated tasks by directors and gracefully decommissioned upon task completion to preserve memory on Ubuntu PRoot ARM64.

### 3.5 Storage & Telemetry
- SQLite database configured with `PRAGMA journal_mode = WAL;`.
- Server-Sent Events (SSE) stream on `127.0.0.1:8000` pushing real-time telemetry to the Android Control Center.
