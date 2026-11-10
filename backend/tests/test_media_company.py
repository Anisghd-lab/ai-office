"""Comprehensive test suite for Autonomous Media Company, Employee System, and FlowKit integration."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.company.employees import employee_service
from app.company.production import production_pipeline
from app.company.accounts import google_account_registry
from app.company.library import library_hour_mgr
from app.flowkit.service import flowkit_service_mgr
from app.database.connection import db_manager


@pytest.fixture
def client():
    return TestClient(app)


# ─── 1. Employee Registry & Levels Tests ──────────────────────────────

def test_employee_registry_seeded():
    """Verify registry seeding from registry.json."""
    employees = employee_service.list_employees()
    assert len(employees) >= 11

    # Check key employees by their unique IDs
    emp_ids = {e["id"] for e in employees}
    assert "emp-res-01" in emp_ids
    assert "emp-scr-01" in emp_ids
    assert "emp-edt-01" in emp_ids
    assert "emp-edt-03" in emp_ids
    assert "emp-gro-01" in emp_ids

    # Check Dr. Aris Vance attributes
    aris = employee_service.get_employee("emp-res-01")
    assert aris is not None
    assert aris["name"] == "Dr. Aris Vance"
    assert aris["department"] == "research"
    assert aris["level"] >= 7


def test_company_overview_metrics():
    """Verify aggregate company overview calculation."""
    overview = employee_service.get_company_overview()
    assert "total_employees" in overview
    assert overview["total_employees"] >= 11
    assert "by_department" in overview
    assert "research" in overview["by_department"]
    assert "scripts" in overview["by_department"]
    assert "editing" in overview["by_department"]


# ─── 2. Employee Sessions & State Transitions ─────────────────────────

@pytest.mark.asyncio
async def test_employee_session_lifecycle():
    """Verify session start, task assignment, status change, and session finish."""
    emp_id = "emp-scr-01"
    session_id = "test-session-marcus-001"
    task_id = "task-script-ai-trends-01"

    # Start session
    session = await employee_service.start_session(
        employee_id=emp_id,
        session_id=session_id,
        task_id=task_id,
        task_name="Write AI Trends Script",
        project_id="proj-ai-trends-2026",
    )
    assert session["session_id"] == session_id
    assert session["status"] == "WORKING"

    # Verify employee status updated to WORKING
    emp = employee_service.get_employee(emp_id)
    assert emp["status"] == "WORKING"
    assert emp["current_task"] == "Write AI Trends Script"
    assert emp["current_project"] == "proj-ai-trends-2026"

    # Finish session
    finished = await employee_service.finish_session(
        employee_id=emp_id,
        session_id=session_id,
        next_status="FREE",
        output_references={"script_id": "scr-test-001"},
    )
    assert finished["status"] == "FREE"

    # Verify employee status returned to FREE
    emp_after = employee_service.get_employee(emp_id)
    assert emp_after["status"] == "FREE"
    assert emp_after["current_task"] is None


# ─── 3. XP Progression & Anti-Duplicate Rule ──────────────────────────

@pytest.mark.asyncio
async def test_xp_award_and_promotion():
    """Verify XP awarding, level promotion threshold, and duplicate XP prevention."""
    emp_id = "emp-edt-03"
    task_id = "task-qc-review-99"

    emp_before = employee_service.get_employee(emp_id)
    assert emp_before is not None
    initial_xp = emp_before["xp"]
    initial_level = emp_before["level"]

    # Award XP
    result = await employee_service.award_xp(
        employee_id=emp_id,
        task_id=task_id,
        xp_amount=150,
        reason="First-pass high quality video QC",
    )
    assert result["xp_awarded"] == 150
    assert result["total_xp"] == initial_xp + 150

    # Verify duplicate XP award for the same task is rejected
    dup_result = await employee_service.award_xp(
        employee_id=emp_id,
        task_id=task_id,
        xp_amount=100,
        reason="Duplicate attempt",
    )
    assert dup_result["awarded"] is False
    assert "already awarded" in dup_result["reason"]

    # Award XP to test level progression
    big_result = await employee_service.award_xp(
        employee_id=emp_id,
        task_id="task-major-breakthrough-01",
        xp_amount=3500,
        reason="Promoted for major pipeline achievement",
    )
    assert big_result["level"] == 10
    assert big_result["title"] == "Professional"


# ─── 4. Autonomous Production Pipeline ───────────────────────────────

@pytest.mark.asyncio
async def test_production_pipeline_lifecycle():
    """Test full production lifecycle: Project -> Script -> Scene Breakdown -> QC -> Needs You Approval."""
    # Phase A: Project Creation
    project = production_pipeline.create_project(
        title="Future of Autonomous Agents 2026",
        topic="AI Autonomous Agents in Enterprise",
        niche="Technology & AI",
        target_audience="Engineers and Tech Founders",
        opportunity_score=9.2,
        confidence_pct=95,
    )
    assert project["project_id"].startswith("proj-")
    project_id = project["project_id"]

    # Phase B: Scriptwriting with Scenes
    scenes_data = [
        {
            "scene_number": 1,
            "duration_seconds": 8,
            "visual_prompt": "Cinematic visual of AI nodes interacting across a glass interface",
            "narration_chunk": "AI agents are no longer chatbots. They are autonomous organizations.",
            "audio_cues": "Subtle ambient synth pulse",
        },
        {
            "scene_number": 2,
            "duration_seconds": 12,
            "visual_prompt": "Fast-paced montage of video rendering timeline and waveform",
            "narration_chunk": "With local engine stitching and cloud generative flows, speed multiplies.",
            "audio_cues": "Upbeat energetic beat drop",
        },
    ]
    script = production_pipeline.create_script(
        project_id=project_id,
        target_platform="YouTube Shorts",
        target_format="SHORT_FORM",
        target_duration_seconds=20,
        hook="What if your entire media company was run by AI agents?",
        full_narration="Today we look inside AI Office and its autonomous FlowKit engine...",
        scenes_data=scenes_data,
        thumbnail_concept="Split screen of AI agent terminal and glassmorphic control center",
    )
    assert script["script_id"].startswith("scr-")
    assert script["scenes_count"] == 2

    # Phase C: Automated QC
    qc_result = production_pipeline.run_quality_check(
        job_id="test-job-001",
        video_path="/root/ai-office/storage/rendered/test_agents.mp4",
        expected_duration_s=20,
        target_format="SHORT_FORM",
    )
    assert qc_result["passed"] is True

    # Phase D: Package & Submit to NEEDS YOU Human Approval Gateway
    package = await production_pipeline.prepare_publication_package(
        project_id=project_id,
        target_platform="YouTube Shorts",
        title="Future of Autonomous Agents in 2026",
        description="Exploring the next frontier of multi-agent media production.",
        hashtags=["ai", "agents", "technology", "shorts"],
        video_asset_id=None,
    )
    assert package["status"] == "WAITING_FOR_OWNER"
    assert "approval_id" in package
    assert package["approval_id"].startswith("appr-")

    # Verify that the approval gateway record exists in database
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM approvals WHERE id = ?", (package["approval_id"],))
        approval_row = cursor.fetchone()
        assert approval_row is not None
        assert approval_row["action_type"] == "PUBLISH_VIDEO"
        assert approval_row["status"] == "PENDING"
        assert approval_row["cost"] == 0.0


# ─── 5. Google Account Quota & Zero-Cost Registry ─────────────────────

def test_google_account_zero_cost_registry():
    """Verify zero-cost Google accounts seeded from migration and quota tracking."""
    accounts = google_account_registry.list_accounts()
    assert len(accounts) >= 3

    acc_ids = {a["id"] for a in accounts}
    assert "gacc-01" in acc_ids
    assert "gacc-02" in acc_ids
    assert "gacc-03" in acc_ids

    # Update quota observation
    updated = google_account_registry.update_quota_observation(
        account_id="gacc-01",
        available_quota="100 free requests",
        current_usage="10 requests used",
        is_available=True,
    )
    assert updated["available_quota"] == "100 free requests"

    # Preflight check without auth should be ineligible
    eligibility = google_account_registry.verify_generation_eligibility("gacc-01")
    assert eligibility["eligible"] is False


# ─── 6. Library Hour Tool Proposal Flow ───────────────────────────────

@pytest.mark.asyncio
async def test_library_hour_proposal():
    """Verify Saturday 1-hour tool evaluation proposal submitted to approval gateway."""
    proposal = library_hour_mgr.propose_tool(
        tool_name="remotion-cli",
        repository_url="https://github.com/remotion-dev/remotion",
        license_name="MIT",
        last_maintenance="2026-10-15",
        dependencies="nodejs, ffmpeg",
        arm64_compatible=True,
        proot_compatible=True,
        security_risks="None identified. Open-source local execution only.",
        required_permissions="Local storage access",
        benefits="Enables high-performance declarative programmatic video transitions",
        installation_size_mb=45.0,
        integration_plan="Test CLI rendering inside PRoot environment during Saturday 1h window",
        recommendation="PROCEED_WITH_BENCHMARK",
    )
    assert proposal["tool_name"] == "remotion-cli"
    assert proposal["status"] == "IN_NEEDS_YOU"
    assert "approval_id" in proposal

    # List proposals
    proposals = library_hour_mgr.list_proposals()
    assert any(p["tool_name"] == "remotion-cli" for p in proposals)


# ─── 7. Media Company REST API Endpoints ──────────────────────────────

def test_api_company_overview(client):
    response = client.get("/api/v1/company/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "AI Office Media Organization"
    assert data["governance"]["human_role"] == "OWNER_PRINCIPAL"
    assert data["governance"]["central_intelligence"] == "AI Office (Nova Prime)"
    assert data["workforce"]["total_employees"] >= 11


def test_api_employees_list(client):
    response = client.get("/api/v1/company/employees")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 11


def test_api_employee_detail(client):
    # Lookup by ID
    response = client.get("/api/v1/company/employees/emp-edt-01")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Elena Vance"
    assert data["department"] == "editing"

    # Lookup by slug
    response_slug = client.get("/api/v1/company/employees/elena-vance")
    assert response_slug.status_code == 200
    data_slug = response_slug.json()
    assert data_slug["name"] == "Elena Vance"


def test_api_flowkit_status(client):
    response = client.get("/api/v1/company/flowkit/status")
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert "endpoint" in data
    assert "port" in data


def test_api_google_accounts(client):
    response = client.get("/api/v1/company/accounts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_api_library_proposals(client):
    response = client.get("/api/v1/company/library/proposals")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
