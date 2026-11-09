# Social Media Integrations & Official API Specifications

## 1. Supported Platforms & Capabilities

AI Office integrates strictly with official developer APIs using standard OAuth 2.0 PKCE and token vault security. Personal account scraping, headless browser automation, or undocumented APIs are strictly prohibited.

| Platform | Official API / Capability | Auth Type | Requirements |
| :--- | :--- | :--- | :--- |
| **TikTok** | TikTok Content Posting API | OAuth 2.0 PKCE | Registered TikTok Developer App, Approved Video/Photo Scope (`video.upload`, `video.publish`) |
| **Facebook** | Meta Graph API (Pages API) | OAuth 2.0 User -> Page Token | Facebook App, `pages_manage_posts`, `pages_read_engagement` |
| **Instagram** | Instagram Graph API (Professional) | OAuth 2.0 via Meta | Instagram Professional / Business Account linked to Facebook Page, `instagram_basic`, `instagram_content_publish` |

---

## 2. CEO Approval Integration Architecture

```
Marketing / Creative Agent
       |  (Prepares draft content, caption, tags)
       v
AI Manager (Reviews and packages action payload)
       |
       v
CEO Approval Gateway (Intercepts action, computes SHA-256 payload hash)
       |
       v
Android Control Center (Renders Glassmorphic preview card for CEO)
       |
 [Approve] / [Reject]
       |
       v  (If Approved)
Gateway verifies payload signature & single-use execution token
       |
       v
Social Media Adapter (Signs request with decrypted OAuth token from Vault)
       |
       v
Official Platform API (TikTok / Meta Graph API)
       |
       v
Audit Ledger records remote Post ID, status, and execution timestamp
```

---

## 3. Account Connection & OAuth Flow

1. **Initiate Authorization**:
   The Android app requests an authorization URL with a unique PKCE `code_verifier` and SHA-256 `code_challenge`.
2. **User Consent**:
   The CEO is directed to the official platform consent page via custom tabs / Android browser.
3. **Callback Processing**:
   The callback delivers the authorization code and matching `state` token to `http://127.0.0.1:8000/api/v1/social/{platform}/callback`.
4. **Token Exchange & Vaulting**:
   The backend exchanges the code for access/refresh tokens and immediately encrypts them with AES-256-GCM in the SQLite token vault.
5. **No Exposure**:
   Client secrets and tokens are never sent to the Android client or written to plaintext log files.
