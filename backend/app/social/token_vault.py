"""AES-256-GCM Token Vault for Social OAuth Tokens."""

from datetime import datetime, timedelta, timezone
import json
import sqlite3
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.core.security import decrypt_token, encrypt_token
from app.database.connection import db_manager
from app.social.base import AccountInfo, AccountStatus, OperationalStatus, SocialPlatform


class TokenVault:
    """Manages encrypted at-rest storage for social platform tokens."""

    def save_account_tokens(
        self,
        platform: SocialPlatform,
        account_id: str,
        username: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in_seconds: int = 3600,
        permissions: Optional[List[str]] = None,
        operational_status: OperationalStatus = OperationalStatus.ACCOUNT_AUTHORIZED,
        capabilities: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
    ) -> None:
        token_bundle = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        encrypted = encrypt_token(json.dumps(token_bundle))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        perms_str = json.dumps(permissions or [])
        caps_str = json.dumps(capabilities or [])
        scopes_str = json.dumps(scopes or [])

        with db_manager.session() as conn:
            conn.execute(
                """INSERT INTO social_accounts (
                    platform, account_id, username, connected, permissions,
                    encrypted_token, token_expires_at, operational_status, capabilities, scopes, last_sync
                ) VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(platform) DO UPDATE SET
                    account_id = excluded.account_id,
                    username = excluded.username,
                    connected = 1,
                    permissions = excluded.permissions,
                    encrypted_token = excluded.encrypted_token,
                    token_expires_at = excluded.token_expires_at,
                    operational_status = excluded.operational_status,
                    capabilities = CASE WHEN excluded.capabilities != '[]' THEN excluded.capabilities ELSE social_accounts.capabilities END,
                    scopes = CASE WHEN excluded.scopes != '[]' THEN excluded.scopes ELSE social_accounts.scopes END,
                    last_sync = CURRENT_TIMESTAMP;""",
                (
                    platform.value,
                    account_id,
                    username,
                    perms_str,
                    encrypted,
                    expires_at.isoformat(),
                    operational_status.value,
                    caps_str,
                    scopes_str,
                ),
            )
            conn.execute(
                """INSERT INTO audit_ledger (actor, action, status, details)
                   VALUES ('TOKEN_VAULT', 'OAUTH_TOKEN_SAVED', 'SUCCESS', ?);""",
                (f"Encrypted token saved for {platform.value} ({account_id})",),
            )
        logger.info(f"Encrypted token saved in vault for {platform.value}")

    def update_test_result(
        self,
        platform: SocialPlatform,
        operational_status: OperationalStatus,
        test_result: Dict[str, Any],
        capabilities: Optional[List[str]] = None,
    ) -> None:
        """Update operational status and test diagnostics."""
        with db_manager.session() as conn:
            test_json = json.dumps(test_result)
            if capabilities:
                conn.execute(
                    """UPDATE social_accounts
                       SET operational_status = ?, last_test_result = ?, capabilities = ?, last_sync = CURRENT_TIMESTAMP
                       WHERE platform = ?;""",
                    (operational_status.value, test_json, json.dumps(capabilities), platform.value),
                )
            else:
                conn.execute(
                    """UPDATE social_accounts
                       SET operational_status = ?, last_test_result = ?, last_sync = CURRENT_TIMESTAMP
                       WHERE platform = ?;""",
                    (operational_status.value, test_json, platform.value),
                )

    def get_access_token(self, platform: SocialPlatform) -> Optional[str]:
        """Decrypts and returns active access token if not expired."""
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT encrypted_token, token_expires_at, connected FROM social_accounts WHERE platform = ?;",
                (platform.value,),
            )
            row = cursor.fetchone()
            if not row or not row["connected"] or not row["encrypted_token"]:
                return None

            expires_at = datetime.fromisoformat(row["token_expires_at"].replace("Z", "+00:00"))
            if datetime.now(timezone.utc) > expires_at:
                logger.warning(f"OAuth token for {platform.value} has expired.")
                return None

            decrypted_raw = decrypt_token(row["encrypted_token"])
            bundle = json.loads(decrypted_raw)
            return bundle.get("access_token")

    def get_account_info(self, platform: SocialPlatform) -> AccountInfo:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM social_accounts WHERE platform = ?;", (platform.value,))
            row = cursor.fetchone()

        if not row:
            return AccountInfo(
                platform=platform,
                status=AccountStatus.DISCONNECTED,
                operational_status=OperationalStatus.DISCONNECTED,
            )

        now = datetime.now(timezone.utc)
        expires_at = datetime.fromisoformat(row["token_expires_at"].replace("Z", "+00:00")) if row["token_expires_at"] else None
        is_connected = bool(row["connected"])

        raw_op_status = row["operational_status"] if "operational_status" in row.keys() else "DISCONNECTED"
        try:
            op_status = OperationalStatus(raw_op_status)
        except Exception:
            op_status = OperationalStatus.DISCONNECTED

        if not is_connected:
            status = AccountStatus.DISCONNECTED
            if op_status not in (OperationalStatus.APP_OPENED, OperationalStatus.ERROR):
                op_status = OperationalStatus.DISCONNECTED
        elif expires_at and now > expires_at:
            status = AccountStatus.EXPIRED
            op_status = OperationalStatus.TOKEN_EXPIRED
        else:
            status = AccountStatus.CONNECTED
            if op_status == OperationalStatus.DISCONNECTED:
                op_status = OperationalStatus.ACCOUNT_AUTHORIZED

        perms = []
        if row["permissions"]:
            try:
                perms = json.loads(row["permissions"])
            except Exception:
                pass

        caps = []
        if "capabilities" in row.keys() and row["capabilities"]:
            try:
                caps = json.loads(row["capabilities"])
            except Exception:
                pass

        scopes = []
        if "scopes" in row.keys() and row["scopes"]:
            try:
                scopes = json.loads(row["scopes"])
            except Exception:
                pass

        test_res = {}
        if "last_test_result" in row.keys() and row["last_test_result"]:
            try:
                test_res = json.loads(row["last_test_result"])
            except Exception:
                pass

        intent_uri = row["app_intent_uri"] if "app_intent_uri" in row.keys() else None

        return AccountInfo(
            platform=platform,
            account_id=row["account_id"],
            username=row["username"],
            status=status,
            operational_status=op_status,
            permissions=perms,
            scopes=scopes,
            token_expires_at=expires_at,
            last_sync=datetime.fromisoformat(row["last_sync"].replace("Z", "+00:00")) if row["last_sync"] else None,
            capabilities=caps,
            last_test_result=test_res,
            app_intent_uri=intent_uri,
        )

    def list_all_accounts(self) -> List[AccountInfo]:
        platforms = [
            SocialPlatform.GOOGLE_1,
            SocialPlatform.GOOGLE_2,
            SocialPlatform.GOOGLE_3,
            SocialPlatform.YOUTUBE,
            SocialPlatform.TIKTOK,
            SocialPlatform.INSTAGRAM,
            SocialPlatform.FACEBOOK,
        ]
        return [self.get_account_info(p) for p in platforms]

    def disconnect_account(self, platform: SocialPlatform) -> None:
        """Revoke / clear tokens and mark account as disconnected."""
        with db_manager.session() as conn:
            conn.execute(
                """UPDATE social_accounts
                   SET connected = 0, operational_status = 'DISCONNECTED', encrypted_token = NULL, last_sync = CURRENT_TIMESTAMP
                   WHERE platform = ?;""",
                (platform.value,),
            )
            conn.execute(
                "INSERT INTO audit_ledger (actor, action, status, details) VALUES ('TOKEN_VAULT', 'OAUTH_DISCONNECT', 'SUCCESS', ?);",
                (f"Disconnected {platform.value}",),
            )
        logger.info(f"Account disconnected: {platform.value}")


token_vault = TokenVault()
