"""Backend core API integration, authentication, and lifecycle tests."""

import pytest
import httpx
from unittest.mock import patch
from app.main import app
from app.config import settings
from app.database.connection import db_manager
from app.database.migrations import migration_manager
from app.core.security import encrypt_token, decrypt_token, canonical_json_hash


@pytest.fixture(autouse=True)
def init_test_db():
    # Ensure migrations are applied before running tests
    with db_manager.session() as conn:
        migration_manager.run_migrations(conn)


@pytest.mark.asyncio
async def test_root_and_health_endpoints():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Root check
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "OPERATIONAL"

        # Health check
        resp_health = await client.get("/api/v1/health")
        assert resp_health.status_code == 200
        data = resp_health.json()
        assert data["status"] == "healthy"
        assert "wal" in data["database"].lower()


@pytest.mark.asyncio
async def test_departments_and_agents_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Departments check
        resp_dept = await client.get("/api/v1/departments")
        assert resp_dept.status_code == 200
        depts = resp_dept.json()
        assert len(depts) == 8
        dept_ids = {d["id"] for d in depts}
        assert "research" in dept_ids
        assert "technology" in dept_ids
        assert "creative" in dept_ids

        # Agents check
        resp_agents = await client.get("/api/v1/agents")
        assert resp_agents.status_code == 200
        agents = resp_agents.json()
        assert len(agents) >= 1
        mgr = [a for a in agents if a["hierarchy_level"] == "MANAGER"][0]
        assert "Nova Prime" in mgr["name"]


@pytest.mark.asyncio
async def test_task_creation_and_retrieval():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        task_payload = {
            "title": "Analyze free LLM benchmarks",
            "description": "Benchmark open-source model latency",
            "department_id": "research",
            "priority": "HIGH",
        }
        resp = await client.post("/api/v1/tasks", json=task_payload)
        assert resp.status_code == 201
        created = resp.json()
        assert created["title"] == task_payload["title"]
        assert created["status"] == "PENDING"
        task_id = created["id"]

        # Retrieve task
        resp_get = await client.get(f"/api/v1/tasks/{task_id}")
        assert resp_get.status_code == 200
        assert resp_get.json()["id"] == task_id


@pytest.mark.asyncio
async def test_metrics_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/metrics")
        assert resp.status_code == 200
        m = resp.json()
        assert "total_agents" in m
        assert "active_tasks" in m
        assert m["today_cost_usd"] == 0.0


def test_encryption_vault_and_payload_hashing():
    original = "token_xyz_sample_secret_12345"
    encrypted = encrypt_token(original)
    assert encrypted != original
    decrypted = decrypt_token(encrypted)
    assert decrypted == original

    # Test deterministic canonical hashing
    payload_a = {"title": "Post", "tags": [1, 2], "active": True}
    payload_b = {"active": True, "tags": [1, 2], "title": "Post"}
    assert canonical_json_hash(payload_a) == canonical_json_hash(payload_b)
