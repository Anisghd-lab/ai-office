"""Google and YouTube capabilities and quota specifications."""

def get_google_capabilities() -> dict:
    return {
        "platform": "Google Account",
        "api_name": "Google Identity & OAuth 2.0 PKCE",
        "supported_media": ["TEXT"],
        "required_scopes": [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        "requires_verification": False,
        "direct_publishing_supported": False,
        "features": ["identity_verification", "profile_read", "email_read"],
    }


def get_youtube_capabilities() -> dict:
    return {
        "platform": "YouTube",
        "api_name": "YouTube Data API v3",
        "supported_media": ["VIDEO"],
        "min_duration_seconds": 1,
        "max_duration_seconds": 43200,
        "required_scopes": [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.upload",
        ],
        "requires_verification": True,
        "direct_publishing_supported": True,
        "features": ["channel_read", "analytics_read", "video_upload", "shorts_publishing"],
    }
