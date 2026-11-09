"""Comprehensive tests for AI Office Free-Tier Provider Architecture."""

import os
import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.providers.base import (
    GenerationResponse,
    ModelInfo,
    PaidEndpointForbiddenError,
    ProviderAuthenticationError,
    ProviderStatus,
    QuotaExhaustedError,
)
from app.providers.discovery import ProviderDiscovery, mask_secret, redact_text
from app.providers.health import ProviderHealthMonitor
from app.providers.model_router import ModelRouter
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.quotas import QuotaTracker, is_rate_limit_error
from app.providers.registry import ProviderRegistry


# ---------------------------------------------------------
# 1. Provider Discovery Tests
# ---------------------------------------------------------
def test_provider_discovery_from_env():
    with patch.dict(os.environ, {
        "OPENROUTER_API_KEY": "sk-or-v1-dummysecrettoken12345678",
        "GROQ_API_KEY": "gsk_dummygroqtokenabcdef123456",
        "LOCAL_OPENAI_BASE_URL": "http://127.0.0.1:11434/v1",
    }):
        tracker = QuotaTracker()
        discovery = ProviderDiscovery(quota_tracker=tracker)
        providers = discovery.discover_all()
        names = [p.name for p in providers]

        assert "openrouter" in names
        assert "groq" in names
        assert "local" in names

        audit = discovery.get_discovery_audit()
        assert audit["openrouter"]["configured"] is True
        assert "dummysecrettoken" not in audit["openrouter"]["masked_key"]
        assert audit["groq"]["configured"] is True


def test_secret_masking_and_redaction():
    secret = "sk-live-1234567890abcdef"
    masked = mask_secret(secret)
    assert masked.startswith("sk-l")
    assert masked.endswith("cdef")
    assert "1234567890" not in masked

    assert mask_secret(None) == "[NOT_CONFIGURED]"
    assert mask_secret("") == "[NOT_CONFIGURED]"
    assert mask_secret("short") == "[REDACTED]"

    sample_log = f"Request failed with key {secret} on endpoint https://api.example.com"
    redacted = redact_text(sample_log, [secret])
    assert secret not in redacted
    assert "[REDACTED_API_KEY]" in redacted


# ---------------------------------------------------------
# 2. Zero-Cost Commercial Constraint Tests
# ---------------------------------------------------------
def test_model_zero_cost_validation():
    free_model = ModelInfo(id="free-llama", name="Free Llama", is_free=True, cost_per_1k_input=0.0)
    free_model.validate_zero_cost()  # Should not raise

    paid_model_1 = ModelInfo(id="paid-gpt", name="Paid GPT", is_free=False)
    with pytest.raises(PaidEndpointForbiddenError):
        paid_model_1.validate_zero_cost()

    paid_model_2 = ModelInfo(id="subsidized-model", name="Subsidized", is_free=True, cost_per_1k_input=0.002)
    with pytest.raises(PaidEndpointForbiddenError):
        paid_model_2.validate_zero_cost()


def test_generation_response_cost_check():
    # Valid free response
    res = GenerationResponse(content="OK", provider="mock", model="m", cost=0.0)
    assert res.cost == 0.0

    # Illegal response with non-zero cost
    with pytest.raises(PaidEndpointForbiddenError):
        GenerationResponse(content="OK", provider="mock", model="m", cost=0.05)


# ---------------------------------------------------------
# 3. Authentication Handling Tests
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_authentication_error_handling():
    provider = OpenAICompatibleProvider(
        name="test_auth",
        base_url="https://api.test.com/v1",
        api_key="invalid-key",
        free_models=[ModelInfo(id="test:free", name="Test Free")],
    )

    mock_resp = httpx.Response(
        status_code=401,
        json={"error": {"message": "Invalid API Key"}},
        request=httpx.Request("POST", "https://api.test.com/v1/chat/completions"),
    )

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
        with pytest.raises(ProviderAuthenticationError):
            await provider.generate("Hello world")

        assert provider.health.status == ProviderStatus.DEGRADED
        assert "Auth failure" in (provider.health.error_message or "")


# ---------------------------------------------------------
# 4. Timeout Handling Tests
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_timeout_handling():
    provider = OpenAICompatibleProvider(
        name="test_timeout",
        base_url="https://api.test.com/v1",
        api_key="valid-key",
        free_models=[ModelInfo(id="test:free", name="Test Free")],
        timeout_seconds=0.1,
    )

    with patch("httpx.AsyncClient.post", new=AsyncMock(side_effect=httpx.TimeoutException("Read timed out"))):
        with pytest.raises(TimeoutError):
            await provider.generate("Test prompt")

        assert provider.health.status == ProviderStatus.DEGRADED
        assert "Timeout" in (provider.health.error_message or "")


# ---------------------------------------------------------
# 5. Invalid Response Handling Tests
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_invalid_and_empty_response():
    provider = OpenAICompatibleProvider(
        name="test_invalid",
        base_url="https://api.test.com/v1",
        free_models=[ModelInfo(id="test:free", name="Test Free")],
    )

    # Empty choices array
    mock_resp = httpx.Response(
        status_code=200,
        json={"choices": []},
        request=httpx.Request("POST", "https://api.test.com/v1/chat/completions"),
    )

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
        with pytest.raises(ValueError, match="Empty choices"):
            await provider.generate("Test prompt")


# ---------------------------------------------------------
# 6. Quota Exhaustion & Rate Limit Detection Tests
# ---------------------------------------------------------
def test_rate_limit_detection_helper():
    assert is_rate_limit_error(429, "") is True
    assert is_rate_limit_error(200, "rate limit exceeded for model") is True
    assert is_rate_limit_error(500, "RESOURCE_EXHAUSTED: quota reached") is True
    assert is_rate_limit_error(200, "all good") is False


@pytest.mark.asyncio
async def test_quota_exhaustion_and_preflight():
    tracker = QuotaTracker(rpm_limit=2)
    provider = OpenAICompatibleProvider(
        name="test_quota",
        base_url="https://api.test.com/v1",
        free_models=[ModelInfo(id="test:free", name="Test Free")],
        quota_tracker=tracker,
    )

    # Simulate 2 quick requests
    tracker.record_request_start("test_quota")
    tracker.record_request_start("test_quota")

    # 3rd request should fail preflight
    with pytest.raises(QuotaExhaustedError, match="exceeded pre-flight RPM limit"):
        await provider.generate("Hello")


# ---------------------------------------------------------
# 7. Model Router Fallback Tests
# ---------------------------------------------------------
@pytest.mark.asyncio
async def test_model_router_fallback():
    tracker = QuotaTracker()
    p1 = OpenAICompatibleProvider(
        name="p1_primary",
        base_url="https://api.p1.com/v1",
        free_models=[ModelInfo(id="m1:free", name="M1 Free")],
        quota_tracker=tracker,
    )
    p2 = OpenAICompatibleProvider(
        name="p2_fallback",
        base_url="https://api.p2.com/v1",
        free_models=[ModelInfo(id="m2:free", name="M2 Free")],
        quota_tracker=tracker,
    )

    # Mock p1 failing with 429
    resp_429 = httpx.Response(
        status_code=429,
        text="Rate limit exceeded",
        request=httpx.Request("POST", "https://api.p1.com/v1/chat/completions"),
    )

    # Mock p2 succeeding
    resp_success = httpx.Response(
        status_code=200,
        json={
            "choices": [{"message": {"content": "Fallback answer from p2"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        },
        request=httpx.Request("POST", "https://api.p2.com/v1/chat/completions"),
    )

    router = ModelRouter(providers=[p1, p2], quota_tracker=tracker)

    async def mock_post(url, *args, **kwargs):
        if "api.p1.com" in str(url):
            return resp_429
        return resp_success

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        result = await router.route_generate(prompt="Explain quantum physics")
        assert result.provider == "p2_fallback"
        assert result.content == "Fallback answer from p2"
        assert p1.health.status == ProviderStatus.RATE_LIMITED


# ---------------------------------------------------------
# 8. Registry Integration
# ---------------------------------------------------------
def test_provider_registry_integration():
    registry = ProviderRegistry()
    assert len(registry.list_all()) == 0

    p = OpenAICompatibleProvider(
        name="reg_test",
        base_url="http://127.0.0.1:11434/v1",
        free_models=[ModelInfo(id="m:free", name="M")],
    )
    registry.register(p)

    assert registry.get("reg_test") is p
    overview = registry.get_status_overview()
    assert "health" in overview
    assert "quotas" in overview
    assert "reg_test" in overview["health"]
