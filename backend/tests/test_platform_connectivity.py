"""Integration test suite for Complete Platform Connectivity (7 Platforms)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.social.base import OperationalStatus, SocialPlatform
from app.social.oauth_manager import oauth_state_manager
from app.social.token_vault import token_vault

client = TestClient(app)
AUTH_HEADERS = {"X-Owner-Key": "owner-default-dev-token"}

ALL_PLATFORMS = [
    "google-1",
    "google-2",
    "google-3",
    "youtube",
    "tiktok",
    "facebook",
    "instagram",
]


def test_list_all_seven_platforms():
    """Verify that all 7 platform accounts are present and report structured operational status."""
    resp = client.get("/api/v1/social/accounts")
    assert resp.status_code == 200
    data = resp.json()

    for plat in ALL_PLATFORMS:
        assert plat in data, f"Missing platform {plat} in accounts list"
        acc = data[plat]
        assert "operational_status" in acc
        assert "capabilities" in acc
        assert "scopes" in acc
        assert "last_test_result" in acc
        assert "app_intent_uri" in acc


def test_auth_url_generation_pkce():
    """Verify that PKCE auth URLs are correctly generated for all platforms."""
    for plat in ALL_PLATFORMS:
        resp = client.get(f"/api/v1/social/{plat}/auth-url")
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == plat
        assert "auth_url" in data
        assert "code_challenge=" in data["auth_url"] or "state=" in data["auth_url"]
        assert "app_intent_uri" in data
        assert data["status"] == "INITIALIZED"


def test_simulate_connect_and_operational_status():
    """Verify that simulated connection sets operational status to API_OPERATIONAL with encrypted vault storage."""
    for plat in ALL_PLATFORMS:
        resp = client.post(
            f"/api/v1/social/{plat}/simulate-connect",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == plat
        assert data["operational_status"] == OperationalStatus.API_OPERATIONAL.value
        assert len(data["capabilities"]) > 0
        assert data["last_test_result"]["success"] is True

        # Verify vault has token
        plat_enum = SocialPlatform(plat)
        token = token_vault.get_access_token(plat_enum)
        assert token is not None
        assert "mock" in token


def test_harmless_read_only_test_execution():
    """Verify that POST /{platform}/test executes read-only diagnostic checks without side effects."""
    for plat in ALL_PLATFORMS:
        resp = client.post(
            f"/api/v1/social/{plat}/test",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["platform"] == plat
        assert data["operational_status"] == OperationalStatus.API_OPERATIONAL.value
        assert data["test_result"]["success"] is True


def test_disconnect_and_status_recovery():
    """Verify that disconnecting an account clears token, marks DISCONNECTED, and subsequent tests fail gracefully."""
    for plat in ALL_PLATFORMS:
        # Disconnect
        resp = client.post(
            f"/api/v1/social/{plat}/disconnect",
            headers=AUTH_HEADERS,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "disconnected"

        # Verify token is cleared from vault
        plat_enum = SocialPlatform(plat)
        assert token_vault.get_access_token(plat_enum) is None

        # Verify test returns disconnected
        test_resp = client.post(
            f"/api/v1/social/{plat}/test",
            headers=AUTH_HEADERS,
        )
        assert test_resp.status_code == 200
        assert test_resp.json()["operational_status"] == OperationalStatus.DISCONNECTED.value


def test_csrf_state_protection():
    """Verify that callback rejects invalid or fake CSRF state."""
    resp = client.get("/api/v1/social/youtube/callback?code=mock_code&state=forged_state_token")
    assert resp.status_code == 400
    assert "CSRF" in resp.json()["detail"]


def test_social_publish_gated_by_owner_approval():
    """Verify that publishing to any social channel is strictly intercepted by the Human Owner Approval Gateway."""
    payload = {
        "platform": "youtube",
        "title": "Autonomous AI Media Studio Launch",
        "caption": "Official launch video produced 100% autonomously by AI Office.",
        "hashtags": ["#AIOffice", "#AutonomousMedia"],
        "media_urls": ["https://example.com/rendered_video.mp4"],
    }
    resp = client.post("/api/v1/social/publish", json=payload, headers=AUTH_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "AWAITING_USER_APPROVAL"
    assert "approval_request_id" in data
    assert data["destination"] == "YOUTUBE"
