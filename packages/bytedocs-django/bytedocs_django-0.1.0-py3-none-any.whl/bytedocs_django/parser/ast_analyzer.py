"""
ByteDocs Django - AST Analyzer
Analyze Python source code using AST to extract response schemas and request bodies
Based on ByteDocs FastAPI AST analyzer
"""

import ast
import inspect
from typing import Any, Dict, Optional, Callable, List


def analyze_handler_source(handler: Callable, source_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze handler function source code using AST
    Returns dict with 'responses' and 'request_body_fields'
    """
    result = {
        'responses': {},
        'request_body_fields': []
    }

    if source_code is None:
        try:
            source_code = inspect.getsource(handler)
        except (OSError, TypeError):
            return result

    try:
        tree = ast.parse(source_code)

        # Find the function definition (both sync and async)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == handler.__name__:
                    # Analyze return statements
                    responses = analyze_return_statements(node)
                    if responses:
                        result['responses'] = responses

                    # Analyze request body usage
                    body_fields = analyze_request_body_usage(node)
                    if body_fields:
                        result['request_body_fields'] = body_fields
                    break

    except SyntaxError as e:
        pass  # Can't parse, skip AST analysis

    return result


def analyze_return_statements(func_node) -> Dict[str, Any]:
    """
    Analyze return statements to infer response structure
    Returns dict of status_code -> response_schema
    Accepts both ast.FunctionDef and ast.AsyncFunctionDef
    """
    responses = {}

    for node in ast.walk(func_node):
        # Look for return statements
        if isinstance(node, ast.Return) and node.value:
            schema = infer_schema_from_ast_node(node.value)
            if schema:
                # Default to 200 status
                responses['200'] = {
                    'description': 'Successful operation',
                    'content': {
                        'application/json': {
                            'schema': schema
                        }
                    }
                }

        # Look for Django JsonResponse/Response with status parameter
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'attr'):
                if node.func.attr in ['JsonResponse', 'Response']:
                    # Try to find status argument
                    status_code = '200'
                    content_value = None

                    for keyword in node.keywords:
                        if keyword.arg == 'status':
                            if isinstance(keyword.value, ast.Constant):
                                status_code = str(keyword.value.value)
                        elif keyword.arg in ['data', 'content']:
                            content_value = keyword.value

                    # If we found content, try to infer schema
                    if content_value:
                        schema = infer_schema_from_ast_node(content_value)
                        if schema:
                            responses[status_code] = {
                                'description': get_status_description(int(status_code)),
                                'content': {
                                    'application/json': {
                                        'schema': schema
                                    }
                                }
                            }

    return responses


def analyze_request_body_usage(func_node) -> List[str]:
    """
    Analyze how request body parameter is used to infer required fields
    Returns list of field names that are accessed
    Accepts both ast.FunctionDef and ast.AsyncFunctionDef
    """
    fields = []

    # Get parameter names
    param_names = [arg.arg for arg in func_node.args.args]

    # Look for attribute access on parameters (e.g., request.data, serializer.data)
    for node in ast.walk(func_node):
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                if node.value.id in param_names:
                    fields.append(node.attr)

    return list(set(fields))  # Remove duplicates


def infer_schema_from_ast_node(node: ast.AST) -> Optional[Dict[str, Any]]:
    """
    Infer OpenAPI schema from AST node
    """
    # Dict literal: {"key": "value", "num": 123}
    if isinstance(node, ast.Dict):
        properties = {}
        for key_node, value_node in zip(node.keys, node.values):
            if isinstance(key_node, ast.Constant):
                key = str(key_node.value)
                value_schema = infer_schema_from_ast_node(value_node)
                if value_schema:
                    properties[key] = value_schema

        if properties:
            return {
                'type': 'object',
                'properties': properties
            }

    # List literal: [...]
    elif isinstance(node, ast.List):
        if node.elts:
            # Infer from first element
            item_schema = infer_schema_from_ast_node(node.elts[0])
            return {
                'type': 'array',
                'items': item_schema or {'type': 'object'}
            }
        return {
            'type': 'array',
            'items': {'type': 'object'}
        }

    # Constant/Literal values
    elif isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, str):
            return {'type': 'string', 'example': value}
        elif isinstance(value, bool):
            return {'type': 'boolean', 'example': value}
        elif isinstance(value, int):
            return {'type': 'integer', 'example': value}
        elif isinstance(value, float):
            return {'type': 'number', 'example': value}

    # String literal (older Python)
    elif isinstance(node, ast.Str):
        return {'type': 'string', 'example': node.s}

    # Number literal (older Python)
    elif isinstance(node, ast.Num):
        if isinstance(node.n, int):
            return {'type': 'integer', 'example': node.n}
        else:
            return {'type': 'number', 'example': node.n}

    # Variable reference (can't infer type)
    elif isinstance(node, ast.Name):
        return {'type': 'object'}

    # Call expression (function call result)
    elif isinstance(node, ast.Call):
        # Check for dict() call
        if isinstance(node.func, ast.Name) and node.func.id == 'dict':
            properties = {}
            for keyword in node.keywords:
                if keyword.arg:
                    value_schema = infer_schema_from_ast_node(keyword.value)
                    if value_schema:
                        properties[keyword.arg] = value_schema

            if properties:
                return {
                    'type': 'object',
                    'properties': properties
                }

        # Check for list() call
        elif isinstance(node.func, ast.Name) and node.func.id == 'list':
            return {
                'type': 'array',
                'items': {'type': 'object'}
            }

    return None


def get_status_description(status: int) -> str:
    """Get HTTP status description"""
    descriptions = {
        200: 'Successful operation',
        201: 'Resource created successfully',
        204: 'No content',
        400: 'Bad request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Resource not found',
        422: 'Validation error',
        500: 'Internal server error',
    }
    return descriptions.get(status, f'HTTP {status}')


def enhance_schema_with_ast(
    existing_schema: Optional[Dict[str, Any]],
    handler: Callable,
    source_code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhance existing schema with AST analysis
    Combines DRF serializer schema with AST-detected response examples
    """
    if existing_schema is None:
        existing_schema = {}

    ast_result = analyze_handler_source(handler, source_code)

    # If we found responses from AST, use them
    if ast_result['responses']:
        # Merge with existing schema
        for status, response in ast_result['responses'].items():
            if status not in existing_schema:
                existing_schema[status] = response
            else:
                # Merge schemas if both exist
                if 'content' in response and 'application/json' in response['content']:
                    ast_schema = response['content']['application/json'].get('schema', {})
                    existing_content = existing_schema[status].get('content', {})
                    existing_json = existing_content.get('application/json', {})
                    existing_json_schema = existing_json.get('schema', {})

                    # If existing schema is generic, replace with AST schema
                    if existing_json_schema.get('type') == 'object' and not existing_json_schema.get('properties'):
                        if ast_schema.get('properties'):
                            existing_json['schema'] = ast_schema
                            existing_content['application/json'] = existing_json
                            existing_schema[status]['content'] = existing_content

    return existing_schema


def get_handler_source_code(handler: Callable) -> Optional[str]:
    """
    Get source code of handler function
    """
    try:
        return inspect.getsource(handler)
    except (OSError, TypeError):
        return None
