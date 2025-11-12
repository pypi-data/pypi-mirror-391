"""
ByteDocs Django - Configuration Management
Load and validate configuration from environment variables
"""

import os
from typing import Optional, List, Dict, Any
from .types import ByteDocsConfig, AuthConfig, UIConfig, AIConfig, AIFeatures, BaseURLOption


def load_dotenv_file() -> None:
    """Load .env file if it exists

    Searches for .env file in:
    1. Current working directory
    2. Parent directories (up to 3 levels)
    """
    try:
        from dotenv import load_dotenv, find_dotenv
        # find_dotenv() searches up the directory tree for .env
        dotenv_path = find_dotenv(usecwd=True)
        if dotenv_path:
            load_dotenv(dotenv_path=dotenv_path)
        else:
            # Fallback to current directory
            load_dotenv()
    except ImportError:
        # python-dotenv not installed, skip
        pass


def load_config_from_env() -> ByteDocsConfig:
    """Load configuration from environment variables

    Supports two naming conventions:
    - BYTEDOCS_* prefix (e.g., BYTEDOCS_TITLE)
    - Simple names (e.g., API_TITLE, API_VERSION)

    BYTEDOCS_* prefix takes priority if both are set.
    """
    # Load .env file first
    load_dotenv_file()

    config = ByteDocsConfig()

    # Basic config - support both BYTEDOCS_* and API_* prefixes
    config.title = os.getenv("BYTEDOCS_TITLE") or os.getenv("API_TITLE", "API Documentation")
    config.version = os.getenv("BYTEDOCS_VERSION") or os.getenv("API_VERSION", "1.0.0")
    config.description = os.getenv("BYTEDOCS_DESCRIPTION") or os.getenv("API_DESCRIPTION")
    config.base_url = os.getenv("BYTEDOCS_BASE_URL") or os.getenv("API_BASE_URL")
    config.docs_path = os.getenv("BYTEDOCS_DOCS_PATH") or os.getenv("DOCS_PATH", "/docs")
    config.auto_detect = os.getenv("BYTEDOCS_AUTO_DETECT", "true").lower() == "true"

    # Exclude paths
    exclude_paths = os.getenv("BYTEDOCS_EXCLUDE_PATHS", "")
    if exclude_paths:
        config.exclude_paths = [p.strip() for p in exclude_paths.split(",")]

    # Base URLs (multiple environments)
    # Support individual environment URLs
    base_urls_list = []
    production_url = os.getenv("BYTEDOCS_PRODUCTION_URL")
    local_url = os.getenv("BYTEDOCS_LOCAL_URL")

    if production_url:
        base_urls_list.append(BaseURLOption(name="Production", url=production_url))
    if local_url:
        base_urls_list.append(BaseURLOption(name="Local", url=local_url))

    # Also support old BYTEDOCS_BASE_URLS format for backward compatibility
    base_urls_str = os.getenv("BYTEDOCS_BASE_URLS")
    if base_urls_str:
        # Format: "Development:http://localhost:8000,Production:https://api.example.com"
        for url_pair in base_urls_str.split(","):
            if ":" in url_pair:
                parts = url_pair.split(":", 1)
                if len(parts) == 2:
                    name, url = parts
                    # Handle URLs with protocol
                    if url.startswith("//"):
                        url = "http:" + url
                    elif not url.startswith("http"):
                        # If there's more colons (like http://), reconstruct
                        remaining = url_pair.split(":", 2)
                        if len(remaining) >= 3:
                            name = remaining[0]
                            url = remaining[1] + ":" + remaining[2]
                    base_urls_list.append(BaseURLOption(name=name.strip(), url=url.strip()))

    if base_urls_list:
        config.base_urls = base_urls_list

    # Auth config
    auth_enabled = os.getenv("BYTEDOCS_AUTH_ENABLED", "false").lower() == "true"
    if auth_enabled:
        config.auth_config = AuthConfig(
            enabled=True,
            type=os.getenv("BYTEDOCS_AUTH_TYPE", "session"),
            username=os.getenv("BYTEDOCS_AUTH_USERNAME"),
            password=os.getenv("BYTEDOCS_AUTH_PASSWORD"),
            api_key=os.getenv("BYTEDOCS_AUTH_API_KEY"),
            api_key_header=os.getenv("BYTEDOCS_AUTH_API_KEY_HEADER", "X-API-Key"),
            realm=os.getenv("BYTEDOCS_AUTH_REALM"),
            session_expire=int(os.getenv("BYTEDOCS_AUTH_SESSION_EXPIRE", "60")),
            ip_ban_enabled=os.getenv("BYTEDOCS_AUTH_IP_BAN_ENABLED", "false").lower() == "true",
            ip_ban_max_attempts=int(os.getenv("BYTEDOCS_AUTH_IP_BAN_MAX_ATTEMPTS", "5")),
            ip_ban_duration=int(os.getenv("BYTEDOCS_AUTH_IP_BAN_DURATION", "30")),
        )

        # Admin whitelist IPs
        whitelist_ips = os.getenv("BYTEDOCS_AUTH_ADMIN_WHITELIST_IPS", "")
        if whitelist_ips:
            config.auth_config.admin_whitelist_ips = [ip.strip() for ip in whitelist_ips.split(",")]

    # UI config
    config.ui_config = UIConfig(
        theme=os.getenv("BYTEDOCS_UI_THEME", "green"),
        dark_mode=os.getenv("BYTEDOCS_UI_DARK_MODE", "false").lower() == "true",
        show_try_it=os.getenv("BYTEDOCS_UI_SHOW_TRY_IT", "true").lower() == "true",
        show_schemas=os.getenv("BYTEDOCS_UI_SHOW_SCHEMAS", "true").lower() == "true",
    )

    # AI config
    ai_enabled = os.getenv("BYTEDOCS_AI_ENABLED", "false").lower() == "true"
    if ai_enabled:
        # Parse max_tokens and max_completion_tokens
        max_tokens = None
        max_completion_tokens = None
        if os.getenv("BYTEDOCS_AI_MAX_TOKENS"):
            max_tokens = int(os.getenv("BYTEDOCS_AI_MAX_TOKENS"))
        if os.getenv("BYTEDOCS_AI_MAX_COMPLETION_TOKENS"):
            max_completion_tokens = int(os.getenv("BYTEDOCS_AI_MAX_COMPLETION_TOKENS"))

        config.ai_config = AIConfig(
            enabled=True,
            provider=os.getenv("BYTEDOCS_AI_PROVIDER", "openai"),
            api_key=os.getenv("BYTEDOCS_AI_API_KEY"),
            features=AIFeatures(
                chat_enabled=os.getenv("BYTEDOCS_AI_CHAT_ENABLED", "true").lower() == "true",
                doc_generation_enabled=os.getenv("BYTEDOCS_AI_DOC_GEN_ENABLED", "true").lower() == "true",
                model=os.getenv("BYTEDOCS_AI_MODEL"),
                max_tokens=max_tokens,
                max_completion_tokens=max_completion_tokens,
                temperature=float(os.getenv("BYTEDOCS_AI_TEMPERATURE", "0.7")),
            ),
        )

    return config


def validate_config(config: ByteDocsConfig) -> tuple[bool, List[str]]:
    """Validate configuration and return validation result"""
    errors = []

    # Validate docs path
    if not config.docs_path.startswith("/"):
        errors.append("docs_path must start with /")

    # Validate auth config
    if config.auth_config and config.auth_config.enabled:
        if config.auth_config.type == "basic":
            if not config.auth_config.username or not config.auth_config.password:
                errors.append("Basic auth requires username and password")
        elif config.auth_config.type == "api_key":
            if not config.auth_config.api_key:
                errors.append("API key auth requires api_key")
        elif config.auth_config.type == "bearer":
            if not config.auth_config.api_key:
                errors.append("Bearer auth requires api_key")
        elif config.auth_config.type == "session":
            if not config.auth_config.password:
                errors.append("Session auth requires password")

    # Validate AI config
    if config.ai_config and config.ai_config.enabled:
        if not config.ai_config.api_key:
            errors.append("AI features require api_key")

    return len(errors) == 0, errors


def merge_configs(env_config: ByteDocsConfig, user_config: Dict[str, Any]) -> ByteDocsConfig:
    """Merge environment config with user-provided config"""
    # Start with env config
    merged = env_config

    # Override with user config
    if "title" in user_config:
        merged.title = user_config["title"]
    if "version" in user_config:
        merged.version = user_config["version"]
    if "description" in user_config:
        merged.description = user_config["description"]
    if "base_url" in user_config:
        merged.base_url = user_config["base_url"]
    if "base_urls" in user_config:
        merged.base_urls = [
            BaseURLOption(**url) if isinstance(url, dict) else url
            for url in user_config["base_urls"]
        ]
    if "docs_path" in user_config:
        merged.docs_path = user_config["docs_path"]
    if "auto_detect" in user_config:
        merged.auto_detect = user_config["auto_detect"]
    if "exclude_paths" in user_config:
        merged.exclude_paths = user_config["exclude_paths"]

    # Auth config
    if "auth_config" in user_config:
        auth = user_config["auth_config"]
        if isinstance(auth, dict):
            merged.auth_config = AuthConfig(**auth)
        else:
            merged.auth_config = auth

    # UI config
    if "ui_config" in user_config:
        ui = user_config["ui_config"]
        if isinstance(ui, dict):
            merged.ui_config = UIConfig(**ui)
        else:
            merged.ui_config = ui

    # AI config
    if "ai_config" in user_config:
        ai = user_config["ai_config"]
        if isinstance(ai, dict):
            features = ai.get("features", {})
            if isinstance(features, dict):
                ai["features"] = AIFeatures(**features)
            merged.ai_config = AIConfig(**ai)
        else:
            merged.ai_config = ai

    return merged
