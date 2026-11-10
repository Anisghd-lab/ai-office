# Saturday Library Hour Policy & Open-Source Tool Evaluation

## 1. Purpose & Scope

The **Saturday Library Hour** is a structured, 1-hour recurring window (Saturdays 14:00 - 15:00 Africa/Algiers) during which the organization researches, evaluates, and proposes open-source tools to expand its audiovisual production capabilities.

---

## 2. Safety Rules & Zero-Cost Mandate

No tool may be proposed or installed unless it strictly adheres to the following criteria:
1. **100% Free / Open Source**: Permitted licenses are MIT, Apache 2.0, BSD, or MPL. No dual-license tools with commercial payment tiers.
2. **ARM64 Native & PRoot Compatible**: Must compile or execute on Linux ARM64 (Ubuntu 24.04 PRoot) without requiring root kernel drivers or virtualization that fails inside PRoot.
3. **No Phantom Quotas / No Subscriptions**: Must not rely on paid external API endpoints.
4. **Mandatory Human Approval**: No tool may be installed autonomously. Every tool candidate MUST be submitted as a formal proposal to the **NEEDS YOU Gateway** for Owner sign-off.

---

## 3. Proposal Schema & Evaluation Criteria

When a tool candidate is curated, `LibraryHourManager.propose_tool()` generates a structured proposal containing:
- `tool_name` & `repository_url`
- `license_name` & `last_maintenance` date
- `dependencies` (e.g. Node.js, FFmpeg, Python)
- `arm64_compatible` & `proot_compatible` booleans
- `security_risks` analysis
- `required_permissions` (e.g. local disk access)
- `benefits` & `installation_size_mb`
- `integration_plan`
- `recommendation` (`PROCEED_WITH_BENCHMARK`, `REJECT_RISKY`, `MONITOR`)

The action is inserted into `approvals` with type `INSTALL_TOOL` and destination `LOCAL_ENVIRONMENT`, ensuring the Human Owner has complete oversight before any disk storage or package installation occurs.
