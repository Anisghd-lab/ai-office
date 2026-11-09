"""Publication calendar and scheduling module."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.social.base import PostDraft, SocialPlatform
from app.social.publisher import social_publisher


class PublicationScheduler:
    """Maintains planned editorial calendar and routes drafts into User Approval Gateway."""

    def __init__(self):
        self.scheduled_calendar: List[Dict[str, Any]] = []

    def schedule_draft(self, draft: PostDraft, scheduled_time: datetime) -> str:
        draft.scheduled_at = scheduled_time
        request_id = social_publisher.propose_publication(draft)
        self.scheduled_calendar.append({
            "request_id": request_id,
            "platform": draft.platform.value,
            "title": draft.title,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "AWAITING_USER_APPROVAL",
        })
        return request_id

    def list_calendar(self) -> List[Dict[str, Any]]:
        return list(self.scheduled_calendar)


publication_scheduler = PublicationScheduler()
