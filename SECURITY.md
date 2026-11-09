# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Model Overview

AI Office enforces a zero-trust multi-agent security framework:

1. **Default-Deny External Action Gateway**:
   Autonomous internal operations (research, brainstorming, draft composition, internal task assignments) are permitted. All external modifications (publishing posts, external messaging, financial commitments, external token creation, deletions) require explicit cryptographic/state approval from the CEO via the Android Control Center.

2. **Payload Hash Invariant**:
   Approval decisions are cryptographically bound to the SHA-256 digest of the exact action payload. Any post-approval mutation invalidates the authorization token.

3. **Single-Use Authorization**:
   Execution grants are one-time tokens that expire within a bounded TTL (default: 30 minutes). Replay attempts are rejected.

4. **Self-Approval Prohibition**:
   No agent (including the AI Manager) possesses the capability or privilege level to authorize its own external actions or bypass the governance gateway.

5. **Local Loopback Isolation**:
   The backend binds strictly to `127.0.0.1` by default to safeguard against unauthorized network ingress on shared local networks. Remote access is opt-in and requires mutual authentication.

6. **Zero Secrets in Code**:
   OAuth refresh tokens and API credentials are kept in a local SQLite-backed token vault encrypted with AES-256-GCM.

## Reporting a Vulnerability

If you discover a security vulnerability, please do NOT file a public issue.
Instead, email security disclosures to `m_ghediri@yahoo.com` or create a private GitHub Security Advisory in the repository.
