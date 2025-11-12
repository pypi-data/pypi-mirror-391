"""
ByteDocs Django - Core Type Definitions
Based on ByteDocs Express implementation
"""

from typing import Any, Dict, List, Optional, Literal, Callable
from dataclasses import dataclass, field
from enum import Enum


class ParameterLocation(str, Enum):
    """Parameter location types"""
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"


@dataclass
class BaseURLOption:
    """Base URL configuration for multiple environments"""
    name: str
    url: str


@dataclass
class AuthConfig:
    """Authentication configuration"""
    enabled: bool = False
    type: Optional[Literal["basic", "api_key", "bearer", "session"]] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    api_key_header: Optional[str] = None
    realm: Optional[str] = None  # For basic auth

    # Session-based auth
    session_expire: int = 60  # Minutes
    ip_ban_enabled: bool = False
    ip_ban_max_attempts: int = 5
    ip_ban_duration: int = 30  # Minutes
    admin_whitelist_ips: List[str] = field(default_factory=list)


@dataclass
class UIConfig:
    """UI configuration"""
    theme: Literal["auto", "green", "blue", "purple", "red", "orange", "teal", "pink"] = "green"
    dark_mode: bool = False
    show_try_it: bool = True
    show_schemas: bool = True


@dataclass
class AIFeatures:
    """AI features configuration"""
    chat_enabled: bool = True
    doc_generation_enabled: bool = True
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    temperature: float = 0.7


@dataclass
class AIConfig:
    """AI configuration"""
    provider: Literal["openai", "gemini", "anthropic", "openrouter"] = "openai"
    api_key: Optional[str] = None
    enabled: bool = False
    features: AIFeatures = field(default_factory=AIFeatures)
    settings: Dict[str, Any] = field(default_factory=dict)


def _default_exclude_paths():
    """Default paths to exclude from documentation"""
    return ["/admin", "/static", "/__debug__"]


@dataclass
class ByteDocsConfig:
    """Main ByteDocs configuration"""
    title: str = "API Documentation"
    version: str = "1.0.0"
    description: Optional[str] = None
    base_url: Optional[str] = None  # Backward compatibility
    base_urls: List[BaseURLOption] = field(default_factory=list)
    docs_path: str = "/docs"
    auto_detect: bool = True
    exclude_paths: List[str] = field(default_factory=_default_exclude_paths)
    auth_config: Optional[AuthConfig] = None
    ui_config: UIConfig = field(default_factory=UIConfig)
    ai_config: Optional[AIConfig] = None


@dataclass
class Schema:
    """OpenAPI schema definition"""
    type: str
    format: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict[str, "Schema"]] = None
    items: Optional["Schema"] = None
    required: Optional[List[str]] = None
    example: Any = None
    enum: Optional[List[Any]] = None
    default: Any = None
    nullable: bool = False
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    ref: Optional[str] = None


@dataclass
class Parameter:
    """OpenAPI parameter definition"""
    name: str
    location: ParameterLocation  # 'in' is reserved keyword in Python
    schema: Schema
    description: Optional[str] = None
    required: bool = False
    example: Any = None


@dataclass
class RequestBody:
    """OpenAPI request body definition"""
    content: Dict[str, Dict[str, Any]]
    description: Optional[str] = None
    required: bool = True


@dataclass
class ResponseDef:
    """OpenAPI response definition"""
    description: str
    content: Optional[Dict[str, Dict[str, Any]]] = None
    headers: Optional[Dict[str, Dict[str, Any]]] = None


@dataclass
class Endpoint:
    """Endpoint definition"""
    path: str
    method: str
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: Dict[str, ResponseDef] = field(default_factory=dict)
    security: Optional[List[Dict[str, List[str]]]] = None
    operation_id: Optional[str] = None
    deprecated: bool = False


@dataclass
class RouteInfo:
    """Route information extracted from Django"""
    method: str
    path: str
    handler: Callable
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: Dict[str, ResponseDef] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class Section:
    """Section for grouping endpoints"""
    name: str
    endpoints: List[Endpoint]


@dataclass
class OpenAPIServer:
    """OpenAPI server definition"""
    url: str
    description: Optional[str] = None


@dataclass
class OpenAPIComponents:
    """OpenAPI components"""
    schemas: Optional[Dict[str, Schema]] = None
    responses: Optional[Dict[str, ResponseDef]] = None
    parameters: Optional[Dict[str, Parameter]] = None
    request_bodies: Optional[Dict[str, RequestBody]] = None
    security_schemes: Optional[Dict[str, Any]] = None


@dataclass
class OpenAPISpec:
    """OpenAPI specification"""
    openapi: str = "3.0.3"
    info: Dict[str, Any] = field(default_factory=dict)
    servers: List[OpenAPIServer] = field(default_factory=list)
    paths: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    components: Optional[OpenAPIComponents] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    tags: Optional[List[Dict[str, Any]]] = None


@dataclass
class SessionData:
    """Session data for authentication"""
    id: str
    created_at: float
    expires_at: float
    ip: str


@dataclass
class IPBanRecord:
    """IP ban record for authentication"""
    ip: str
    attempts: int
    banned_at: Optional[float] = None
    expires_at: Optional[float] = None
