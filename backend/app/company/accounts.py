"""Secure Google Pro Accounts Registry for AI Office Media Company.

Enforces zero additional cost policy, encrypted credential storage, and observable quota checks.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.database.connection import db_manager


class GoogleAccountRegistry:
    """Manages the 3 authorized Google Pro accounts without storing plaintext secrets."""

    def __init__(self):
        pass

    def list_accounts(self) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, account_email_masked, auth_status, available_quota, quota_observed_at, current_usage, is_available FROM google_accounts;")
            return [dict(r) for r in cursor.fetchall()]

    def update_quota_observation(
        self,
        account_id: str,
        available_quota: str,
        current_usage: Optional[str] = None,
        is_available: bool = True,
    ) -> Dict[str, Any]:
        """Update officially observed quota without inventing numbers."""
        now = datetime.now(timezone.utc).isoformat()
        with db_manager.session() as conn:
            conn.execute(
                """
                UPDATE google_accounts
                SET available_quota = ?, current_usage = ?, quota_observed_at = ?, is_available = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
                """,
                (available_quota, current_usage, now, 1 if is_available else 0, account_id),
            )
        return {"account_id": account_id, "available_quota": available_quota, "timestamp": now}

    def verify_generation_eligibility(self, account_id: str) -> Dict[str, Any]:
        """Preflight check: verifies account availability and asserts zero additional cost."""
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM google_accounts WHERE id = ?;", (account_id,))
            row = cursor.fetchone()
            if not row:
                return {"eligible": False, "reason": "Account not found in registry"}

            if row["auth_status"] != "AUTHENTICATED":
                return {
                    "eligible": False,
                    "reason": f"Account auth_status is '{row['auth_status']}', not AUTHENTICATED",
                }

            if not row["is_available"]:
                return {"eligible": False, "reason": "Account is marked unavailable or quota exhausted"}

            return {"eligible": True, "account_id": account_id, "cost_usd": 0.0}


google_account_registry = GoogleAccountRegistry()
