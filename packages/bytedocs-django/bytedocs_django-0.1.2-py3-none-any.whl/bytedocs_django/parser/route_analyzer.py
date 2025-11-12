"""
ByteDocs Django - Route Analyzer
Analyze Django URLconf and extract route information
"""

import inspect
import re
from typing import List, Dict, Any, Optional, Callable, get_type_hints, Union
from dataclasses import asdict
from django.urls import URLPattern, URLResolver, get_resolver
from django.urls.resolvers import RoutePattern, RegexPattern
from django.views import View

from ..core.types import RouteInfo, Parameter, ParameterLocation, Schema, RequestBody, ResponseDef
from .schema_extractor import SchemaExtractor
from .ast_analyzer import enhance_schema_with_ast, get_handler_source_code


class RouteAnalyzer:
    """Analyze Django routes and extract documentation"""

    def __init__(self, urlconf=None):
        """Initialize route analyzer

        Args:
            urlconf: Django URLconf module (default: ROOT_URLCONF from settings)
        """
        self.urlconf = urlconf
        self.resolver = get_resolver(urlconf)

    def get_all_routes(self) -> List[RouteInfo]:
        """Get all routes from Django URLconf

        Returns:
            List of RouteInfo objects
        """
        routes = []
        self._extract_routes(self.resolver.url_patterns, routes, prefix="")
        return routes

    def _extract_routes(
        self,
        url_patterns: List[Union[URLPattern, URLResolver]],
        routes: List[RouteInfo],
        prefix: str = "",
    ) -> None:
        """Recursively extract routes from URL patterns

        Args:
            url_patterns: List of URL patterns or resolvers
            routes: List to append RouteInfo objects to
            prefix: URL prefix for nested patterns
        """
        for pattern in url_patterns:
            if isinstance(pattern, URLResolver):
                # Nested URL patterns (include())
                new_prefix = prefix + str(pattern.pattern)
                self._extract_routes(pattern.url_patterns, routes, prefix=new_prefix)
            elif isinstance(pattern, URLPattern):
                # Single URL pattern
                path = prefix + str(pattern.pattern)
                callback = pattern.callback

                # Skip if no callback (shouldn't happen)
                if callback is None:
                    continue

                # Get view function
                view_func = self._get_view_function(callback)

                # Extract route info (returns list of routes for different HTTP methods)
                route_infos = self._analyze_view(view_func, path, pattern)
                if route_infos:
                    routes.extend(route_infos)

    def _get_view_function(self, callback: Callable) -> Callable:
        """Get the actual view function from callback

        Args:
            callback: View callback (function or class-based view)

        Returns:
            View function
        """
        # Handle class-based views
        if inspect.isclass(callback) and issubclass(callback, View):
            # For CBV, we'll use the dispatch method
            return callback.as_view()

        # Handle function-based views
        return callback

    def _analyze_view(
        self,
        view_func: Callable,
        path: str,
        pattern: URLPattern,
    ) -> List[RouteInfo]:
        """Analyze a view function and extract route information

        Args:
            view_func: View function to analyze
            path: URL path
            pattern: URL pattern object

        Returns:
            List of RouteInfo objects (one per HTTP method)
        """
        # Determine HTTP methods
        methods = self._get_http_methods(view_func)

        # Extract parameters from URL pattern
        parameters = self._extract_path_parameters(pattern)

        # Get docstring
        class_docstring = inspect.getdoc(view_func) or ""

        # Get tags from view function
        tags = self._get_tags(view_func, path)

        # Extract request body and responses from DRF ViewSet
        request_body = self._extract_request_body(view_func, path)
        responses = self._extract_responses(view_func, path)

        # Enhance responses with AST analysis
        source_code = get_handler_source_code(view_func)
        if source_code:
            responses = enhance_schema_with_ast(responses, view_func, source_code)

        # Parse DRF ViewSet docstring format (action-based)
        action_docs = self._parse_drf_docstring(class_docstring)

        # Create RouteInfo for each HTTP method
        routes = []
        for method in methods:
            # Get action name from view_func.actions if available
            action_name = None
            if hasattr(view_func, 'actions') and method.lower() in view_func.actions:
                action_name = view_func.actions[method.lower()]

            # Get summary and description for this specific action
            summary = None
            description = None

            # For custom actions (not standard CRUD), get docstring from the action method directly
            if action_name and action_name not in ['list', 'create', 'retrieve', 'update', 'partial_update', 'destroy']:
                # This is a custom action, get docstring from the action method
                if hasattr(view_func, 'cls'):
                    view_class = view_func.cls
                    if hasattr(view_class, action_name):
                        action_method = getattr(view_class, action_name)
                        action_docstring = inspect.getdoc(action_method) or ""
                        if action_docstring:
                            summary, description = self._parse_docstring(action_docstring)

            # If not found from custom action, try standard action docs
            if not summary and action_name and action_name in action_docs:
                summary = action_docs[action_name].get('summary')
                description = action_docs[action_name].get('description')

            # Final fallback to parsing class docstring
            if not summary:
                summary, description = self._parse_docstring(class_docstring)

            route_info = RouteInfo(
                method=method,
                path=self._convert_path_pattern(path),
                handler=view_func,
                summary=summary or self._generate_summary(method, path),
                description=description or "",  # OpenAPI requires string, not None
                parameters=parameters[:],  # Copy parameters
                request_body=request_body if method in ['POST', 'PUT', 'PATCH'] else None,
                responses=responses,
                tags=tags,
            )
            routes.append(route_info)

        return routes

    def _get_http_methods(self, view_func: Callable) -> List[str]:
        """Get HTTP methods supported by view

        Args:
            view_func: View function

        Returns:
            List of HTTP methods (uppercase)
        """
        # Check if it's a DRF view with actions attribute (from router)
        if hasattr(view_func, 'actions'):
            # DRF router sets actions like {'get': 'list', 'post': 'create'}
            return [method.upper() for method in view_func.actions.keys()]

        # Check if view has explicit allowed methods
        if hasattr(view_func, 'allowed_methods'):
            return [m.upper() for m in view_func.allowed_methods]

        # Check if it's a class-based view
        if hasattr(view_func, 'view_class'):
            view_class = view_func.view_class
            if hasattr(view_class, 'http_method_names'):
                # Get allowed methods from class
                allowed_methods = []
                for method in view_class.http_method_names:
                    if hasattr(view_class, method):
                        allowed_methods.append(method.upper())
                return allowed_methods

        # Default to GET only for safety
        return ['GET']

    def _extract_path_parameters(self, pattern: URLPattern) -> List[Parameter]:
        """Extract path parameters from URL pattern

        Args:
            pattern: URL pattern object

        Returns:
            List of Parameter objects
        """
        parameters = []

        # Get pattern regex
        if isinstance(pattern.pattern, RoutePattern):
            # Django 2.0+ path() syntax
            # Extract parameters from <type:name> syntax
            regex = pattern.pattern._route
            matches = re.findall(r'<(\w+:)?(\w+)>', regex)
            for match in matches:
                param_type, param_name = match
                param_type = param_type.rstrip(':') if param_type else 'str'

                # Map Django parameter types to OpenAPI types
                schema = self._get_schema_for_param_type(param_type)

                parameters.append(Parameter(
                    name=param_name,
                    location=ParameterLocation.PATH,
                    schema=schema,
                    required=True,
                ))
        elif isinstance(pattern.pattern, RegexPattern):
            # Old re_path() syntax
            # Extract named groups from regex
            regex = pattern.pattern.regex.pattern
            matches = re.findall(r'\?P<(\w+)>', regex)
            for param_name in matches:
                parameters.append(Parameter(
                    name=param_name,
                    location=ParameterLocation.PATH,
                    schema=Schema(type="string"),
                    required=True,
                ))

        return parameters

    def _get_schema_for_param_type(self, param_type: str) -> Schema:
        """Get OpenAPI schema for Django path parameter type

        Args:
            param_type: Django parameter type (int, str, slug, uuid, path)

        Returns:
            Schema object
        """
        type_mapping = {
            'int': Schema(type='integer', format='int32'),
            'str': Schema(type='string'),
            'slug': Schema(type='string', pattern=r'^[-a-zA-Z0-9_]+$'),
            'uuid': Schema(type='string', format='uuid'),
            'path': Schema(type='string'),
        }
        return type_mapping.get(param_type, Schema(type='string'))

    def _convert_path_pattern(self, path: str) -> str:
        """Convert Django path pattern to OpenAPI path format

        Args:
            path: Django path pattern

        Returns:
            OpenAPI path format (e.g., /users/{id})
        """
        converted = path

        # Convert regex named groups (?P<name>pattern) to {name}
        # This handles DRF router patterns like (?P<pk>[^/.]+)
        converted = re.sub(r'\(\?P<(\w+)>[^\)]+\)', r'{\1}', converted)

        # Convert Django <type:name> to OpenAPI {name}
        converted = re.sub(r'<(\w+):(\w+)>', r'{\2}', converted)
        # Convert Django <name> to OpenAPI {name}
        converted = re.sub(r'<(\w+)>', r'{\1}', converted)

        # Remove all regex anchors and special chars
        converted = converted.replace('^', '')
        converted = converted.replace('$', '')

        # Ensure path starts with /
        if not converted.startswith('/'):
            converted = '/' + converted
        # Keep trailing slashes for Django compatibility (DRF requires them by default)

        return converted

    def _parse_drf_docstring(self, docstring: str) -> Dict[str, Dict[str, str]]:
        """Parse DRF ViewSet docstring with action-specific docs

        Args:
            docstring: ViewSet docstring

        Returns:
            Dict mapping action names to their documentation
            Example: {'list': {'summary': 'Get all items', 'description': '...'}}
        """
        if not docstring:
            return {}

        action_docs = {}
        lines = docstring.strip().split('\n')

        current_action = None
        current_lines = []

        for line in lines:
            # Check if line is an action declaration (ends with :)
            stripped = line.strip()
            if stripped and stripped.endswith(':') and not stripped.startswith('-'):
                # Save previous action if exists
                if current_action and current_lines:
                    text = '\n'.join(current_lines).strip()
                    # First line is summary, rest is description
                    parts = text.split('\n', 1)
                    action_docs[current_action] = {
                        'summary': parts[0].strip() if parts else '',
                        'description': parts[1].strip() if len(parts) > 1 else None
                    }

                # Start new action
                current_action = stripped.rstrip(':').strip()
                current_lines = []
            elif current_action:
                # Add line to current action
                if stripped:
                    current_lines.append(stripped)

        # Save last action
        if current_action and current_lines:
            text = '\n'.join(current_lines).strip()
            parts = text.split('\n', 1)
            action_docs[current_action] = {
                'summary': parts[0].strip() if parts else '',
                'description': parts[1].strip() if len(parts) > 1 else None
            }

        return action_docs

    def _parse_docstring(self, docstring: str) -> tuple[Optional[str], Optional[str]]:
        """Parse docstring into summary and description

        Args:
            docstring: Function docstring

        Returns:
            Tuple of (summary, description)
        """
        if not docstring:
            return None, None

        lines = docstring.strip().split('\n')
        if not lines:
            return None, None

        # First line is summary
        summary = lines[0].strip()

        # Rest is description
        description = None
        if len(lines) > 1:
            desc_lines = [line.strip() for line in lines[1:] if line.strip()]
            if desc_lines:
                description = '\n'.join(desc_lines)

        return summary, description

    def _generate_summary(self, method: str, path: str) -> str:
        """Generate summary from method and path

        Args:
            method: HTTP method
            path: URL path

        Returns:
            Generated summary
        """
        # Remove parameters and convert to words
        clean_path = re.sub(r'\{[^}]+\}', '', path)
        parts = [p for p in clean_path.split('/') if p]

        if not parts:
            resource = "root"
        else:
            resource = parts[-1].replace('_', ' ').replace('-', ' ')

        method_action = {
            'GET': 'Get',
            'POST': 'Create',
            'PUT': 'Update',
            'PATCH': 'Partially update',
            'DELETE': 'Delete',
        }.get(method, method.title())

        return f"{method_action} {resource}"

    def _get_tags(self, view_func: Callable, path: str) -> List[str]:
        """Get tags for endpoint

        Args:
            view_func: View function
            path: URL path

        Returns:
            List of tags
        """
        # Check if view has explicit tags
        if hasattr(view_func, 'bytedocs_tags'):
            return view_func.bytedocs_tags

        # Check if view class has tags
        if hasattr(view_func, 'view_class') and hasattr(view_func.view_class, 'bytedocs_tags'):
            return view_func.view_class.bytedocs_tags

        # Generate tag from path
        parts = [p for p in path.split('/') if p and not p.startswith('{')]
        if parts:
            tag = parts[0].replace('_', ' ').replace('-', ' ').title()
            return [tag]

        return ['Default']

    def _extract_request_body(self, view_func: Callable, path: str) -> Optional[RequestBody]:
        """Extract request body from DRF ViewSet

        Args:
            view_func: View function
            path: URL path

        Returns:
            RequestBody object or None
        """
        # Check if view has serializer_class (DRF ViewSet)
        serializer_class = None

        if hasattr(view_func, 'cls'):
            # DRF ViewSet
            view_class = view_func.cls
            if hasattr(view_class, 'serializer_class'):
                serializer_class = view_class.serializer_class
            elif hasattr(view_class, 'get_serializer_class'):
                try:
                    # Try to get serializer class
                    serializer_class = view_class().get_serializer_class()
                except Exception:
                    pass
        elif hasattr(view_func, 'view_class'):
            view_class = view_func.view_class
            if hasattr(view_class, 'serializer_class'):
                serializer_class = view_class.serializer_class

        if serializer_class:
            schema = SchemaExtractor.extract_from_serializer(serializer_class)
            return RequestBody(
                description="Request body",
                required=True,
                content={
                    "application/json": {
                        "schema": schema,
                    }
                },
            )

        return None

    def _extract_responses(self, view_func: Callable, path: str) -> Dict[str, ResponseDef]:
        """Extract responses from DRF ViewSet

        Args:
            view_func: View function
            path: URL path

        Returns:
            Dict of status code to ResponseDef
        """
        responses = {}

        # Check if view has serializer_class (DRF ViewSet)
        serializer_class = None

        if hasattr(view_func, 'cls'):
            # DRF ViewSet
            view_class = view_func.cls
            if hasattr(view_class, 'serializer_class'):
                serializer_class = view_class.serializer_class
            elif hasattr(view_class, 'get_serializer_class'):
                try:
                    serializer_class = view_class().get_serializer_class()
                except Exception:
                    pass
        elif hasattr(view_func, 'view_class'):
            view_class = view_func.view_class
            if hasattr(view_class, 'serializer_class'):
                serializer_class = view_class.serializer_class

        if serializer_class:
            schema = SchemaExtractor.extract_from_serializer(serializer_class)
            responses['200'] = ResponseDef(
                description="Successful operation",
                content={
                    "application/json": {
                        "schema": schema,
                    }
                },
            )
        else:
            # Default response
            responses['200'] = ResponseDef(
                description="Successful operation",
                content={
                    "application/json": {
                        "schema": Schema(type="object"),
                    }
                },
            )

        return responses


def get_routes(urlconf=None) -> List[RouteInfo]:
    """Get all routes from Django URLconf

    Args:
        urlconf: Django URLconf module (default: ROOT_URLCONF from settings)

    Returns:
        List of RouteInfo objects
    """
    analyzer = RouteAnalyzer(urlconf)
    return analyzer.get_all_routes()
