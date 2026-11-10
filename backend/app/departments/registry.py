"""Department Directors registry and charter initialization."""

from pathlib import Path
from typing import Dict, List, Optional
from app.agents.base import BaseAgent, HierarchyLevel
from app.agents.runtime import runtime_manager


def load_department_charter(department_id: str) -> Optional[str]:
    """Load the official department charter markdown file from team/."""
    candidates = [
        Path(__file__).resolve().parents[3] / "team" / f"{department_id}.md",
        Path("/root/ai-office/team") / f"{department_id}.md",
        Path("team") / f"{department_id}.md",
    ]
    for p in candidates:
        if p.is_file():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                pass
    return None


class DepartmentDirector(BaseAgent):
    """Persistent Department Director agent backed by official department charter."""

    def __init__(self, id: str, name: str, department_id: str, role: str, system_prompt: str):
        charter = load_department_charter(department_id)
        effective_prompt = system_prompt
        if charter:
            effective_prompt = f"{system_prompt}\n\n## Official Department Charter:\n{charter}"

        super().__init__(
            id=id,
            name=name,
            department_id=department_id,
            role=role,
            hierarchy_level=HierarchyLevel.DIRECTOR,
            system_prompt=effective_prompt,
        )
        self.charter = charter


DEPARTMENT_DIRECTORS = [
    DepartmentDirector(
        id="dir-research",
        name="Dr. Aris Vance",
        department_id="research",
        role="Director of Research & Intelligence",
        system_prompt="You lead the Research Department. Verify facts, analyze citations, and provide empirical intelligence.",
    ),
    DepartmentDirector(
        id="dir-technology",
        name="Marcus Sterling",
        department_id="technology",
        role="Director of Technology & Engineering",
        system_prompt="You lead Technology. Build robust, well-tested Python and Kotlin architectures under zero-cost constraints.",
    ),
    DepartmentDirector(
        id="dir-marketing",
        name="Elena Rostova",
        department_id="marketing",
        role="Director of Marketing & Communications",
        system_prompt="You lead Marketing. Draft compelling social media campaigns for TikTok, Facebook, and Instagram.",
    ),
    DepartmentDirector(
        id="dir-finance",
        name="Cassian Drake",
        department_id="finance",
        role="Director of Finance & Economic Guardrails",
        system_prompt="You lead Finance. Enforce the zero-cost invariant strictly. Block any action with cost > 0.0.",
    ),
    DepartmentDirector(
        id="dir-operations",
        name="Tariq Benali",
        department_id="operations",
        role="Director of Operations & Logistics",
        system_prompt="You lead Operations. Manage task queues, pipeline handoffs, scheduler jobs, and system recovery.",
    ),
    DepartmentDirector(
        id="dir-creative",
        name="Lyra Silvers",
        department_id="creative",
        role="Director of Creative Studio",
        system_prompt="You lead Creative. Design visual concepts, prompt matrices, and video storyboards with iOS Glassmorphism aesthetics.",
    ),
    DepartmentDirector(
        id="dir-strategy",
        name="Kaelen Thorne",
        department_id="strategy",
        role="Director of Strategy & Governance",
        system_prompt="You lead Strategy. Align departmental objectives with the corporate roadmap and evaluate risk matrices.",
    ),
    DepartmentDirector(
        id="dir-hr",
        name="Sora Tanaka",
        department_id="hr",
        role="Director of Human Resources",
        system_prompt="You lead Human Resources. Manage the dynamic specialist workforce and maintain strict permission boundaries.",
    ),
]


def initialize_directors() -> None:
    """Register all 8 directors into the active runtime and persistent store."""
    for director in DEPARTMENT_DIRECTORS:
        runtime_manager.register_agent(director, persist=True)


# Auto-initialize directors on import
initialize_directors()
