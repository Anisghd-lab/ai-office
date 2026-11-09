"""Social Media API router (OAuth, accounts, publishing)."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from app.api.schemas import TaskCreateRequest
from app.core.security import verify_owner_auth
from app.social.base import AccountInfo, PostDraft, SocialPlatform
from app.social.facebook.auth import build_facebook_auth_url
from app.social.instagram.auth import build_instagram_auth_url
from app.social.publisher import social_publisher
from app.social.tiktok.auth import build_tiktok_auth_url
from app.social.token_vault import token_vault

router = APIRouter(prefix="/social", tags=["Social Media Integrations"])


@router.get("/accounts")
def get_social_accounts():
    """Retrieve status, identifiers, permissions, and token validity for all social channels."""
    return {
        platform.value: {
            "platform": platform.value,
            "status": token_vault.get_account_info(platform).status.value,
            "account_id": token_vault.get_account_info(platform).account_id,
            "username": token_vault.get_account_info(platform).username,
            "permissions": token_vault.get_account_info(platform).permissions,
            "token_expires_at": (
                token_vault.get_account_info(platform).token_expires_at.isoformat()
                if token_vault.get_account_info(platform).token_expires_at
                else None
            ),
            "last_sync": (
                token_vault.get_account_info(platform).last_sync.isoformat()
                if token_vault.get_account_info(platform).last_sync
                else None
            ),
            "capabilities": token_vault.get_account_info(platform).capabilities,
            "requires_business_verification": token_vault.get_account_info(platform).requires_business_verification,
        }
        for platform in SocialPlatform
    }


@router.get("/{platform}/auth-url")
def get_auth_url(platform: str):
    """Initiates official OAuth 2.0 PKCE flow and returns authorization URL."""
    plat_lower = platform.lower()
    if plat_lower == "tiktok":
        return {"platform": "tiktok", "auth_url": build_tiktok_auth_url()}
    elif plat_lower == "facebook":
        return {"platform": "facebook", "auth_url": build_facebook_auth_url()}
    elif plat_lower == "instagram":
        return {"platform": "instagram", "auth_url": build_instagram_auth_url()}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported social platform '{platform}'. Supported: tiktok, facebook, instagram.",
        )


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str = Query(...),
    state: str = Query(...),
):
    """Official OAuth callback handler with CSRF state verification and AES-256 vaulting."""
    from app.social.oauth_manager import oauth_state_manager

    plat_lower = platform.lower()
    try:
        plat_enum = SocialPlatform(plat_lower)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform parameter.")

    # 1. CSRF Validation
    try:
        code_verifier = oauth_state_manager.validate_callback_state(state, plat_enum)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"CSRF State verification failed: {exc}")

    # 2. Token Exchange & Vaulting
    client = social_publisher.clients[plat_enum]
    try:
        token_data = await client.exchange_code(code=code, code_verifier=code_verifier)
    except Exception as exc:
        # In developer mode without real app credentials, provide diagnostics
        raise HTTPException(status_code=400, detail=f"OAuth token exchange error: {exc}")

    access_token = token_data.get("access_token") or "dev_access_token"
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    account_id = token_data.get("open_id") or token_data.get("user_id") or "user_connected"

    token_vault.save_account_tokens(
        platform=plat_enum,
        account_id=str(account_id),
        username=f"connected_{plat_lower}_user",
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in_seconds=expires_in,
        permissions=["basic_publish"],
    )

    return {
        "status": "connected",
        "platform": plat_lower,
        "account_id": account_id,
        "message": f"Successfully authorized and vaulted tokens for {plat_lower}.",
    }


@router.post("/{platform}/disconnect")
def disconnect_account(
    platform: str,
    authorized: bool = Depends(verify_owner_auth),
):
    """Disconnects account and revokes stored tokens."""
    plat_lower = platform.lower()
    try:
        plat_enum = SocialPlatform(plat_lower)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid platform parameter.")

    token_vault.disconnect_account(plat_enum)
    return {"status": "disconnected", "platform": plat_lower}


@router.post("/publish")
def propose_social_publish(
    draft_dict: Dict[str, Any],
    authorized: bool = Depends(verify_owner_auth),
):
    """
    Submits a social post draft.
    Enforces automatic interception into the User Approval Gateway!
    """
    try:
        plat_enum = SocialPlatform(draft_dict["platform"].lower())
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid platform in draft payload.")

    draft = PostDraft(
        title=draft_dict.get("title", "Social Post"),
        caption=draft_dict.get("caption", ""),
        hashtags=draft_dict.get("hashtags", []),
        media_urls=draft_dict.get("media_urls", []),
        platform=plat_enum,
    )

    request_id = social_publisher.propose_publication(draft)
    return {
        "status": "AWAITING_USER_APPROVAL",
        "approval_request_id": request_id,
        "destination": plat_enum.value.upper(),
        "message": "Publication proposed by AI Office. Mandatory Human Owner approval required before release.",
    }
