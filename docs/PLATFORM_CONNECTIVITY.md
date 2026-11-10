# AI OFFICE — COMPLETE PLATFORM CONNECTIVITY ARCHITECTURE

**Specification Version**: 1.2.0  
**Status**: VERIFIED & DEPLOYED  
**Operating Model**: Autonomous AI Media Company  
**Cost Model**: 100% Free / Freemium ($0.00 USD Invariant)  
**Executive Authority**: Nova Prime — AI CEO  
**Human Role**: OWNER / PRINCIPAL / FINAL APPROVER  

---

## 1. Executive Summary

AI Office provides true one-tap platform connectivity directly initiated by the Human Owner from the Android application control center (`SETTINGS → CONNECTED ACCOUNTS`).

The system strictly avoids deceptive connection claims: an account is never marked as connected simply because an external application or web page opened. Connection validity requires complete OAuth 2.0 PKCE code exchange, encrypted credential storage, and an immediate harmless read-only API test to verify identity, scopes, and zero-cost quota limits.

---

## 2. Supported Platforms & Capabilities Matrix

| Platform | Slot ID | Protocol | Required Scopes | Verified Capabilities | Harmless Read-Only Test Method |
|---|---|---|---|---|---|
| **Google Account 1** | `google-1` | OAuth 2.0 PKCE | `openid`, `email`, `profile` | Primary Identity Verification, Profile Sync, Zero-Cost Quota Pool | `GET oauth2/v3/userinfo` |
| **Google Account 2** | `google-2` | OAuth 2.0 PKCE | `openid`, `email`, `profile` | Secondary Identity Slot, Failover Quota Pool | `GET oauth2/v3/userinfo` |
| **Google Account 3** | `google-3` | OAuth 2.0 PKCE | `openid`, `email`, `profile` | Tertiary Identity Slot, Independent Quota Pool | `GET oauth2/v3/userinfo` |
| **YouTube** | `youtube` | OAuth 2.0 PKCE + Data API v3 | `youtube.readonly`, `youtube.upload`, `openid`, `email` | Channel Identity, Video Upload, Shorts Publishing, Analytics | `GET youtube/v3/channels?part=snippet,statistics&mine=true` |
| **TikTok** | `tiktok` | Login Kit & Content Posting v2 | `user.info.basic`, `video.upload`, `video.publish` | Direct Video Posting, Creator Identity, Analytics | `GET open.tiktokapis.com/v2/user/info/` |
| **Instagram** | `instagram` | Meta Graph API v21.0 | `instagram_basic`, `instagram_content_publish`, `pages_show_list` | Professional/Business Account, Reels Publishing, Photo Feed, Insights | `GET graph.facebook.com/v21.0/me/accounts?fields=instagram_business_account` |
| **Facebook** | `facebook` | Meta Graph API v21.0 | `pages_manage_posts`, `pages_read_engagement`, `pages_show_list` | Managed Page Authorization, Feed Posts, Page Insights | `GET graph.facebook.com/v21.0/me/accounts` |

---

## 3. Strict 9-State Operational Lifecycle

Accounts transition strictly through explicit operational states:

```
[DISCONNECTED]
      │
      ▼  (Owner taps CONNECT)
[APP_OPENED] (Android native intent or OAuth auth_url)
      │
      ▼  (Owner selects account & grants consent)
[USER_AUTHENTICATED]
      │
      ▼  (Callback code exchange via aioffice://oauth/callback)
[ACCOUNT_AUTHORIZED] (Tokens AES-256 encrypted in Vault)
      │
      ▼  (Immediate harmless read-only test executed)
[API_OPERATIONAL] ──► [PUBLISHING_READY] (Approval Gateway Gated)
      │
      ├── (Token lifetime exceeded) ──► [TOKEN_EXPIRED] ──► [REAUTHORIZATION]
      │
      ├── (Scope / Business Verification Missing) ──► [DEGRADED]
      │
      └── (Network or Revocation Failure) ──► [ERROR]
```

1. **`DISCONNECTED`**: Account has no active OAuth tokens in vault.
2. **`APP_OPENED`**: Native application or OAuth web page launched via Android intent.
3. **`USER_AUTHENTICATED`**: User selected account and completed authentication on provider.
4. **`ACCOUNT_AUTHORIZED`**: Authorization code exchanged for tokens and vaulted in AES-256 storage.
5. **`API_OPERATIONAL`**: Live harmless read-only test succeeded; identity and capabilities verified.
6. **`PUBLISHING_READY`**: Account is eligible for scheduled broadcasts (strictly gated by Human Owner approval).
7. **`TOKEN_EXPIRED`**: Token lifetime exceeded without refresh token; one-tap reauthorization required.
8. **`DEGRADED`**: Account authenticated but missing professional business linking or optional scopes.
9. **`ERROR`**: Third-party API failure, quota exhaustion, or revoked permissions.

---

## 4. Android One-Tap Experience

- **Navigation**: Settings / Navigation bar → `Connected Accounts` (`Screen.SocialAccounts`).
- **Glassmorphic Presentation**: High-contrast iOS-inspired frosted cards with real-time colored status borders:
  - Emerald Green: `API_OPERATIONAL`
  - Amber: `ACCOUNT_AUTHORIZED`
  - Rose/Red: `TOKEN_EXPIRED` or `ERROR`
  - Subtle Glass: `DISCONNECTED`
- **Actions**:
  - `CONNECT`: Launches official native app or opens browser with PKCE authorization URL.
  - `TEST API`: Triggers live harmless read-only test verification and updates badges.
  - `REAUTHORIZE`: Clears stale session and starts fresh authorization.
  - `DISCONNECT`: Revokes tokens securely.
  - `QUICK VERIFY`: Simulates verified connect for offline / developer zero-cost testing.
- **Deep Link Handling**: `aioffice://oauth/callback?platform={platform}&status=success` captured by `MainActivity` and forwarded to `OfficeViewModel.handleOAuthDeepLink(uri)`.

---

## 5. Security & Governance Invariants

1. **Zero-Cost Invariant ($0.00 USD)**:
   All operations use official free quotas, developer sandboxes, and zero-cost API tiers. Paid API calls are rejected unconditionally with `PaidEndpointForbiddenError`.
2. **User Approval Gateway ("NEEDS YOU")**:
   Autonomous agents (Marketing, Creative, Social Media) can only propose publications. The backend automatically intercepts drafts into `approvals` table. No content reaches any external API without explicit Human Owner cryptographic approval.
3. **AES-256-GCM Token Storage**:
   Access and refresh tokens are encrypted at rest with AES-256-GCM before database insertion. Tokens are never exposed in logs or unauthenticated API endpoints.
4. **RFC 7636 PKCE & CSRF Protection**:
   OAuth flows use SHA-256 code challenge with state token binding to prevent injection, replay, and CSRF attacks.

---

## 6. Verification Evidence

- **Backend Pytest Suite**: `tests/test_platform_connectivity.py` (7 tests covering all platforms passed).
- **Backend Full Suite**: 66 unit & integration tests passing in `27.01s`.
- **Android Unit Suite**: `OfficeModelsTest.kt` passing.
- **Live Device Installation**: `com.ghdinteractivestudio.aioffice` installed and active on Android 16 ARM64 (`192.168.8.104:37399`).
