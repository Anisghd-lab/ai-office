"""Comprehensive tests for Social Media Integrations and OAuth Vault."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.database.connection import db_manager
from app.database.migrations import migration_manager
from app.governance.gateway import ApprovalGateway, ReplayAttackError, UnauthorizedExecutionError
from app.main import app
from app.social.base import AccountStatus, MediaType, PostDraft, SocialPlatform
from app.social.oauth_manager import generate_pkce_pair, OAuthStateManager
from app.social.publisher import SocialPublisher
from app.social.token_vault import TokenVault


@pytest.fixture(autouse=True)
def setup_social_db():
    with db_manager.session() as conn:
        migration_manager.run_migrations(conn)


# ---------------------------------------------------------
# 1. PKCE Generation & CSRF State Validation
# ---------------------------------------------------------
def test_pkce_pair_generation():
    verifier, challenge = generate_pkce_pair()
    assert len(verifier) >= 43
    assert len(challenge) >= 43
    assert verifier != challenge


def test_oauth_state_and_csrf_validation():
    sm = OAuthStateManager(ttl_seconds=60)
    state, _ = sm.create_authorization_session(
        platform=SocialPlatform.TIKTOK,
        code_verifier="test_code_verifier_123",
    )

    # Valid validation
    verifier = sm.validate_callback_state(state, SocialPlatform.TIKTOK)
    assert verifier == "test_code_verifier_123"

    # Replay state -> CSRF protection must reject
    with pytest.raises(ValueError, match="Invalid, unknown, or expired"):
        sm.validate_callback_state(state, SocialPlatform.TIKTOK)

    # Wrong platform -> reject
    state2, _ = sm.create_authorization_session(platform=SocialPlatform.FACEBOOK)
    with pytest.raises(ValueError, match="platform mismatch"):
        sm.validate_callback_state(state2, SocialPlatform.TIKTOK)


# ---------------------------------------------------------
# 2. Token Vault Encryption, Expiration & Disconnect
# ---------------------------------------------------------
def test_token_vault_lifecycle():
    vault = TokenVault()
    # 1. Save valid token
    vault.save_account_tokens(
        platform=SocialPlatform.TIKTOK,
        account_id="tiktok_user_999",
        username="ai_office_official",
        access_token="act_valid_sample_token",
        refresh_token="ref_valid_sample_token",
        expires_in_seconds=3600,
        permissions=["video.upload", "video.publish"],
    )

    info = vault.get_account_info(SocialPlatform.TIKTOK)
    assert info.status == AccountStatus.CONNECTED
    assert info.account_id == "tiktok_user_999"
    assert "video.publish" in info.permissions

    token = vault.get_access_token(SocialPlatform.TIKTOK)
    assert token == "act_valid_sample_token"

    # 2. Simulate Token Expiration
    vault.save_account_tokens(
        platform=SocialPlatform.FACEBOOK,
        account_id="fb_page_123",
        username="ai_office_fb",
        access_token="expired_token",
        expires_in_seconds=-10,  # Expired
    )
    assert vault.get_access_token(SocialPlatform.FACEBOOK) is None
    info_fb = vault.get_account_info(SocialPlatform.FACEBOOK)
    assert info_fb.status == AccountStatus.EXPIRED

    # 3. Disconnect Account
    vault.disconnect_account(SocialPlatform.TIKTOK)
    assert vault.get_access_token(SocialPlatform.TIKTOK) is None
    info_disc = vault.get_account_info(SocialPlatform.TIKTOK)
    assert info_disc.status == AccountStatus.DISCONNECTED


# ---------------------------------------------------------
# 3. Publishing Workflow: Propose -> User Approve -> Execute
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_social_publishing_approval_flow():
    vault = TokenVault()
    vault.save_account_tokens(
        platform=SocialPlatform.TIKTOK,
        account_id="tt-brand-01",
        username="brand_acc",
        access_token="valid_tiktok_secret_token",
        expires_in_seconds=3600,
    )

    publisher = SocialPublisher()
    draft = PostDraft(
        title="AI Office Launch Video",
        caption="Autonomous Multi-Agent Organization controlled from Android 16!",
        hashtags=["#ai", "#android", "#innovation"],
        media_urls=["https://example.com/demo.mp4"],
        media_type=MediaType.VIDEO,
        platform=SocialPlatform.TIKTOK,
    )

    # 1. Marketing agent proposes publication
    req_id = publisher.propose_publication(draft)
    assert req_id.startswith("apr-")

    # 2. Direct execution without User approval MUST fail
    with pytest.raises(UnauthorizedExecutionError):
        await publisher.execute_approved_publication(req_id, draft)

    # 3. Human Owner approves in Android Control Center
    gw = ApprovalGateway()
    gw.approve_action(req_id, comment="Approved for TikTok by Human Owner")

    # 4. Mock TikTok API post response
    mock_post_resp = httpx.Response(
        status_code=200,
        json={"data": {"publish_id": "tt-pub-real-987"}},
        request=httpx.Request("POST", "https://open.tiktokapis.com/v2/post/publish/video/init/"),
    )

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_post_resp)):
        result = await publisher.execute_approved_publication(req_id, draft)
        assert result.status == "SUCCESS"
        assert result.post_id == "tt-pub-real-987"
        assert "tt-pub-real-987" in (result.permalink or "")

    # 5. Replay attempt MUST fail
    with pytest.raises(ReplayAttackError):
        await publisher.execute_approved_publication(req_id, draft)


# ---------------------------------------------------------
# 4. API Endpoints: Social Accounts & Auth URLs
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_social_api_endpoints():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Accounts list
        resp = await client.get("/api/v1/social/accounts")
        assert resp.status_code == 200
        accounts = resp.json()
        assert "tiktok" in accounts
        assert "facebook" in accounts
        assert "instagram" in accounts

        # TikTok Auth URL
        resp_url = await client.get("/api/v1/social/tiktok/auth-url")
        assert resp_url.status_code == 200
        data = resp_url.json()
        assert "tiktok.com" in data["auth_url"]
        assert "code_challenge=" in data["auth_url"]

        # Propose publish via API
        post_payload = {
            "title": "API Test",
            "caption": "Testing API Proposal",
            "hashtags": ["#test"],
            "platform": "facebook",
        }
        resp_prop = await client.post("/api/v1/social/publish", json=post_payload)
        assert resp_prop.status_code == 200
        data_prop = resp_prop.json()
        assert data_prop["status"] == "AWAITING_USER_APPROVAL"
        assert "approval_request_id" in data_prop


# ---------------------------------------------------------
# 5. Talk to AI CEO API
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_talk_to_ai_ceo_api():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Talk to CEO
        chat_req = {"message": "Explore entering the autonomous agent tools market."}
        resp = await client.post("/api/v1/ceo/chat", json=chat_req)
        assert resp.status_code == 200
        chat_data = resp.json()
        assert "reply" in chat_data
        assert len(chat_data["decisions"]) >= 1

        # CEO Profile
        resp_prof = await client.get("/api/v1/ceo/profile")
        assert resp_prof.status_code == 200
        prof_data = resp_prof.json()
        assert "Nova Prime" in prof_data["name"]
        assert prof_data["departments_supervised"] == 8

        # CEO Strategy
        resp_strat = await client.get("/api/v1/ceo/strategy")
        assert resp_strat.status_code == 200
        assert "strategic_pillars" in resp_strat.json()
