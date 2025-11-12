"""
ByteDocs Flask - IMPROVED AST Analyzer
Analyze Python source code using AST to extract response schemas and request bodies
"""

import ast
import inspect
from typing import Any, Dict, Optional, Callable, List, Set


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

                    # Analyze request body usage (IMPROVED)
                    body_fields = analyze_request_body_usage_improved(node)
                    if body_fields:
                        result['request_body_fields'] = body_fields
                    break

    except SyntaxError as e:
        pass  # Can't parse, skip AST analysis

    return result


def analyze_return_statements(func_node) -> Dict[str, Any]:
    """
    IMPROVED: Analyze return statements to infer response structure
    Handles: return jsonify({...}), 201
    """
    responses = {}

    # Look for return statements in the function body
    for stmt in func_node.body:
        if isinstance(stmt, ast.Return) and stmt.value:
            # Check if it's a tuple return: (jsonify({...}), 201)
            if isinstance(stmt.value, ast.Tuple) and len(stmt.value.elts) >= 2:
                # First element is the response (jsonify call)
                response_node = stmt.value.elts[0]
                # Second element is status code
                status_node = stmt.value.elts[1]

                # Extract status code
                status_code = '200'
                if isinstance(status_node, ast.Constant):
                    status_code = str(status_node.value)

                # Extract schema from jsonify() call
                schema = None
                if isinstance(response_node, ast.Call):
                    if isinstance(response_node.func, ast.Name) and response_node.func.id == 'jsonify':
                        if response_node.args:
                            schema = infer_schema_from_ast_node(response_node.args[0])

                if schema:
                    responses[status_code] = {
                        'description': get_status_description(int(status_code)),
                        'content': {
                            'application/json': {
                                'schema': schema
                            }
                        }
                    }

            # Regular return: return jsonify({...})
            elif isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Name) and stmt.value.func.id == 'jsonify':
                    if stmt.value.args:
                        schema = infer_schema_from_ast_node(stmt.value.args[0])
                        if schema:
                            responses['200'] = {
                                'description': 'Successful operation',
                                'content': {
                                    'application/json': {
                                        'schema': schema
                                    }
                                }
                            }

    return responses


def analyze_request_body_usage_improved(func_node) -> List[str]:
    """
    IMPROVED: Detect request body fields from pattern:
    data = request.json
    name = data.get('name')
    email = data.get('email')
    """
    fields: Set[str] = set()

    # Step 1: Find variables assigned from request.json
    # Pattern: data = request.json
    request_json_vars: Set[str] = set()

    for stmt in func_node.body:
        if isinstance(stmt, ast.Assign):
            # Check if RHS is request.json
            if isinstance(stmt.value, ast.Attribute):
                if (isinstance(stmt.value.value, ast.Name) and
                    stmt.value.value.id == 'request' and
                    stmt.value.attr == 'json'):
                    # Found: data = request.json
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            request_json_vars.add(target.id)

    # Step 2: Find data.get('field') calls
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # Check if it's a .get() call
                if node.func.attr == 'get':
                    # Check if it's called on a request.json variable
                    if isinstance(node.func.value, ast.Name):
                        var_name = node.func.value.id
                        if var_name in request_json_vars:
                            # This is data.get('field')
                            if node.args and isinstance(node.args[0], ast.Constant):
                                field_name = node.args[0].value
                                if isinstance(field_name, str):
                                    fields.add(field_name)

    # Step 3: Also check direct request.json.get('field') calls
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'get':
                    # Check if it's request.json.get()
                    if isinstance(node.func.value, ast.Attribute):
                        if (isinstance(node.func.value.value, ast.Name) and
                            node.func.value.value.id == 'request' and
                            node.func.value.attr == 'json'):
                            # This is request.json.get('field')
                            if node.args and isinstance(node.args[0], ast.Constant):
                                field_name = node.args[0].value
                                if isinstance(field_name, str):
                                    fields.add(field_name)

    return sorted(list(fields))


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

    # Variable reference (can't infer type fully, but return string type)
    elif isinstance(node, ast.Name):
        return {'type': 'string'}

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
    Combines existing schema with AST-detected response examples
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
