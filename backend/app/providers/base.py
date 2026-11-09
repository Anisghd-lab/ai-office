"""Base abstractions for AI Office Free-Tier Providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class ProviderStatus(str, Enum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    RATE_LIMITED = "RATE_LIMITED"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class PaidEndpointForbiddenError(Exception):
    """Raised when an attempt is made to use a paid model or billable endpoint."""
    pass


class QuotaExhaustedError(Exception):
    """Raised when a provider's free-tier rate limit or quota is exhausted."""
    pass


class ProviderAuthenticationError(Exception):
    """Raised when authentication credentials for a provider fail."""
    pass


@dataclass
class ModelInfo:
    id: str
    name: str
    is_free: bool = True
    context_window: int = 8192
    max_output_tokens: int = 4096
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0

    def validate_zero_cost(self) -> None:
        if not self.is_free or self.cost_per_1k_input > 0.0 or self.cost_per_1k_output > 0.0:
            raise PaidEndpointForbiddenError(
                f"Model '{self.id}' violates the zero-cost commercial constraint! Cost must be 0.0."
            )


@dataclass
class ProviderHealth:
    provider_name: str
    status: ProviderStatus = ProviderStatus.UNKNOWN
    latency_ms: float = 0.0
    last_checked: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    consecutive_failures: int = 0


@dataclass
class GenerationResponse:
    content: str
    provider: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0
    cost: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.cost > 0.0:
            raise PaidEndpointForbiddenError("Execution generated a non-zero financial cost.")


class BaseAIProvider(ABC):
    """Abstract Base Class for AI Providers in AI Office."""

    def __init__(self, name: str, base_url: str, api_key: Optional[str] = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key or ""
        self._health = ProviderHealth(provider_name=name)

    @property
    def health(self) -> ProviderHealth:
        return self._health

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> GenerationResponse:
        """Generate a completion from the provider using strictly free models."""
        pass

    @abstractmethod
    async def check_health(self) -> ProviderHealth:
        """Probe connectivity and latency."""
        pass

    @abstractmethod
    async def get_available_models(self) -> List[ModelInfo]:
        """Return list of free models available under this provider."""
        pass
