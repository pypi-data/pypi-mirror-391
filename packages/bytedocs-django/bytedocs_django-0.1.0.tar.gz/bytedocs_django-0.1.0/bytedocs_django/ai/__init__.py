"""
AI Module - Multi-provider AI support for ByteDocs
Based on bytedocs-go AI implementation
"""

from .types import (
    AIConfig,
    AIFeatures,
    AIClient,
    ChatRequest,
    ChatResponse,
    ClientFactory,
)
from .factory import (
    register_client_factory,
    create_client,
    get_available_providers,
)

# Import providers to trigger registration
from . import providers  # noqa: F401


__all__ = [
    # Types
    "AIConfig",
    "AIFeatures",
    "AIClient",
    "ChatRequest",
    "ChatResponse",
    "ClientFactory",
    # Factory functions
    "register_client_factory",
    "create_client",
    "get_available_providers",
]
