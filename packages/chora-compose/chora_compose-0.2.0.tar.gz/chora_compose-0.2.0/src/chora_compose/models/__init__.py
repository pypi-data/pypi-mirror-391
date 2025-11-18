"""Data models for chora-compose v3.0.0.

This module provides Pydantic V2 models for:
- Artifact: Generated content with freshness metadata
- Collection: Group of artifacts with shared configuration
- Template: Blueprint for generating artifacts
- FreshnessPolicy: Time-based staleness rules
"""

from .artifact import Artifact
from .collection import Collection
from .freshness import FreshnessPolicy
from .template import GeneratorType, Template

__all__ = [
    "Artifact",
    "Collection",
    "FreshnessPolicy",
    "GeneratorType",
    "Template",
]
