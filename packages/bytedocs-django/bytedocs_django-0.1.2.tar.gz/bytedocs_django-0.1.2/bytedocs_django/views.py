"""
ByteDocs Django - Views
View functions for documentation endpoints
"""

from django.http import HttpRequest, HttpResponse
from .core.bytedocs import get_bytedocs_instance
from .ui.handlers import (
    create_docs_ui_handler,
    create_api_data_handler,
    create_openapi_json_handler,
    create_openapi_yaml_handler,
    create_chat_handler,
)


def docs_ui(request: HttpRequest) -> HttpResponse:
    """Serve documentation UI"""
    bytedocs = get_bytedocs_instance()
    if bytedocs is None:
        return HttpResponse(
            "ByteDocs not initialized. Please call setup_bytedocs() in your settings or urls.",
            status=500
        )

    # Lazy detect routes on first access
    if not bytedocs._detected:
        bytedocs.detect_routes()

    handler = create_docs_ui_handler(bytedocs)
    return handler(request)


def api_data(request: HttpRequest) -> HttpResponse:
    """Serve API data as JSON"""
    bytedocs = get_bytedocs_instance()
    if bytedocs is None:
        return HttpResponse(
            "ByteDocs not initialized. Please call setup_bytedocs() in your settings or urls.",
            status=500
        )

    # Lazy detect routes on first access
    if not bytedocs._detected:
        bytedocs.detect_routes()

    handler = create_api_data_handler(bytedocs)
    return handler(request)


def openapi_json(request: HttpRequest) -> HttpResponse:
    """Serve OpenAPI specification as JSON"""
    bytedocs = get_bytedocs_instance()
    if bytedocs is None:
        return HttpResponse(
            "ByteDocs not initialized. Please call setup_bytedocs() in your settings or urls.",
            status=500
        )

    handler = create_openapi_json_handler(bytedocs)
    return handler(request)


def openapi_yaml(request: HttpRequest) -> HttpResponse:
    """Serve OpenAPI specification as YAML"""
    bytedocs = get_bytedocs_instance()
    if bytedocs is None:
        return HttpResponse(
            "ByteDocs not initialized. Please call setup_bytedocs() in your settings or urls.",
            status=500
        )

    handler = create_openapi_yaml_handler(bytedocs)
    return handler(request)


def ai_chat(request: HttpRequest) -> HttpResponse:
    """Handle AI chat requests"""
    bytedocs = get_bytedocs_instance()
    if bytedocs is None:
        return HttpResponse(
            "ByteDocs not initialized. Please call setup_bytedocs() in your settings or urls.",
            status=500
        )

    handler = create_chat_handler(bytedocs)
    return handler(request)
