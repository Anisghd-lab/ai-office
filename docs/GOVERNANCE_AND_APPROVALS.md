# AI Office Governance, Approvals, and the "NEEDS YOU" Gateway

## 1. Governance Principles

The operational framework of AI Office enforces strict human sovereignty over external actions while granting full autonomous agency to AI Executive **Nova Prime** for internal organizational decisions.

### Autonomous Internal Operations (Permitted Without Approval):
- Scanning content velocity, search trends, and niche metrics.
- Writing, editing, polishing, and formatting video scripts.
- Breaking down scripts into scenes, visual prompts, and narration chunks.
- Starting and stopping internal employee sessions.
- Calculating XP progression and awarding level promotions.
- Rendering test audio, generating video scenes with FlowKit, and stitching timelines with FFmpeg.
- Performing automated Quality Control checks (aspect ratio, duration, audio normalization, black frames).

### External Action Boundary (Strictly Requires Human Approval):
- **Publishing media or posts to external social networks** (YouTube Shorts, TikTok, Instagram, Twitter/X).
- **Spending any financial currency** (enforced at $0.00 zero-cost invariant).
- **Modifying accounts, credentials, or API configurations**.
- **Installing new third-party software, libraries, or tools** (including Library Hour evaluations).

---

## 2. The "NEEDS YOU" Approval Gateway

When an autonomous pipeline reaches Phase F (Publication Preparation) or an employee proposes a new tool during Saturday Library Hour, the action is automatically halted and intercepted by the **NEEDS YOU Gateway**.

```
[Autonomous Media Pipeline]
         │
         ▼
[Phase F: Publication Package Assembled]
         │
         ▼
[Compute Canonical JSON Hash: SHA-256]
         │
         ▼
[Insert Gateway Record (Status: PENDING, Cost: $0.00)]
         │
         ▼
[SSE Broadcast: "approval.created"] ───► [Android Control Center: "NEEDS YOU"]
                                                        │
                                                        ▼
                                            [Human Owner Decision]
                                            ├── [APPROVE] ──► Dispatch Authorized Action
                                            └── [REJECT]  ──► Feedback Sent to Nova Prime
```

### Deterministic Cryptographic Hashing
To prevent tampering or race conditions between proposal and execution, every action payload is serialized to canonical sorted JSON and hashed with SHA-256:
```python
canonical_str = json.dumps(
    payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
)
payload_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
```
The Human Owner approves the exact hash. If the payload is modified after proposal, the hash verification fails and execution is rejected.

---

## 3. Human Owner Authentication

Requests originating from the Android Control Center pass the Human Owner authorization header:
```http
X-Owner-Key: <AES-GCM or pre-shared Owner Secret>
```
The backend verifies the key using timing-safe comparison (`secrets.compare_digest`). In development environments bound to local loopback (`127.0.0.1`), safe loopback authentication defaults are applied to allow seamless paired testing.
