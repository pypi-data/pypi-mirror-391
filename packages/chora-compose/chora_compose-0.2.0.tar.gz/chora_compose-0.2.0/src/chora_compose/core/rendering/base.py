"""Abstract base class for template renderers."""

from abc import ABC, abstractmethod
from typing import Any

from chora_compose.models.template import Template


class TemplateRenderer(ABC):
    """Abstract base class for template rendering.

    Subclasses must implement the render() method to support
    different rendering backends (LLM, Jinja2, etc.).
    """

    @abstractmethod
    def render(self, template: Template, context: dict[str, Any]) -> str:
        """Render template with context.

        Args:
            template: Template to render
            context: Runtime context variables

        Returns:
            Rendered content as string

        Raises:
            ValueError: If template or context is invalid
            RuntimeError: If rendering fails
        """
        pass
