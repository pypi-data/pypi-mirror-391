"""
AI Provider Clients
Register all available providers
"""

from ..factory import register_client_factory
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .anthropic_client import AnthropicClient
from .openrouter_client import OpenRouterClient


# Register all providers
def _register_providers():
    """Register all available AI provider factories"""
    register_client_factory("openai", lambda config: OpenAIClient(config))
    register_client_factory("gemini", lambda config: GeminiClient(config))
    register_client_factory("anthropic", lambda config: AnthropicClient(config))
    register_client_factory("openrouter", lambda config: OpenRouterClient(config))


# Auto-register on import
_register_providers()


__all__ = [
    "OpenAIClient",
    "GeminiClient",
    "AnthropicClient",
    "OpenRouterClient",
]
