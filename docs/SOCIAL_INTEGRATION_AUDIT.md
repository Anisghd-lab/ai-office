# AI Office — Social Media Integration Audit

**Audit Date**: 2026-11-10  
**Repository**: [Anisghd-lab/ai-office](https://github.com/Anisghd-lab/ai-office)  
**Lead**: Social Media API Integration Engineering  
**Scope**: TikTok, Facebook, Instagram OAuth 2.0 PKCE, Publishing Pipeline, Approval Interception.

---

## 1. Executive Summary

The social media integration module enables AI Office departments (primarily Marketing & Communications) to prepare content for TikTok, Facebook, and Instagram while strictly preventing unauthorized publishing.

Every outbound transmission requires an unforgeable, cryptographically signed approval decision from the **Human Owner / Principal**.

**Audit Status**: **PASS — Default-deny publishing, PKCE security, and vault persistence verified**.

---

## 2. Authentication Architecture (OAuth 2.0 + PKCE)

All external social accounts use OAuth 2.0 with PKCE (RFC 7636) to prevent authorization code interception:

1. **Code Verifier & Challenge**:
   - High-entropy cryptographic random string generated for each authorization flow (`secrets.token_urlsafe(64)`).
   - Code challenge derived via `SHA-256` and URL-safe base64 encoding without padding.
2. **CSRF State Tokens**:
   - Ephemeral CSRF tokens validated on redirect callback.
   - Mitigates cross-site request forgery and replay attacks.
3. **Encrypted Token Vault**:
   - Access tokens and refresh tokens stored encrypted in SQLite using AES-256-GCM.
   - Plaintext credentials never logged or sent to frontend clients.

---

## 3. End-to-End Publishing Governance Lifecycle

```
[ Marketing Director / Agent ]
              │
              ▼ (1. Formulates Post)
    [ Draft Social Post ]
              │
              ▼ (2. Submits Proposal to Gateway)
    [ User Approval Gateway ] ──(Status: PENDING)
              │
              ▼ (3. Notification via StateFlow)
    [ Android Native App: Pending Approvals Screen ]
              │
              ├──► [ Human Owner REJECTS ] ──► Action Discarded
              │
              └──► [ Human Owner APPROVES ]
                        │
                        ▼ (4. Re-hashes payload, verifies Actor == OWNER)
              [ Gateway Dispatches Post ]
                        │
                        ▼ (5. Authenticated API Call)
              [ TikTok / Facebook / Instagram API ]
```

### Direct Publishing Prevention:
- Direct calls to social API publishing endpoints bypass without a valid `approval_token` are rejected with `HTTP 403 Forbidden` (`UnauthorizedPublicationError`).
- Any alteration to the caption, media URL, or target platform between approval and dispatch invalidates the payload hash and halts publication.

---

## 4. Test Suite Verification

The social integration suite (`backend/tests/test_social.py`) validates:

1. `test_pkce_pair_generation`: Confirms RFC 7636 compliant S256 code challenge generation.
2. `test_oauth_state_and_csrf_validation`: Rejects invalid or expired OAuth state parameters.
3. `test_token_vault_lifecycle`: Confirms AES-256-GCM storage, retrieval, and revocation of tokens.
4. `test_social_publishing_approval_flow`: End-to-end simulation of proposal -> human approval -> publication execution.
5. `test_social_api_endpoints`: Verifies FastAPI REST endpoints for accounts, posts, and status.
6. `test_talk_to_ai_ceo_api`: Verifies interactive conversational briefing between Owner and Nova Prime.

**Status**: **6/6 PASSED** (Execution time: 1.84s).
