"""
OpenRouter Provider Client
Based on bytedocs-go OpenRouter implementation
"""

import os
from typing import Optional
from openai import AsyncOpenAI

from ..types import AIConfig, AIClient, ChatRequest, ChatResponse
from ..context_optimizer import get_optimizer


class OpenRouterClient(AIClient):
    """OpenRouter client implementation (OpenAI-compatible)"""

    def __init__(self, config: AIConfig):
        self.config = config

        # Get API key from config or environment
        api_key = config.api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenRouter API key is required (set api_key in config or OPENROUTER_API_KEY environment variable)"
            )

        # Create OpenAI-compatible client with OpenRouter base URL
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        # Default model
        self.model = config.features.model or "openai/gpt-3.5-turbo"

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send chat request to OpenRouter"""
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self._build_system_prompt(request)},
                {"role": "user", "content": request.message},
            ]

            # Prepare kwargs
            kwargs = {
                "model": self.model,
                "messages": messages,
            }

            # Add optional parameters
            if self.config.features.max_tokens > 0:
                kwargs["max_tokens"] = self.config.features.max_tokens
            if self.config.features.max_completion_tokens > 0:
                kwargs["max_completion_tokens"] = self.config.features.max_completion_tokens
            if self.config.features.temperature > 0:
                kwargs["temperature"] = self.config.features.temperature

            # Make API call
            response = await self.client.chat.completions.create(**kwargs)

            # Extract response
            if not response.choices:
                raise ValueError("No response choices returned")

            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            return ChatResponse(
                response=content,
                provider=self.get_provider(),
                model=response.model,
                tokens_used=tokens_used,
            )

        except Exception as e:
            return ChatResponse(
                response="",
                provider=self.get_provider(),
                model=self.model,
                error=str(e),
            )

    def get_provider(self) -> str:
        """Get provider name"""
        return "openrouter"

    def get_model(self) -> str:
        """Get model name"""
        return self.model

    def _build_system_prompt(self, request: ChatRequest) -> str:
        """Build optimized system prompt with context"""
        optimizer = get_optimizer()

        # Use optimized prompt
        base_prompt = optimizer.optimize_system_prompt("")

        # Add API context (OpenAPI JSON) - already optimized
        if request.context:
            base_prompt += f"\n\nAPI Spec:\n{request.context}"

        # Add endpoint context if provided
        if request.endpoint:
            base_prompt += "\n\nFocused endpoint provided. Prioritize info about this endpoint."

        return base_prompt
