"""TikTok Content Posting API Client."""

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

TIKTOK_TOKEN_ENDPOINT = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_PUBLISH_INIT_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/video/init/"


class TikTokClient(BaseSocialClient):
    """Official TikTok Content Posting API Adapter."""

    def __init__(self):
        super().__init__(platform=SocialPlatform.TIKTOK)
        self.client_key = settings.TIKTOK_CLIENT_KEY or ""
        self.client_secret = settings.TIKTOK_CLIENT_SECRET or ""
        self.redirect_uri = settings.TIKTOK_REDIRECT_URI

    def generate_auth_url(self, state: str, code_verifier: Optional[str] = None) -> str:
        from app.social.tiktok.auth import build_tiktok_auth_url
        return build_tiktok_auth_url()

    async def exchange_code(self, code: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(TIKTOK_TOKEN_ENDPOINT, data=data)
            if resp.status_code != 200:
                raise RuntimeError(f"TikTok token exchange failed: HTTP {resp.status_code}: {resp.text}")
            return resp.json().get("data", {})

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(TIKTOK_TOKEN_ENDPOINT, data=data)
            if resp.status_code != 200:
                raise RuntimeError(f"TikTok token refresh failed: HTTP {resp.status_code}")
            return resp.json().get("data", {})

    async def publish_post(self, token: str, draft: PostDraft) -> PublishResult:
        """Publish video to TikTok using official Content Posting API."""
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
        }
        post_title = f"{draft.caption} {' '.join(draft.hashtags)}".strip()
        body = {
            "post_info": {
                "title": post_title[:150],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": draft.media_urls[0] if draft.media_urls else "https://example.com/video.mp4",
            },
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(TIKTOK_PUBLISH_INIT_ENDPOINT, headers=headers, json=body)
            if resp.status_code not in (200, 201):
                return PublishResult(
                    post_id="",
                    platform=SocialPlatform.TIKTOK,
                    status="FAILED",
                    error_message=f"TikTok API HTTP {resp.status_code}: {resp.text[:200]}",
                )
            data = resp.json().get("data", {})
            publish_id = data.get("publish_id", "tt-pub-unknown")
            return PublishResult(
                post_id=publish_id,
                platform=SocialPlatform.TIKTOK,
                status="SUCCESS",
                permalink=f"https://www.tiktok.com/@user/video/{publish_id}",
            )

    async def get_account_info(self, token: str) -> AccountInfo:
        return AccountInfo(
            platform=SocialPlatform.TIKTOK,
            status=AccountStatus.CONNECTED,
            capabilities=["publish_video", "video_analytics"],
        )
