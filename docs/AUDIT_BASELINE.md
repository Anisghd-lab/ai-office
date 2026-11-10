# AUDIT BASELINE
**AI Office — Autonomous Multi-Agent Organization**

- **UTC Timestamp**: 2026-11-10T09:42:00Z
- **Repository URL**: `https://github.com/Anisghd-lab/ai-office`
- **Current Branch**: `audit/full-compliance-and-release` (branched from `main` at `6b434ac`)
- **Base Commit SHA**: `6b434acd488b066cca2781639f0da3f76ece9d8a`
- **Working-Tree Status**: Clean (no uncommitted or untracked changes at branch point)
- **GitHub Authentication**: Authenticated as `Anisghd-lab` via GitHub CLI (`gh`)
- **Remote Synchronization**: `origin/main` was synchronized at commit `6b434ac`
- **Existing Git Tags**: None (`git tag -l` returned 0 tags)
- **Existing GitHub Releases**: None (`gh release list` returned "no releases found")

---

## 1. Runtime Environment & Toolchain Versions

| Component | Detected Version | Details |
| :--- | :--- | :--- |
| **OS / Architecture** | Linux 6.17.0-PRoot-Distro `aarch64` | Ubuntu 24.04 PRoot on Android 16 ARM64 |
| **Python** | Python 3.12.3 | `/usr/bin/python3` & `backend/.venv/bin/python3` |
| **Pytest** | pytest 9.2.0 | `backend/.venv/bin/pytest` |
| **Java / JDK** | OpenJDK 21.0.12.1 (build 21.0.12.1+1-1-24.04.4-Ubuntu) | `/usr/lib/jvm/java-21-openjdk-arm64` |
| **Gradle** | Gradle 8.9 | Wrapper `./gradlew` in `android/` |
| **Kotlin (Gradle)** | Kotlin 1.9.23 (embed), Kotlin 2.0.0 (app) | Configured in `android/build.gradle.kts` |
| **Android SDK** | Android SDK Tools installed | SDK platforms `android-34`, `android-35` in `/root/Android/Sdk` |
| **Android Build Tools** | 34.0.0, 36.0.0-rc1, 37.0.0-rc1 | AAPT2 and DEX compilers verified |
| **Git** | git version 2.43.0 | Configured with `gh auth setup-git` helper |
| **GitHub CLI** | gh 2.45.0 | Authenticated as `Anisghd-lab` |

---

## 2. Baseline Source Tree Structure

- `backend/`: FastAPI application, SQLite WAL manager, multi-agent engine, social platform adapters, executive scheduler, unit tests.
- `android/`: Native Android 16 Kotlin 2.0 Jetpack Compose application (`com.ghdinteractivestudio.aioffice`) with 12 Glassmorphic dashboard screens.
- `team/`: Department charters and AI CEO role definitions.
- `docs/`: Architecture, roadmap, security model, API contract, and execution records.
- `scripts/`: Production startup, migration, test runner, and APK build scripts.
- `.github/workflows/`: CI/CD workflow configuration (`ci.yml`).
