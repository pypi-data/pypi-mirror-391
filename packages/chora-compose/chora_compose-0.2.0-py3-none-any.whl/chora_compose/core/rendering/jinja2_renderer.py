"""Jinja2 template renderer."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

from chora_compose.models.template import Template
from .base import TemplateRenderer


class Jinja2Renderer(TemplateRenderer):
    """Jinja2-based template renderer for deterministic templates.

    Uses Jinja2's StrictUndefined to catch missing variables at render time.

    Attributes:
        env: Jinja2 Environment with FileSystemLoader

    Examples:
        >>> renderer = Jinja2Renderer(template_dir=Path("templates"))
        >>> template = Template(...)
        >>> content = renderer.render(template, {"name": "World"})
    """

    def __init__(self, template_dir: Path | str | None = None):
        """Initialize Jinja2 renderer.

        Args:
            template_dir: Directory containing Jinja2 templates (default: "templates")
        """
        if template_dir is None:
            template_dir = Path("templates")
        else:
            template_dir = Path(template_dir)

        # Create environment with strict undefined checking
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            undefined=StrictUndefined,  # Raise error on undefined variables
        )

    def render(self, template: Template, context: dict[str, Any]) -> str:
        """Render Jinja2 template with context.

        Args:
            template: Template with JINJA2 generator type
            context: Runtime context variables

        Returns:
            Rendered content as string

        Raises:
            FileNotFoundError: If template file not found
            TemplateSyntaxError: If template has syntax errors
            UndefinedError: If template references undefined variable
        """
        # Get template path from generator_config
        template_path = template.generator_config.get("template_path")
        if not template_path:
            raise ValueError(
                "Jinja2 template requires 'template_path' in generator_config"
            )

        # Merge default_context with runtime context (runtime overrides default)
        merged_context = {**template.default_context, **context}

        try:
            # Load and render template
            jinja_template = self.env.get_template(template_path)
            return jinja_template.render(**merged_context)
        except TemplateNotFound:
            # Convert Jinja2 exception to FileNotFoundError
            raise FileNotFoundError(
                f"Jinja2 template file not found: {template_path}"
            ) from None
