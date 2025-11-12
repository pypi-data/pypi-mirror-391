"""
Google Gemini Provider Client
Based on bytedocs-go Gemini implementation
"""

import os
from typing import Optional
import google.generativeai as genai

from ..types import AIConfig, AIClient, ChatRequest, ChatResponse
from ..context_optimizer import get_optimizer


class GeminiClient(AIClient):
    """Google Gemini client implementation"""

    def __init__(self, config: AIConfig):
        self.config = config

        # Get API key from config or environment
        api_key = config.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Gemini API key is required (set api_key in config or GEMINI_API_KEY environment variable)"
            )

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Default model
        self.model_name = config.features.model or "gemini-2.0-flash-exp"

        # Create model
        generation_config = {
            "temperature": config.features.temperature,
        }
        if config.features.max_tokens > 0:
            generation_config["max_output_tokens"] = config.features.max_tokens

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
        )

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send chat request to Gemini"""
        try:
            # Build full prompt (Gemini doesn't have separate system/user messages in the same way)
            full_prompt = self._build_system_prompt(request) + f"\n\nUser: {request.message}"

            # Make API call
            response = await self.model.generate_content_async(full_prompt)

            # Extract response
            if not response.text:
                raise ValueError("No response content returned")

            # Get tokens used (if available)
            tokens_used = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                tokens_used = response.usage_metadata.total_token_count

            return ChatResponse(
                response=response.text,
                provider=self.get_provider(),
                model=self.model_name,
                tokens_used=tokens_used,
            )

        except Exception as e:
            return ChatResponse(
                response="",
                provider=self.get_provider(),
                model=self.model_name,
                error=str(e),
            )

    def get_provider(self) -> str:
        """Get provider name"""
        return "gemini"

    def get_model(self) -> str:
        """Get model name"""
        return self.model_name

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
