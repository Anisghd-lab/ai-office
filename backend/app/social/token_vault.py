"""AES-256-GCM Token Vault for Social OAuth Tokens."""

from datetime import datetime, timedelta, timezone
import json
import sqlite3
from typing import Dict, List, Optional
from app.core.logging import logger
from app.core.security import decrypt_token, encrypt_token
from app.database.connection import db_manager
from app.social.base import AccountInfo, AccountStatus, SocialPlatform


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
    ) -> None:
        token_bundle = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        encrypted = encrypt_token(json.dumps(token_bundle))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        perms_str = json.dumps(permissions or [])

        with db_manager.session() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO social_accounts (
                    platform, account_id, username, connected, permissions,
                    encrypted_token, token_expires_at, last_sync
                ) VALUES (?, ?, ?, 1, ?, ?, ?, CURRENT_TIMESTAMP);""",
                (
                    platform.value,
                    account_id,
                    username,
                    perms_str,
                    encrypted,
                    expires_at.isoformat(),
                ),
            )
            conn.execute(
                """INSERT INTO audit_ledger (actor, action, status, details)
                   VALUES ('TOKEN_VAULT', 'OAUTH_TOKEN_SAVED', 'SUCCESS', ?);""",
                (f"Encrypted token saved for {platform.value} ({account_id})",),
            )
        logger.info(f"Encrypted token saved in vault for {platform.value}")

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

        if not row or not row["connected"]:
            return AccountInfo(platform=platform, status=AccountStatus.DISCONNECTED)

        now = datetime.now(timezone.utc)
        expires_at = datetime.fromisoformat(row["token_expires_at"].replace("Z", "+00:00")) if row["token_expires_at"] else None
        status = AccountStatus.EXPIRED if (expires_at and now > expires_at) else AccountStatus.CONNECTED

        perms = []
        if row["permissions"]:
            try:
                perms = json.loads(row["permissions"])
            except Exception:
                pass

        return AccountInfo(
            platform=platform,
            account_id=row["account_id"],
            username=row["username"],
            status=status,
            permissions=perms,
            token_expires_at=expires_at,
            last_sync=datetime.fromisoformat(row["last_sync"].replace("Z", "+00:00")) if row["last_sync"] else None,
            capabilities=["publish_video" if platform == SocialPlatform.TIKTOK else "publish_post"],
        )

    def disconnect_account(self, platform: SocialPlatform) -> None:
        """Revoke / clear tokens and mark account as disconnected."""
        with db_manager.session() as conn:
            conn.execute(
                """UPDATE social_accounts
                   SET connected = 0, encrypted_token = NULL, last_sync = CURRENT_TIMESTAMP
                   WHERE platform = ?;""",
                (platform.value,),
            )
            conn.execute(
                "INSERT INTO audit_ledger (actor, action, status, details) VALUES ('TOKEN_VAULT', 'OAUTH_DISCONNECT', 'SUCCESS', ?);",
                (f"Disconnected {platform.value}",),
            )
        logger.info(f"Account disconnected: {platform.value}")


token_vault = TokenVault()
