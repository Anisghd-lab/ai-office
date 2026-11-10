"""REST API routes for AI Office Autonomous Media Company."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.security import verify_owner_auth as verify_owner_key
from app.company.employees import employee_service
from app.company.production import production_pipeline
from app.company.accounts import google_account_registry
from app.company.library import library_hour_mgr
from app.flowkit.service import flowkit_service_mgr
from app.flowkit.adapter import flowkit_adapter

router = APIRouter(prefix="/company", tags=["Media Company"])


# ─── Pydantic Schemas ──────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    employee_id: str
    session_id: str
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    project_id: Optional[str] = None


class FinishSessionRequest(BaseModel):
    employee_id: str
    session_id: str
    next_status: str = "FREE"
    output_references: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AwardXpRequest(BaseModel):
    task_id: str
    xp_amount: int = Field(gt=0)
    reason: str = "Task accepted and verified"


class CreateProjectRequest(BaseModel):
    title: str
    topic: str
    niche: str
    target_audience: str
    opportunity_score: float = 8.5
    confidence_pct: int = 90


class CreateScriptRequest(BaseModel):
    target_platform: str
    target_format: str
    target_duration_seconds: int
    hook: str
    full_narration: str
    scenes: List[Dict[str, Any]]
    thumbnail_concept: Optional[str] = None


class StartJobRequest(BaseModel):
    project_id: str
    script_id: str
    engine: str = "FLOWKIT"


class PreparePackageRequest(BaseModel):
    project_id: str
    target_platform: str
    title: str
    description: str
    hashtags: List[str]
    video_asset_id: Optional[str] = None


class LibraryProposalRequest(BaseModel):
    tool_name: str
    repository_url: str
    license_name: str
    last_maintenance: str
    dependencies: str
    arm64_compatible: bool = True
    proot_compatible: bool = True
    security_risks: str
    required_permissions: str
    benefits: str
    installation_size_mb: float
    integration_plan: str
    recommendation: str


# ─── 1. Live Office Board & Employees ─────────────────────────────

@router.get("/overview")
async def get_company_overview(_: str = Depends(verify_owner_key)):
    """Live Office Board aggregated state."""
    overview = employee_service.get_company_overview()
    projects = production_pipeline.list_projects()
    engine_status = await flowkit_service_mgr.get_status()

    return {
        "company_name": "AI Office Media Organization",
        "governance": {
            "human_role": "OWNER_PRINCIPAL",
            "central_intelligence": "AI Office (Nova Prime)",
        },
        "workforce": overview,
        "projects_count": len(projects),
        "engine_state": engine_status.get("state", "UNKNOWN"),
        "employees": employee_service.list_employees(),
    }


@router.get("/employees")
async def list_employees(_: str = Depends(verify_owner_key)):
    return employee_service.list_employees()


@router.get("/employees/{employee_id}")
async def get_employee(employee_id: str, _: str = Depends(verify_owner_key)):
    emp = employee_service.get_employee(employee_id)
    if not emp:
        raise HTTPException(404, f"Employee '{employee_id}' not found.")
    return emp


@router.post("/employees/sessions/start")
@router.post("/employees/session/start")
async def start_employee_session(req: StartSessionRequest, _: str = Depends(verify_owner_key)):
    return await employee_service.start_session(
        employee_id=req.employee_id,
        session_id=req.session_id,
        task_id=req.task_id,
        task_name=req.task_name,
        project_id=req.project_id,
    )


@router.post("/employees/sessions/finish")
@router.post("/employees/session/finish")
async def finish_employee_session(req: FinishSessionRequest, _: str = Depends(verify_owner_key)):
    return await employee_service.finish_session(
        employee_id=req.employee_id,
        session_id=req.session_id,
        next_status=req.next_status,
        output_references=req.output_references,
        error_message=req.error_message,
    )


@router.post("/employees/{employee_id}/award-xp")
@router.post("/employees/{employee_id}/xp")
async def award_employee_xp(employee_id: str, req: AwardXpRequest, _: str = Depends(verify_owner_key)):
    result = await employee_service.award_xp(
        employee_id=employee_id,
        task_id=req.task_id,
        xp_amount=req.xp_amount,
        awarded_by="OWNER",
        reason=req.reason,
    )
    return result


# ─── 2. Production Pipeline & Projects ─────────────────────────────

@router.get("/projects")
async def list_projects(status: Optional[str] = None, _: str = Depends(verify_owner_key)):
    return production_pipeline.list_projects(status=status)


@router.post("/projects")
async def create_project(req: CreateProjectRequest, _: str = Depends(verify_owner_key)):
    return production_pipeline.create_project(
        title=req.title,
        topic=req.topic,
        niche=req.niche,
        target_audience=req.target_audience,
        opportunity_score=req.opportunity_score,
        confidence_pct=req.confidence_pct,
    )


@router.get("/projects/{project_id}")
async def get_project(project_id: str, _: str = Depends(verify_owner_key)):
    proj = production_pipeline.get_project(project_id)
    if not proj:
        raise HTTPException(404, f"Project '{project_id}' not found.")
    return proj


@router.post("/projects/{project_id}/scripts")
async def create_script(project_id: str, req: CreateScriptRequest, _: str = Depends(verify_owner_key)):
    return production_pipeline.create_script(
        project_id=project_id,
        target_platform=req.target_platform,
        target_format=req.target_format,
        target_duration_seconds=req.target_duration_seconds,
        hook=req.hook,
        full_narration=req.full_narration,
        scenes_data=req.scenes,
        thumbnail_concept=req.thumbnail_concept,
    )


@router.post("/production/jobs")
async def start_production_job(req: StartJobRequest, _: str = Depends(verify_owner_key)):
    return await production_pipeline.start_production_job(
        project_id=req.project_id,
        script_id=req.script_id,
        engine=req.engine,
    )


@router.post("/production/packages")
async def prepare_publication_package(req: PreparePackageRequest, _: str = Depends(verify_owner_key)):
    return await production_pipeline.prepare_publication_package(
        project_id=req.project_id,
        target_platform=req.target_platform,
        title=req.title,
        description=req.description,
        hashtags=req.hashtags,
        video_asset_id=req.video_asset_id,
    )


# ─── 3. FlowKit Video Engine Control ──────────────────────────────

@router.get("/flowkit/status")
async def get_flowkit_status(_: str = Depends(verify_owner_key)):
    return await flowkit_service_mgr.get_status()


@router.post("/flowkit/control/{action}")
async def control_flowkit(action: str, _: str = Depends(verify_owner_key)):
    if action == "start":
        return await flowkit_service_mgr.start()
    elif action == "stop":
        return await flowkit_service_mgr.stop()
    elif action == "restart":
        return await flowkit_service_mgr.restart()
    else:
        raise HTTPException(400, f"Unsupported action '{action}'. Use start, stop, or restart.")


@router.get("/flowkit/logs")
async def get_flowkit_logs(_: str = Depends(verify_owner_key)):
    logs = await flowkit_service_mgr.get_logs()
    return {"logs": logs}


@router.get("/flowkit/queue")
async def get_flowkit_queue(_: str = Depends(verify_owner_key)):
    return await flowkit_adapter.get_queue_status()


# ─── 4. Google Pro Accounts Registry ──────────────────────────────

@router.get("/accounts")
@router.get("/google-accounts")
async def list_google_accounts(_: str = Depends(verify_owner_key)):
    return google_account_registry.list_accounts()


# ─── 5. Library Hour ──────────────────────────────────────────────

@router.get("/library/proposals")
async def list_library_proposals(_: str = Depends(verify_owner_key)):
    return library_hour_mgr.list_proposals()


@router.post("/library/proposals")
async def create_library_proposal(req: LibraryProposalRequest, _: str = Depends(verify_owner_key)):
    return library_hour_mgr.propose_tool(
        tool_name=req.tool_name,
        repository_url=req.repository_url,
        license_name=req.license_name,
        last_maintenance=req.last_maintenance,
        dependencies=req.dependencies,
        arm64_compatible=req.arm64_compatible,
        proot_compatible=req.proot_compatible,
        security_risks=req.security_risks,
        required_permissions=req.required_permissions,
        benefits=req.benefits,
        installation_size_mb=req.installation_size_mb,
        integration_plan=req.integration_plan,
        recommendation=req.recommendation,
    )
