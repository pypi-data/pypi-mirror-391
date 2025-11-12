"""
AI Types and Configuration
Based on bytedocs-go AI implementation
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod


@dataclass
class AIFeatures:
    """AI feature configuration"""
    chat_enabled: bool = True
    doc_generation_enabled: bool = False
    model: str = ""
    max_tokens: int = 0
    max_completion_tokens: int = 0
    temperature: float = 0.7


@dataclass
class AIConfig:
    """AI configuration for providers"""
    provider: str  # openai, gemini, anthropic, openrouter, etc.
    api_key: str = ""
    enabled: bool = False
    features: AIFeatures = field(default_factory=AIFeatures)
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatRequest:
    """Chat request model"""
    message: str
    context: Optional[str] = None
    endpoint: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatResponse:
    """Chat response model"""
    response: str
    provider: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None


class AIClient(ABC):
    """Base AI client interface"""

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send chat request and get response"""
        pass

    @abstractmethod
    def get_provider(self) -> str:
        """Get provider name"""
        pass

    @abstractmethod
    def get_model(self) -> str:
        """Get model name"""
        pass


class ClientFactory(Protocol):
    """Protocol for client factory functions"""

    def __call__(self, config: AIConfig) -> AIClient:
        """Create AI client from config"""
        ...
