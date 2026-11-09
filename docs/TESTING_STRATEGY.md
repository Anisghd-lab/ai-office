# Testing & Quality Assurance Strategy

## 1. Testing Philosophy

In AI Office, code is never marked complete merely because it compiles. All modules must adhere to automated test verification:
- **Zero Hallucination of Results**: Real test commands are executed with exit codes and outputs logged.
- **Fail-Stop**: If any test fails, progression halts until the defect is analyzed and resolved.
- **Continuous Gate Enforcement**: Every phase requires running the corresponding test suite before committing and pushing.

---

## 2. Test Pyramid & Scope

```
                / \
               /   \      E2E Integration & Gateway Tests (Phase 4, 7, 10)
              /     \     - Full CEO Approval Flow
             /-------\    - SSE Stream & Reconnection
            /         \   
           /           \   Component Integration Tests (Phase 2, 3, 5)
          /             \  - Multi-Agent Orchestration & SQLite WAL
         /---------------\ - OAuth PKCE & Fallback Provider Router
        /                 \
       /                   \ Unit Tests (Phases 1-6)
      /                     \ - Pydantic Schemas, Hashing, Redaction, Mocking
     /-----------------------\
```

---

## 3. Test Suites

### 3.1 Backend Test Suites (`backend/tests/`)
1. `test_providers.py`:
   - Free provider discovery and registration.
   - Fallback router switching on HTTP 429 rate limit.
   - Sensitive credential redaction in logs and reports.
   - Quota tracking.
2. `test_database.py`:
   - SQLite WAL initialization, concurrent reads/writes.
   - Migration integrity and process restart persistence.
3. `test_governance.py`:
   - Default-deny interceptor verification.
   - Payload hash mutation detection.
   - Prevention of agent self-approval.
   - Expired token rejection.
   - Nonce single-use enforcement.
4. `test_agents.py`:
   - AI Manager task planning and delegation.
   - 8 Department Director instantiation.
   - Dynamic specialist spawning and teardown.
   - Inter-agent messaging and shared memory.
5. `test_social.py`:
   - OAuth state CSRF token validation.
   - PKCE challenge generation and validation.
   - Social publishing gateway interception.
6. `test_scheduler.py`:
   - Africa/Algiers timezone scheduling.
   - Daily briefing and Sunday board meeting generation.
7. `test_api.py`:
   - FastAPI endpoints and response schema validation.
   - SSE connection lifecycle and event formatting.

### 3.2 Android Test Suites (`android/app/src/test/`)
1. Unit tests for ViewModels (`OfficeBoardViewModelTest`, `ApprovalViewModelTest`, `AgentViewModelTest`).
2. Data layer tests for Retrofit client, SSE flow, and DataStore caching.
3. Gradle build verification.
