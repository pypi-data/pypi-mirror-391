"""
AI Client Factory
Based on bytedocs-go factory pattern
"""

from typing import Dict, Callable
from .types import AIConfig, AIClient


# Registry of client factories
_client_factories: Dict[str, Callable[[AIConfig], AIClient]] = {}


def register_client_factory(provider: str, factory: Callable[[AIConfig], AIClient]) -> None:
    """Register a client factory for a provider"""
    _client_factories[provider] = factory


def create_client(config: AIConfig) -> AIClient:
    """Create AI client based on configuration"""
    if not config or not config.enabled:
        raise ValueError("AI configuration is not enabled")

    factory = _client_factories.get(config.provider)
    if not factory:
        raise ValueError(f"Unsupported AI provider: {config.provider}")

    return factory(config)


def get_available_providers() -> list:
    """Get list of available providers"""
    return list(_client_factories.keys())
