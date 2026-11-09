"""Instagram Professional Publishing API Client."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from app.config import settings
from app.social.base import (
    AccountInfo,
    AccountStatus,
    BaseSocialClient,
    MediaType,
    PostDraft,
    PublishResult,
    SocialPlatform,
)

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


class InstagramClient(BaseSocialClient):
    """Instagram Content Publishing API Adapter."""

    def __init__(self):
        super().__init__(platform=SocialPlatform.INSTAGRAM)
        self.app_id = settings.INSTAGRAM_CLIENT_ID or ""
        self.app_secret = settings.INSTAGRAM_CLIENT_SECRET or ""
        self.redirect_uri = settings.INSTAGRAM_REDIRECT_URI

    def generate_auth_url(self, state: str, code_verifier: Optional[str] = None) -> str:
        from app.social.instagram.auth import build_instagram_auth_url
        return build_instagram_auth_url()

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
                raise RuntimeError(f"Instagram token exchange failed: HTTP {resp.status_code}")
            return resp.json()

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": refresh_token,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{GRAPH_API_BASE}/oauth/access_token", params=params)
            if resp.status_code != 200:
                raise RuntimeError(f"Instagram token refresh failed: HTTP {resp.status_code}")
            return resp.json()

    async def publish_post(self, token: str, draft: PostDraft) -> PublishResult:
        """Execute two-step container publishing flow for Instagram."""
        ig_user_id = draft.target_account_id or "me"
        caption = f"{draft.caption}\n\n{' '.join(draft.hashtags)}".strip()
        media_url = draft.media_urls[0] if draft.media_urls else "https://example.com/image.jpg"

        # Step 1: Create media container
        container_payload: Dict[str, Any] = {
            "caption": caption,
            "access_token": token,
        }
        if draft.media_type == MediaType.VIDEO:
            container_payload["media_type"] = "REELS"
            container_payload["video_url"] = media_url
        else:
            container_payload["image_url"] = media_url

        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Container creation
            res1 = await client.post(f"{GRAPH_API_BASE}/{ig_user_id}/media", data=container_payload)
            if res1.status_code not in (200, 201):
                return PublishResult(
                    post_id="",
                    platform=SocialPlatform.INSTAGRAM,
                    status="FAILED",
                    error_message=f"Container creation failed: {res1.text[:200]}",
                )
            container_id = res1.json().get("id")

            # 2. Container publish
            res2 = await client.post(
                f"{GRAPH_API_BASE}/{ig_user_id}/media_publish",
                data={"creation_id": container_id, "access_token": token},
            )
            if res2.status_code not in (200, 201):
                return PublishResult(
                    post_id="",
                    platform=SocialPlatform.INSTAGRAM,
                    status="FAILED",
                    error_message=f"Media publish failed: {res2.text[:200]}",
                )

            published_id = res2.json().get("id", "ig-post-unknown")
            return PublishResult(
                post_id=published_id,
                platform=SocialPlatform.INSTAGRAM,
                status="SUCCESS",
                permalink=f"https://www.instagram.com/p/{published_id}",
            )

    async def get_account_info(self, token: str) -> AccountInfo:
        return AccountInfo(
            platform=SocialPlatform.INSTAGRAM,
            status=AccountStatus.CONNECTED,
            capabilities=["reels_publish", "photo_publish"],
            requires_business_verification=True,
        )
