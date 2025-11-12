"""
ByteDocs Flask - Main Documentation Engine
Based on ByteDocs FastAPI implementation
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import asdict
from flask import Flask, Blueprint, request, Response, jsonify

import yaml

from .types import (
    ByteDocsConfig,
    RouteInfo,
    Endpoint,
    Section,
    OpenAPISpec,
    OpenAPIServer,
    Parameter,
)
from .config import load_config_from_env, validate_config, merge_configs
from ..parser.route_analyzer import extract_routes, convert_path_to_openapi
from ..ui.handlers import (
    create_docs_ui_handler,
    create_api_data_handler,
    create_openapi_json_handler,
)


class ByteDocs:
    """Main ByteDocs documentation class for Flask"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
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

        self.routes: List[RouteInfo] = []
        self.endpoints: List[Endpoint] = []
        self.sections: List[Section] = []
        self.generated = False

        # Add docs path to exclude paths
        if self.config.docs_path not in self.config.exclude_paths:
            self.config.exclude_paths.append(self.config.docs_path)

    def setup_flask(self, app: Flask) -> None:
        """Setup ByteDocs for Flask application"""
        docs_path = self.config.docs_path

        # Create a blueprint for docs routes
        bp = Blueprint('bytedocs', __name__)

        # Main documentation route
        @bp.route('/')
        def docs_ui():
            # Auto-detect routes on first request
            if self.config.auto_detect and not self.generated:
                self.detect_routes(app)
                self.generate()

            handler = create_docs_ui_handler(
                lambda: self.get_documentation_data(), self.config
            )
            return handler()

        # API data endpoint
        @bp.route('/api-data.json')
        def api_data():
            if self.config.auto_detect and not self.generated:
                self.detect_routes(app)
                self.generate()

            handler = create_api_data_handler(
                lambda: self.get_documentation_data(), self.config
            )
            return handler()

        # OpenAPI JSON endpoint
        @bp.route('/openapi.json')
        def openapi_json():
            if self.config.auto_detect and not self.generated:
                self.detect_routes(app)
                self.generate()

            handler = create_openapi_json_handler(
                lambda: self.get_openapi_spec(), self.config
            )
            return handler()

        # OpenAPI YAML endpoint
        @bp.route('/openapi.yaml')
        def openapi_yaml():
            if self.config.auto_detect and not self.generated:
                self.detect_routes(app)
                self.generate()

            try:
                spec = self.get_openapi_spec()
                # Convert dataclasses to dict for YAML serialization
                spec_dict = self._to_dict(spec)
                yaml_content = yaml.dump(
                    spec_dict, indent=2, default_flow_style=False, sort_keys=False
                )

                return Response(
                    yaml_content,
                    mimetype='application/x-yaml',
                    headers={
                        'Content-Disposition': 'attachment; filename="openapi.yaml"'
                    }
                )
            except Exception as e:
                import traceback
                print(f"[ByteDocs] Failed to generate YAML: {e}")
                traceback.print_exc()
                return jsonify({
                    "success": False,
                    "error": "Failed to export OpenAPI YAML",
                    "message": str(e),
                }), 500

        # AI Chat endpoint (if AI is enabled)
        if self.config.ai_config and self.config.ai_config.enabled:
            @bp.route('/chat', methods=['POST'])
            def ai_chat():
                """Chat with AI assistant about API documentation"""
                try:
                    # Get request data
                    data = request.get_json()
                    message = data.get('message')
                    endpoint_id = data.get('endpoint_id')

                    # Import AI modules
                    from ..ai import create_client, ChatRequest as AIChatRequest
                    from ..ai.context_optimizer import get_optimizer

                    # Create AI client
                    ai_client = create_client(self.config.ai_config)

                    # Get OpenAPI spec as context
                    if not self.generated:
                        self.detect_routes(app)
                        self.generate()

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
                    ai_request = AIChatRequest(
                        message=message,
                        context=optimized_context,
                        endpoint=endpoint_data,
                    )

                    # Get response from AI (handle both sync and async)
                    import asyncio
                    if asyncio.iscoroutinefunction(ai_client.chat):
                        # If the chat method is async, we need to run it in event loop
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        response = loop.run_until_complete(ai_client.chat(ai_request))
                        loop.close()
                    else:
                        response = ai_client.chat(ai_request)

                    return jsonify({
                        "response": response.response,
                        "provider": response.provider,
                        "model": response.model,
                        "tokensUsed": response.tokens_used,
                        "tokensSaved": savings["tokens_saved"],
                        "error": response.error,
                    })

                except Exception as e:
                    import traceback
                    print(f"[ByteDocs] AI Chat error: {e}")
                    traceback.print_exc()
                    return jsonify({
                        "success": False,
                        "error": "AI chat failed",
                        "message": str(e),
                    }), 500

        # Register blueprint
        app.register_blueprint(bp, url_prefix=docs_path)

        # Auto-detect routes immediately if enabled
        if self.config.auto_detect:
            self.detect_routes(app)
            self.generate()

    def detect_routes(self, app: Flask) -> None:
        """Detect routes from Flask application"""
        self.routes = extract_routes(app, self.config.exclude_paths)

    def add_route(self, route: RouteInfo) -> None:
        """Add route manually"""
        self.routes.append(route)
        self.generated = False

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

        self.generated = True

    def _route_to_endpoint(self, route: RouteInfo) -> Endpoint:
        """Convert route to endpoint"""
        path = convert_path_to_openapi(route.path)
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

    def _get_default_responses(self, method: str) -> Dict[str, Any]:
        """Get default responses for method"""
        from .types import ResponseDef, Schema

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
        info = {
            "title": self.config.title or "API Documentation",
            "version": self.config.version or "1.0.0",
        }

        # Only add description if not None (OpenAPI spec requirement)
        if self.config.description:
            info["description"] = self.config.description

        spec = {
            "openapi": "3.0.3",
            "info": info,
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
                "tags": endpoint.tags,
                "parameters": [self._to_dict(p) for p in endpoint.parameters],
                "responses": {
                    status: self._to_dict(resp)
                    for status, resp in endpoint.responses.items()
                },
            }

            # Only add description if not None (OpenAPI spec requirement)
            if endpoint.description:
                operation["description"] = endpoint.description

            if endpoint.request_body:
                operation["requestBody"] = self._to_dict(endpoint.request_body)

            if endpoint.operation_id:
                operation["operationId"] = endpoint.operation_id

            if endpoint.deprecated:
                operation["deprecated"] = True

            spec["paths"][endpoint.path][endpoint.method.lower()] = operation

        return spec

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
            # For non-serializable objects, try to convert to string or return None
            try:
                # Try json.dumps to see if it's serializable
                import json
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                # Not serializable, return None or str representation
                return None


def setup_bytedocs(app: Flask, config: Optional[Dict[str, Any]] = None) -> ByteDocs:
    """Setup ByteDocs for Flask (convenience function)"""
    bytedocs = ByteDocs(config)
    bytedocs.setup_flask(app)
    return bytedocs
