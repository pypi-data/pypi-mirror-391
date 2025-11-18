"""Template model for artifact generation blueprints.

This module implements the Template model following
chora-compose v3.0.0 design specification.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class GeneratorType(str, Enum):
    """Type of generator for template.

    Attributes:
        LLM: LLM-based generation (prompt + model)
        JINJA2: Jinja2 template rendering
    """

    LLM = "llm"
    JINJA2 = "jinja2"


class Template(BaseModel):
    """Template for generating artifacts.

    Attributes:
        id: Unique identifier (e.g., "sap-overview")
        validation_schema: JSON Schema for validation
        generator: How to generate (LLM vs Jinja2)
        generator_config: Generator-specific configuration
        default_context: Default variables for generation

    Generator-specific config structure:
        LLM: {"prompt": str, "model": str, "temperature": float (optional)}
        Jinja2: {"template_path": str, "filters": dict (optional)}

    Examples:
        >>> # LLM template
        >>> template = Template(
        ...     id="sap-overview",
        ...     validation_schema={"type": "object"},
        ...     generator=GeneratorType.LLM,
        ...     generator_config={"prompt": "Generate SAP", "model": "claude-3-5-sonnet-20241022"}
        ... )
        >>> template.generator
        <GeneratorType.LLM: 'llm'>

        >>> # Jinja2 template
        >>> template = Template(
        ...     id="readme",
        ...     validation_schema={"type": "object"},
        ...     generator=GeneratorType.JINJA2,
        ...     generator_config={"template_path": "templates/readme.j2"}
        ... )
        >>> template.generator
        <GeneratorType.JINJA2: 'jinja2'>
    """

    id: str = Field(..., min_length=1, description="Unique template identifier")
    validation_schema: dict[str, Any] = Field(..., description="JSON Schema for validation")
    generator: GeneratorType = Field(..., description="Generator type (LLM or Jinja2)")
    generator_config: dict[str, Any] = Field(..., description="Generator-specific configuration")
    default_context: dict[str, Any] = Field(default_factory=dict, description="Default variables")

    @field_validator("generator_config")
    @classmethod
    def validate_generator_config(cls, v: dict[str, Any], info) -> dict[str, Any]:
        """Validate generator_config matches generator type requirements.

        Args:
            v: generator_config dict
            info: Validation context with other field values

        Returns:
            Validated generator_config

        Raises:
            ValueError: If required keys are missing for generator type
        """
        # Get generator type from context (might not be set yet)
        generator = info.data.get("generator")
        if generator is None:
            # Generator not set yet, will be validated on next pass
            return v

        if generator == GeneratorType.LLM:
            # LLM requires "prompt" and "model"
            if "prompt" not in v:
                raise ValueError(
                    "LLM generator requires 'prompt' in generator_config. "
                    f"Got keys: {list(v.keys())}"
                )
            if "model" not in v:
                raise ValueError(
                    "LLM generator requires 'model' in generator_config. "
                    f"Got keys: {list(v.keys())}"
                )

        elif generator == GeneratorType.JINJA2:
            # Jinja2 requires "template_path"
            if "template_path" not in v:
                raise ValueError(
                    "Jinja2 generator requires 'template_path' in generator_config. "
                    f"Got keys: {list(v.keys())}"
                )

        return v
