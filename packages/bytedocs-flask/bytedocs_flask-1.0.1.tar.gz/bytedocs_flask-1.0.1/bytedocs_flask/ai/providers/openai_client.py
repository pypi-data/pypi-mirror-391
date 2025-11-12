"""
OpenAI Provider Client
Based on bytedocs-go OpenAI implementation
"""

import os
from typing import Optional
from openai import AsyncOpenAI

from ..types import AIConfig, AIClient, ChatRequest, ChatResponse
from ..context_optimizer import get_optimizer


class OpenAIClient(AIClient):
    """OpenAI client implementation"""

    def __init__(self, config: AIConfig):
        self.config = config

        # Get API key from config or environment
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is required (set api_key in config or OPENAI_API_KEY environment variable)"
            )

        # Create OpenAI client
        self.client = AsyncOpenAI(api_key=api_key)

        # Default model
        self.model = config.features.model or "gpt-4o-mini"

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send chat request to OpenAI"""
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self._build_system_prompt(request)},
                {"role": "user", "content": request.message},
            ]

            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config.features.temperature,
                max_tokens=self.config.features.max_tokens if self.config.features.max_tokens > 0 else None,
            )

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
        return "openai"

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
