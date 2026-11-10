# AI Office Zero Additional Cost Financial Policy

## 1. Absolute Financial Invariant

**Zero Additional Financial Cost ($0.00 USD).**

AI Office is designed, built, and operated under the strict constraint that no monetary charges, recurring subscriptions, paid API tokens, paid cloud hosting, or paid third-party SDKs may ever be incurred.

---

## 2. Resource Discovery & Free Quota Strategy

### 2.1 AI Model Providers
AI Office utilizes only verified free-tier and legitimately available quota endpoints:
1. **OpenRouter Free Tier**:
   - `meta-llama/llama-3.2-3b-instruct:free`
   - `google/gemini-2.0-flash-exp:free`
   - Models ending in `:free` with verified 0.00 cost per token.
2. **Google Gemini Free Tier**:
   - `gemini-1.5-flash` / `gemini-2.0-flash` free promotional and developer quotas.
3. **Local Fallback Heuristics**:
   - Deterministic rule engines that operate completely offline if no cloud network connection is available.

### 2.2 Google Pro Accounts Registry (Migration 002)
AI Office integrates 3 authorized Google Pro accounts without storing plaintext secrets:
- Table `google_accounts` stores masked email handles (`pro.account.1***@gmail.com`).
- Credentials (session cookies/tokens) are encrypted using **AES-256-GCM** with 96-bit random nonces.
- Quotas are actively audited from real responses (`available_quota`, `current_usage`).
- Preflight eligibility check (`verify_generation_eligibility`) asserts `cost_usd == 0.0` before any generation job is dispatched.

---

## 3. Financial Guardrails in Code

1. **Pre-Action Audit**: Every proposed action calculates an estimated financial cost.
2. **Hard Ceiling**: If any operation estimates `cost > 0.0`, the backend rejects the action before contacting external networks.
3. **Approval Interception**: Even if a user were to configure a paid endpoint, the default-deny approval gateway forces explicit confirmation with cost prominently displayed in neon amber.
4. **Local Rendering**: Video timeline assembly and audio mixing utilize local FFmpeg 6.1.1 on device ARM64 PRoot, incurring zero cloud rendering expenses.
