# Autonomous Organizational Scheduler & Executive Reports

## 1. Operating Rhythm & Autonomous Cron Schedules

AI Office operates on an autonomous organizational schedule configured in `app/scheduler/engine.py`:

| Routine Event | Timing (Africa/Algiers) | Purpose | Output |
| :--- | :--- | :--- | :--- |
| **Daily Executive Briefing** | Every Day at 08:00 | Synthesize yesterday's production, active jobs, and quota health | `ceo_briefings` record + Android notification |
| **Trend & Opportunity Scan** | Every 4 Hours | Detect new high-velocity search queries and emerging niches | `content_opportunities` records |
| **Automated Pipeline Sweep** | Every 30 Minutes | Advance pending scenes, run QC, and surface completed jobs | Updates in `projects` and `production_jobs` |
| **Weekly Retrospective** | Every Friday at 17:00 | Aggregate weekly employee XP awards, task velocity, and zero-cost audits | `weekly_reports` record |
| **Saturday Library Hour** | Saturday at 14:00 (1h) | Curate and benchmark promising open-source tools within PRoot boundary | `library_proposals` submitted to Needs You gateway |

---

## 2. Executive Memory & Reporting

1. **Organizational Memory**: All major decisions made by AI CEO Nova Prime and the Human Owner are archived in the `knowledge_base` with provenance tracking.
2. **Weekly Performance Analytics**: Evaluates departmental throughput, QC first-pass acceptance rate, and quota efficiency.
3. **Audit Trail**: Every action transition, approval decision, and XP event is immutably logged with UTC timestamps in SQLite WAL tables.
