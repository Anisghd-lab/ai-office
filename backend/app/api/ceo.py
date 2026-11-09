"""AI CEO Executive API router (Talk to CEO, CEO Office, Decisions, Strategy)."""

from datetime import datetime, timezone
import sqlite3
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from app.agents.manager import ai_ceo
from app.core.security import verify_owner_auth
from app.database.connection import get_db
from app.api.schemas import AICEOProfileResponse, OwnerChatRequest, OwnerChatResponse

router = APIRouter(prefix="/ceo", tags=["AI CEO Executive Authority"])


@router.post("/chat", response_model=OwnerChatResponse)
async def chat_with_ceo(
    req: OwnerChatRequest,
    authorized: bool = Depends(verify_owner_auth),
):
    """Direct conversation between Human Owner and AI CEO."""
    res = await ai_ceo.discuss_with_owner(req.message)
    return OwnerChatResponse(
        reply=res["reply"],
        decisions=res["decisions"],
        tasks_created=res["tasks_created"],
        timestamp=res["timestamp"],
    )


@router.get("/profile", response_model=AICEOProfileResponse)
def get_ceo_profile(conn: sqlite3.Connection = Depends(get_db)):
    """Executive status, identity, and performance indicators of the AI CEO."""
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM audit_ledger WHERE actor = 'AI_CEO' AND action = 'CEO_DECISION';")
    total_decisions = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM departments;")
    dept_count = cursor.fetchone()[0]

    return AICEOProfileResponse(
        id=ai_ceo.id,
        name=ai_ceo.name,
        title=ai_ceo.role,
        status=ai_ceo.status.value,
        active_strategic_goals=[
            "100% Free / Zero-Cost Operational Integrity",
            "Autonomous multi-department synchronization",
            "High-impact organic social expansion (TikTok, Meta)",
            "Fail-safe User Approval Gateway compliance",
        ],
        total_autonomous_decisions=total_decisions,
        departments_supervised=dept_count,
        tokens_consumed=ai_ceo.tokens_input + ai_ceo.tokens_output,
        executive_health="OPTIMAL",
    )


@router.get("/decisions")
def list_ceo_decisions(conn: sqlite3.Connection = Depends(get_db)):
    """List autonomous internal organizational decisions made by the AI CEO."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, timestamp, details FROM audit_ledger WHERE actor = 'AI_CEO' AND action = 'CEO_DECISION' ORDER BY id DESC LIMIT 50;"
    )
    rows = cursor.fetchall()
    return [
        {"id": r["id"], "timestamp": str(r["timestamp"]), "decision": r["details"]}
        for r in rows
    ]


@router.get("/strategy")
def get_ceo_strategy():
    """Retrieve the overarching organizational strategy established by the AI CEO."""
    return {
        "presenter": "Nova Prime (AI CEO)",
        "executive_summary": "Autonomous multi-agent execution with zero commercial infrastructure cost.",
        "strategic_pillars": [
            {
                "pillar": "Autonomous Internal Operations",
                "focus": "Research, task assignment, draft preparation, and inter-departmental collaboration proceed autonomously.",
            },
            {
                "pillar": "Mandatory Human Owner Authorization",
                "focus": "All external side-effects (publishing, external messaging, credentials) require explicit Owner approval.",
            },
            {
                "pillar": "Zero-Cost Guardrails",
                "focus": "Exclusive utilization of legitimately available free-tier API quotas and local execution.",
            },
            {
                "pillar": "Native Mobile Command",
                "focus": "High-fidelity Android 16 Control Center featuring Glassmorphism 2.0 aesthetics connected to loopback.",
            },
        ],
        "roadmap_milestones": [
            "Q4: Automated multi-channel publishing workflows across TikTok and Meta",
            "Q1: Local on-device SLM inference integration with PRoot ARM64 fallback",
            "Q2: Advanced automated competitor benchmarking and real-time trend ingestion",
        ],
    }
