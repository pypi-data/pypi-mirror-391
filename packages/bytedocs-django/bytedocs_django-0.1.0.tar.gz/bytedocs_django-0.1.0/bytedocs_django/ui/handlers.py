"""
ByteDocs Django - UI Handlers
Create view functions for documentation endpoints
"""

import json
import yaml
from typing import Any, Dict, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
from .template_loader import load_template, render_template


def create_docs_ui_handler(bytedocs_instance):
    """Create documentation UI handler

    Args:
        bytedocs_instance: ByteDocs instance with documentation data

    Returns:
        Django view function
    """
    def docs_ui(request: HttpRequest) -> HttpResponse:
        """Serve documentation UI"""
        # Auto-detect routes if needed
        if bytedocs_instance.config.auto_detect and not bytedocs_instance._detected:
            bytedocs_instance.detect_routes()

        # Get documentation data
        doc_data = bytedocs_instance.get_documentation_data()

        # Load template
        template = load_template("template.html")

        # Prepare data for template
        template_data = {
            "title": bytedocs_instance.config.title,
            "description": bytedocs_instance.config.description or "",
            "api_data": json.dumps(doc_data, default=str),
            "config_data": json.dumps({
                "theme": bytedocs_instance.config.ui_config.theme,
                "darkMode": bytedocs_instance.config.ui_config.dark_mode,
                "showTryIt": bytedocs_instance.config.ui_config.show_try_it,
                "showSchemas": bytedocs_instance.config.ui_config.show_schemas,
                "aiEnabled": bytedocs_instance.config.ai_config.enabled if bytedocs_instance.config.ai_config else False,
                "chatEnabled": (
                    bytedocs_instance.config.ai_config.features.chat_enabled
                    if bytedocs_instance.config.ai_config and bytedocs_instance.config.ai_config.enabled
                    else False
                ),
            }, default=str),
        }

        # Render template
        html = render_template(template, template_data)

        return HttpResponse(html, content_type="text/html")

    return docs_ui


def create_api_data_handler(bytedocs_instance):
    """Create API data JSON handler

    Args:
        bytedocs_instance: ByteDocs instance with documentation data

    Returns:
        Django view function
    """
    def api_data(request: HttpRequest) -> JsonResponse:
        """Serve API documentation data as JSON"""
        # Auto-detect routes if needed
        if bytedocs_instance.config.auto_detect and not bytedocs_instance._detected:
            bytedocs_instance.detect_routes()

        # Get documentation data
        doc_data = bytedocs_instance.get_documentation_data()

        return JsonResponse(doc_data, safe=False)

    return api_data


def create_openapi_json_handler(bytedocs_instance):
    """Create OpenAPI JSON handler

    Args:
        bytedocs_instance: ByteDocs instance with documentation data

    Returns:
        Django view function
    """
    def openapi_json(request: HttpRequest) -> JsonResponse:
        """Serve OpenAPI specification as JSON"""
        # Auto-detect routes if needed
        if bytedocs_instance.config.auto_detect and not bytedocs_instance._detected:
            bytedocs_instance.detect_routes()

        # Get OpenAPI spec
        openapi_spec = bytedocs_instance.get_openapi_spec()

        return JsonResponse(openapi_spec, safe=False)

    return openapi_json


def create_openapi_yaml_handler(bytedocs_instance):
    """Create OpenAPI YAML handler

    Args:
        bytedocs_instance: ByteDocs instance with documentation data

    Returns:
        Django view function
    """
    def openapi_yaml(request: HttpRequest) -> HttpResponse:
        """Serve OpenAPI specification as YAML"""
        # Auto-detect routes if needed
        if bytedocs_instance.config.auto_detect and not bytedocs_instance._detected:
            bytedocs_instance.detect_routes()

        # Get OpenAPI spec
        openapi_spec = bytedocs_instance.get_openapi_spec()

        # Convert to YAML
        yaml_content = yaml.dump(openapi_spec, sort_keys=False, allow_unicode=True)

        return HttpResponse(yaml_content, content_type="application/x-yaml")

    return openapi_yaml


def create_chat_handler(bytedocs_instance):
    """Create AI chat handler

    Args:
        bytedocs_instance: ByteDocs instance with documentation data

    Returns:
        Django view function
    """
    def chat(request: HttpRequest) -> JsonResponse:
        """Handle AI chat requests"""
        # Check if AI is enabled
        if not bytedocs_instance.config.ai_config or not bytedocs_instance.config.ai_config.enabled:
            return JsonResponse(
                {"error": "AI features are not enabled"},
                status=400
            )

        # Check if chat is enabled
        if not bytedocs_instance.config.ai_config.features.chat_enabled:
            return JsonResponse(
                {"error": "Chat feature is not enabled"},
                status=400
            )

        # Only accept POST requests
        if request.method != "POST":
            return JsonResponse(
                {"error": "Method not allowed"},
                status=405
            )

        try:
            # Parse request body
            data = json.loads(request.body)
            message = data.get("message")
            endpoint_id = data.get("endpoint_id")

            if not message:
                return JsonResponse(
                    {"error": "Message is required"},
                    status=400
                )

            # Get AI response
            response = bytedocs_instance.handle_chat(message, endpoint_id)

            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=500
            )

    return chat
