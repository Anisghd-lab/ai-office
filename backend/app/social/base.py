"""Base abstractions and data models for official social media integrations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class SocialPlatform(str, Enum):
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class AccountStatus(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    EXPIRED = "EXPIRED"
    UNAUTHORIZED = "UNAUTHORIZED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class MediaType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


@dataclass
class AccountInfo:
    platform: SocialPlatform
    account_id: Optional[str] = None
    username: Optional[str] = None
    status: AccountStatus = AccountStatus.DISCONNECTED
    permissions: List[str] = field(default_factory=list)
    token_expires_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    capabilities: List[str] = field(default_factory=list)
    requires_business_verification: bool = False


@dataclass
class PostDraft:
    title: str
    caption: str
    hashtags: List[str] = field(default_factory=list)
    media_urls: List[str] = field(default_factory=list)
    media_type: MediaType = MediaType.TEXT
    platform: SocialPlatform = SocialPlatform.TIKTOK
    target_account_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None

    def to_payload_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "media_urls": self.media_urls,
            "media_type": self.media_type.value,
            "platform": self.platform.value,
            "target_account_id": self.target_account_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
        }


@dataclass
class PublishResult:
    post_id: str
    platform: SocialPlatform
    status: str  # "SUCCESS", "FAILED"
    permalink: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseSocialClient(ABC):
    """Abstract client for official platform API interactions."""

    def __init__(self, platform: SocialPlatform):
        self.platform = platform

    @abstractmethod
    def generate_auth_url(self, state: str, code_verifier: Optional[str] = None) -> str:
        """Construct official OAuth 2.0 PKCE authorization URL."""
        pass

    @abstractmethod
    async def exchange_code(self, code: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        """Exchange authorization code for tokens."""
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token."""
        pass

    @abstractmethod
    async def publish_post(self, token: str, draft: PostDraft) -> PublishResult:
        """Publish approved draft to the official platform API."""
        pass

    @abstractmethod
    async def get_account_info(self, token: str) -> AccountInfo:
        """Fetch linked account identifier and capabilities."""
        pass
