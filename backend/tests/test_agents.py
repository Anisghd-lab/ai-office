"""Comprehensive tests for AI Organization, Manager, and Dynamic Agents."""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.base import AgentStatus, HierarchyLevel
from app.agents.manager import ai_manager
from app.agents.runtime import runtime_manager, SharedMemory
from app.database.connection import db_manager
from app.database.migrations import migration_manager
from app.departments.registry import DEPARTMENT_DIRECTORS, initialize_directors
from app.providers.base import GenerationResponse


@pytest.fixture(autouse=True)
def setup_agents_test():
    with db_manager.session() as conn:
        migration_manager.run_migrations(conn)
    initialize_directors()


# ---------------------------------------------------------
# 1. Manager Delegation Test
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_manager_plan_and_delegation():
    mock_plan_json = """
    {
        "tasks": [
            {"title": "Competitor Analysis", "department_id": "research", "priority": "HIGH", "description": "Scan competitors"},
            {"title": "Draft Video Concept", "department_id": "creative", "priority": "HIGH", "description": "Create storyboard"},
            {"title": "Prepare TikTok Copy", "department_id": "marketing", "priority": "HIGH", "description": "Draft captions"}
        ]
    }
    """
    mock_response = GenerationResponse(
        content=mock_plan_json,
        provider="mock",
        model="mock-free",
        tokens_input=50,
        tokens_output=100,
        cost=0.0,
    )

    with patch.object(ai_manager, "execute_task", new=AsyncMock(return_value=mock_response)):
        tasks = await ai_manager.plan_and_delegate("Launch high-impact TikTok campaign")
        assert len(tasks) == 3
        dept_ids = [t["department_id"] for t in tasks]
        assert "research" in dept_ids
        assert "creative" in dept_ids
        assert "marketing" in dept_ids

        # Verify persisted in database
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM tasks WHERE title = 'Competitor Analysis';")
            assert cursor.fetchone()[0] >= 1


# ---------------------------------------------------------
# 2. Multi-Department Collaboration Test
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_multi_department_collaboration():
    sender_id = "dir-research"
    recipient_id = "dir-marketing"
    content = "Market findings complete: Gen-Z audience prioritizes glassmorphism aesthetic."

    msg = await runtime_manager.send_inter_agent_message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        content=content,
    )

    marketing_dir = runtime_manager.active_agents[recipient_id]
    assert len(marketing_dir.inbox) > 0
    assert marketing_dir.inbox[-1].content == content

    # Verify audit ledger record
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM audit_ledger WHERE action = 'INTER_AGENT_MSG';")
        assert cursor.fetchone()[0] >= 1


# ---------------------------------------------------------
# 3. Dynamic Agent Creation & Teardown Test
# ---------------------------------------------------------
def test_dynamic_agent_lifecycle():
    task_id = "tsk-spec-test-01"
    spec = runtime_manager.spawn_dynamic_specialist(
        department_id="technology",
        role="Rust Core Optimizer",
        task_id=task_id,
    )

    assert spec.id.startswith("spec-tec-")
    assert spec.hierarchy_level == HierarchyLevel.SPECIALIST
    assert spec.id in runtime_manager.active_agents

    # Verify persisted in database
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM agents WHERE id = ?;", (spec.id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["status"] == "IDLE"

    # Teardown
    runtime_manager.teardown_dynamic_specialist(spec.id)
    assert spec.id not in runtime_manager.active_agents

    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM agents WHERE id = ?;", (spec.id,))
        assert cursor.fetchone()["status"] == "COMPLETED"


# ---------------------------------------------------------
# 4. Agent Isolation & Security Boundaries
# ---------------------------------------------------------
def test_agent_isolation():
    spec = runtime_manager.spawn_dynamic_specialist(
        department_id="finance",
        role="Ledger Checker",
        task_id="tsk-iso-1",
    )
    # Specialist hierarchy cannot independently promote itself to MANAGER or AI_CEO
    assert spec.hierarchy_level != HierarchyLevel.MANAGER
    assert spec.hierarchy_level != HierarchyLevel.AI_CEO


# ---------------------------------------------------------
# 5. Shared Memory Consistency Test
# ---------------------------------------------------------
def test_shared_memory_consistency():
    memory = SharedMemory()
    test_key = "q4_financial_ceiling"
    test_value = {"max_cost": 0.0, "currency": "USD", "strict": True}

    memory.set(test_key, test_value, provenance="dir-finance")

    # Read back from fresh instance
    memory2 = SharedMemory()
    retrieved = memory2.get(test_key)
    assert retrieved == test_value

    # Verify backed by SQLite knowledge_items
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT provenance FROM knowledge_items WHERE id = ?;", (f"mem-{test_key}",))
        row = cursor.fetchone()
        assert row is not None
        assert row["provenance"] == "dir-finance"


# ---------------------------------------------------------
# 6. Conflicting Task Detection Test
# ---------------------------------------------------------
def test_conflict_detection_and_resolution():
    import uuid
    uid = uuid.uuid4().hex[:6]
    id1, id2 = f"tsk-dup-1-{uid}", f"tsk-dup-2-{uid}"
    title = f"Identical Task {uid}"

    with db_manager.session() as conn:
        conn.execute(
            "INSERT INTO tasks (id, title, department_id, status) VALUES (?, ?, 'operations', 'ASSIGNED');",
            (id1, title),
        )
        conn.execute(
            "INSERT INTO tasks (id, title, department_id, status) VALUES (?, ?, 'operations', 'PENDING');",
            (id2, title),
        )

    resolved = ai_manager.detect_and_resolve_conflicts()
    assert len(resolved) >= 1
    assert any(r["retained_task"] == id1 for r in resolved)

    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tasks WHERE id = ?;", (id2,))
        assert cursor.fetchone()["status"] == "BLOCKED"


# ---------------------------------------------------------
# 7. Agent Restart Recovery Test
# ---------------------------------------------------------
def test_agent_restart_recovery():
    # Insert an active agent directly into SQLite
    with db_manager.session() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO agents (id, name, department_id, role, hierarchy_level, status)
               VALUES ('spec-recover-01', 'Rehydration Specialist', 'research', 'Archivist', 'SPECIALIST', 'WORKING');"""
        )

    # Clear active memory cache
    runtime_manager.active_agents.pop("spec-recover-01", None)

    # Run recovery
    count = runtime_manager.recover_from_restart()
    assert count >= 1
    assert "spec-recover-01" in runtime_manager.active_agents
    recovered_agent = runtime_manager.active_agents["spec-recover-01"]
    assert recovered_agent.status == AgentStatus.WORKING
    assert recovered_agent.name == "Rehydration Specialist"


# ---------------------------------------------------------
# 8. Executive Briefing Generation Test
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_executive_briefing_generation():
    briefing = await ai_manager.generate_executive_briefing()
    assert "# AI OFFICE EXECUTIVE BRIEFING" in briefing
    assert "Nova Prime (AI CEO)" in briefing
    assert "Zero-Cost Invariant Verified" in briefing

    # Verify persisted in reports table
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM reports WHERE report_type = 'DAILY_BRIEFING';")
        assert cursor.fetchone()[0] >= 1
