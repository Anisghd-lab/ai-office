"""Instagram Graph API OAuth 2.0 implementation."""

import urllib.parse
from app.config import settings
from app.social.base import SocialPlatform
from app.social.oauth_manager import oauth_state_manager

IG_AUTH_ENDPOINT = "https://www.facebook.com/v21.0/dialog/oauth"
IG_SCOPES = ["instagram_basic", "instagram_content_publish", "pages_read_engagement"]


def build_instagram_auth_url() -> str:
    app_id = settings.INSTAGRAM_CLIENT_ID or settings.FACEBOOK_APP_ID or "dummy-ig-client-id"
    redirect_uri = settings.INSTAGRAM_REDIRECT_URI

    state, _ = oauth_state_manager.create_authorization_session(platform=SocialPlatform.INSTAGRAM)
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": ",".join(IG_SCOPES),
        "response_type": "code",
    }
    return f"{IG_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"
