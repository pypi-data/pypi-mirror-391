"""
ByteDocs Flask - UI Handlers
Handle documentation UI requests
"""

import json
from typing import Any, Callable, Dict
from flask import Response, request, jsonify

from .template_loader import load_template


def create_docs_ui_handler(get_doc_data: Callable[[], Any], config: Any):
    """Create documentation UI handler"""

    def handler():
        try:
            template = load_template("template.html")
            doc_data = get_doc_data()

            # Prepare config data for frontend
            # Convert base_urls to dict format (handle dataclass or dict)
            base_urls = []
            if config.base_urls:
                for url in config.base_urls:
                    if hasattr(url, 'name'):  # dataclass
                        base_urls.append({"name": url.name, "url": url.url})
                    else:  # dict
                        base_urls.append(url)
            elif config.base_url:
                base_urls = [{"name": "Default", "url": config.base_url}]

            frontend_config = {
                "title": config.title or "API Documentation",
                "version": config.version or "1.0.0",
                "description": config.description or "",
                "baseUrls": base_urls,
            }

            # Replace placeholders with actual data
            rendered = template
            rendered = rendered.replace(
                "__BYTEDOCS_API_DATA__", json.dumps(doc_data, default=str)
            )
            rendered = rendered.replace(
                "__BYTEDOCS_CONFIG_DATA__", json.dumps(frontend_config, default=str)
            )
            rendered = rendered.replace(
                "__BYTEDOCS_TITLE__", config.title or "API Documentation"
            )
            rendered = rendered.replace(
                "__BYTEDOCS_VERSION__", config.version or "1.0.0"
            )
            rendered = rendered.replace(
                "__BYTEDOCS_DESCRIPTION__",
                config.description or "Modern API Documentation",
            )

            return Response(rendered, mimetype='text/html')

        except Exception as e:
            import traceback
            print(f"[ByteDocs] Error rendering docs UI: {e}")
            traceback.print_exc()
            return jsonify({
                "error": "Failed to render documentation",
                "detail": str(e)
            }), 500

    return handler


def create_api_data_handler(get_doc_data: Callable[[], Any], config: Any):
    """Create API data JSON handler"""

    def handler():
        try:
            doc_data = get_doc_data()
            return jsonify(doc_data)
        except Exception as e:
            print(f"[ByteDocs] Error getting API data: {e}")
            return jsonify({
                "error": "Failed to get API data"
            }), 500

    return handler


def create_openapi_json_handler(get_openapi_spec: Callable[[], Any], config: Any):
    """Create OpenAPI JSON handler"""

    def handler():
        try:
            spec = get_openapi_spec()
            return jsonify(spec)
        except Exception as e:
            print(f"[ByteDocs] Error generating OpenAPI spec: {e}")
            return jsonify({
                "error": "Failed to generate OpenAPI specification"
            }), 500

    return handler


def get_client_ip() -> str:
    """Get client IP address from request"""
    # Check X-Forwarded-For header first
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Fall back to remote_addr
    return request.remote_addr or "unknown"
