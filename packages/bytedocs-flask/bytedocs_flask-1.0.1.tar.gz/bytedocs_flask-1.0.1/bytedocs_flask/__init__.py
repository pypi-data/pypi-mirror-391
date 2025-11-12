"""
ByteDocs Flask - Automatic API Documentation Generator
Inspired by Scramble for Laravel, based on ByteDocs Express and ByteDocs FastAPI
"""

from .core.bytedocs import ByteDocs, setup_bytedocs
from .core.config import load_config_from_env, validate_config, merge_configs
from .core.types import (
    ByteDocsConfig,
    AuthConfig,
    UIConfig,
    AIConfig,
    BaseURLOption,
    Endpoint,
    Parameter,
    RequestBody,
    ResponseDef,
    Schema,
    Section,
    RouteInfo,
)
from .parser.route_analyzer import extract_routes, convert_path_to_openapi

__version__ = "1.0.0"
__author__ = "ByteDocs Contributors"

__all__ = [
    # Main classes
    "ByteDocs",
    "setup_bytedocs",
    # Config functions
    "load_config_from_env",
    "validate_config",
    "merge_configs",
    # Types
    "ByteDocsConfig",
    "AuthConfig",
    "UIConfig",
    "AIConfig",
    "BaseURLOption",
    "Endpoint",
    "Parameter",
    "RequestBody",
    "ResponseDef",
    "Schema",
    "Section",
    "RouteInfo",
    # Parser functions
    "extract_routes",
    "convert_path_to_openapi",
]
