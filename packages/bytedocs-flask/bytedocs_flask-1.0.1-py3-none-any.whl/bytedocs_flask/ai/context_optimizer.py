"""
Context Optimizer for LLM Token Reduction
Implements JSON minification, context compression, and prompt optimization
"""

import json
from typing import Dict, Any, Optional


class ContextOptimizer:
    """Optimize context for LLM to reduce token usage"""

    def __init__(self):
        # Fields to keep in OpenAPI spec (remove unnecessary fields)
        self.essential_fields = {
            "paths": True,
            "info": ["title", "version"],
            "servers": True,
            "tags": True,
        }

    def minify_json(self, data: Dict[str, Any]) -> str:
        """Minify JSON by removing whitespace and formatting

        Token Savings: ~30-40%
        """
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

    def compress_openapi_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Compress OpenAPI spec by removing non-essential fields

        Token Savings: ~40-60%
        """
        compressed = {}

        # Keep only essential info fields
        if "info" in spec:
            compressed["info"] = {
                "title": spec["info"].get("title", ""),
                "version": spec["info"].get("version", "")
            }

        # Keep servers (base URLs)
        if "servers" in spec:
            compressed["servers"] = spec["servers"]

        # Compress paths - this is the main content
        if "paths" in spec:
            compressed["paths"] = self._compress_paths(spec["paths"])

        # Keep tags for organization
        if "tags" in spec:
            compressed["tags"] = spec["tags"]

        return compressed

    def _compress_paths(self, paths: Dict[str, Any]) -> Dict[str, Any]:
        """Compress paths by removing verbose descriptions and examples

        Keep only:
        - Method
        - Summary (short description)
        - Parameters (name, in, required, type)
        - Request body schema (minimal)
        - Response status codes
        """
        compressed_paths = {}

        for path, methods in paths.items():
            compressed_paths[path] = {}

            for method, details in methods.items():
                if method.startswith("_"):  # Skip private fields
                    continue

                compressed_method = {}

                # Summary only (no long description)
                if "summary" in details:
                    compressed_method["s"] = details["summary"]  # Shortened key

                # Tags
                if "tags" in details:
                    compressed_method["t"] = details["tags"]

                # Parameters - minimal info
                if "parameters" in details and details["parameters"]:
                    compressed_method["p"] = [
                        {
                            "n": p.get("name"),  # name
                            "i": p.get("in"),     # in (location)
                            "r": p.get("required", False),  # required
                            "t": self._get_param_type(p)    # type
                        }
                        for p in details["parameters"]
                    ]

                # Request body - just schema type
                if "requestBody" in details:
                    req_body = details["requestBody"]
                    if "content" in req_body:
                        for content_type, content_data in req_body["content"].items():
                            if "schema" in content_data:
                                compressed_method["rb"] = self._compress_schema(
                                    content_data["schema"]
                                )
                                break  # Only take first content type

                # Responses - just status codes
                if "responses" in details:
                    compressed_method["rs"] = list(details["responses"].keys())

                compressed_paths[path][method] = compressed_method

        return compressed_paths

    def _get_param_type(self, param: Dict[str, Any]) -> str:
        """Extract parameter type from schema"""
        if "schema" in param:
            schema = param["schema"]
            if isinstance(schema, dict):
                return schema.get("type", "string")
        return "string"

    def _compress_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Compress schema to minimal representation"""
        if not isinstance(schema, dict):
            return {}

        compressed = {}

        # Type
        if "type" in schema:
            compressed["t"] = schema["type"]

        # Properties (for objects)
        if "properties" in schema:
            compressed["pr"] = {}
            for prop_name, prop_schema in schema["properties"].items():
                if isinstance(prop_schema, dict):
                    compressed["pr"][prop_name] = {
                        "t": prop_schema.get("type", "string")
                    }

        # Required fields
        if "required" in schema:
            compressed["r"] = schema["required"]

        return compressed

    def optimize_system_prompt(self, base_prompt: str) -> str:
        """Optimize system prompt to reduce tokens while maintaining effectiveness

        Token Savings: ~50-60%
        """
        # Shortened, more concise prompt
        optimized = """You're an API docs assistant. Use ONLY the provided OpenAPI spec.

Rules:
1. Only mention endpoints in the spec
2. Never invent endpoints/params
3. If endpoint doesn't exist, say so
4. Be clear and detailed in responses
5. Match user's language

The spec uses shortened keys to save tokens:
- s = summary
- t = tags
- p = parameters (n=name, i=in, r=required, t=type)
- rb = request body (pr=properties)
- rs = response statuses

IMPORTANT: When responding to users, always use FULL descriptive text, NOT abbreviations.
Example:
Bad: "s: Get users, t: [Users], rs: [200]"
Good: "GET /users - Get all users. Tags: Users. Returns status 200."

Format your responses clearly with proper labels like:
- Endpoint, Method, Summary, Description
- Parameters, Request Body, Responses
Use complete sentences and proper formatting."""

        return optimized

    def get_optimized_context(
        self,
        openapi_spec: Dict[str, Any],
        endpoint_id: Optional[str] = None
    ) -> str:
        """Get fully optimized context for LLM

        Combines all optimization techniques:
        1. Compress spec (remove non-essential fields)
        2. Filter by endpoint if provided
        3. Minify JSON

        Total Token Savings: ~70-80%
        """
        # Step 1: Compress the spec
        compressed_spec = self.compress_openapi_spec(openapi_spec)

        # Step 2: If endpoint_id provided, filter to relevant paths only
        if endpoint_id and "paths" in compressed_spec:
            compressed_spec = self._filter_by_endpoint(compressed_spec, endpoint_id)

        # Step 3: Minify to remove whitespace
        minified = self.minify_json(compressed_spec)

        return minified

    def _filter_by_endpoint(
        self,
        spec: Dict[str, Any],
        endpoint_id: str
    ) -> Dict[str, Any]:
        """Filter spec to only include relevant endpoint and related ones

        For example, if asking about POST /users, include:
        - POST /users (exact match)
        - GET /users (same resource)
        - GET /users/{id} (related resource)
        """
        if "paths" not in spec:
            return spec

        # Extract path from endpoint_id (format: method_path_params)
        # e.g., "post_users" -> "/users"
        path_part = endpoint_id.lower().replace("_", "/")

        # Find matching and related paths
        filtered_paths = {}
        for path, methods in spec["paths"].items():
            path_normalized = path.lower().replace("{", "").replace("}", "")

            # Include if path matches or is related
            if path_part in path_normalized or path_normalized in path_part:
                filtered_paths[path] = methods

        # If we found related paths, use them; otherwise return all
        if filtered_paths:
            spec["paths"] = filtered_paths

        return spec

    def estimate_token_savings(
        self,
        original_size: int,
        optimized_size: int
    ) -> Dict[str, Any]:
        """Estimate token savings (rough approximation: 1 token ≈ 4 chars)"""
        original_tokens = original_size / 4
        optimized_tokens = optimized_size / 4
        saved_tokens = original_tokens - optimized_tokens
        percentage = (saved_tokens / original_tokens * 100) if original_tokens > 0 else 0

        return {
            "original_chars": original_size,
            "optimized_chars": optimized_size,
            "original_tokens_est": int(original_tokens),
            "optimized_tokens_est": int(optimized_tokens),
            "tokens_saved": int(saved_tokens),
            "percentage_saved": f"{percentage:.1f}%"
        }


# Global optimizer instance
_optimizer = ContextOptimizer()


def get_optimizer() -> ContextOptimizer:
    """Get global context optimizer instance"""
    return _optimizer
