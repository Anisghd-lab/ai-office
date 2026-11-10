"""AI CEO Executive API router (Talk to CEO, CEO Office, Decisions, Strategy)."""

from datetime import datetime, timezone
import sqlite3
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from app.agents.manager import ai_ceo
from app.core.security import verify_owner_auth
from app.database.connection import get_db
from app.api.schemas import (
    AICEOProfileResponse,
    CalendarEventResponse,
    CeoDecisionResponse,
    KnowledgeItemResponse,
    OwnerChatRequest,
    OwnerChatResponse,
    ReportResponse,
)

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


@router.get("/reports", response_model=List[ReportResponse])
def list_reports(conn: sqlite3.Connection = Depends(get_db)):
    """Retrieve executive reports, daily briefings, and weekly board minutes."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, report_type, department_id, reporting_period, content, created_at FROM reports ORDER BY created_at DESC LIMIT 50;"
    )
    rows = cursor.fetchall()
    return [
        ReportResponse(
            id=r["id"],
            report_type=r["report_type"],
            department_id=r["department_id"],
            reporting_period=r["reporting_period"],
            content=r["content"],
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


@router.get("/memory", response_model=List[KnowledgeItemResponse])
def list_memory(conn: sqlite3.Connection = Depends(get_db)):
    """Retrieve curated corporate intelligence, verified research, and organizational memory."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, category, content, provenance, created_at FROM knowledge_items ORDER BY created_at DESC LIMIT 50;"
    )
    rows = cursor.fetchall()
    return [
        KnowledgeItemResponse(
            id=r["id"],
            title=r["title"],
            category=r["category"],
            content=r["content"],
            provenance=r["provenance"] or "system",
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


@router.get("/calendar", response_model=List[CalendarEventResponse])
def get_office_calendar(conn: sqlite3.Connection = Depends(get_db)):
    """Retrieve automated executive cadence schedule and meetings (Africa/Algiers timezone)."""
    events = [
        CalendarEventResponse(
            id="cad-daily-brief",
            title="Daily Executive Briefing",
            schedule_time="Every Day at 08:00 (Africa/Algiers)",
            description="AI CEO Nova Prime consolidates 24h operational telemetry and prepares executive briefing for Human Owner.",
            status="ACTIVE_RECURRING",
        ),
        CalendarEventResponse(
            id="cad-sunday-board",
            title="Sunday Executive Board Meeting",
            schedule_time="Every Sunday at 10:00 (Africa/Algiers)",
            description="All 8 Department Directors submit weekly throughput and strategic recommendations for consolidation.",
            status="ACTIVE_RECURRING",
        ),
        CalendarEventResponse(
            id="cad-library-hour",
            title="Weekly Knowledge Library Hour",
            schedule_time="Every Wednesday at 15:00 (Africa/Algiers)",
            description="Research Department curates and grounds new models, API quotas, and intelligence into organizational memory.",
            status="ACTIVE_RECURRING",
        ),
    ]

    cursor = conn.cursor()
    cursor.execute("SELECT id, meeting_type, scheduled_at, status FROM executive_meetings ORDER BY scheduled_at DESC LIMIT 10;")
    rows = cursor.fetchall()
    for r in rows:
        events.append(
            CalendarEventResponse(
                id=r["id"],
                title=f"Executive Meeting: {r['meeting_type']}",
                schedule_time=str(r["scheduled_at"]),
                description=f"Status: {r['status']} • Concluded with all directors present.",
                status=r["status"],
            )
        )

    return events

