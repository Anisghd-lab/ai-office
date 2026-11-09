"""Governance and CEO Approval Gateway API router."""

from datetime import datetime, timezone
import json
import sqlite3
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.config import settings
from app.core.security import canonical_json_hash, verify_ceo_auth
from app.database.connection import get_db
from app.events.bus import event_bus
from app.api.schemas import ApprovalDecisionRequest, ApprovalResponse

router = APIRouter(prefix="/governance", tags=["CEO Governance & Approvals"])


@router.get("/approvals", response_model=List[ApprovalResponse])
def list_approvals(status_filter: Optional[str] = None, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    query = "SELECT * FROM approvals WHERE 1=1"
    params = []
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter.upper())
    query += " ORDER BY created_at DESC;"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    return [
        ApprovalResponse(
            id=r["id"],
            agent_id=r["agent_id"],
            department_id=r["department_id"],
            action_type=r["action_type"],
            destination=r["destination"],
            payload=r["payload"],
            payload_hash=r["payload_hash"],
            risk_level=r["risk_level"],
            cost=float(r["cost"]),
            status=r["status"],
            decision_comment=r["decision_comment"],
            decided_by=r["decided_by"],
            decided_at=str(r["decided_at"]) if r["decided_at"] else None,
            execution_status=r["execution_status"],
            execution_result=r["execution_result"],
            executed_at=str(r["executed_at"]) if r["executed_at"] else None,
            expires_at=str(r["expires_at"]),
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


@router.get("/approvals/{request_id}", response_model=ApprovalResponse)
def get_approval(request_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
    r = cursor.fetchone()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request '{request_id}' not found.",
        )
    return ApprovalResponse(
        id=r["id"],
        agent_id=r["agent_id"],
        department_id=r["department_id"],
        action_type=r["action_type"],
        destination=r["destination"],
        payload=r["payload"],
        payload_hash=r["payload_hash"],
        risk_level=r["risk_level"],
        cost=float(r["cost"]),
        status=r["status"],
        decision_comment=r["decision_comment"],
        decided_by=r["decided_by"],
        decided_at=str(r["decided_at"]) if r["decided_at"] else None,
        execution_status=r["execution_status"],
        execution_result=r["execution_result"],
        executed_at=str(r["executed_at"]) if r["executed_at"] else None,
        expires_at=str(r["expires_at"]),
        created_at=str(r["created_at"]),
    )


@router.post("/approvals/{request_id}/approve", response_model=ApprovalResponse)
async def approve_request(
    request_id: str,
    req: ApprovalDecisionRequest,
    conn: sqlite3.Connection = Depends(get_db),
    authorized: bool = Depends(verify_ceo_auth),
):
    if req.decision != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision payload must be 'APPROVED' for this endpoint.",
        )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
    record = cursor.fetchone()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

    if record["status"] != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot approve request in status '{record['status']}'. Must be 'PENDING'.",
        )

    # Check expiration
    now = datetime.now(timezone.utc)
    expires_at = datetime.fromisoformat(record["expires_at"].replace("Z", "+00:00"))
    if now > expires_at:
        cursor.execute("UPDATE approvals SET status = 'EXPIRED' WHERE id = ?;", (request_id,))
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Approval request has expired.")

    cursor.execute(
        """UPDATE approvals
           SET status = 'APPROVED',
               decision_comment = ?,
               decided_by = 'CEO',
               decided_at = CURRENT_TIMESTAMP
           WHERE id = ?;""",
        (req.comment, request_id),
    )

    cursor.execute(
        "INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details) VALUES (?, ?, ?, ?, ?, ?);",
        ("CEO", record["department_id"], "APPROVAL_GRANTED", "APPROVED", record["payload_hash"], f"Approved {request_id}: {req.comment}"),
    )

    await event_bus.publish(
        "approval.approved",
        {"request_id": request_id, "action_type": record["action_type"], "destination": record["destination"]},
    )

    cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
    r = cursor.fetchone()
    return ApprovalResponse(
        id=r["id"],
        agent_id=r["agent_id"],
        department_id=r["department_id"],
        action_type=r["action_type"],
        destination=r["destination"],
        payload=r["payload"],
        payload_hash=r["payload_hash"],
        risk_level=r["risk_level"],
        cost=float(r["cost"]),
        status=r["status"],
        decision_comment=r["decision_comment"],
        decided_by=r["decided_by"],
        decided_at=str(r["decided_at"]) if r["decided_at"] else None,
        execution_status=r["execution_status"],
        execution_result=r["execution_result"],
        executed_at=str(r["executed_at"]) if r["executed_at"] else None,
        expires_at=str(r["expires_at"]),
        created_at=str(r["created_at"]),
    )


@router.post("/approvals/{request_id}/reject", response_model=ApprovalResponse)
async def reject_request(
    request_id: str,
    req: ApprovalDecisionRequest,
    conn: sqlite3.Connection = Depends(get_db),
    authorized: bool = Depends(verify_ceo_auth),
):
    if req.decision != "REJECTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision payload must be 'REJECTED' for this endpoint.",
        )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
    record = cursor.fetchone()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

    if record["status"] != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot reject request in status '{record['status']}'. Must be 'PENDING'.",
        )

    cursor.execute(
        """UPDATE approvals
           SET status = 'REJECTED',
               decision_comment = ?,
               decided_by = 'CEO',
               decided_at = CURRENT_TIMESTAMP
           WHERE id = ?;""",
        (req.comment, request_id),
    )

    cursor.execute(
        "INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details) VALUES (?, ?, ?, ?, ?, ?);",
        ("CEO", record["department_id"], "APPROVAL_REJECTED", "REJECTED", record["payload_hash"], f"Rejected {request_id}: {req.comment}"),
    )

    await event_bus.publish(
        "approval.rejected",
        {"request_id": request_id, "reason": req.comment},
    )

    cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
    r = cursor.fetchone()
    return ApprovalResponse(
        id=r["id"],
        agent_id=r["agent_id"],
        department_id=r["department_id"],
        action_type=r["action_type"],
        destination=r["destination"],
        payload=r["payload"],
        payload_hash=r["payload_hash"],
        risk_level=r["risk_level"],
        cost=float(r["cost"]),
        status=r["status"],
        decision_comment=r["decision_comment"],
        decided_by=r["decided_by"],
        decided_at=str(r["decided_at"]) if r["decided_at"] else None,
        execution_status=r["execution_status"],
        execution_result=r["execution_result"],
        executed_at=str(r["executed_at"]) if r["executed_at"] else None,
        expires_at=str(r["expires_at"]),
        created_at=str(r["created_at"]),
    )
