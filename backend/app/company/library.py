"""Weekly Library Hour Management for AI Office.

Curates open-source tools, checks ARM64/PRoot compatibility, and submits installation proposals to NEEDS YOU.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.database.connection import db_manager


class LibraryHourManager:
    """Manages open-source skill and tool evaluations."""

    def __init__(self):
        pass

    def list_proposals(self) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM library_proposals ORDER BY created_at DESC;")
            return [dict(r) for r in cursor.fetchall()]

    def propose_tool(
        self,
        tool_name: str,
        repository_url: str,
        license_name: str,
        last_maintenance: str,
        dependencies: str,
        arm64_compatible: bool,
        proot_compatible: bool,
        security_risks: str,
        required_permissions: str,
        benefits: str,
        installation_size_mb: float,
        integration_plan: str,
        recommendation: str,
    ) -> Dict[str, Any]:
        """Record tool analysis and submit installation proposal to NEEDS YOU gateway."""
        proposal_id = f"lib-{uuid.uuid4().hex[:8]}"
        approval_id = f"appr-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        expires_at = datetime.fromtimestamp(datetime.now().timestamp() + 86400 * 7, timezone.utc).isoformat()

        # Action payload for Needs You gateway
        action_payload = {
            "proposal_id": proposal_id,
            "tool_name": tool_name,
            "repository_url": repository_url,
            "installation_size_mb": installation_size_mb,
            "action": "INSTALL_OPEN_SOURCE_TOOL",
        }
        import hashlib
        payload_canonical = json.dumps(action_payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_canonical.encode("utf-8")).hexdigest()

        with db_manager.session() as conn:
            # 1. Create approval request
            conn.execute(
                """
                INSERT INTO approvals (id, agent_id, department_id, action_type, destination, payload, payload_hash, risk_level, cost, status, expires_at)
                VALUES (?, 'mgr-001', 'research', 'INSTALL_TOOL', 'LOCAL_ENVIRONMENT', ?, ?, 'MEDIUM', 0.0, 'PENDING', ?);
                """,
                (approval_id, payload_canonical, payload_hash, expires_at),
            )

            # 2. Insert library proposal
            conn.execute(
                """
                INSERT INTO library_proposals (
                    id, tool_name, repository_url, license, last_maintenance, dependencies,
                    arm64_compatible, proot_compatible, security_risks, required_permissions,
                    benefits, installation_size_mb, integration_plan, recommendation,
                    status, approval_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'IN_NEEDS_YOU', ?, ?);
                """,
                (
                    proposal_id, tool_name, repository_url, license_name, last_maintenance, dependencies,
                    1 if arm64_compatible else 0, 1 if proot_compatible else 0, security_risks, required_permissions,
                    benefits, installation_size_mb, integration_plan, recommendation, approval_id, now
                ),
            )

        return {
            "proposal_id": proposal_id,
            "approval_id": approval_id,
            "tool_name": tool_name,
            "status": "IN_NEEDS_YOU",
        }


library_hour_mgr = LibraryHourManager()
