"""Dynamic Agent Runtime, shared memory, and lifecycle orchestrator."""

import asyncio
import json
import sqlite3
import uuid
from typing import Any, Dict, List, Optional
from app.agents.base import AgentMessage, AgentStatus, BaseAgent, HierarchyLevel
from app.core.logging import logger
from app.database.connection import db_manager
from app.events.bus import event_bus


class SharedMemory:
    """Thread-safe persistent shared memory across departments and agents."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def set(self, key: str, value: Any, provenance: str = "agent-runtime") -> None:
        self._cache[key] = value
        with db_manager.session() as conn:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            conn.execute(
                """INSERT OR REPLACE INTO knowledge_items (id, title, category, content, provenance)
                   VALUES (?, ?, 'shared_memory', ?, ?);""",
                (f"mem-{key}", key, val_str, provenance),
            )

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._cache:
            return self._cache[key]
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM knowledge_items WHERE id = ?;", (f"mem-{key}",))
            row = cursor.fetchone()
            if row:
                try:
                    val = json.loads(row["content"])
                except Exception:
                    val = row["content"]
                self._cache[key] = val
                return val
        return default


class AgentRuntimeManager:
    """Orchestrates persistent directors and dynamic specialists."""

    def __init__(self):
        self.active_agents: Dict[str, BaseAgent] = {}
        self.shared_memory = SharedMemory()
        self._lock = asyncio.Lock()

    def register_agent(self, agent: BaseAgent, persist: bool = True) -> None:
        self.active_agents[agent.id] = agent
        if persist:
            with db_manager.session() as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO agents (id, name, department_id, role, hierarchy_level, status, current_provider, current_model)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                    (
                        agent.id,
                        agent.name,
                        agent.department_id,
                        agent.role,
                        agent.hierarchy_level.value,
                        agent.status.value,
                        agent.preferred_provider,
                        agent.preferred_model,
                    ),
                )

    def spawn_dynamic_specialist(
        self,
        department_id: str,
        role: str,
        task_id: str,
        name: Optional[str] = None,
    ) -> BaseAgent:
        """Spawn an ephemeral specialist agent to tackle a specialized task."""
        agent_id = f"spec-{department_id[:3]}-{uuid.uuid4().hex[:6]}"
        agent_name = name or f"Specialist ({role})"
        agent = BaseAgent(
            id=agent_id,
            name=agent_name,
            department_id=department_id,
            role=role,
            hierarchy_level=HierarchyLevel.SPECIALIST,
            system_prompt=f"You are an ephemeral specialist agent in {department_id}. Execute your assigned task with maximum precision and zero hallucinations.",
        )
        agent.current_task_id = task_id
        self.register_agent(agent, persist=True)
        logger.info(f"Spawned dynamic specialist agent: {agent_id} ({agent_name}) for task {task_id}")
        return agent

    def teardown_dynamic_specialist(self, agent_id: str) -> None:
        """Gracefully decommission an ephemeral specialist after task completion."""
        agent = self.active_agents.pop(agent_id, None)
        if agent:
            with db_manager.session() as conn:
                conn.execute(
                    "UPDATE agents SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
                    (agent_id,),
                )
            logger.info(f"Teardown complete for specialist agent: {agent_id}")

    async def send_inter_agent_message(self, sender_id: str, recipient_id: str, content: str) -> AgentMessage:
        """Deliver messages between agents with audit tracking."""
        msg = AgentMessage(sender_id=sender_id, recipient_id=recipient_id, content=content)
        recipient = self.active_agents.get(recipient_id)
        if recipient:
            recipient.receive_message(msg)

        # Audit ledger
        with db_manager.session() as conn:
            conn.execute(
                "INSERT INTO audit_ledger (actor, action, status, details) VALUES (?, ?, ?, ?);",
                (sender_id, "INTER_AGENT_MSG", "DELIVERED", f"To {recipient_id}: {content[:100]}"),
            )

        await event_bus.publish(
            "agent.message",
            {"sender_id": sender_id, "recipient_id": recipient_id, "content": content},
        )
        return msg

    def recover_from_restart(self) -> int:
        """Reload active agents from SQLite upon backend process restart."""
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agents WHERE status IN ('IDLE', 'WORKING', 'PAUSED');")
            rows = cursor.fetchall()
            recovered = 0
            for r in rows:
                if r["id"] not in self.active_agents:
                    agent = BaseAgent(
                        id=r["id"],
                        name=r["name"],
                        department_id=r["department_id"],
                        role=r["role"],
                        hierarchy_level=HierarchyLevel(r["hierarchy_level"]),
                        system_prompt=f"Agent rehydrated after restart in {r['department_id']}.",
                        preferred_provider=r["current_provider"],
                        preferred_model=r["current_model"],
                    )
                    agent.status = AgentStatus(r["status"])
                    agent.current_task_id = r["current_task_id"]
                    self.active_agents[agent.id] = agent
                    recovered += 1
            logger.info(f"Recovered {recovered} agents from SQLite persistence.")
            return recovered


runtime_manager = AgentRuntimeManager()
