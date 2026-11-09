"""Central Registry for AI Office Free Providers."""

from typing import Dict, List, Optional
from app.providers.base import BaseAIProvider, ModelInfo
from app.providers.discovery import ProviderDiscovery
from app.providers.health import ProviderHealthMonitor
from app.providers.model_router import ModelRouter
from app.providers.quotas import QuotaTracker


class ProviderRegistry:
    """Manages the lifecycle, quotas, and routing of all registered AI providers."""

    def __init__(self):
        self.quota_tracker = QuotaTracker()
        self.discovery = ProviderDiscovery(quota_tracker=self.quota_tracker)
        self.health_monitor = ProviderHealthMonitor()
        self.router = ModelRouter(quota_tracker=self.quota_tracker)
        self._providers: Dict[str, BaseAIProvider] = {}
        self._initialized = False

    def initialize(self) -> None:
        """Autodiscover providers from environment."""
        if self._initialized:
            return
        discovered = self.discovery.discover_all()
        for p in discovered:
            self.register(p)
        self._initialized = True

    def register(self, provider: BaseAIProvider) -> None:
        self._providers[provider.name] = provider
        self.health_monitor.register(provider)
        self.router.add_provider(provider)

    def get(self, name: str) -> Optional[BaseAIProvider]:
        return self._providers.get(name)

    def list_all(self) -> List[BaseAIProvider]:
        return list(self._providers.values())

    async def get_all_models(self) -> Dict[str, List[ModelInfo]]:
        res = {}
        for name, provider in self._providers.items():
            res[name] = await provider.get_available_models()
        return res

    def get_status_overview(self) -> dict:
        return {
            "health": self.health_monitor.get_summary(),
            "quotas": self.quota_tracker.get_summary(),
            "discovery": self.discovery.get_discovery_audit(),
        }


# Global registry singleton
provider_registry = ProviderRegistry()
