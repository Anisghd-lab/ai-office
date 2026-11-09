"""OpenAI-compatible client adapter for free tiers (OpenRouter, Groq, Local Ollama, etc.)."""

import time
from typing import Any, Dict, List, Optional
import httpx

from app.providers.base import (
    BaseAIProvider,
    GenerationResponse,
    ModelInfo,
    PaidEndpointForbiddenError,
    ProviderAuthenticationError,
    ProviderHealth,
    ProviderStatus,
    QuotaExhaustedError,
)
from app.providers.quotas import QuotaTracker, is_rate_limit_error


class OpenAICompatibleProvider(BaseAIProvider):
    """Client for any OpenAI-compatible completions API operating strictly in free mode."""

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        free_models: Optional[List[ModelInfo]] = None,
        default_model: Optional[str] = None,
        quota_tracker: Optional[QuotaTracker] = None,
        timeout_seconds: float = 30.0,
    ):
        super().__init__(name=name, base_url=base_url.rstrip("/"), api_key=api_key)
        self.free_models: Dict[str, ModelInfo] = {
            m.id: m for m in (free_models or [])
        }
        self.default_model = default_model or (list(self.free_models.keys())[0] if self.free_models else "")
        self.quota_tracker = quota_tracker or QuotaTracker()
        self.timeout_seconds = timeout_seconds

    def add_free_model(self, model: ModelInfo) -> None:
        model.validate_zero_cost()
        self.free_models[model.id] = model
        if not self.default_model:
            self.default_model = model.id

    async def get_available_models(self) -> List[ModelInfo]:
        return list(self.free_models.values())

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> GenerationResponse:
        target_model = model or self.default_model
        if not target_model:
            raise ValueError(f"No free model configured for provider {self.name}.")

        # Enforce zero-cost model check
        if target_model in self.free_models:
            self.free_models[target_model].validate_zero_cost()
        else:
            # If not pre-registered, verify it doesn't violate free naming (e.g. OpenRouter :free)
            if not target_model.endswith(":free") and not self.base_url.startswith("http://127.0.0.1"):
                raise PaidEndpointForbiddenError(
                    f"Model '{target_model}' is not registered as a zero-cost free model on provider '{self.name}'."
                )

        self.quota_tracker.check_preflight_quota(self.name)
        self.quota_tracker.record_request_start(self.name)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": target_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

            latency_ms = (time.time() - start_time) * 1000.0

            if response.status_code in (401, 403):
                self._health.status = ProviderStatus.DEGRADED
                self._health.error_message = f"Auth failure: HTTP {response.status_code}"
                self.quota_tracker.record_failure(self.name)
                raise ProviderAuthenticationError(
                    f"Authentication failed for provider '{self.name}' (HTTP {response.status_code})."
                )

            if is_rate_limit_error(response.status_code, response.text):
                self._health.status = ProviderStatus.RATE_LIMITED
                self._health.error_message = "Rate limit / Quota exceeded"
                self.quota_tracker.record_rate_limit(self.name)
                raise QuotaExhaustedError(
                    f"Free quota exhausted / rate limit reached on provider '{self.name}': {response.text[:200]}"
                )

            if response.status_code >= 400:
                self._health.status = ProviderStatus.DEGRADED
                self._health.error_message = f"HTTP {response.status_code}: {response.text[:100]}"
                self.quota_tracker.record_failure(self.name)
                raise RuntimeError(
                    f"Provider '{self.name}' returned HTTP {response.status_code}: {response.text[:200]}"
                )

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise ValueError(f"Empty choices in response from {self.name}")

            content = choices[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            tokens_in = usage.get("prompt_tokens", 0)
            tokens_out = usage.get("completion_tokens", 0)

            self.quota_tracker.record_success(
                provider_name=self.name,
                input_tokens=tokens_in,
                output_tokens=tokens_out,
                latency_ms=latency_ms,
                cost=0.0,
            )

            self._health.status = ProviderStatus.ONLINE
            self._health.latency_ms = latency_ms
            self._health.consecutive_failures = 0
            self._health.error_message = None

            return GenerationResponse(
                content=content,
                provider=self.name,
                model=target_model,
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                latency_ms=latency_ms,
                cost=0.0,
            )

        except (httpx.TimeoutException, TimeoutError) as exc:
            self._health.consecutive_failures += 1
            if self._health.consecutive_failures >= 3:
                self._health.status = ProviderStatus.OFFLINE
            else:
                self._health.status = ProviderStatus.DEGRADED
            self._health.error_message = f"Timeout after {self.timeout_seconds}s"
            self.quota_tracker.record_failure(self.name)
            raise TimeoutError(f"Request to '{self.name}' timed out.") from exc
        except (ProviderAuthenticationError, QuotaExhaustedError, PaidEndpointForbiddenError):
            raise
        except Exception as exc:
            self._health.consecutive_failures += 1
            self._health.status = ProviderStatus.DEGRADED
            self._health.error_message = str(exc)[:200]
            self.quota_tracker.record_failure(self.name)
            raise

    async def check_health(self) -> ProviderHealth:
        start_time = time.time()
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(f"{self.base_url}/models", headers=headers)
                latency_ms = (time.time() - start_time) * 1000.0
                if res.status_code in (200, 204):
                    self._health.status = ProviderStatus.ONLINE
                    self._health.latency_ms = latency_ms
                    self._health.consecutive_failures = 0
                    self._health.error_message = None
                elif res.status_code in (401, 403):
                    self._health.status = ProviderStatus.DEGRADED
                    self._health.latency_ms = latency_ms
                    self._health.error_message = "Authentication invalid"
                elif res.status_code == 429:
                    self._health.status = ProviderStatus.RATE_LIMITED
                    self._health.latency_ms = latency_ms
                    self._health.error_message = "Rate limited"
                else:
                    self._health.status = ProviderStatus.DEGRADED
                    self._health.latency_ms = latency_ms
                    self._health.error_message = f"HTTP {res.status_code}"
        except Exception as exc:
            self._health.status = ProviderStatus.OFFLINE
            self._health.error_message = str(exc)[:200]
        return self._health
