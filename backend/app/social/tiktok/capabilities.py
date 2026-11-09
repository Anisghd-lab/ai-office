"""TikTok API capabilities and eligibility constraints."""

def get_tiktok_capabilities() -> dict:
    return {
        "platform": "TikTok",
        "api_name": "TikTok Content Posting API v2",
        "supported_media": ["VIDEO"],
        "min_duration_seconds": 3,
        "max_duration_seconds": 600,
        "required_scopes": ["user.info.basic", "video.upload", "video.publish"],
        "requires_app_review": True,
        "direct_publishing_supported": True,
    }
