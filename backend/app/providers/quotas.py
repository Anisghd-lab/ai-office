"""Free Quota and Rate Limit Tracker for AI Office Providers."""

import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.providers.base import PaidEndpointForbiddenError, QuotaExhaustedError


RATE_LIMIT_PATTERNS = [
    re.compile(r"rate[_\s-]?limit", re.IGNORECASE),
    re.compile(r"quota[_\s-]?exceeded", re.IGNORECASE),
    re.compile(r"resource[_\s-]?exhausted", re.IGNORECASE),
    re.compile(r"too many requests", re.IGNORECASE),
    re.compile(r"429", re.IGNORECASE),
    re.compile(r"tokens per minute", re.IGNORECASE),
    re.compile(r"requests per minute", re.IGNORECASE),
]


def is_rate_limit_error(status_code: int, error_message: str) -> bool:
    """Detect if an HTTP status or error payload signals a quota or rate-limit event."""
    if status_code == 429:
        return True
    for pattern in RATE_LIMIT_PATTERNS:
        if pattern.search(error_message):
            return True
    return False


@dataclass
class ProviderUsageMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    recent_latencies_ms: List[float] = field(default_factory=list)
    request_timestamps: List[float] = field(default_factory=list)


class QuotaTracker:
    """Thread-safe / Async in-memory quota tracking for free-tier providers."""

    def __init__(self, rpm_limit: int = 60, rpd_limit: int = 1000):
        self.default_rpm_limit = rpm_limit
        self.default_rpd_limit = rpd_limit
        self._metrics: Dict[str, ProviderUsageMetrics] = defaultdict(ProviderUsageMetrics)
        self._provider_rpm_limits: Dict[str, int] = {}

    def set_provider_limit(self, provider_name: str, rpm: int) -> None:
        self._provider_rpm_limits[provider_name] = rpm

    def check_preflight_quota(self, provider_name: str) -> bool:
        """Check if provider has capacity within the rolling 60-second window."""
        limit = self._provider_rpm_limits.get(provider_name, self.default_rpm_limit)
        now = time.time()
        m = self._metrics[provider_name]
        # Clean timestamps older than 60 seconds
        m.request_timestamps = [ts for ts in m.request_timestamps if now - ts < 60.0]
        if len(m.request_timestamps) >= limit:
            raise QuotaExhaustedError(
                f"Provider '{provider_name}' exceeded pre-flight RPM limit of {limit} requests/min."
            )
        return True

    def record_request_start(self, provider_name: str) -> None:
        now = time.time()
        m = self._metrics[provider_name]
        m.request_timestamps.append(now)
        m.total_requests += 1

    def record_success(
        self,
        provider_name: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        cost: float = 0.0,
    ) -> None:
        if cost > 0.0:
            raise PaidEndpointForbiddenError(
                f"Provider '{provider_name}' attempted to accrue a cost of ${cost:.4f}. Prohibited."
            )
        m = self._metrics[provider_name]
        m.successful_requests += 1
        m.total_input_tokens += input_tokens
        m.total_output_tokens += output_tokens
        m.recent_latencies_ms.append(latency_ms)
        if len(m.recent_latencies_ms) > 50:
            m.recent_latencies_ms.pop(0)

    def record_rate_limit(self, provider_name: str) -> None:
        m = self._metrics[provider_name]
        m.failed_requests += 1
        m.rate_limit_hits += 1

    def record_failure(self, provider_name: str) -> None:
        m = self._metrics[provider_name]
        m.failed_requests += 1

    def get_metrics(self, provider_name: str) -> ProviderUsageMetrics:
        return self._metrics[provider_name]

    def get_summary(self) -> Dict[str, dict]:
        now = time.time()
        summary = {}
        for name, m in self._metrics.items():
            active_rpm = len([ts for ts in m.request_timestamps if now - ts < 60.0])
            avg_latency = (
                sum(m.recent_latencies_ms) / len(m.recent_latencies_ms)
                if m.recent_latencies_ms
                else 0.0
            )
            summary[name] = {
                "total_requests": m.total_requests,
                "successful_requests": m.successful_requests,
                "failed_requests": m.failed_requests,
                "rate_limit_hits": m.rate_limit_hits,
                "active_rpm": active_rpm,
                "total_input_tokens": m.total_input_tokens,
                "total_output_tokens": m.total_output_tokens,
                "total_cost_usd": 0.0,
                "avg_latency_ms": round(avg_latency, 2),
            }
        return summary
