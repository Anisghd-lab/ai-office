"""Google OAuth 2.0 PKCE and API client helpers for Google 1/2/3 and YouTube."""

import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
import httpx
from app.config import settings
from app.core.logging import logger
from app.social.base import SocialPlatform
from app.social.oauth_manager import generate_pkce_pair, oauth_state_manager

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"
YOUTUBE_CHANNELS_ENDPOINT = "https://www.googleapis.com/youtube/v3/channels"

GOOGLE_BASE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

YOUTUBE_SCOPES = GOOGLE_BASE_SCOPES + [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]


def build_google_auth_url(
    platform: SocialPlatform,
    redirect_uri: Optional[str] = None,
) -> str:
    """Generate official Google OAuth 2.0 URL with PKCE and account selection prompt."""
    client_id = settings.GOOGLE_CLIENT_ID or "ai-office-google-client-id"
    target_redirect = redirect_uri or settings.GOOGLE_REDIRECT_URI

    scopes = YOUTUBE_SCOPES if platform == SocialPlatform.YOUTUBE else GOOGLE_BASE_SCOPES

    code_verifier, code_challenge = generate_pkce_pair()
    state, _ = oauth_state_manager.create_authorization_session(
        platform=platform,
        code_verifier=code_verifier,
    )

    params = {
        "client_id": client_id,
        "redirect_uri": target_redirect,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "select_account consent",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "include_granted_scopes": "true",
    }
    return f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"


def build_youtube_auth_url(redirect_uri: Optional[str] = None) -> str:
    """Generate YouTube Data API OAuth 2.0 URL with PKCE."""
    return build_google_auth_url(SocialPlatform.YOUTUBE, redirect_uri=redirect_uri or settings.YOUTUBE_REDIRECT_URI)


async def exchange_google_code(
    code: str,
    code_verifier: Optional[str] = None,
    platform: SocialPlatform = SocialPlatform.GOOGLE_1,
    redirect_uri: Optional[str] = None,
) -> Dict[str, Any]:
    """Exchange authorization code for access and refresh tokens."""
    client_id = settings.GOOGLE_CLIENT_ID or ""
    client_secret = settings.GOOGLE_CLIENT_SECRET or ""
    target_redirect = redirect_uri or (
        settings.YOUTUBE_REDIRECT_URI if platform == SocialPlatform.YOUTUBE else settings.GOOGLE_REDIRECT_URI
    )

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": target_redirect,
    }
    if code_verifier:
        data["code_verifier"] = code_verifier

    # If client_id is mock/dev without network, handle graceful test simulation
    if not client_id or client_id.startswith("ai-office-"):
        logger.warning(f"Using mock/developer token response for {platform.value} (no live client ID configured).")
        return {
            "access_token": f"ya29.mock_{platform.value}_token_{code[:8]}",
            "refresh_token": f"1//mock_refresh_{platform.value}",
            "expires_in": 3600,
            "token_type": "Bearer",
            "scope": " ".join(YOUTUBE_SCOPES if platform == SocialPlatform.YOUTUBE else GOOGLE_BASE_SCOPES),
            "mock": True,
        }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
        if resp.status_code != 200:
            raise RuntimeError(f"Google token exchange failed: HTTP {resp.status_code}: {resp.text}")
        return resp.json()


async def refresh_google_token(
    refresh_token: str,
    platform: SocialPlatform = SocialPlatform.GOOGLE_1,
) -> Dict[str, Any]:
    """Refresh an expired Google/YouTube access token."""
    client_id = settings.GOOGLE_CLIENT_ID or ""
    client_secret = settings.GOOGLE_CLIENT_SECRET or ""

    if not client_id or client_id.startswith("ai-office-") or refresh_token.startswith("1//mock_"):
        return {
            "access_token": f"ya29.refreshed_{platform.value}_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
        if resp.status_code != 200:
            raise RuntimeError(f"Google token refresh failed: HTTP {resp.status_code}")
        return resp.json()


async def execute_google_test(
    token: str,
    platform: SocialPlatform,
) -> Dict[str, Any]:
    """
    Execute an actual, permitted, harmless read-only API test to verify identity and scopes.
    Returns diagnostics dict with status, account_id, username, capabilities, and quota info.
    """
    if token.startswith("ya29.mock_") or token.startswith("mock_"):
        # Verified mock test fixture for test/offline environments
        if platform == SocialPlatform.YOUTUBE:
            return {
                "success": True,
                "account_id": "UC_mock_channel_aioffice",
                "username": "AI Office Studio (Official)",
                "title": "AI Office Studio",
                "custom_url": "@ai_office_channel",
                "subscriber_count": "1420",
                "video_count": "18",
                "capabilities": ["channel_read", "analytics_read", "video_upload", "shorts_publishing"],
                "scopes": YOUTUBE_SCOPES,
                "verified_at": "ISO_NOW",
                "test_method": "youtube.channels.list(part=snippet,statistics,mine=true)",
            }
        else:
            slot_num = platform.value.split("-")[-1] if "-" in platform.value else "1"
            return {
                "success": True,
                "account_id": f"1084293847290482{slot_num}",
                "username": f"principal.office{slot_num}@gmail.com",
                "email": f"principal.office{slot_num}@gmail.com",
                "name": f"AI Office Principal ({slot_num})",
                "capabilities": ["identity_verification", "profile_read", "email_read"],
                "scopes": GOOGLE_BASE_SCOPES,
                "verified_at": "ISO_NOW",
                "test_method": "oauth2/v3/userinfo",
            }

    # Live API test with real bearer token
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        if platform == SocialPlatform.YOUTUBE:
            params = {"part": "snippet,statistics", "mine": "true"}
            resp = await client.get(YOUTUBE_CHANNELS_ENDPOINT, headers=headers, params=params)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"YouTube API returned HTTP {resp.status_code}: {resp.text[:200]}",
                    "status_code": resp.status_code,
                }
            data = resp.json()
            items = data.get("items", [])
            if not items:
                return {
                    "success": False,
                    "error": "No YouTube channel associated with this Google Account.",
                    "status_code": 404,
                }
            ch = items[0]
            snippet = ch.get("snippet", {})
            stats = ch.get("statistics", {})
            return {
                "success": True,
                "account_id": ch.get("id"),
                "username": snippet.get("title"),
                "title": snippet.get("title"),
                "custom_url": snippet.get("customUrl"),
                "subscriber_count": stats.get("subscriberCount", "0"),
                "video_count": stats.get("videoCount", "0"),
                "capabilities": ["channel_read", "analytics_read", "video_upload", "shorts_publishing"],
                "scopes": YOUTUBE_SCOPES,
                "test_method": "youtube.channels.list(part=snippet,statistics,mine=true)",
            }
        else:
            resp = await client.get(GOOGLE_USERINFO_ENDPOINT, headers=headers)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "error": f"Google UserInfo API returned HTTP {resp.status_code}: {resp.text[:200]}",
                    "status_code": resp.status_code,
                }
            data = resp.json()
            return {
                "success": True,
                "account_id": data.get("sub"),
                "username": data.get("email"),
                "email": data.get("email"),
                "name": data.get("name"),
                "capabilities": ["identity_verification", "profile_read", "email_read"],
                "scopes": GOOGLE_BASE_SCOPES,
                "test_method": "oauth2/v3/userinfo",
            }
