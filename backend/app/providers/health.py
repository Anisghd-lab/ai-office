"""Health monitoring and latency telemetry for AI Office providers."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.providers.base import BaseAIProvider, ProviderHealth, ProviderStatus


class ProviderHealthMonitor:
    """Manages active health checks and latency recording across providers."""

    def __init__(self, providers: Optional[List[BaseAIProvider]] = None):
        self.providers: Dict[str, BaseAIProvider] = {
            p.name: p for p in (providers or [])
        }

    def register(self, provider: BaseAIProvider) -> None:
        self.providers[provider.name] = provider

    def unregister(self, provider_name: str) -> None:
        self.providers.pop(provider_name, None)

    async def check_provider(self, provider_name: str) -> ProviderHealth:
        provider = self.providers.get(provider_name)
        if not provider:
            return ProviderHealth(
                provider_name=provider_name,
                status=ProviderStatus.OFFLINE,
                error_message="Provider not registered",
            )
        return await provider.check_health()

    async def check_all(self) -> Dict[str, ProviderHealth]:
        tasks = [p.check_health() for p in self.providers.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        health_map = {}
        for provider, res in zip(self.providers.values(), results):
            if isinstance(res, Exception):
                health_map[provider.name] = ProviderHealth(
                    provider_name=provider.name,
                    status=ProviderStatus.OFFLINE,
                    error_message=str(res)[:100],
                )
            else:
                health_map[provider.name] = res
        return health_map

    def get_summary(self) -> Dict[str, dict]:
        summary = {}
        for name, provider in self.providers.items():
            h = provider.health
            summary[name] = {
                "status": h.status.value,
                "latency_ms": round(h.latency_ms, 2),
                "last_checked": h.last_checked.isoformat(),
                "error_message": h.error_message,
                "consecutive_failures": h.consecutive_failures,
            }
        return summary
