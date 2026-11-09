"""Health and metrics API router."""

from datetime import datetime, timezone
import sqlite3
from fastapi import APIRouter, Depends
from app.config import settings
from app.database.connection import get_db
from app.providers.registry import provider_registry
from app.api.schemas import HealthResponse, OfficeMetricsResponse

router = APIRouter(tags=["Health & Telemetry"])


@router.get("/health", response_model=HealthResponse)
def get_health(conn: sqlite3.Connection = Depends(get_db)):
    # Verify SQLite WAL connectivity
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    mode = cursor.fetchone()[0]

    active_providers = [p.name for p in provider_registry.list_all()]

    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        database=f"connected (mode: {mode})",
        active_providers=active_providers,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/metrics", response_model=OfficeMetricsResponse)
def get_metrics(conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()

    cursor.execute("SELECT status, count(*) FROM agents GROUP BY status;")
    agent_counts = dict(cursor.fetchall())

    total_agents = sum(agent_counts.values())
    online_agents = sum(v for k, v in agent_counts.items() if k != "OFFLINE")
    idle_agents = agent_counts.get("IDLE", 0)
    working_agents = agent_counts.get("WORKING", 0)
    failed_agents = agent_counts.get("FAILED", 0)

    cursor.execute("SELECT count(*) FROM tasks WHERE status IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS');")
    active_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM tasks WHERE status = 'COMPLETED';")
    completed_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM approvals WHERE status = 'PENDING';")
    pending_approvals = cursor.fetchone()[0]

    return OfficeMetricsResponse(
        total_agents=total_agents,
        online_agents=online_agents,
        idle_agents=idle_agents,
        working_agents=working_agents,
        failed_agents=failed_agents,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        pending_approvals=pending_approvals,
        today_cost_usd=0.0,
        provider_health=provider_registry.health_monitor.get_summary(),
    )
