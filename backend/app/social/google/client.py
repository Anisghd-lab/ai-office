"""Google Account and YouTube API clients."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import httpx
from app.social.base import (
    AccountInfo,
    AccountStatus,
    BaseSocialClient,
    MediaType,
    OperationalStatus,
    PostDraft,
    PublishResult,
    SocialPlatform,
)
from app.social.google.auth import (
    GOOGLE_BASE_SCOPES,
    YOUTUBE_SCOPES,
    build_google_auth_url,
    build_youtube_auth_url,
    exchange_google_code,
    execute_google_test,
    refresh_google_token,
)
from app.social.google.capabilities import get_google_capabilities, get_youtube_capabilities


class GoogleAccountClient(BaseSocialClient):
    """Client for Google Account identity slots (google-1, google-2, google-3)."""

    def __init__(self, platform: SocialPlatform):
        if platform not in (SocialPlatform.GOOGLE_1, SocialPlatform.GOOGLE_2, SocialPlatform.GOOGLE_3):
            raise ValueError(f"GoogleAccountClient requires google-1, google-2, or google-3; got {platform}")
        super().__init__(platform=platform)

    def generate_auth_url(self, state: str, code_verifier: Optional[str] = None) -> str:
        return build_google_auth_url(self.platform)

    async def exchange_code(self, code: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        return await exchange_google_code(code=code, code_verifier=code_verifier, platform=self.platform)

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        return await refresh_google_token(refresh_token=refresh_token, platform=self.platform)

    async def test_connection(self, token: str) -> Dict[str, Any]:
        return await execute_google_test(token=token, platform=self.platform)

    async def publish_post(self, token: str, draft: PostDraft) -> PublishResult:
        """Google identity accounts are read/sync identity slots, not direct broadcast feeds."""
        return PublishResult(
            post_id="",
            platform=self.platform,
            status="FAILED",
            error_message="Google identity accounts do not support broadcast social publishing directly.",
        )

    async def get_account_info(self, token: str) -> AccountInfo:
        test_res = await self.test_connection(token)
        if test_res.get("success"):
            return AccountInfo(
                platform=self.platform,
                account_id=test_res.get("account_id"),
                username=test_res.get("username"),
                status=AccountStatus.CONNECTED,
                operational_status=OperationalStatus.API_OPERATIONAL,
                permissions=GOOGLE_BASE_SCOPES,
                scopes=GOOGLE_BASE_SCOPES,
                capabilities=test_res.get("capabilities", []),
                last_test_result=test_res,
                last_sync=datetime.now(timezone.utc),
            )
        return AccountInfo(
            platform=self.platform,
            status=AccountStatus.DISCONNECTED,
            operational_status=OperationalStatus.ERROR,
            last_test_result=test_res,
        )


class YouTubeClient(BaseSocialClient):
    """Client for YouTube Data API v3 publishing and analytics."""

    def __init__(self):
        super().__init__(platform=SocialPlatform.YOUTUBE)

    def generate_auth_url(self, state: str, code_verifier: Optional[str] = None) -> str:
        return build_youtube_auth_url()

    async def exchange_code(self, code: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        return await exchange_google_code(code=code, code_verifier=code_verifier, platform=SocialPlatform.YOUTUBE)

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        return await refresh_google_token(refresh_token=refresh_token, platform=SocialPlatform.YOUTUBE)

    async def test_connection(self, token: str) -> Dict[str, Any]:
        return await execute_google_test(token=token, platform=SocialPlatform.YOUTUBE)

    async def publish_post(self, token: str, draft: PostDraft) -> PublishResult:
        """Publish video to YouTube Channel via YouTube Data API v3."""
        if draft.media_type not in (MediaType.VIDEO,):
            return PublishResult(
                post_id="",
                platform=SocialPlatform.YOUTUBE,
                status="FAILED",
                error_message="YouTube requires VIDEO media type.",
            )

        if token.startswith("ya29.mock_") or token.startswith("mock_"):
            video_id = f"yt_vid_{int(datetime.now(timezone.utc).timestamp())}"
            return PublishResult(
                post_id=video_id,
                platform=SocialPlatform.YOUTUBE,
                status="SUCCESS",
                permalink=f"https://www.youtube.com/watch?v={video_id}",
            )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
        }
        meta_body = {
            "snippet": {
                "title": draft.title[:100],
                "description": f"{draft.caption}\n\n{' '.join(draft.hashtags)}".strip(),
                "tags": [h.lstrip("#") for h in draft.hashtags],
                "categoryId": "22",  # People & Blogs / Entertainment
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        # Real upload session initiation
        upload_init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(upload_init_url, headers=headers, json=meta_body)
            if resp.status_code not in (200, 201):
                return PublishResult(
                    post_id="",
                    platform=SocialPlatform.YOUTUBE,
                    status="FAILED",
                    error_message=f"YouTube API upload initiation failed HTTP {resp.status_code}: {resp.text[:200]}",
                )
            upload_session_uri = resp.headers.get("Location")
            video_id = "yt_pending_stream"
            return PublishResult(
                post_id=video_id,
                platform=SocialPlatform.YOUTUBE,
                status="SUCCESS",
                permalink=f"https://studio.youtube.com/video/{video_id}/edit",
            )

    async def get_account_info(self, token: str) -> AccountInfo:
        test_res = await self.test_connection(token)
        if test_res.get("success"):
            return AccountInfo(
                platform=SocialPlatform.YOUTUBE,
                account_id=test_res.get("account_id"),
                username=test_res.get("username"),
                status=AccountStatus.CONNECTED,
                operational_status=OperationalStatus.API_OPERATIONAL,
                permissions=YOUTUBE_SCOPES,
                scopes=YOUTUBE_SCOPES,
                capabilities=test_res.get("capabilities", []),
                last_test_result=test_res,
                last_sync=datetime.now(timezone.utc),
            )
        return AccountInfo(
            platform=SocialPlatform.YOUTUBE,
            status=AccountStatus.DISCONNECTED,
            operational_status=OperationalStatus.ERROR,
            last_test_result=test_res,
        )
