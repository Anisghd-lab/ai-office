"""Base Agent abstraction and execution context."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from app.providers.base import GenerationResponse
from app.providers.registry import provider_registry


class HierarchyLevel(str, Enum):
    AI_CEO = "AI_CEO"
    MANAGER = "MANAGER"
    DIRECTOR = "DIRECTOR"
    SPECIALIST = "SPECIALIST"


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    WORKING = "WORKING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class AgentMessage:
    id: str = field(default_factory=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    sender_id: str = ""
    recipient_id: str = ""
    content: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseAgent:
    """Represents an autonomous agent with strict security and zero-cost constraints."""

    def __init__(
        self,
        id: str,
        name: str,
        department_id: str,
        role: str,
        hierarchy_level: HierarchyLevel,
        system_prompt: str,
        preferred_provider: Optional[str] = None,
        preferred_model: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.department_id = department_id
        self.role = role
        self.hierarchy_level = hierarchy_level
        self.system_prompt = system_prompt
        self.preferred_provider = preferred_provider
        self.preferred_model = preferred_model
        self.status = AgentStatus.IDLE
        self.current_task_id: Optional[str] = None
        self.tokens_input: int = 0
        self.tokens_output: int = 0
        self.inbox: List[AgentMessage] = []

    async def execute_task(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> GenerationResponse:
        """Executes task prompt using strictly free-tier AI router."""
        self.status = AgentStatus.WORKING
        try:
            full_system = f"{self.system_prompt}\nDepartment: {self.department_id}\nRole: {self.role}\nAgent: {self.name}"
            response = await provider_registry.router.route_generate(
                prompt=prompt,
                system_prompt=full_system,
                preferred_provider=self.preferred_provider,
                preferred_model=self.preferred_model,
            )
            self.tokens_input += response.tokens_input
            self.tokens_output += response.tokens_output
            self.status = AgentStatus.IDLE
            return response
        except Exception as exc:
            self.status = AgentStatus.FAILED
            raise exc

    def receive_message(self, message: AgentMessage) -> None:
        self.inbox.append(message)
