# AI OFFICE — FINANCIAL POLICY: ZERO ADDITIONAL COST ($0.00)

## 1. Absolute Commercial Invariant
AI Office operates under a strict **Zero Additional Cost ($0.00)** constraint:
- No paid API calls.
- No commercial subscriptions.
- No credit purchases or token top-ups.
- No paid fallbacks or automatic upgrades.
- No services with automatic billing or hidden trial conversions.

## 2. Google Pro Accounts Management
The Human Owner provides three Google Pro accounts with existing quotas.
Rules for utilization:
1. **Secure Registry**: Credentials, refresh tokens, and cookies are stored encrypted in the local SQLite vault (`AES-256-GCM`). Plaintext passwords and session cookies are NEVER logged.
2. **Quota Verification**: Before submitting any video or image generation job, the engine inspects observable quota availability. If quota is unknown or depleted, the operation pauses gracefully.
3. **No Circumvention**: Account rotation is used solely for legitimate load allocation permitted by service terms. The system strictly respects rate limits, abuse prevention gates, and terms of service.
4. **Preflight Cost Assertion**: If an operation has uncertain billing implications or could incur unexpected costs, it is rejected immediately.

## 3. Fallback Protocol on Quota Exhaustion
When external generation quotas are temporarily exhausted:
1. The active task transitions to `BLOCKED_BY_QUOTA` or `WAITING_FOR_QUOTA`.
2. The engine searches for an approved zero-cost alternative (e.g. local FFmpeg stitching, open-source models).
3. The situation is logged to the daily briefing and notified to Nova Prime.
4. The system never generates paid calls.
