"""Factory for selecting renderer based on template type."""

from chora_compose.models.template import GeneratorType, Template
from .base import TemplateRenderer
from .jinja2_renderer import Jinja2Renderer
from .llm_renderer import LLMRenderer


class RendererFactory:
    """Factory for creating renderer instances based on Template.generator."""

    @staticmethod
    def get_renderer(template: Template) -> TemplateRenderer:
        """Get appropriate renderer for template.

        Args:
            template: Template with generator type

        Returns:
            Renderer instance (LLMRenderer or Jinja2Renderer)

        Raises:
            ValueError: If generator type is unknown
        """
        if template.generator == GeneratorType.JINJA2:
            return Jinja2Renderer()
        elif template.generator == GeneratorType.LLM:
            return LLMRenderer()
        else:
            raise ValueError(f"Unknown generator type: {template.generator}")
