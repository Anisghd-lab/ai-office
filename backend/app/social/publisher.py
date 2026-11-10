"""Social Media Publishing Orchestrator gated by User Approval Gateway."""

from typing import Any, Dict, Optional
from app.core.logging import logger
from app.governance.gateway import approval_gateway
from app.social.base import (
    BaseSocialClient,
    PostDraft,
    PublishResult,
    SocialPlatform,
)
from app.social.facebook.client import FacebookClient
from app.social.google.client import GoogleAccountClient, YouTubeClient
from app.social.instagram.client import InstagramClient
from app.social.tiktok.client import TikTokClient
from app.social.token_vault import token_vault


class SocialPublisher:
    """Manages the full social publishing lifecycle strictly gated by Human Owner approval."""

    def __init__(self):
        self.clients: Dict[SocialPlatform, BaseSocialClient] = {
            SocialPlatform.GOOGLE_1: GoogleAccountClient(SocialPlatform.GOOGLE_1),
            SocialPlatform.GOOGLE_2: GoogleAccountClient(SocialPlatform.GOOGLE_2),
            SocialPlatform.GOOGLE_3: GoogleAccountClient(SocialPlatform.GOOGLE_3),
            SocialPlatform.YOUTUBE: YouTubeClient(),
            SocialPlatform.TIKTOK: TikTokClient(),
            SocialPlatform.FACEBOOK: FacebookClient(),
            SocialPlatform.INSTAGRAM: InstagramClient(),
        }

    def propose_publication(self, draft: PostDraft, proposing_agent_id: str = "dir-marketing") -> str:
        """
        Marketing or Creative agent proposes a social publication.
        Gateway intercepts and creates a Pending User Approval.
        """
        logger.info(f"Proposing publication to {draft.platform.value}: {draft.title}")
        payload = draft.to_payload_dict()
        request_id = approval_gateway.propose_action(
            agent_id=proposing_agent_id,
            department_id="marketing",
            action_type="SOCIAL_PUBLISH",
            destination=draft.platform.value.upper(),
            payload=payload,
            risk_level="MEDIUM",
            cost=0.0,
        )
        return request_id

    async def execute_approved_publication(self, request_id: str, draft: PostDraft) -> PublishResult:
        """
        Executes publication after verified Human Owner approval.
        Revalidates canonical payload hash and calls official platform API.
        """
        async def _executor(payload: Dict[str, Any]) -> Dict[str, Any]:
            platform_enum = SocialPlatform(payload["platform"])
            token = token_vault.get_access_token(platform_enum)
            if not token:
                raise RuntimeError(
                    f"Cannot publish to {platform_enum.value}: account is not connected via official OAuth or token is expired. Please connect account in Social Accounts center."
                )

            client = self.clients[platform_enum]
            result = await client.publish_post(token=token, draft=draft)
            if result.status != "SUCCESS":
                raise RuntimeError(f"Platform publish failed: {result.error_message}")
            return {
                "post_id": result.post_id,
                "platform": result.platform.value,
                "permalink": result.permalink,
                "status": "SUCCESS",
            }

        exec_res = await approval_gateway.execute_action(
            request_id=request_id,
            execution_payload=draft.to_payload_dict(),
            executor_func=_executor,
        )

        return PublishResult(
            post_id=exec_res["post_id"],
            platform=SocialPlatform(exec_res["platform"]),
            status="SUCCESS",
            permalink=exec_res.get("permalink"),
        )


social_publisher = SocialPublisher()
