"""Comprehensive security tests for CEO Approval Gateway invariants."""

import json
from datetime import datetime, timedelta, timezone
import pytest
from app.database.connection import db_manager
from app.database.migrations import migration_manager
from app.governance.gateway import (
    ApprovalGateway,
    ApprovalExpiredError,
    AgentSelfApprovalForbiddenError,
    PayloadTamperedError,
    ReplayAttackError,
    UnauthorizedExecutionError,
)
from app.providers.base import PaidEndpointForbiddenError


@pytest.fixture(autouse=True)
def setup_gateway_db():
    with db_manager.session() as conn:
        migration_manager.run_migrations(conn)


# ---------------------------------------------------------
# 1. Unauthorized Publication Blocked
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_unauthorized_publication_blocked():
    gw = ApprovalGateway()
    payload = {"caption": "Breaking AI Office News", "tags": ["#ai", "#autonomy"]}
    req_id = gw.propose_action(
        agent_id="dir-marketing",
        department_id="marketing",
        action_type="SOCIAL_PUBLISH",
        destination="TIKTOK",
        payload=payload,
    )

    # Attempt to execute while still PENDING
    with pytest.raises(UnauthorizedExecutionError, match="Must be 'APPROVED'"):
        await gw.execute_action(
            request_id=req_id,
            execution_payload=payload,
            executor_func=lambda p: {"status": "published"},
        )


# ---------------------------------------------------------
# 2. Unauthorized Spending Blocked
# ---------------------------------------------------------
def test_unauthorized_spending_blocked():
    gw = ApprovalGateway()
    # Attempting to propose any action with cost > 0.0
    with pytest.raises(PaidEndpointForbiddenError, match="zero-cost constraint"):
        gw.propose_action(
            agent_id="dir-finance",
            department_id="finance",
            action_type="FINANCIAL_TRANSACTION",
            destination="STRIPE",
            payload={"amount": 10.00},
            cost=10.00,
        )

    # Attempting to purchase a service
    with pytest.raises(PaidEndpointForbiddenError):
        gw.propose_action(
            agent_id="dir-finance",
            department_id="finance",
            action_type="PURCHASE_SERVICE",
            destination="CLOUD_GPU",
            payload={"provider": "paid-cloud"},
            cost=0.0,
        )


# ---------------------------------------------------------
# 3. Payload Modification Rejected (Tamper Resistance)
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_payload_modification_rejected():
    gw = ApprovalGateway()
    original_payload = {"caption": "Safe Original Caption", "platform": "Instagram"}
    req_id = gw.propose_action(
        agent_id="dir-marketing",
        department_id="marketing",
        action_type="SOCIAL_PUBLISH",
        destination="INSTAGRAM",
        payload=original_payload,
    )

    # CEO approves the original payload
    gw.approve_action(req_id, comment="Approved original caption")

    # Attacker / agent attempts to substitute tampered payload
    tampered_payload = {"caption": "MALICIOUS INJECTED STATEMENT", "platform": "Instagram"}

    with pytest.raises(PayloadTamperedError, match="Payload mismatch"):
        await gw.execute_action(
            request_id=req_id,
            execution_payload=tampered_payload,
            executor_func=lambda p: {"status": "published"},
        )

    # Verify security audit alert recorded in ledger
    with db_manager.session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM audit_ledger WHERE action = 'PAYLOAD_TAMPER_DETECTED';")
        row = cursor.fetchone()
        assert row is not None
        assert row["status"] == "SECURITY_ALERT"


# ---------------------------------------------------------
# 4. Expired Approval Rejected
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_expired_approval_rejected():
    # Setup gateway with negative TTL to simulate expiration
    gw = ApprovalGateway(ttl_seconds=-10)
    payload = {"message": "Urgent update"}
    req_id = gw.propose_action(
        agent_id="dir-operations",
        department_id="operations",
        action_type="EXTERNAL_MESSAGE",
        destination="SLACK",
        payload=payload,
    )

    # Attempt approval of expired token
    with pytest.raises(ApprovalExpiredError):
        gw.approve_action(req_id, comment="Too late")


# ---------------------------------------------------------
# 5. Duplicate Execution Prevented (Replay Attack)
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_duplicate_execution_prevented():
    gw = ApprovalGateway()
    payload = {"caption": "Official Launch Post", "video_id": "vid-123"}
    req_id = gw.propose_action(
        agent_id="dir-marketing",
        department_id="marketing",
        action_type="SOCIAL_PUBLISH",
        destination="FACEBOOK",
        payload=payload,
    )

    gw.approve_action(req_id, comment="Approved for Facebook")

    # 1st Execution: Succeeds
    res1 = await gw.execute_action(
        request_id=req_id,
        execution_payload=payload,
        executor_func=lambda p: {"post_id": "fb-999"},
    )
    assert res1["post_id"] == "fb-999"

    # 2nd Execution: Replay attempt MUST fail
    with pytest.raises(ReplayAttackError, match="already executed"):
        await gw.execute_action(
            request_id=req_id,
            execution_payload=payload,
            executor_func=lambda p: {"post_id": "fb-999"},
        )


# ---------------------------------------------------------
# 6. Agent Self-Approval Prevented
# ---------------------------------------------------------
def test_agent_self_approval_prevented():
    gw = ApprovalGateway()
    payload = {"text": "Self authorized post"}
    req_id = gw.propose_action(
        agent_id="dir-marketing",
        department_id="marketing",
        action_type="SOCIAL_PUBLISH",
        destination="TIKTOK",
        payload=payload,
    )

    # Agent attempts to approve its own action
    with pytest.raises(AgentSelfApprovalForbiddenError, match="Only CEO may approve"):
        gw.approve_action(req_id, comment="Self-approved", actor="dir-marketing")

    # Central AI Manager attempts to approve
    with pytest.raises(AgentSelfApprovalForbiddenError):
        gw.approve_action(req_id, comment="Manager override", actor="mgr-001")


# ---------------------------------------------------------
# 7. Gateway Restart Recovery Verified
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_gateway_restart_recovery():
    gw1 = ApprovalGateway()
    payload = {"status_msg": "Persistent check"}
    req_id = gw1.propose_action(
        agent_id="dir-technology",
        department_id="technology",
        action_type="EXTERNAL_MESSAGE",
        destination="WEBHOOK",
        payload=payload,
    )
    gw1.approve_action(req_id, comment="CEO Approved")

    # Simulate backend restart: instantiate new ApprovalGateway instance
    gw2 = ApprovalGateway()
    result = await gw2.execute_action(
        request_id=req_id,
        execution_payload=payload,
        executor_func=lambda p: {"delivered": True},
    )
    assert result["delivered"] is True
