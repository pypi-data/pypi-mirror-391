"""LLM template renderer using Anthropic API."""

import os
import time
from typing import Any

from anthropic import Anthropic, APIError, AuthenticationError, RateLimitError

from chora_compose.models.template import Template
from .base import TemplateRenderer


class LLMRenderer(TemplateRenderer):
    """LLM-based renderer using Anthropic Claude.

    Uses the Anthropic SDK with retry logic for transient errors.

    Attributes:
        client: Anthropic API client instance

    Examples:
        >>> renderer = LLMRenderer()
        >>> template = Template(...)
        >>> content = renderer.render(template, {"name": "World"})
    """

    def __init__(self):
        """Initialize LLM renderer with Anthropic client.

        Raises:
            ValueError: If ANTHROPIC_API_KEY environment variable is not set
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not found. "
                "Please set it to use the LLM renderer."
            )

        self.client = Anthropic(api_key=api_key)

    def render(self, template: Template, context: dict[str, Any]) -> str:
        """Render template with LLM.

        Args:
            template: Template with LLM generator type
            context: Runtime context variables

        Returns:
            Generated content from LLM

        Raises:
            ValueError: If required generator_config fields are missing
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit exceeded after retries
            APIError: If API error occurs after retries
        """
        # Get configuration
        prompt_template = template.generator_config.get("prompt")
        if not prompt_template:
            raise ValueError("LLM template requires 'prompt' in generator_config")

        model = template.generator_config.get("model", "claude-3-5-sonnet-20241022")

        # Merge contexts (runtime overrides default)
        merged_context = {**template.default_context, **context}

        # Format prompt with context
        formatted_prompt = prompt_template.format(**merged_context)

        # Call API with retry logic
        return self._call_api_with_retry(model=model, prompt=formatted_prompt)

    def _call_api_with_retry(
        self, model: str, prompt: str, max_attempts: int = 3
    ) -> str:
        """Call Anthropic API with exponential backoff retry.

        Args:
            model: Model ID to use
            prompt: Formatted prompt
            max_attempts: Maximum number of retry attempts

        Returns:
            Generated content from LLM

        Raises:
            AuthenticationError: If API key is invalid (no retry)
            RateLimitError: If rate limit exceeded after retries
            APIError: If API error occurs after retries
        """
        last_exception = None

        for attempt in range(max_attempts):
            try:
                message = self.client.messages.create(
                    model=model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )
                # Extract text from first content block
                return message.content[0].text

            except AuthenticationError:
                # Don't retry authentication errors
                raise

            except (RateLimitError, APIError) as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2**attempt
                    time.sleep(wait_time)
                    continue
                # Last attempt failed, re-raise
                raise

        # This shouldn't be reached, but just in case
        if last_exception:
            raise last_exception
