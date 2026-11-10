# Employee 10-Level Progression System & Live Office Board

## 1. Overview

AI Office organizes its workforce with an authoritative 10-level skill and experience progression schema. Every employee begins with an initial level and XP based on their specialization, and advances dynamically as tasks are successfully executed, verified, and accepted by AI CEO Nova Prime or the Human Owner.

---

## 2. Level Progression Matrix (`team/employees/levels.json`)

| Level | Title | XP Required | Promotion Criteria | Operational Autonomy |
| :---: | :--- | :---: | :--- | :--- |
| **1** | Beginner | 0 | Entry into workforce | Assisted tasks only |
| **2** | Trainee | 100 | 2 simple tasks completed | Basic task execution |
| **3** | Junior | 250 | 5 tasks verified | Independent draft generation |
| **4** | Associate | 450 | Consistent quality metrics | Specialized prompt workflows |
| **5** | Intermediate | 700 | Cross-department collaboration | Multi-step task pipelines |
| **6** | Advanced | 1,000 | Zero-defect task track record | Autonomous scene breakdowns |
| **7** | Senior | 1,400 | Departmental mentoring | Strategy formulation & quality review |
| **8** | Expert | 1,900 | High velocity opportunity capture | Director-level operational leadership |
| **9** | Specialist | 2,500 | Complex pipeline mastery | Department lead & architecture oversight |
| **10** | Professional | 3,200+ | Master organizational impact | Autonomous executive authority |

---

## 3. Strict Anti-Duplicate XP Constraint

To prevent gaming or accidental XP double-counting, the database enforces a unique constraint on `(employee_id, task_id)` in the `employee_xp_events` table:

```sql
CREATE TABLE IF NOT EXISTS employee_xp_events (
    id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL REFERENCES employees(id),
    task_id TEXT NOT NULL,
    xp_amount INTEGER NOT NULL,
    awarded_by TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, task_id)
);
```

When an attempt is made to award XP for an already credited task, the service logs a warning and gracefully rejects the duplication without throwing unhandled database errors:
```json
{
  "awarded": false,
  "reason": "XP already awarded for this task",
  "current_xp": 2100,
  "level": 8
}
```

---

## 4. Live Office Board Telemetry

The Live Office Board provides real-time visibility into the current state of every employee in the organization:
- **Session Lifecycle**: When an employee begins working, their status transitions from `FREE` to `WORKING`, updating their `current_task`, `current_project`, and `session_id`.
- **Completion & Feedback**: Upon session finish, output artifacts (script ID, scene renders) are linked in the database and their status returns to `FREE`.
- **Live SSE Event Distribution**: Any session change or XP award immediately broadcasts an event over SSE (`employee.session_started`, `employee.session_finished`, `employee.xp_awarded`), allowing the Android Live Office Board to update reactively without continuous polling.
