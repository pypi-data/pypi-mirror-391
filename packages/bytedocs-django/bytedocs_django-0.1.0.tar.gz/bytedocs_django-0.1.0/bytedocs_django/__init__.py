"""
ByteDocs Django - Alternative to Swagger/Scramble for Django
Beautiful API documentation with AI-powered features
"""

from .core.bytedocs import ByteDocs, setup_bytedocs, get_bytedocs_instance
from .core.types import (
    ByteDocsConfig,
    AuthConfig,
    UIConfig,
    AIConfig,
    AIFeatures,
    BaseURLOption,
    Schema,
    Parameter,
    ParameterLocation,
    RequestBody,
    ResponseDef,
    Endpoint,
    RouteInfo,
    Section,
)
from .core.config import load_config_from_env, validate_config, merge_configs

__version__ = "0.1.0"
__all__ = [
    "ByteDocs",
    "setup_bytedocs",
    "get_bytedocs_instance",
    "ByteDocsConfig",
    "AuthConfig",
    "UIConfig",
    "AIConfig",
    "AIFeatures",
    "BaseURLOption",
    "Schema",
    "Parameter",
    "ParameterLocation",
    "RequestBody",
    "ResponseDef",
    "Endpoint",
    "RouteInfo",
    "Section",
    "load_config_from_env",
    "validate_config",
    "merge_configs",
]
