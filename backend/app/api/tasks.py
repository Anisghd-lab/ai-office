"""Tasks API router."""

import sqlite3
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_ceo_auth
from app.database.connection import get_db
from app.events.bus import event_bus
from app.api.schemas import TaskCreateRequest, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
def list_tasks(
    department_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    conn: sqlite3.Connection = Depends(get_db),
):
    cursor = conn.cursor()
    query = "SELECT id, title, description, department_id, assigned_agent_id, status, priority, progress_pct, payload, result, error_message, created_at, updated_at FROM tasks WHERE 1=1"
    params = []
    if department_id:
        query += " AND department_id = ?"
        params.append(department_id)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter.upper())
    query += " ORDER BY created_at DESC;"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    return [
        TaskResponse(
            id=r["id"],
            title=r["title"],
            description=r["description"],
            department_id=r["department_id"],
            assigned_agent_id=r["assigned_agent_id"],
            status=r["status"],
            priority=r["priority"],
            progress_pct=r["progress_pct"],
            payload=r["payload"],
            result=r["result"],
            error_message=r["error_message"],
            created_at=str(r["created_at"]),
            updated_at=str(r["updated_at"]),
        )
        for r in rows
    ]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    req: TaskCreateRequest,
    conn: sqlite3.Connection = Depends(get_db),
    authorized: bool = Depends(verify_ceo_auth),
):
    task_id = f"tsk-{uuid.uuid4().hex[:8]}"
    cursor = conn.cursor()

    # Check department validity
    cursor.execute("SELECT id FROM departments WHERE id = ?;", (req.department_id,))
    if not cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department '{req.department_id}' does not exist.",
        )

    cursor.execute(
        """INSERT INTO tasks (id, title, description, department_id, assigned_agent_id, priority, payload, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING');""",
        (task_id, req.title, req.description, req.department_id, req.assigned_agent_id, req.priority.upper(), req.payload),
    )

    cursor.execute(
        "INSERT INTO audit_ledger (actor, department_id, action, status, details) VALUES (?, ?, ?, ?, ?);",
        ("CEO", req.department_id, "TASK_CREATE", "CREATED", f"Task {task_id}: {req.title}"),
    )

    await event_bus.publish(
        "task.created",
        {"task_id": task_id, "title": req.title, "department_id": req.department_id},
    )

    cursor.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,))
    r = cursor.fetchone()
    return TaskResponse(
        id=r["id"],
        title=r["title"],
        description=r["description"],
        department_id=r["department_id"],
        assigned_agent_id=r["assigned_agent_id"],
        status=r["status"],
        priority=r["priority"],
        progress_pct=r["progress_pct"],
        payload=r["payload"],
        result=r["result"],
        error_message=r["error_message"],
        created_at=str(r["created_at"]),
        updated_at=str(r["updated_at"]),
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,))
    r = cursor.fetchone()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")
    return TaskResponse(
        id=r["id"],
        title=r["title"],
        description=r["description"],
        department_id=r["department_id"],
        assigned_agent_id=r["assigned_agent_id"],
        status=r["status"],
        priority=r["priority"],
        progress_pct=r["progress_pct"],
        payload=r["payload"],
        result=r["result"],
        error_message=r["error_message"],
        created_at=str(r["created_at"]),
        updated_at=str(r["updated_at"]),
    )
