# AI Office Environment & API Discovery Audit

Date: 2026-11-09  
Target Platform: Android 16 ARM64 + Termux / Ubuntu 24.04 PRoot Container  
Architecture: `aarch64` (ARM64)  
Linux Kernel: `6.17.0-PRoot-Distro aarch64`

---

## 1. Toolchain & Runtime Environment

| Component | Detected Version | Path / Reference | Status |
| :--- | :--- | :--- | :--- |
| **Python** | 3.12.3 | `/usr/bin/python3` | Verified |
| **SQLite (Python module)** | 3.45.1 (WAL supported) | Python standard library | Verified |
| **Java / OpenJDK** | 21.0.12.1+1-1-24.04.4 | `/usr/lib/jvm/java-21-openjdk-arm64` | Verified |
| **Gradle** | 8.9 | `/usr/local/bin/gradle` | Verified |
| **Android SDK** | Platforms: 34, 35; Build-tools: 34, 36, 37 | `/root/Android/Sdk` | Verified |
| **Git** | 2.43.0 | `/usr/bin/git` | Verified |
| **GitHub CLI** | 2.x | `/usr/bin/gh` (Authenticated: `Anisghd-lab`) | Verified |
| **Networking CLI** | curl, wget, jq, rsync, zip, unzip | `/usr/bin/*` | Verified |

---

## 2. AI Provider Discovery & Quota Audit

### 2.1 Discovered Provider Credentials in Environment

| Provider | Variable Detected | Availability | Tier / Models | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **OpenRouter** | `OPENROUTER_API_KEY` | Available (Masked) | Free tier (`:free` suffix models) | Supports `meta-llama/llama-3.2-3b-instruct:free`, `google/gemini-2.0-flash-exp:free`, `mistralai/mistral-7b-instruct:free`, `qwen/qwen-2.5-coder-32b-instruct:free` |
| **Local OpenAI-Compatible** | Configurable via `LOCAL_OPENAI_BASE_URL` | Optional (default: `http://127.0.0.1:11434/v1`) | Free local execution (Ollama/llama.cpp/vLLM) | Zero external data transit, 100% free |
| **Google Gemini** | Configurable via `GEMINI_API_KEY` | Free quota tier (15 RPM / 1M TPM on free models) | `gemini-1.5-flash`, `gemini-2.0-flash-exp` | Free tier quota tracking enabled |
| **Groq** | Configurable via `GROQ_API_KEY` | Free developer tier | `llama-3.3-70b-versatile`, `llama-3.1-8b-instant` | Free quota tracking enabled |
| **Hugging Face** | Configurable via `HUGGINGFACE_API_KEY` | Free inference API | Open access models | Rate-limited free tier |

### 2.2 Security & Redaction Policy
- No API keys, credentials, or session tokens are stored in source control or printed in system logs.
- Dynamic key redaction is implemented in all log formatters and error handlers: any key matching regex patterns for tokens is masked with `[REDACTED_API_KEY]`.
- Accidental paid tier requests are forbidden by the Model Router: endpoints with non-zero pricing or unapproved billable tokens are rejected.

---

## 3. Storage & Process Constraints

- **PRoot Memory Budget**: Lightweight daemon target < 150 MB RSS.
- **Persistence**: SQLite database with Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) and memory-mapped I/O (`PRAGMA mmap_size = 268435456;`).
- **Loopback Binding**: Backend strictly binds to `127.0.0.1:8000` to prevent exposure across local mobile hotspot or Wi-Fi subnets.
