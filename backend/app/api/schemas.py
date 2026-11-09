"""Pydantic schemas for the AI Office API."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    active_providers: List[str]
    timestamp: str


class OfficeMetricsResponse(BaseModel):
    total_agents: int
    online_agents: int
    idle_agents: int
    working_agents: int
    failed_agents: int
    active_tasks: int
    completed_tasks: int
    pending_approvals: int
    today_cost_usd: float = 0.0
    provider_health: Dict[str, dict]


class DepartmentResponse(BaseModel):
    id: str
    name: str
    director_name: str
    mission: str
    kpi_metrics: Optional[str] = None
    status: str
    created_at: str


class AgentResponse(BaseModel):
    id: str
    name: str
    department_id: str
    role: str
    hierarchy_level: str
    status: str
    current_task_id: Optional[str] = None
    current_provider: Optional[str] = None
    current_model: Optional[str] = None
    tokens_input: int = 0
    tokens_output: int = 0
    last_activity: str


class AgentInstructionRequest(BaseModel):
    instruction: str
    priority: str = "HIGH"


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    department_id: str
    assigned_agent_id: Optional[str] = None
    priority: str = "MEDIUM"
    payload: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    department_id: str
    assigned_agent_id: Optional[str] = None
    status: str
    priority: str
    progress_pct: int
    payload: Optional[str] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class ApprovalResponse(BaseModel):
    id: str
    agent_id: str
    department_id: str
    action_type: str
    destination: str
    payload: str
    payload_hash: str
    risk_level: str
    cost: float
    status: str
    decision_comment: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None
    execution_status: Optional[str] = None
    execution_result: Optional[str] = None
    executed_at: Optional[str] = None
    expires_at: str
    created_at: str


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    comment: Optional[str] = None


class ExecutionRequest(BaseModel):
    execution_token: Optional[str] = None
