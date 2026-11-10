# Database Migration Report: Schema 002 (Media Company Evolution)

## 1. Migration Overview

- **Migration File**: `backend/migrations/002_media_company_and_employees.sql`
- **Engine**: SQLite 3.45+ in Write-Ahead Logging (WAL) Mode (`PRAGMA journal_mode = WAL`)
- **Execution Date**: 2026-11-10
- **Baseline Version**: 001 (`001_initial_schema.sql`)
- **New Target Version**: 002 (`002_media_company_and_employees.sql`)

---

## 2. Table Additions & Schema Architecture

Migration 002 establishes 12 high-performance tables designed for high-concurrency local agent operations:

1. **`employees`**:
   - Master workforce registry tracking unique IDs (`emp-res-01`, `emp-edt-01`), names, departments, roles, levels (1-10), XP, and real-time status (`WORKING`, `FREE`, `WAITING_FOR_OWNER`, `STUCK`, `OFFLINE`).
   - Indexes: `idx_employees_dept`, `idx_employees_status`.

2. **`employee_sessions`**:
   - Live tracking of active and historical agent work sessions, associated tasks, project IDs, timestamps, and JSON output artifact references.
   - Index: `idx_emp_sessions_emp`.

3. **`employee_xp_events`**:
   - Implements the strict anti-duplicate XP award constraint via `UNIQUE(employee_id, task_id)`.
   - Records XP quantity, awarding authority (`OWNER` or `SYSTEM_ACCEPTED`), and reason.

4. **`projects`**:
   - Master audiovisual production projects with topic, target audience, niche, opportunity score (1-10), confidence percentage, and pipeline state.

5. **`content_opportunities`**:
   - High-velocity search and trend opportunities discovered by Research, linking evidence sources, velocity ratings, and format recommendations.

6. **`scripts`**:
   - Production scripts containing hook, narrative body, call-to-action, format specifications, and thumbnail concepts.

7. **`scenes`**:
   - Granular scene breakdowns specifying order, target duration, visual generation prompts, narration chunks, and audio cues.

8. **`production_jobs`**:
   - Rendering and generation jobs dispatched to FlowKit and local FFmpeg, tracking progress percentages, output paths, and automated QC reports.

9. **`media_assets`**:
   - Registry of rendered video clips, audio tracks, thumbnail images, and subtitle files with SHA-256 integrity checksums.

10. **`google_accounts`**:
    - Zero additional cost account registry. Stores masked email handles, encrypted credentials (AES-256-GCM), and real quota telemetry. Seeds the initial 3 authorized accounts (`gacc-01`, `gacc-02`, `gacc-03`).

11. **`library_proposals`**:
    - Saturday Library Hour tool evaluation proposals linking repository URLs, licenses, PRoot compatibility, and approval IDs.

12. **`publication_packages`**:
    - Final publication bundles combining video assets, titles, descriptions, and hashtags with links to the `approvals` table.

---

## 3. Idempotency & Verification

- Every statement uses `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.
- Seed data uses `INSERT OR IGNORE` to guarantee that repeated migration executions cause zero data corruption or duplication.
- Applied automatically by `MigrationManager` during application startup and validated in the test suite (`test_migrations_and_idempotency`).
