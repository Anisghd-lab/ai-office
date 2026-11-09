"""Facebook OAuth 2.0 implementation for Pages API."""

import urllib.parse
from app.config import settings
from app.social.base import SocialPlatform
from app.social.oauth_manager import oauth_state_manager

FB_AUTH_ENDPOINT = "https://www.facebook.com/v21.0/dialog/oauth"
FB_SCOPES = ["pages_manage_posts", "pages_read_engagement"]


def build_facebook_auth_url() -> str:
    app_id = settings.FACEBOOK_APP_ID or "dummy-fb-app-id"
    redirect_uri = settings.FACEBOOK_REDIRECT_URI

    state, _ = oauth_state_manager.create_authorization_session(platform=SocialPlatform.FACEBOOK)
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": ",".join(FB_SCOPES),
        "response_type": "code",
    }
    return f"{FB_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"
