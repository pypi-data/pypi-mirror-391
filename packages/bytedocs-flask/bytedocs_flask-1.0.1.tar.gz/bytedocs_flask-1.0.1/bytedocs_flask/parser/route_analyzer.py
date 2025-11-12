"""
ByteDocs Flask - Route Analyzer
Auto-detect and analyze Flask routes
"""

import inspect
import re
from typing import Any, Callable, Dict, List, Optional
from flask import Flask

from ..core.types import (
    RouteInfo,
    Parameter,
    ParameterLocation,
    RequestBody,
    ResponseDef,
    Schema,
)
from .ast_analyzer import enhance_schema_with_ast, get_handler_source_code


def extract_routes(app: Flask, exclude_paths: List[str] = None) -> List[RouteInfo]:
    """Extract all routes from Flask application"""
    if exclude_paths is None:
        exclude_paths = []

    routes = []

    # Iterate through Flask's URL map
    for rule in app.url_map.iter_rules():
        path = rule.rule

        # Check if should be excluded
        if should_exclude_path(path, exclude_paths):
            continue

        # Skip static routes
        if rule.endpoint == 'static':
            continue

        # Get methods for this route
        methods = rule.methods or {'GET'}

        # Remove HEAD and OPTIONS from methods (they're automatic)
        methods = methods - {'HEAD', 'OPTIONS'}

        for method in methods:
            try:
                # Get the view function
                handler = app.view_functions.get(rule.endpoint)

                if handler:
                    route_info = analyze_route(rule, method, path, handler)
                    if route_info:
                        routes.append(route_info)
            except Exception as e:
                print(f"[ByteDocs] Error analyzing route {method} {path}: {e}")
                continue

    print(f"[ByteDocs] Detected {len(routes)} routes")
    return routes


def should_exclude_path(path: str, exclude_paths: List[str]) -> bool:
    """Check if path should be excluded"""
    for exclude_pattern in exclude_paths:
        if path.startswith(exclude_pattern):
            return True
    return False


def analyze_route(rule, method: str, path: str, handler: Callable) -> Optional[RouteInfo]:
    """Analyze a single route and extract metadata"""
    try:
        # Get basic info from handler docstring
        summary, description = extract_docstring_info(handler)

        # Generate summary if not found
        if not summary:
            summary = generate_summary(method, path)

        # Infer tags from path
        tags = infer_tags(path)

        # Extract parameters (path and query)
        parameters = extract_parameters(rule, handler)

        # Extract request body
        request_body = extract_request_body(handler, method)

        # Extract responses
        responses = extract_responses(handler, method)

        return RouteInfo(
            method=method.upper(),
            path=convert_path_to_openapi(path),
            handler=handler,
            summary=summary,
            description=description,
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            tags=tags,
        )
    except Exception as e:
        print(f"[ByteDocs] Error analyzing route {method} {path}: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_docstring_info(handler: Callable) -> tuple[Optional[str], Optional[str]]:
    """Extract summary and description from handler docstring"""
    if not handler.__doc__:
        return None, None

    doc = handler.__doc__.strip()

    # Split into lines
    lines = [line.strip() for line in doc.split('\n') if line.strip()]

    if not lines:
        return None, None

    # First line is summary
    summary = lines[0]

    # Remaining lines are description
    description = '\n'.join(lines[1:]) if len(lines) > 1 else None

    return summary, description


def extract_parameters(rule, handler: Callable) -> List[Parameter]:
    """Extract parameters from route"""
    parameters = []

    # Extract path parameters from rule
    # Flask uses <type:name> or <name> format
    path_params = rule.arguments if hasattr(rule, 'arguments') else set()

    for param_name in path_params:
        # Try to infer type from rule converters
        param_type = "string"

        if hasattr(rule, '_converters') and param_name in rule._converters:
            converter = rule._converters[param_name]
            converter_type = type(converter).__name__

            if 'int' in converter_type.lower():
                param_type = "integer"
            elif 'float' in converter_type.lower():
                param_type = "number"
            elif 'uuid' in converter_type.lower():
                param_type = "string"

        parameters.append(
            Parameter(
                name=param_name,
                location=ParameterLocation.PATH,
                schema=Schema(type=param_type),
                description=None,
                required=True,
            )
        )

    # Try to extract query parameters from handler signature
    try:
        sig = inspect.signature(handler)

        for param_name, param in sig.parameters.items():
            # Skip path parameters
            if param_name in path_params:
                continue

            # Skip special Flask parameters
            if param_name in ['self', 'cls']:
                continue

            # Infer this is a query parameter
            param_type = "string"
            required = param.default == inspect.Parameter.empty
            default_value = None if required else param.default

            # Try to infer type from annotation
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"

            schema = Schema(type=param_type)
            if default_value is not None:
                try:
                    import json
                    json.dumps(default_value)
                    schema.default = default_value
                except (TypeError, ValueError):
                    pass

            parameters.append(
                Parameter(
                    name=param_name,
                    location=ParameterLocation.QUERY,
                    schema=schema,
                    description=None,
                    required=required,
                )
            )
    except Exception as e:
        # If signature extraction fails, continue with what we have
        pass

    return parameters


def extract_request_body(handler: Callable, method: str) -> Optional[RequestBody]:
    """Extract request body schema from handler using AST"""
    # Only for methods that typically have body
    if method.upper() not in ["POST", "PUT", "PATCH"]:
        return None

    try:
        # Get source code
        source_code = get_handler_source_code(handler)
        if not source_code:
            return None

        # Use AST to analyze request body usage
        from .ast_analyzer import analyze_handler_source
        ast_result = analyze_handler_source(handler, source_code)

        if ast_result['request_body_fields']:
            # Build schema from detected fields
            properties = {}
            for field_name in ast_result['request_body_fields']:
                properties[field_name] = Schema(type="string")

            if properties:
                return RequestBody(
                    description="Request body",
                    required=True,
                    content={
                        "application/json": {
                            "schema": Schema(
                                type="object",
                                properties=properties
                            ),
                        }
                    },
                )
    except Exception as e:
        # AST analysis failed, return None
        pass

    return None


def extract_responses(handler: Callable, method: str) -> Dict[str, ResponseDef]:
    """Extract response schemas from handler using AST"""
    responses = {}

    # Default response
    default_status = "201" if method.upper() == "POST" else "200"
    responses[default_status] = ResponseDef(
        description=get_status_description(int(default_status)),
        content={
            "application/json": {
                "schema": Schema(type="object"),
            }
        },
    )

    # Enhance with AST analysis
    try:
        source_code = get_handler_source_code(handler)
        if source_code:
            # Convert ResponseDef to dict for AST enhancement
            responses_dict = {}
            for status, resp_def in responses.items():
                resp_dict = {"description": resp_def.description}
                if resp_def.content:
                    resp_dict["content"] = {}
                    for content_type, content_data in resp_def.content.items():
                        resp_dict["content"][content_type] = {
                            "schema": dataclass_to_dict(content_data.get("schema"))
                            if "schema" in content_data
                            else {}
                        }
                responses_dict[status] = resp_dict

            # Enhance with AST
            enhanced = enhance_schema_with_ast(responses_dict, handler, source_code)

            # Convert back to ResponseDef
            for status, resp_data in enhanced.items():
                if "content" in resp_data:
                    content_dict = {}
                    for ct, ct_data in resp_data["content"].items():
                        content_dict[ct] = {
                            "schema": dict_to_schema(ct_data.get("schema", {}))
                        }

                    # Create or update response
                    if status in responses:
                        responses[status].content = content_dict
                    else:
                        responses[status] = ResponseDef(
                            description=resp_data.get("description", get_status_description(int(status))),
                            content=content_dict
                        )
    except Exception as e:
        # AST analysis failed, continue with existing responses
        pass

    return responses


def generate_summary(method: str, path: str) -> str:
    """Generate summary from method and path"""
    method_upper = method.upper()
    path_parts = [p for p in path.split("/") if p and not p.startswith("<")]
    resource = path_parts[-1] if path_parts else "resource"

    resource_name = resource.replace("-", " ").replace("_", " ").strip()

    summary_map = {
        "GET": f"Get {resource_name}" if "<" in path else f"List {resource_name}",
        "POST": f"Create {resource_name}",
        "PUT": f"Update {resource_name}",
        "PATCH": f"Partially update {resource_name}",
        "DELETE": f"Delete {resource_name}",
    }

    return summary_map.get(method_upper, f"{method_upper} {resource_name}")


def infer_tags(path: str) -> List[str]:
    """Infer tags from path"""
    parts = [p for p in path.split("/") if p and not p.startswith("<")]
    if parts:
        tag = parts[0].replace("-", " ").replace("_", " ").title()
        return [tag]
    return ["Default"]


def get_status_description(status: int) -> str:
    """Get HTTP status description"""
    descriptions = {
        200: "Successful operation",
        201: "Resource created successfully",
        204: "No content",
        400: "Bad request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Resource not found",
        422: "Validation error",
        500: "Internal server error",
    }
    return descriptions.get(status, f"HTTP {status}")


def dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert dataclass Schema to dict"""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            if value is not None:
                if hasattr(value, "__dataclass_fields__"):
                    result[field_name] = dataclass_to_dict(value)
                elif isinstance(value, dict):
                    result[field_name] = {k: dataclass_to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in value.items()}
                elif isinstance(value, list):
                    result[field_name] = [dataclass_to_dict(item) if hasattr(item, "__dataclass_fields__") else item for item in value]
                else:
                    result[field_name] = value
        return result
    return obj


def dict_to_schema(data: Dict[str, Any]) -> Schema:
    """Convert dict to Schema dataclass"""
    schema_args = {}
    for key, value in data.items():
        if key in Schema.__dataclass_fields__:
            if key == "properties" and isinstance(value, dict):
                # Convert nested properties
                schema_args[key] = {k: dict_to_schema(v) if isinstance(v, dict) else v for k, v in value.items()}
            elif key == "items" and isinstance(value, dict):
                schema_args[key] = dict_to_schema(value)
            else:
                schema_args[key] = value
    return Schema(**schema_args) if schema_args else Schema(type="object")


def convert_path_to_openapi(path: str) -> str:
    """
    Convert Flask path format to OpenAPI format
    Flask: /users/<int:id> or /users/<id>
    OpenAPI: /users/{id}
    """
    # Replace <type:name> with {name}
    path = re.sub(r'<(?:\w+:)?(\w+)>', r'{\1}', path)
    return path
