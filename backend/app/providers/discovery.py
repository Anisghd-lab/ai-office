"""Automatic discovery and configuration of zero-cost AI providers."""

import os
from typing import Dict, List, Optional, Tuple
from app.providers.base import BaseAIProvider, ModelInfo
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.quotas import QuotaTracker


def mask_secret(secret: Optional[str]) -> str:
    """Mask sensitive tokens so they never appear in logs or reports."""
    if not secret:
        return "[NOT_CONFIGURED]"
    if len(secret) <= 8:
        return "[REDACTED]"
    return f"{secret[:4]}...{secret[-4:]}"


def redact_text(text: str, secrets: List[str]) -> str:
    """Redact any occurrences of sensitive secrets from arbitrary text."""
    redacted = text
    for sec in secrets:
        if sec and len(sec) > 4:
            redacted = redacted.replace(sec, "[REDACTED_API_KEY]")
    return redacted


class ProviderDiscovery:
    """Discovers and instantiates available free AI providers from the environment."""

    def __init__(self, quota_tracker: Optional[QuotaTracker] = None):
        self.quota_tracker = quota_tracker or QuotaTracker()

    def discover_all(self) -> List[BaseAIProvider]:
        providers: List[BaseAIProvider] = []

        # 1. OpenRouter (Free tier models)
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            free_models = [
                ModelInfo(id="meta-llama/llama-3.3-70b-instruct:free", name="Llama 3.3 70B Instruct (Free)", is_free=True),
                ModelInfo(id="meta-llama/llama-3.1-8b-instruct:free", name="Llama 3.1 8B Instruct (Free)", is_free=True),
                ModelInfo(id="deepseek/deepseek-r1:free", name="DeepSeek R1 (Free)", is_free=True),
                ModelInfo(id="google/gemini-2.0-flash-exp:free", name="Gemini 2.0 Flash Exp (Free)", is_free=True),
                ModelInfo(id="qwen/qwen-2.5-coder-32b-instruct:free", name="Qwen 2.5 Coder 32B (Free)", is_free=True),
            ]
            openrouter = OpenAICompatibleProvider(
                name="openrouter",
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                free_models=free_models,
                default_model="meta-llama/llama-3.3-70b-instruct:free",
                quota_tracker=self.quota_tracker,
            )
            self.quota_tracker.set_provider_limit("openrouter", rpm=20)
            providers.append(openrouter)

        # 2. Groq (Free developer quota)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            groq_models = [
                ModelInfo(id="llama-3.3-70b-versatile", name="Groq Llama 3.3 70B", is_free=True),
                ModelInfo(id="llama-3.1-8b-instant", name="Groq Llama 3.1 8B Instant", is_free=True),
            ]
            groq = OpenAICompatibleProvider(
                name="groq",
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_key,
                free_models=groq_models,
                default_model="llama-3.1-8b-instant",
                quota_tracker=self.quota_tracker,
            )
            self.quota_tracker.set_provider_limit("groq", rpm=30)
            providers.append(groq)

        # 3. Local OpenAI-Compatible Server (Ollama / Local LLM)
        local_url = os.getenv("LOCAL_OPENAI_BASE_URL", "http://127.0.0.1:11434/v1")
        enable_local = os.getenv("ENABLE_LOCAL_LLM", "false").lower() in ("true", "1", "yes")
        if enable_local or os.getenv("LOCAL_OPENAI_BASE_URL"):
            local_provider = OpenAICompatibleProvider(
                name="local",
                base_url=local_url,
                api_key=os.getenv("LOCAL_OPENAI_API_KEY", "dummy-free-key"),
                free_models=[
                    ModelInfo(id="local-model", name="Local Autonomous Model", is_free=True)
                ],
                default_model="local-model",
                quota_tracker=self.quota_tracker,
            )
            self.quota_tracker.set_provider_limit("local", rpm=120)
            providers.append(local_provider)

        return providers

    def get_discovery_audit(self) -> Dict[str, dict]:
        """Produce safe discovery audit with masked keys."""
        return {
            "openrouter": {
                "configured": bool(os.getenv("OPENROUTER_API_KEY")),
                "masked_key": mask_secret(os.getenv("OPENROUTER_API_KEY")),
                "type": "remote_free_tier",
            },
            "groq": {
                "configured": bool(os.getenv("GROQ_API_KEY")),
                "masked_key": mask_secret(os.getenv("GROQ_API_KEY")),
                "type": "remote_free_tier",
            },
            "gemini": {
                "configured": bool(os.getenv("GEMINI_API_KEY")),
                "masked_key": mask_secret(os.getenv("GEMINI_API_KEY")),
                "type": "remote_free_tier",
            },
            "huggingface": {
                "configured": bool(os.getenv("HUGGINGFACE_API_KEY")),
                "masked_key": mask_secret(os.getenv("HUGGINGFACE_API_KEY")),
                "type": "remote_free_tier",
            },
            "local": {
                "configured": bool(os.getenv("LOCAL_OPENAI_BASE_URL")),
                "base_url": os.getenv("LOCAL_OPENAI_BASE_URL", "http://127.0.0.1:11434/v1"),
                "type": "local_zero_cost",
            },
        }
