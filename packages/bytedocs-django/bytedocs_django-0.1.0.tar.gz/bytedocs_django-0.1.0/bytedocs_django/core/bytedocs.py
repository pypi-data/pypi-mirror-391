"""
ByteDocs Django - Main Documentation Engine
Based on ByteDocs Express implementation
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import asdict

from .types import (
    ByteDocsConfig,
    RouteInfo,
    Endpoint,
    Section,
    OpenAPISpec,
    OpenAPIServer,
    Parameter,
    ResponseDef,
    Schema,
)
from .config import load_config_from_env, validate_config, merge_configs
from ..parser.route_analyzer import RouteAnalyzer


class ByteDocs:
    """Main ByteDocs documentation class for Django"""

    def __init__(self, config: Optional[Dict[str, Any]] = None, urlconf=None):
        # Load from environment
        env_config = load_config_from_env()

        # Merge with user config
        if config:
            self.config = merge_configs(env_config, config)
        else:
            self.config = env_config

        # Validate config
        is_valid, errors = validate_config(self.config)
        if not is_valid:
            print(f"[ByteDocs] Configuration warnings: {errors}")

        self.urlconf = urlconf
        self.routes: List[RouteInfo] = []
        self.endpoints: List[Endpoint] = []
        self.sections: List[Section] = []
        self._detected = False

        # Add docs path to exclude paths
        if self.config.docs_path not in self.config.exclude_paths:
            self.config.exclude_paths.append(self.config.docs_path)

    def detect_routes(self, urlconf=None) -> None:
        """Detect routes from Django URLconf"""
        analyzer = RouteAnalyzer(urlconf or self.urlconf)
        all_routes = analyzer.get_all_routes()

        # Filter excluded paths and duplicates
        self.routes = []
        seen_routes = set()  # Track unique (method, path) combinations

        for route in all_routes:
            should_exclude = False

            # Skip excluded paths
            for exclude_path in self.config.exclude_paths:
                if route.path.startswith(exclude_path):
                    should_exclude = True
                    break

            # Skip DRF format suffix patterns (e.g., /api/items\.{format}/? or /api/{format})
            if '\\.{format}' in route.path or '.{format}' in route.path or route.path.endswith('/{format}'):
                should_exclude = True

            # Skip DRF API root views (e.g., /api/, /v1/, etc.) - they just list endpoints
            # Only exclude if it's exactly a root path (ends with / and has no resource name after)
            if route.path.count('/') == 2 and route.path.endswith('/'):
                # Paths like /api/ or /v1/ have exactly 2 slashes and end with /
                # But /api/users/ has 3 slashes, so won't be excluded
                if route.summary and 'root view' in route.summary.lower():
                    should_exclude = True

            # Skip regex patterns that leaked through
            if any(char in route.path for char in ['\\', '?', '*', '+', '[', ']']):
                should_exclude = True

            # Skip duplicate routes (same method + path)
            route_key = (route.method, route.path)
            if route_key in seen_routes:
                should_exclude = True

            if not should_exclude:
                self.routes.append(route)
                seen_routes.add(route_key)

        self._detected = True

        # Auto-generate documentation
        if self.config.auto_detect:
            self.generate()

    def add_route(self, route: RouteInfo) -> None:
        """Add route manually"""
        self.routes.append(route)
        self._detected = False

    def generate(self) -> None:
        """Generate documentation from routes"""
        self.endpoints = []
        self.sections = []

        # Convert routes to endpoints
        for route in self.routes:
            endpoint = self._route_to_endpoint(route)
            self.endpoints.append(endpoint)

        # Post-process: Copy request body schema from POST to PUT/PATCH
        self._copy_request_body_from_post()

        # Group endpoints into sections
        self.sections = self._group_endpoints_into_sections(self.endpoints)

    def _route_to_endpoint(self, route: RouteInfo) -> Endpoint:
        """Convert route to endpoint"""
        path = route.path
        method = route.method.upper()

        # Generate unique ID
        operation_id = f"{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}"

        return Endpoint(
            path=path,
            method=method,
            summary=route.summary,
            description=route.description,
            tags=route.tags or self._infer_tags(path),
            parameters=route.parameters or [],
            request_body=route.request_body,
            responses=route.responses or self._get_default_responses(method),
            operation_id=operation_id,
        )

    def _infer_tags(self, path: str) -> List[str]:
        """Infer tags from path"""
        parts = [p for p in path.split("/") if p and not p.startswith("{")]
        if parts:
            tag = parts[0].replace("-", " ").replace("_", " ").title()
            return [tag]
        return ["Default"]

    def _get_default_responses(self, method: str) -> Dict[str, ResponseDef]:
        """Get default responses for method"""
        success_status = "201" if method.upper() == "POST" else "200"

        return {
            success_status: ResponseDef(
                description="Successful operation",
                content={
                    "application/json": {"schema": Schema(type="object")}
                },
            )
        }

    def _copy_request_body_from_post(self) -> None:
        """Copy request body schema from POST to PUT/PATCH endpoints"""
        # Create map of POST endpoints
        post_endpoints: Dict[str, Endpoint] = {}

        for endpoint in self.endpoints:
            if endpoint.method == "POST" and endpoint.request_body:
                post_endpoints[endpoint.path] = endpoint

        # Update PUT/PATCH endpoints
        for endpoint in self.endpoints:
            if endpoint.method in ["PUT", "PATCH"]:
                # Check if request body is empty
                has_empty_body = (
                    not endpoint.request_body
                    or not endpoint.request_body.content.get("application/json", {}).get(
                        "schema"
                    )
                )

                if has_empty_body:
                    # Find corresponding POST endpoint
                    base_path = endpoint.path
                    # Remove path parameters like /{id}
                    if "/" in base_path:
                        parts = base_path.split("/")
                        if parts[-1].startswith("{"):
                            base_path = "/".join(parts[:-1])

                    post_endpoint = post_endpoints.get(base_path)
                    if post_endpoint and post_endpoint.request_body:
                        print(
                            f"[ByteDocs] Copying request body from POST {base_path} to {endpoint.method} {endpoint.path}"
                        )
                        # Deep copy request body
                        endpoint.request_body = post_endpoint.request_body

    def _group_endpoints_into_sections(
        self, endpoints: List[Endpoint]
    ) -> List[Section]:
        """Group endpoints into sections by tags"""
        section_map: Dict[str, List[Endpoint]] = {}

        for endpoint in endpoints:
            section_name = endpoint.tags[0] if endpoint.tags else "Default"

            if section_name not in section_map:
                section_map[section_name] = []

            section_map[section_name].append(endpoint)

        sections = []
        for name, endpoints in section_map.items():
            sections.append(Section(name=name, endpoints=endpoints))

        return sections

    def get_documentation_data(self) -> Dict[str, Any]:
        """Get documentation data for UI"""
        # Transform sections to add IDs
        sections_with_ids = []
        for section in self.sections:
            endpoints_with_ids = []
            for endpoint in section.endpoints:
                endpoint_dict = self._to_dict(endpoint)
                endpoint_dict["id"] = endpoint.operation_id or f"{endpoint.method.lower()}_{endpoint.path}"

                # Convert snake_case to camelCase for UI compatibility
                if "request_body" in endpoint_dict:
                    endpoint_dict["requestBody"] = endpoint_dict.pop("request_body")
                if "operation_id" in endpoint_dict:
                    endpoint_dict["operationId"] = endpoint_dict.pop("operation_id")

                endpoints_with_ids.append(endpoint_dict)

            sections_with_ids.append(
                {"name": section.name, "endpoints": endpoints_with_ids}
            )

        # Convert base_urls to dict format (handle dataclass or dict)
        base_urls_list = []
        if self.config.base_urls:
            for url in self.config.base_urls:
                if hasattr(url, 'name'):  # dataclass
                    base_urls_list.append({"name": url.name, "url": url.url})
                else:  # dict
                    base_urls_list.append(url)
        elif self.config.base_url:
            base_urls_list = [{"name": "Default", "url": self.config.base_url}]

        return {
            "title": self.config.title,
            "version": self.config.version,
            "description": self.config.description,
            "baseURLs": base_urls_list,
            "endpoints": sections_with_ids,
        }

    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI specification"""
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": self.config.title or "API Documentation",
                "version": self.config.version or "1.0.0",
                "description": self.config.description,
            },
            "paths": {},
        }

        # Add servers
        if self.config.base_urls:
            spec["servers"] = [
                {"url": base_url.url, "description": base_url.name}
                for base_url in self.config.base_urls
            ]
        elif self.config.base_url:
            spec["servers"] = [{"url": self.config.base_url}]

        # Add tags
        tags = set()
        for endpoint in self.endpoints:
            if endpoint.tags:
                for tag in endpoint.tags:
                    tags.add(tag)

        if tags:
            spec["tags"] = [{"name": tag} for tag in sorted(tags)]

        # Add paths
        for endpoint in self.endpoints:
            if endpoint.path not in spec["paths"]:
                spec["paths"][endpoint.path] = {}

            operation = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": [self._to_dict(p) for p in endpoint.parameters],
                "responses": {
                    status: self._to_dict(resp)
                    for status, resp in endpoint.responses.items()
                },
            }

            if endpoint.request_body:
                operation["requestBody"] = self._to_dict(endpoint.request_body)

            if endpoint.operation_id:
                operation["operationId"] = endpoint.operation_id

            if endpoint.deprecated:
                operation["deprecated"] = True

            spec["paths"][endpoint.path][endpoint.method.lower()] = operation

        return spec

    def handle_chat(self, message: str, endpoint_id: Optional[str] = None) -> Dict[str, Any]:
        """Handle AI chat request

        Args:
            message: User message
            endpoint_id: Optional endpoint ID for context

        Returns:
            AI response dict
        """
        if not self.config.ai_config or not self.config.ai_config.enabled:
            raise ValueError("AI features are not enabled")

        try:
            from ..ai import create_client, ChatRequest
            from ..ai.context_optimizer import get_optimizer

            # Create AI client
            ai_client = create_client(self.config.ai_config)

            # Get OpenAPI spec as context
            openapi_spec = self.get_openapi_spec()

            # Optimize context to reduce token usage (70-80% savings)
            optimizer = get_optimizer()

            # Get original size for comparison
            original_context = json.dumps(openapi_spec, indent=2)
            original_size = len(original_context)

            # Get optimized context
            optimized_context = optimizer.get_optimized_context(
                openapi_spec,
                endpoint_id=endpoint_id
            )
            optimized_size = len(optimized_context)

            # Log token savings
            savings = optimizer.estimate_token_savings(original_size, optimized_size)
            print(f"[ByteDocs] Context optimization - Tokens saved: {savings['tokens_saved']} ({savings['percentage_saved']})")

            # Find endpoint if endpoint_id provided
            endpoint_data = None
            if endpoint_id:
                for section in self.sections:
                    for endpoint in section.endpoints:
                        if endpoint.operation_id == endpoint_id:
                            endpoint_data = endpoint
                            break

            # Create chat request with optimized context
            ai_request = ChatRequest(
                message=message,
                context=optimized_context,
                endpoint=endpoint_data,
            )

            # Get response from AI (sync call for Django)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            response = loop.run_until_complete(ai_client.chat(ai_request))

            return {
                "response": response.response,
                "provider": response.provider,
                "model": response.model,
                "tokensUsed": response.tokens_used,
                "tokensSaved": savings["tokens_saved"],
                "error": response.error,
            }

        except Exception as e:
            import traceback
            print(f"[ByteDocs] AI Chat error: {e}")
            traceback.print_exc()
            raise

    def get_routes(self) -> List[RouteInfo]:
        """Get all routes"""
        return self.routes.copy()

    def get_endpoints(self) -> List[Endpoint]:
        """Get all endpoints"""
        return self.endpoints.copy()

    def get_sections(self) -> List[Section]:
        """Get all sections"""
        return self.sections.copy()

    def get_config(self) -> ByteDocsConfig:
        """Get configuration"""
        return self.config

    def _to_dict(self, obj: Any) -> Any:
        """Convert dataclass/object to dict recursively"""
        if hasattr(obj, "__dataclass_fields__"):
            result = {}
            for field_name, field in obj.__dataclass_fields__.items():
                value = getattr(obj, field_name)
                # Convert field name from snake_case to camelCase for 'location' -> 'in'
                if field_name == "location" and hasattr(obj, "__class__") and obj.__class__.__name__ == "Parameter":
                    key = "in"
                    result[key] = value.value if hasattr(value, "value") else value
                # Convert snake_case to camelCase for OpenAPI schema properties
                elif field_name == "min_length":
                    key = "minLength"
                    if value is not None:
                        result[key] = self._to_dict(value)
                elif field_name == "max_length":
                    key = "maxLength"
                    if value is not None:
                        result[key] = self._to_dict(value)
                else:
                    key = field_name
                    if value is not None:
                        result[key] = self._to_dict(value)
            return result
        elif isinstance(obj, (list, tuple)):
            return [self._to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "value"):  # Enum
            return obj.value
        elif isinstance(obj, (str, int, float, bool, type(None))):
            # JSON-serializable primitives
            return obj
        else:
            # For non-serializable objects
            try:
                # Try json.dumps to see if it's serializable
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # Not serializable, return None
                return None


# Global ByteDocs instance
_bytedocs_instance: Optional[ByteDocs] = None


def setup_bytedocs(config: Optional[Dict[str, Any]] = None, urlconf=None) -> ByteDocs:
    """Setup ByteDocs for Django (convenience function)

    Args:
        config: Optional configuration dict
        urlconf: Optional URLconf module

    Returns:
        ByteDocs instance
    """
    global _bytedocs_instance
    _bytedocs_instance = ByteDocs(config, urlconf)
    return _bytedocs_instance


def get_bytedocs_instance() -> Optional[ByteDocs]:
    """Get global ByteDocs instance

    Returns:
        ByteDocs instance or None
    """
    return _bytedocs_instance
