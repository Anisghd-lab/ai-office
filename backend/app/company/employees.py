"""Employee registry, session tracking, Live Office Board, and XP/Level progression."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.database.connection import db_manager
from app.events.bus import event_bus

REGISTRY_PATH = Path(__file__).parent.parent.parent.parent / "team" / "employees" / "registry.json"
LEVELS_PATH = Path(__file__).parent.parent.parent.parent / "team" / "employees" / "levels.json"

XP_LEVEL_THRESHOLDS = [
    (10, 3200, "Professional"),
    (9, 2500, "Specialist"),
    (8, 1900, "Expert"),
    (7, 1400, "Senior"),
    (6, 1000, "Advanced"),
    (5, 700, "Intermediate"),
    (4, 450, "Associate"),
    (3, 250, "Junior"),
    (2, 100, "Trainee"),
    (1, 0, "Beginner"),
]


class EmployeeService:
    """Manages company workforce, Live Office Board, sessions, and XP progression."""

    def __init__(self, registry_file: Path = REGISTRY_PATH):
        self.registry_file = registry_file
        self.sync_registry_to_db()

    def sync_registry_to_db(self) -> None:
        """Seed or synchronize employees from registry.json into SQLite employees table."""
        if not self.registry_file.exists():
            return

        try:
            data = json.loads(self.registry_file.read_text(encoding="utf-8"))
            employees = data.get("employees", [])

            with db_manager.session() as conn:
                for emp in employees:
                    blockers_json = json.dumps(emp.get("current_blockers", []))
                    conn.execute(
                        """
                        INSERT INTO employees (id, name, department, role, level, xp, status, current_task, current_project, last_activity, session_id, current_blockers)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            name=excluded.name,
                            department=excluded.department,
                            role=excluded.role,
                            updated_at=CURRENT_TIMESTAMP;
                        """,
                        (
                            emp["id"],
                            emp["name"],
                            emp["department"],
                            emp["role"],
                            emp.get("level", 1),
                            emp.get("xp", 0),
                            emp.get("status", "FREE"),
                            emp.get("current_task"),
                            emp.get("current_project"),
                            emp.get("last_activity"),
                            emp.get("session_id"),
                            blockers_json,
                        ),
                    )
        except Exception as e:
            logger.error(f"Error syncing employees registry to database: {e}")

    def list_employees(self) -> List[Dict[str, Any]]:
        """List all employees for the Live Office Board."""
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, department, role, level, xp, status, current_task, current_project,
                       last_activity, session_id, current_blockers
                FROM employees ORDER BY level DESC, xp DESC;
                """
            )
            rows = cursor.fetchall()
            result = []
            for r in rows:
                blockers = []
                if r["current_blockers"]:
                    try:
                        blockers = json.loads(r["current_blockers"])
                    except Exception:
                        pass
                result.append(
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "department": r["department"],
                        "role": r["role"],
                        "level": r["level"],
                        "xp": r["xp"],
                        "status": r["status"],
                        "current_task": r["current_task"],
                        "current_project": r["current_project"],
                        "last_activity": r["last_activity"],
                        "session_id": r["session_id"],
                        "current_blockers": blockers,
                    }
                )
            return result

    def get_company_overview(self) -> Dict[str, Any]:
        """Get aggregate metrics across all employees and departments."""
        employees = self.list_employees()
        active = [e for e in employees if e["status"] == "WORKING"]
        free = [e for e in employees if e["status"] == "FREE"]
        waiting = [e for e in employees if e["status"] == "WAITING_FOR_OWNER"]
        stuck = [e for e in employees if e["status"] == "STUCK"]
        offline = [e for e in employees if e["status"] == "OFFLINE"]

        dept_counts: Dict[str, int] = {}
        for e in employees:
            dept = e["department"]
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        return {
            "total_employees": len(employees),
            "working": len(active),
            "free": len(free),
            "waiting_for_owner": len(waiting),
            "stuck": len(stuck),
            "offline": len(offline),
            "by_department": dept_counts,
        }

    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, department, role, level, xp, status, current_task, current_project,
                       last_activity, session_id, current_blockers
                FROM employees 
                WHERE id = ? 
                   OR LOWER(id) = LOWER(?)
                   OR LOWER(REPLACE(name, ' ', '-')) = LOWER(?)
                   OR LOWER(REPLACE(REPLACE(name, 'Dr. ', ''), ' ', '-')) = LOWER(?);
                """,
                (employee_id, employee_id, employee_id, employee_id),
            )
            r = cursor.fetchone()
            if not r:
                return None
            blockers = []
            if r["current_blockers"]:
                try:
                    blockers = json.loads(r["current_blockers"])
                except Exception:
                    pass
            return {
                "id": r["id"],
                "name": r["name"],
                "department": r["department"],
                "role": r["role"],
                "level": r["level"],
                "xp": r["xp"],
                "status": r["status"],
                "current_task": r["current_task"],
                "current_project": r["current_project"],
                "last_activity": r["last_activity"],
                "session_id": r["session_id"],
                "current_blockers": blockers,
            }

    async def start_session(
        self,
        employee_id: str,
        session_id: str,
        task_id: Optional[str] = None,
        task_name: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record session start, transition status to WORKING, and broadcast SSE event."""
        now = datetime.now(timezone.utc).isoformat()
        with db_manager.session() as conn:
            conn.execute(
                """
                INSERT INTO employee_sessions (session_id, employee_id, task_id, project_id, status, started_at)
                VALUES (?, ?, ?, ?, 'WORKING', ?)
                ON CONFLICT(session_id) DO UPDATE SET status='WORKING', started_at=?;
                """,
                (session_id, employee_id, task_id, project_id, now, now),
            )
            conn.execute(
                """
                UPDATE employees
                SET status='WORKING', current_task=?, current_project=?, session_id=?, last_activity=?, updated_at=CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (task_name or task_id, project_id, session_id, now, employee_id),
            )

        event_payload = {
            "employee_id": employee_id,
            "session_id": session_id,
            "status": "WORKING",
            "task": task_name or task_id,
            "project_id": project_id,
            "timestamp": now,
        }
        await event_bus.publish("employee.session_started", event_payload)
        return event_payload

    async def finish_session(
        self,
        employee_id: str,
        session_id: str,
        next_status: str = "FREE",
        output_references: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record session finish, transition status, persist outputs, and broadcast SSE event."""
        now = datetime.now(timezone.utc).isoformat()
        outputs_json = json.dumps(output_references or {})

        with db_manager.session() as conn:
            conn.execute(
                """
                UPDATE employee_sessions
                SET status = ?, finished_at = ?, output_references = ?, error_message = ?
                WHERE session_id = ?;
                """,
                (next_status, now, outputs_json, error_message, session_id),
            )
            conn.execute(
                """
                UPDATE employees
                SET status = ?, current_task = NULL, session_id = NULL, last_activity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (next_status, now, employee_id),
            )

        event_payload = {
            "employee_id": employee_id,
            "session_id": session_id,
            "status": next_status,
            "timestamp": now,
            "outputs": output_references or {},
        }
        await event_bus.publish("employee.session_finished", event_payload)
        return event_payload

    def calculate_level_for_xp(self, xp: int) -> int:
        """Compute employee level from XP according to company progression policy."""
        for level, threshold, _ in XP_LEVEL_THRESHOLDS:
            if xp >= threshold:
                return level
        return 1

    def get_title_for_level(self, level: int) -> str:
        """Return title name for level."""
        for lvl, _, title in XP_LEVEL_THRESHOLDS:
            if lvl == level:
                return title
        return "Beginner"

    async def award_xp(
        self,
        employee_id: str,
        task_id: str,
        xp_amount: int,
        awarded_by: str = "OWNER",
        reason: str = "Task accepted and verified",
    ) -> Dict[str, Any]:
        """Award XP to employee upon OWNER acceptance. Guaranteed idempotent (anti-duplicate)."""
        import uuid
        event_id = f"xp-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        with db_manager.session() as conn:
            # Check if XP already awarded for this task to this employee
            cursor = conn.cursor()
            cursor.execute(
                "SELECT xp_amount FROM employee_xp_events WHERE employee_id = ? AND task_id = ?;",
                (employee_id, task_id),
            )
            existing = cursor.fetchone()
            if existing:
                logger.warning(f"XP already awarded for employee {employee_id} on task {task_id}.")
                emp = self.get_employee(employee_id)
                return {
                    "awarded": False,
                    "reason": "XP already awarded for this task",
                    "current_xp": emp["xp"] if emp else 0,
                    "level": emp["level"] if emp else 1,
                }

            # Insert XP event
            conn.execute(
                """
                INSERT INTO employee_xp_events (id, employee_id, task_id, xp_amount, awarded_by, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (event_id, employee_id, task_id, xp_amount, awarded_by, reason, now),
            )

            # Update employee XP and recompute Level
            cursor.execute("SELECT xp, level FROM employees WHERE id = ?;", (employee_id,))
            row = cursor.fetchone()
            current_xp = (row["xp"] if row else 0) + xp_amount
            new_level = self.calculate_level_for_xp(current_xp)

            conn.execute(
                """
                UPDATE employees
                SET xp = ?, level = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (current_xp, new_level, employee_id),
            )

        title = self.get_title_for_level(new_level)
        payload = {
            "employee_id": employee_id,
            "task_id": task_id,
            "xp_awarded": xp_amount,
            "total_xp": current_xp,
            "level": new_level,
            "title": title,
            "timestamp": now,
        }
        await event_bus.publish("employee.xp_awarded", payload)
        return {"awarded": True, **payload}


employee_service = EmployeeService()
