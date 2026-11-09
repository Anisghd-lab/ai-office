"""Meta Graph API Client for Facebook Pages."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from app.config import settings
from app.social.base import (
    AccountInfo,
    AccountStatus,
    BaseSocialClient,
    PostDraft,
    PublishResult,
    SocialPlatform,
)

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class FacebookClient(BaseSocialClient):
    """Meta Graph API Client for Facebook Pages."""

    def __init__(self):
        super().__init__(platform=SocialPlatform.FACEBOOK)
        self.app_id = settings.FACEBOOK_APP_ID or ""
        self.app_secret = settings.FACEBOOK_APP_SECRET or ""
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI

    def generate_auth_url(self, state: str, code_verifier: Optional[str] = None) -> str:
        from app.social.facebook.auth import build_facebook_auth_url
        return build_facebook_auth_url()

    async def exchange_code(self, code: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{GRAPH_API_BASE}/oauth/access_token", params=params)
            if resp.status_code != 200:
                raise RuntimeError(f"Facebook token exchange failed: HTTP {resp.status_code}: {resp.text}")
            return resp.json()

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        # Meta long-lived tokens
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": refresh_token,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{GRAPH_API_BASE}/oauth/access_token", params=params)
            if resp.status_code != 200:
                raise RuntimeError(f"Facebook token refresh failed: HTTP {resp.status_code}")
            return resp.json()

    async def publish_post(self, token: str, draft: PostDraft) -> PublishResult:
        """Publish post to a Facebook Page."""
        page_id = draft.target_account_id or "me"
        content = f"{draft.caption}\n\n{' '.join(draft.hashtags)}".strip()
        payload = {
            "message": content,
            "access_token": token,
        }
        if draft.media_urls:
            payload["link"] = draft.media_urls[0]

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{GRAPH_API_BASE}/{page_id}/feed", data=payload)
            if resp.status_code not in (200, 201):
                return PublishResult(
                    post_id="",
                    platform=SocialPlatform.FACEBOOK,
                    status="FAILED",
                    error_message=f"Facebook API HTTP {resp.status_code}: {resp.text[:200]}",
                )
            post_id = resp.json().get("id", "fb-post-unknown")
            return PublishResult(
                post_id=post_id,
                platform=SocialPlatform.FACEBOOK,
                status="SUCCESS",
                permalink=f"https://www.facebook.com/{post_id}",
            )

    async def get_account_info(self, token: str) -> AccountInfo:
        return AccountInfo(
            platform=SocialPlatform.FACEBOOK,
            status=AccountStatus.CONNECTED,
            capabilities=["page_feed_publish", "page_read_engagement"],
        )
