"""Agents API router."""

from datetime import datetime, timezone
import sqlite3
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_ceo_auth
from app.database.connection import get_db
from app.events.bus import event_bus
from app.api.schemas import AgentInstructionRequest, AgentResponse

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=List[AgentResponse])
def list_agents(department_id: Optional[str] = None, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    if department_id:
        cursor.execute(
            "SELECT id, name, department_id, role, hierarchy_level, status, current_task_id, current_provider, current_model, tokens_input, tokens_output, last_activity FROM agents WHERE department_id = ? ORDER BY name ASC;",
            (department_id,),
        )
    else:
        cursor.execute(
            "SELECT id, name, department_id, role, hierarchy_level, status, current_task_id, current_provider, current_model, tokens_input, tokens_output, last_activity FROM agents ORDER BY name ASC;"
        )
    rows = cursor.fetchall()
    return [
        AgentResponse(
            id=r["id"],
            name=r["name"],
            department_id=r["department_id"],
            role=r["role"],
            hierarchy_level=r["hierarchy_level"],
            status=r["status"],
            current_task_id=r["current_task_id"],
            current_provider=r["current_provider"],
            current_model=r["current_model"],
            tokens_input=r["tokens_input"],
            tokens_output=r["tokens_output"],
            last_activity=str(r["last_activity"]),
        )
        for r in rows
    ]


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, department_id, role, hierarchy_level, status, current_task_id, current_provider, current_model, tokens_input, tokens_output, last_activity FROM agents WHERE id = ?;",
        (agent_id,),
    )
    r = cursor.fetchone()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")
    return AgentResponse(
        id=r["id"],
        name=r["name"],
        department_id=r["department_id"],
        role=r["role"],
        hierarchy_level=r["hierarchy_level"],
        status=r["status"],
        current_task_id=r["current_task_id"],
        current_provider=r["current_provider"],
        current_model=r["current_model"],
        tokens_input=r["tokens_input"],
        tokens_output=r["tokens_output"],
        last_activity=str(r["last_activity"]),
    )


@router.post("/{agent_id}/instruction")
async def send_agent_instruction(
    agent_id: str,
    req: AgentInstructionRequest,
    conn: sqlite3.Connection = Depends(get_db),
    authorized: bool = Depends(verify_ceo_auth),
):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, department_id FROM agents WHERE id = ?;", (agent_id,))
    agent = cursor.fetchone()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")

    # Audit the CEO instruction
    cursor.execute(
        "INSERT INTO audit_ledger (actor, department_id, action, status, details) VALUES (?, ?, ?, ?, ?);",
        ("CEO", agent["department_id"], "DIRECT_INSTRUCTION", "DELIVERED", req.instruction[:200]),
    )

    # Publish SSE event
    await event_bus.publish(
        "agent.instruction",
        {"agent_id": agent_id, "instruction": req.instruction, "priority": req.priority},
    )

    return {"status": "delivered", "agent_id": agent_id, "instruction": req.instruction}


@router.post("/{agent_id}/pause")
async def pause_agent(
    agent_id: str,
    conn: sqlite3.Connection = Depends(get_db),
    authorized: bool = Depends(verify_ceo_auth),
):
    cursor = conn.cursor()
    cursor.execute("UPDATE agents SET status = 'PAUSED', updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (agent_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")

    cursor.execute(
        "INSERT INTO audit_ledger (actor, action, status, details) VALUES (?, ?, ?, ?);",
        ("CEO", "AGENT_PAUSE", "SUCCESS", f"Agent {agent_id} paused"),
    )

    await event_bus.publish("agent.paused", {"agent_id": agent_id})
    return {"status": "paused", "agent_id": agent_id}


@router.post("/{agent_id}/resume")
async def resume_agent(
    agent_id: str,
    conn: sqlite3.Connection = Depends(get_db),
    authorized: bool = Depends(verify_ceo_auth),
):
    cursor = conn.cursor()
    cursor.execute("UPDATE agents SET status = 'IDLE', updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (agent_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")

    cursor.execute(
        "INSERT INTO audit_ledger (actor, action, status, details) VALUES (?, ?, ?, ?);",
        ("CEO", "AGENT_RESUME", "SUCCESS", f"Agent {agent_id} resumed"),
    )

    await event_bus.publish("agent.resumed", {"agent_id": agent_id})
    return {"status": "resumed", "agent_id": agent_id}
