"""Artifact model for generated content with freshness tracking.

This module implements the Artifact model following
chora-compose v3.0.0 design specification.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .freshness import FreshnessPolicy


class Artifact(BaseModel):
    """Generated artifact with freshness tracking.

    Attributes:
        id: Unique identifier (e.g., "sap-029/overview.md")
        content: Generated content (text)
        template_id: Template used for generation
        context: Generation context (variables passed to template)
        generated_at: When artifact was generated (UTC)
        freshness_policy: Policy for determining staleness
        collection_id: Parent collection (if member), optional

    Examples:
        >>> from datetime import datetime, timezone
        >>> artifact = Artifact(
        ...     id="hello.md",
        ...     content="# Hello World",
        ...     template_id="hello-template",
        ...     context={"name": "World"},
        ...     generated_at=datetime.now(timezone.utc),
        ...     freshness_policy=FreshnessPolicy.daily()
        ... )
        >>> artifact.id
        'hello.md'
        >>> artifact.is_fresh
        True
    """

    id: str = Field(..., min_length=1, description="Unique artifact identifier")
    content: str = Field(default="", description="Generated content (can be empty for placeholders)")
    template_id: str = Field(..., min_length=1, description="Template used for generation")
    context: dict[str, Any] = Field(default_factory=dict, description="Generation context")
    generated_at: datetime = Field(..., description="When artifact was generated (UTC)")
    freshness_policy: FreshnessPolicy = Field(..., description="Freshness policy")
    collection_id: str | None = Field(default=None, description="Parent collection (optional)")

    @field_validator("generated_at")
    @classmethod
    def validate_generated_at(cls, v: datetime) -> datetime:
        """Validate generated_at is not in the future and has UTC timezone.

        Args:
            v: generated_at timestamp

        Returns:
            Validated timestamp with UTC timezone

        Raises:
            ValueError: If timestamp is in the future
        """
        # Ensure timezone is set (convert naive to UTC)
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)

        # Check not in future (allow 1 second tolerance for clock skew)
        now = datetime.now(timezone.utc)
        if v > now + timedelta(seconds=1):
            raise ValueError(
                f"generated_at cannot be in the future. "
                f"Got: {v.isoformat()}, Now: {now.isoformat()}"
            )

        return v

    @property
    def age_days(self) -> float:
        """Age of artifact in days since generation.

        Returns:
            Age in days (fractional)

        Examples:
            >>> artifact.age_days  # doctest: +SKIP
            2.5
        """
        now = datetime.now(timezone.utc)
        age_seconds = (now - self.generated_at).total_seconds()
        return age_seconds / 86400

    @property
    def is_fresh(self) -> bool:
        """Check if artifact is fresh based on freshness policy.

        Returns:
            True if age < max_age_days, False otherwise

        Examples:
            >>> # Artifact generated 1 day ago with 7-day policy
            >>> artifact.is_fresh  # doctest: +SKIP
            True
        """
        return self.age_days < self.freshness_policy.max_age_days
