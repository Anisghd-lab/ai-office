# Security Model & Governance Specification

## 1. Threat Model & Principles

AI Office operates in a zero-trust model where autonomous AI agents cannot execute external side-effects without explicit, cryptographic CEO approval.

### Primary Threat Vectors:
1. **Prompt Injection / Jailbreak**: Malicious content in research inputs attempting to instruct agents to publish unauthorized statements or perform destructive actions.
2. **Autonomous Scope Escalation**: Agents generating tasks that attempt to bypass approval or grant themselves elevated privileges.
3. **Payload Tampering**: Modifying the content, destination, or parameters of an approval request after CEO review but prior to execution.
4. **Replay Attacks**: Re-executing a previously approved token for subsequent unauthorized publications.
5. **Secret Exfiltration**: Accidental logging or committing of API keys, OAuth access tokens, or refresh tokens.

---

## 2. Invariants of the CEO Approval Gateway

1. **Default-Deny Invariant**:
   Any action touching external network interfaces, third-party APIs, or persistent credential changes is blocked at the gateway level until a valid approval token signed by the CEO exists.

2. **Self-Approval Prohibition**:
   No agent, including the AI Manager, possesses endpoints or capability tokens to authorize an approval request. Only the CEO's client on `127.0.0.1` (or authenticated session) can execute the approve endpoint.

3. **Cryptographic Payload Binding**:
   When an approval request is generated:
   $$\text{payload\_hash} = \text{SHA-256}(\text{canonical\_json}(\text{payload}))$$
   At execution time:
   $$\text{current\_hash} = \text{SHA-256}(\text{canonical\_json}(\text{execution\_payload}))$$
   If $\text{payload\_hash} \neq \text{current\_hash}$, execution is instantly aborted with `HTTP 403 (Payload Mismatch)`.

4. **Single-Use Nonce & Expiry**:
   Each approval token can be redeemed exactly once. Upon execution, its status moves atomically to `EXECUTED`. Any secondary attempt results in `HTTP 409 (Token Already Used)`. Requests expire automatically after 30 minutes.

5. **Immutable Audit Ledger**:
   All state transitions (`PENDING`, `APPROVED`, `REJECTED`, `EXECUTED`, `FAILED`, `EXPIRED`) are written to an append-only SQLite table with timestamp, agent ID, department ID, action type, hash, and decision audit logs.

---

## 3. Cryptographic Storage & Vault

OAuth tokens (TikTok, Facebook, Instagram) are encrypted at rest using AES-256-GCM:
- Nonces (12 bytes) generated via `os.urandom(12)`.
- Key derived from environment variable `ENCRYPTION_KEY_32BYTES_BASE64` or local secure keyfile with strict `0600` permissions.
- In memory, decrypted tokens exist solely within transient execution scopes and are zeroed or garbage-collected immediately after network requests.
