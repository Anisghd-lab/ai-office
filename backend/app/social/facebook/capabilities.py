"""Facebook Pages API capabilities and constraints."""

def get_facebook_capabilities() -> dict:
    return {
        "platform": "Facebook",
        "api_name": "Meta Graph API v21.0 Pages Feed",
        "supported_media": ["TEXT", "IMAGE", "VIDEO"],
        "required_scopes": ["pages_manage_posts", "pages_read_engagement"],
        "requires_page_admin": True,
        "direct_publishing_supported": True,
    }
