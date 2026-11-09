"""Intelligent fallback model router operating exclusively within free tiers."""

import logging
from typing import Any, List, Optional
from app.providers.base import (
    BaseAIProvider,
    GenerationResponse,
    PaidEndpointForbiddenError,
    ProviderAuthenticationError,
    ProviderStatus,
    QuotaExhaustedError,
)
from app.providers.quotas import QuotaTracker

logger = logging.getLogger("ai_office.model_router")


class ModelRouter:
    """Routes generation requests to active free providers with automatic fallback."""

    def __init__(
        self,
        providers: Optional[List[BaseAIProvider]] = None,
        quota_tracker: Optional[QuotaTracker] = None,
    ):
        self.providers: List[BaseAIProvider] = providers or []
        self.quota_tracker = quota_tracker or QuotaTracker()

    def add_provider(self, provider: BaseAIProvider) -> None:
        if provider not in self.providers:
            self.providers.append(provider)

    def set_priority(self, provider_names: List[str]) -> None:
        name_map = {p.name: p for p in self.providers}
        reordered = []
        for name in provider_names:
            if name in name_map:
                reordered.append(name_map[name])
        for p in self.providers:
            if p not in reordered:
                reordered.append(p)
        self.providers = reordered

    async def route_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        preferred_model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> GenerationResponse:
        """Execute generation with automatic zero-cost fallback."""
        if not self.providers:
            raise RuntimeError("No AI providers configured in Model Router.")

        # Build candidate list: preferred first if specified
        candidates = list(self.providers)
        if preferred_provider:
            candidates.sort(key=lambda p: 0 if p.name == preferred_provider else 1)

        errors: List[str] = []

        for provider in candidates:
            # Skip providers currently marked OFFLINE after multiple failures unless preferred
            if (
                provider.health.status == ProviderStatus.OFFLINE
                and provider.health.consecutive_failures >= 3
                and provider.name != preferred_provider
            ):
                continue

            try:
                # Target model determination
                model = preferred_model if provider.name == preferred_provider else None
                response = await provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )
                return response

            except PaidEndpointForbiddenError:
                # Fatal commercial violation - never swallow!
                raise

            except (QuotaExhaustedError, TimeoutError, ProviderAuthenticationError, Exception) as exc:
                err_msg = f"Provider '{provider.name}' failed: {type(exc).__name__}: {str(exc)[:120]}"
                logger.warning(err_msg)
                errors.append(err_msg)
                continue

        error_summary = " | ".join(errors)
        raise RuntimeError(f"All configured free AI providers failed to generate response. Fallback trail: {error_summary}")
