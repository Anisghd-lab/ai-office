"""Mandatory CEO Approval Security Gateway (Default-Deny External Action Engine)."""

import asyncio
from datetime import datetime, timedelta, timezone
import json
import sqlite3
import uuid
from typing import Any, Callable, Dict, Optional
from app.config import settings
from app.core.logging import logger
from app.core.security import canonical_json_hash
from app.database.connection import db_manager
from app.events.bus import event_bus
from app.providers.base import PaidEndpointForbiddenError


class GatewaySecurityViolation(Exception):
    """Raised when an operation attempts to bypass or violate the CEO Approval Gateway."""
    pass


class PayloadTamperedError(GatewaySecurityViolation):
    """Raised when the execution payload hash does not match the approved payload hash."""
    pass


class ApprovalExpiredError(GatewaySecurityViolation):
    """Raised when an attempt is made to execute an expired approval request."""
    pass


class UnauthorizedExecutionError(GatewaySecurityViolation):
    """Raised when execution is attempted without a valid CEO approval."""
    pass


class ReplayAttackError(GatewaySecurityViolation):
    """Raised when an already-executed approval is replayed."""
    pass


class AgentSelfApprovalForbiddenError(GatewaySecurityViolation):
    """Raised when an agent attempts to approve its own or peer actions."""
    pass


EXTERNAL_ACTION_TYPES = {
    "SOCIAL_PUBLISH",
    "EXTERNAL_MESSAGE",
    "EXTERNAL_EMAIL",
    "EXTERNAL_UPLOAD",
    "FINANCIAL_TRANSACTION",
    "PURCHASE_SERVICE",
    "SUBSCRIBE_SERVICE",
    "CREDENTIAL_CHANGE",
    "EXTERNAL_INTEGRATION_CONNECT",
    "EXTERNAL_RESOURCE_DELETE",
}


class ApprovalGateway:
    """Default-deny external action governance gateway."""

    def __init__(self, ttl_seconds: Optional[int] = None):
        self.ttl_seconds = ttl_seconds or settings.CEO_APPROVAL_TOKEN_TTL_SECONDS

    def propose_action(
        self,
        agent_id: str,
        department_id: str,
        action_type: str,
        destination: str,
        payload: Any,
        risk_level: str = "MEDIUM",
        cost: float = 0.0,
    ) -> str:
        """Agent proposes an external action. Returns generated request_id."""
        action_upper = action_type.upper()
        if action_upper not in EXTERNAL_ACTION_TYPES:
            raise ValueError(f"Unrecognized external action type: '{action_type}'.")

        # Zero-cost assertion: any action attempting to spend money is strictly forbidden!
        if cost > 0.0 or action_upper in ("FINANCIAL_TRANSACTION", "PURCHASE_SERVICE", "SUBSCRIBE_SERVICE"):
            raise PaidEndpointForbiddenError(
                f"Action '{action_type}' incurs financial cost of ${cost:.2f}. Absolute zero-cost constraint forbids this."
            )

        payload_str = json.dumps(payload) if not isinstance(payload, str) else payload
        payload_hash = canonical_json_hash(payload)

        request_id = f"apr-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=self.ttl_seconds)

        with db_manager.session() as conn:
            conn.execute(
                """INSERT INTO approvals (
                    id, agent_id, department_id, action_type, destination,
                    payload, payload_hash, risk_level, cost, status, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?);""",
                (
                    request_id,
                    agent_id,
                    department_id,
                    action_upper,
                    destination.upper(),
                    payload_str,
                    payload_hash,
                    risk_level.upper(),
                    0.0,
                    expires_at.isoformat(),
                ),
            )
            conn.execute(
                """INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details)
                   VALUES (?, ?, ?, 'PENDING', ?, ?);""",
                (
                    agent_id,
                    department_id,
                    f"PROPOSE_{action_upper}",
                    payload_hash,
                    f"Proposal {request_id} for {destination} awaiting CEO approval",
                ),
            )

        logger.info(f"CEO Approval Gateway intercepted action: {request_id} ({action_upper} to {destination})")

        # Broadcast SSE event to Android client
        asyncio_loop_or_task = True
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    event_bus.publish(
                        "approval.created",
                        {
                            "request_id": request_id,
                            "agent_id": agent_id,
                            "department_id": department_id,
                            "action_type": action_upper,
                            "destination": destination,
                            "risk_level": risk_level,
                            "payload_hash": payload_hash,
                        },
                    )
                )
        except Exception:
            pass

        return request_id

    def approve_action(self, request_id: str, comment: Optional[str] = None, actor: str = "CEO") -> None:
        """Authorize an action. Only the human CEO can authorize."""
        if actor != "CEO":
            raise AgentSelfApprovalForbiddenError(
                f"Actor '{actor}' is not authorized to approve gateway requests. Only CEO may approve."
            )

        now = datetime.now(timezone.utc)
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
            record = cursor.fetchone()
            if not record:
                raise ValueError(f"Approval request '{request_id}' not found.")

            if record["status"] != "PENDING":
                raise UnauthorizedExecutionError(
                    f"Cannot approve request with status '{record['status']}'. Must be 'PENDING'."
                )

            expires_at = datetime.fromisoformat(record["expires_at"].replace("Z", "+00:00"))
            if now > expires_at:
                conn.execute("UPDATE approvals SET status = 'EXPIRED' WHERE id = ?;", (request_id,))
                raise ApprovalExpiredError(f"Approval request '{request_id}' expired at {record['expires_at']}.")

            conn.execute(
                """UPDATE approvals
                   SET status = 'APPROVED',
                       decision_comment = ?,
                       decided_by = ?,
                       decided_at = CURRENT_TIMESTAMP
                   WHERE id = ?;""",
                (comment or "Approved by CEO", actor, request_id),
            )
            conn.execute(
                """INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details)
                   VALUES (?, ?, 'APPROVAL_DECISION', 'APPROVED', ?, ?);""",
                (actor, record["department_id"], record["payload_hash"], f"Approved {request_id}: {comment}"),
            )

        logger.info(f"CEO Approval granted for {request_id}")

    def reject_action(self, request_id: str, reason: str, actor: str = "CEO") -> None:
        """Reject an action."""
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
            record = cursor.fetchone()
            if not record:
                raise ValueError(f"Approval request '{request_id}' not found.")

            conn.execute(
                """UPDATE approvals
                   SET status = 'REJECTED',
                       decision_comment = ?,
                       decided_by = ?,
                       decided_at = CURRENT_TIMESTAMP
                   WHERE id = ?;""",
                (reason, actor, request_id),
            )
            conn.execute(
                """INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details)
                   VALUES (?, ?, 'APPROVAL_DECISION', 'REJECTED', ?, ?);""",
                (actor, record["department_id"], record["payload_hash"], f"Rejected {request_id}: {reason}"),
            )

        logger.info(f"CEO Approval rejected for {request_id}: {reason}")

    async def execute_action(
        self,
        request_id: str,
        execution_payload: Any,
        executor_func: Callable[[Any], Any],
    ) -> Any:
        """
        Validate all 8 security invariants, execute external action, and record audit trail.
        """
        now = datetime.now(timezone.utc)

        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approvals WHERE id = ?;", (request_id,))
            record = cursor.fetchone()

        if not record:
            raise UnauthorizedExecutionError(f"Approval request '{request_id}' does not exist.")

        # Invariant 6: Single-use / Nonce replay prevention
        if record["status"] == "EXECUTED" or record["execution_status"] in ("SUCCESS", "EXECUTED", "EXECUTING"):
            raise ReplayAttackError(f"Approval token '{request_id}' was already executed. Replay forbidden.")

        # Invariant 1: No approval means no external action
        if record["status"] != "APPROVED":
            raise UnauthorizedExecutionError(
                f"Request '{request_id}' status is '{record['status']}'. Must be 'APPROVED' by CEO."
            )

        # Invariant 2 & 3: Agent cannot self-approve / manager cannot bypass
        if record["decided_by"] != "CEO":
            raise AgentSelfApprovalForbiddenError(
                f"Approval was signed by non-CEO actor '{record['decided_by']}'. Execution aborted."
            )

        # Invariant 7: Expired approval cannot execute
        expires_at = datetime.fromisoformat(record["expires_at"].replace("Z", "+00:00"))
        if now > expires_at:
            with db_manager.session() as conn:
                conn.execute("UPDATE approvals SET status = 'EXPIRED' WHERE id = ?;", (request_id,))
            raise ApprovalExpiredError(f"Approval token '{request_id}' has expired.")

        # Invariant 4 & 5: Payload exact binding and tamper rejection
        current_hash = canonical_json_hash(execution_payload)
        if current_hash != record["payload_hash"]:
            with db_manager.session() as conn:
                conn.execute(
                    "UPDATE approvals SET execution_status = 'TAMPERED_FAILED' WHERE id = ?;",
                    (request_id,),
                )
                conn.execute(
                    """INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details)
                       VALUES ('SECURITY_GATEWAY', ?, 'PAYLOAD_TAMPER_DETECTED', 'SECURITY_ALERT', ?, ?);""",
                    (
                        record["department_id"],
                        current_hash,
                        f"Expected {record['payload_hash']}, got {current_hash}",
                    ),
                )
            raise PayloadTamperedError(
                f"Payload mismatch for '{request_id}'. Approved hash: {record['payload_hash']}, execution hash: {current_hash}."
            )

        # Atomically mark as EXECUTING to prevent race conditions
        with db_manager.session() as conn:
            conn.execute(
                "UPDATE approvals SET execution_status = 'EXECUTING' WHERE id = ?;",
                (request_id,),
            )

        # Execute external adapter
        try:
            if asyncio.iscoroutinefunction(executor_func):
                result = await executor_func(execution_payload)
            else:
                result = executor_func(execution_payload)

            result_str = json.dumps(result) if not isinstance(result, str) else result

            # Invariant 8: All execution results must be audited
            with db_manager.session() as conn:
                conn.execute(
                    """UPDATE approvals
                       SET status = 'EXECUTED',
                           execution_status = 'SUCCESS',
                           execution_result = ?,
                           executed_at = CURRENT_TIMESTAMP
                       WHERE id = ?;""",
                    (result_str, request_id),
                )
                conn.execute(
                    """INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details)
                       VALUES ('EXECUTOR', ?, 'EXTERNAL_EXECUTION_SUCCESS', 'SUCCESS', ?, ?);""",
                    (
                        record["department_id"],
                        record["payload_hash"],
                        f"Executed {record['action_type']} to {record['destination']}",
                    ),
                )

            await event_bus.publish(
                "approval.executed",
                {"request_id": request_id, "status": "SUCCESS", "destination": record["destination"]},
            )
            return result

        except Exception as exc:
            with db_manager.session() as conn:
                conn.execute(
                    """UPDATE approvals
                       SET execution_status = 'FAILED',
                           execution_result = ?,
                           executed_at = CURRENT_TIMESTAMP
                       WHERE id = ?;""",
                    (str(exc)[:500], request_id),
                )
                conn.execute(
                    """INSERT INTO audit_ledger (actor, department_id, action, status, payload_hash, details)
                       VALUES ('EXECUTOR', ?, 'EXTERNAL_EXECUTION_FAILED', 'FAILED', ?, ?);""",
                    (record["department_id"], record["payload_hash"], str(exc)[:200]),
                )
            raise


# Global gateway singleton
approval_gateway = ApprovalGateway()
