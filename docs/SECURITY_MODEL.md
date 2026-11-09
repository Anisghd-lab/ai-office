# Security Model & Governance Specification

## 1. Threat Model & Principles

AI Office operates under a zero-trust governance model where the **Human User / Owner** exercises final veto over external side effects, while the **AI CEO** holds autonomous operational executive power internally.

---

## 2. Governance Boundary Invariants

1. **Human Owner Approval Invariant**:
   Any action touching external network interfaces, third-party APIs (social media publishing), or persistent credential modifications is blocked at the gateway until a valid approval token signed by the **Human Owner / User** is verified.

2. **AI CEO Self-Approval Prohibition**:
   The AI CEO runs internal operations autonomously but **CANNOT** authorize its own external actions or bypass the User Approval Gateway.

3. **Cryptographic Payload Binding**:
   When an external action is proposed:
   $$\text{payload\_hash} = \text{SHA-256}(\text{canonical\_json}(\text{payload}))$$
   At execution time:
   $$\text{current\_hash} = \text{SHA-256}(\text{canonical\_json}(\text{execution\_payload}))$$
   If $\text{payload\_hash} \neq \text{current\_hash}$, execution aborts immediately with `PayloadTamperedError` and an alert is recorded in `audit_ledger`.

4. **Single-Use Nonce & Expiry**:
   Each approval token can be redeemed exactly once. Upon execution, its status atomically becomes `EXECUTED`. Replay attempts fail with `ReplayAttackError`.

5. **Zero-Cost Commercial Guardrail**:
   Financial transactions, subscriptions, and paid endpoints are strictly rejected with `PaidEndpointForbiddenError`.

6. **Local Loopback Isolation**:
   The backend binds strictly to `127.0.0.1` by default. Requests from the Android Control Center supply the `X-Owner-Key` header.
