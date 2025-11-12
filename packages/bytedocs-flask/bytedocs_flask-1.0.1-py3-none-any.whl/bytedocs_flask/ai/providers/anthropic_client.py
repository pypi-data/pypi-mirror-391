"""
Anthropic Claude Provider Client
"""

import os
from typing import Optional
from anthropic import AsyncAnthropic

from ..types import AIConfig, AIClient, ChatRequest, ChatResponse
from ..context_optimizer import get_optimizer


class AnthropicClient(AIClient):
    """Anthropic Claude client implementation"""

    def __init__(self, config: AIConfig):
        self.config = config

        # Get API key from config or environment
        api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key is required (set api_key in config or ANTHROPIC_API_KEY environment variable)"
            )

        # Create Anthropic client
        self.client = AsyncAnthropic(api_key=api_key)

        # Default model
        self.model = config.features.model or "claude-3-5-sonnet-20241022"

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send chat request to Anthropic Claude"""
        try:
            # Make API call
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.config.features.max_tokens or 1024,
                temperature=self.config.features.temperature,
                system=self._build_system_prompt(request),
                messages=[
                    {"role": "user", "content": request.message}
                ],
            )

            # Extract response
            if not response.content:
                raise ValueError("No response content returned")

            content = response.content[0].text if response.content else ""
            tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else 0

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
        return "anthropic"

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
