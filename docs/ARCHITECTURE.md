# AI Office Architecture Documentation

## 1. Executive Summary

AI Office is a localized, zero-cost, multi-agent enterprise framework orchestrated on Android ARM64 (under Termux / Ubuntu 24.04 PRoot) with an Android 16 Native Control Center (Kotlin 2.0 + Jetpack Compose) styled with Glassmorphism 2.0 aesthetics.

The system empowers a single human CEO to govern eight autonomous AI departments via a centralized AI Manager, subject to a cryptographically validated, default-deny human approval gateway for all external actions.

---

## 2. System Topology

```
+-------------------------------------------------------------+
|                     Human CEO (Mobile)                      |
+-------------------------------------------------------------+
                              |
                     Biometric / UI Action
                              v
+-------------------------------------------------------------+
|        Android 16 Native App (com.ghdinteractivestudio)      |
|    - Kotlin 2.0 + Jetpack Compose + Material 3 Glass        |
|    - Office Board, 8 Departments, Agent Profiles            |
|    - Real-Time Approval Center                              |
|    - SSE Client & Local Cache (DataStore / Memory)          |
+-------------------------------------------------------------+
                              |
               REST API & SSE on 127.0.0.1:8000
                              v
+-------------------------------------------------------------+
|               Python 3.12 FastAPI Core Engine               |
|  +-------------------------------------------------------+  |
|  |           CEO Approval Security Gateway               |  |
|  |   - Default-Deny interceptor                          |  |
|  |   - SHA-256 Payload Hash verification                 |  |
|  |   - Nonce & TTL validation                            |  |
|  |   - Audit Ledger (SQLite WAL)                         |  |
|  +-------------------------------------------------------+  |
|  |                Central AI Manager                     |  |
|  |   - Task planning, delegation & conflict resolution   |  |
|  |   - Executive briefings & board meeting generation    |  |
|  +-------------------------------------------------------+  |
|  |                 8 Department Directors                |  |
|  |   Research | Tech | Marketing | Finance | Ops ...    |  |
|  +-------------------------------------------------------+  |
|  |               Dynamic Specialist Pool                 |  |
|  |   Ephemeral worker agents created per task            |  |
|  +-------------------------------------------------------+  |
|  |       AI Provider Registry & Fallback Router          |  |
|  |   Groq | Gemini | OpenRouter Free | Local Ollama/vLLM |  |
|  +-------------------------------------------------------+  |
|  |         Social Media Vault & Adapters (PKCE)          |  |
|  |   TikTok API | Instagram Graph API | Facebook Pages   |  |
|  +-------------------------------------------------------+  |
|  |              SQLite WAL Persistence Layer             |  |
+-------------------------------------------------------------+
```

---

## 3. Core Subsystems

### 3.1 CEO Approval Gateway
- **Zero Self-Granting**: Agents cannot escalate privileges or approve their own actions.
- **Payload Immutability**: Any alteration to proposed post captions, video links, or parameters between request time and execution time invalidates the approval token.
- **Audit Ledger**: Every approval, rejection, and execution attempt is permanently recorded in SQLite.

### 3.2 Multi-Agent Hierarchy
1. **CEO (Human)**: Executive authority, sets strategic directives, reviews briefings, approves/denies external actions.
2. **AI Manager**: Translates directives into department tasks, schedules milestones, monitors agent workloads, manages escalations.
3. **Department Directors (8)**:
   - **Research**: Market scanning, competitor intelligence, scientific analysis.
   - **Technology**: Code generation, system health, infrastructure monitoring.
   - **Marketing**: Campaign planning, audience engagement, social strategy.
   - **Finance**: Budget simulation, free-quota tracking, unit economic forecasts.
   - **Operations**: Process optimization, workflow routing, scheduler verification.
   - **Creative**: Visual asset prompts, copywriting, video storyboard creation.
   - **Strategy**: Long-term roadmapping, organizational alignment, risk evaluation.
   - **Human Resources**: Agent skill allocation, workload balancing, prompt optimization.
4. **Dynamic Specialist Pool**: Ephemeral sub-agents created by directors for isolated tasks.

### 3.3 Zero-Cost AI Provider Engine
- Automatically probes configured free tiers (e.g. Groq free rate limits, Google Gemini free tier, OpenRouter `:free` models, local OpenAI-compatible endpoints).
- Employs an intelligent fallback router: if provider A encounters rate limiting (HTTP 429), the router seamlessly falls back to provider B while recording quota usage.
- Never falls back to paid endpoints.

### 3.4 Storage & Reliability
- SQLite configured with `PRAGMA journal_mode = WAL` and `PRAGMA synchronous = NORMAL`.
- High concurrency for PRoot ARM64 with minimal memory footprint (< 150MB RSS for backend).
- Seamless recovery from process terminations: agents persist in-flight task state in the database.
