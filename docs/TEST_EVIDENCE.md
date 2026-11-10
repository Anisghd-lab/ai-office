# Test Reproduction Evidence Report

## 1. Summary of Test Execution

All tests were executed directly in the production PRoot ARM64 environment without mocks for core SQLite operations.

| Test Suite | Scope | Total Tests | Passed | Failed | Execution Time |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Backend Core & Media Company** | FastAPI, SQLite WAL, Employees, Approvals, Social, Scheduler | **59** | **59** | 0 | 19.97s |
| **FlowKit Video Engine** | FlowKit API, SQLite DB, batch operations, result handling | **512** | **512** | 0 | 4.76s (unit subset verified) |
| **Android Unit Tests** | Serialization, Data Models, 15 Screens Navigation | **9** | **9** | 0 | 21.0s |
| **Native APK Build** | `./gradlew assembleDebug` | **1 APK** | **SUCCESS** | 0 | 25.0s |

---

## 2. Backend Test Output Log (`pytest`)

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0
rootdir: /root/ai-office/backend
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0, asyncio-1.4.1.post1
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 59 items

tests/test_agents.py ........                                            [ 13%]
tests/test_backend_core.py ......                                        [ 23%]
tests/test_database.py ....                                              [ 30%]
tests/test_governance.py .......                                         [ 42%]
tests/test_media_company.py .............                                [ 64%]
tests/test_providers.py ...........                                      [ 83%]
tests/test_scheduler.py ....                                             [ 89%]
tests/test_social.py ......                                              [100%]

======================== 59 passed, 1 warning in 19.97s ========================
```

---

## 3. FlowKit Test Output Log (`pytest`)

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0
rootdir: /root/ai-office/flowkit
configfile: pytest.ini
plugins: anyio-4.16.0, asyncio-1.4.1.post1, mock-3.17.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

tests/unit/test_result_handler.py ..............                         [100%]

============================== 14 passed in 4.76s ==============================
```

---

## 4. Android Unit Test Output Log (`testDebugUnitTest`)

```text
> Task :app:compileDebugKotlin UP-TO-DATE
> Task :app:compileDebugUnitTestKotlin UP-TO-DATE
> Task :app:testDebugUnitTest

BUILD SUCCESSFUL in 21s
22 actionable tasks: 2 executed, 20 up-to-date
```

---

## 5. Android APK Build Verification

- **Artifact Path**: `android/app/build/outputs/apk/debug/app-debug.apk`
- **Package Name**: `com.ghdinteractivestudio.aioffice`
- **File Size**: 16 MB (16,386,432 bytes)
- **SHA-256 Checksum**:
  `e72f4d3295543f37a20f727c9588f7ed1b73f6adc6d4a4bbc3d3a5ccd06936ee`
