"""TikTok OAuth 2.0 PKCE implementation."""

import urllib.parse
from typing import Optional
from app.config import settings
from app.social.base import SocialPlatform
from app.social.oauth_manager import generate_pkce_pair, oauth_state_manager

TIKTOK_AUTH_ENDPOINT = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_SCOPES = ["user.info.basic", "video.upload", "video.publish"]


def build_tiktok_auth_url() -> str:
    """Generate official TikTok authorization URL with PKCE."""
    client_key = settings.TIKTOK_CLIENT_KEY or "dummy-tiktok-client-key"
    redirect_uri = settings.TIKTOK_REDIRECT_URI

    code_verifier, code_challenge = generate_pkce_pair()
    state, _ = oauth_state_manager.create_authorization_session(
        platform=SocialPlatform.TIKTOK,
        code_verifier=code_verifier,
    )

    params = {
        "client_key": client_key,
        "scope": ",".join(TIKTOK_SCOPES),
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{TIKTOK_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"
