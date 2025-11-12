"""
AI Provider Clients
Register all available providers
"""

from ..factory import register_client_factory

# Try to import each provider, register only if available
_available_clients = []

# OpenAI
try:
    from .openai_client import OpenAIClient
    register_client_factory("openai", lambda config: OpenAIClient(config))
    _available_clients.append("OpenAIClient")
except ImportError:
    pass

# Gemini
try:
    from .gemini_client import GeminiClient
    register_client_factory("gemini", lambda config: GeminiClient(config))
    _available_clients.append("GeminiClient")
except ImportError:
    pass

# Anthropic
try:
    from .anthropic_client import AnthropicClient
    register_client_factory("anthropic", lambda config: AnthropicClient(config))
    _available_clients.append("AnthropicClient")
except ImportError:
    pass

# OpenRouter
try:
    from .openrouter_client import OpenRouterClient
    register_client_factory("openrouter", lambda config: OpenRouterClient(config))
    _available_clients.append("OpenRouterClient")
except ImportError:
    pass


__all__ = _available_clients
