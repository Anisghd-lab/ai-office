# AI Office — Autonomous Multi-Agent Organization

![Platform](https://img.shields.io/badge/Platform-Android%2016%20ARM64%20%7C%20Ubuntu%2024.04%20PRoot-blue)
![Backend](https://img.shields.io/badge/Backend-Python%203.12%20%7C%20FastAPI%20%7C%20SQLite%20WAL-green)
![Android](https://img.shields.io/badge/Android-Kotlin%202.0%20%7C%20Jetpack%20Compose%20%7C%20Material%203-emerald)
![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey)
![Cost](https://img.shields.io/badge/Cost-100%25%20Free%20%2F%20Zero--Cost-brightgreen)

AI Office is an enterprise-grade autonomous multi-agent organization designed to run in a lightweight, zero-cost environment on Android ARM64 (Termux / Ubuntu 24.04 PRoot) paired with a native Android 16 Control Center built with Kotlin 2.0 and Jetpack Compose featuring iOS-inspired Glassmorphism 2.0 aesthetics.

A single human CEO directs a central AI Manager who oversees eight specialized departments:
- **Research**
- **Technology**
- **Marketing**
- **Finance**
- **Operations**
- **Creative**
- **Strategy**
- **Human Resources**

---

## Key Pillars

1. **Mandatory Human-in-the-Loop Gateway (CEO Approval Center):**
   Default-deny external action policy. The autonomous agents can research, debate, draft, analyze, and synthesize internally. However, content publication, external communication, purchases, subscription adjustments, credential access, and destructive operations strictly require cryptographic authorization from the CEO via the Android Native Control Center.

2. **100% Free / Freemium Only:**
   Operates strictly within verified free-tier API quotas, local lightweight models/endpoints, and free OAuth platform endpoints. No paid subscriptions, no unexpected API credit billing, and no credit card gates.

3. **Genuinely Native Android Experience:**
   No WebView, no Flutter, no React Native. Built with modern Kotlin 2.0, Jetpack Compose, Material 3, Coroutines, StateFlow, Kotlin Serialization, and real-time Server-Sent Events (SSE) connected to `127.0.0.1`.

4. **Self-Healing Multi-Agent Architecture:**
   Persistent department directors manage dynamic specialist subagents with lifecycle tracking, task conflict resolution, shared memory, and automatic recovery across backend restarts.

5. **Official Social Media Integration:**
   Standard PKCE OAuth workflows for TikTok, Facebook, and Instagram with preview rendering, strict payload validation, and CEO-gated publication.

---

## Architecture Overview

```
+-------------------------------------------------------+
|              Android 16 Control Center                |
|           (Kotlin 2.0 + Jetpack Compose)              |
|        Glassmorphism 2.0 / Material 3 Surface         |
+-------------------------------------------------------+
                           |
               HTTP REST & SSE Events
                    (127.0.0.1)
                           v
+-------------------------------------------------------+
|             AI Office Central Backend                 |
|          (Python 3.12 + FastAPI + SQLite)             |
|                                                       |
|  +-------------------------------------------------+  |
|  |           CEO Approval Security Gateway         |  |
|  |      (Default-Deny External Action Engine)      |  |
|  +-------------------------------------------------+  |
|                          |                            |
|  +-------------------------------------------------+  |
|  |             Central AI Manager                  |  |
|  +-------------------------------------------------+  |
|      |        |        |        |        |      |     |
|   Research  Tech   Marketing Finance   Ops   HR ...   |
|                                                       |
|  +-------------------------------------------------+  |
|  |    Provider Registry & Model Router (Free Tier) |  |
|  +-------------------------------------------------+  |
|  |    Social Vault (TikTok, Meta Graph API)        |  |
|  +-------------------------------------------------+  |
|  |    Executive Scheduler (Algiers Timezone)       |  |
|  +-------------------------------------------------+  |
|  |    WAL SQLite Persistence & Knowledge Engine    |  |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
```

---

## Directory Structure

```
ai-office/
├── docs/                # Architecture, security model, and API specs
├── backend/             # Python 3.12 FastAPI core and agent runtime
│   ├── app/             # Application source modules
│   │   ├── api/         # REST & SSE endpoints
│   │   ├── core/        # Configuration and base models
│   │   ├── agents/      # Agent runtime and lifecycle
│   │   ├── departments/ # Eight department implementations
│   │   ├── providers/   # Free AI provider registry & fallback router
│   │   ├── governance/  # CEO Approval Gateway & Audit Ledger
│   │   ├── social/      # TikTok, Facebook, Instagram adapters
│   │   ├── scheduler/   # Executive briefings & weekly board routines
│   │   └── database/    # SQLite WAL schema & migrations
│   └── tests/           # Comprehensive backend test suite
├── android/             # Android Kotlin 2.0 Jetpack Compose application
│   ├── app/             # Application source code
│   │   └── src/main/java/com/ghdinteractivestudio/aioffice/
│   │       ├── ui/      # Glassmorphic Compose screens & components
│   │       ├── data/    # Network client, SSE listener, repository
│   │       └── domain/  # Domain models and business logic
├── team/                # Department charters, hierarchies, and rules
├── reports/             # Generated briefings, weekly audits, meeting minutes
├── scripts/             # Startup, migration, and automation tools
└── tests/               # Cross-system integration and verification tests
```

---

## Quick Start

### Backend (Ubuntu 24.04 PRoot / Linux ARM64)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Android Native Application

Open `android/` in Android Studio or build via Gradle:

```bash
cd android
./gradlew assembleDebug
```

---

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
