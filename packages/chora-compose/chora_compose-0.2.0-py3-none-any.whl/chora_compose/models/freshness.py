"""FreshnessPolicy model for determining artifact staleness.

This module implements time-based freshness policies following
chora-compose v3.0.0 design specification.
"""

import math

from pydantic import BaseModel, field_serializer, field_validator


class FreshnessPolicy(BaseModel):
    """Policy for determining artifact freshness.

    Attributes:
        max_age_days: Maximum age in days before artifact is stale (fractional days supported)
        check_dependencies: Include dependency freshness in staleness check
        inherit_from_collection: Inherit collection policy if artifact is member

    Examples:
        >>> # Create daily refresh policy
        >>> policy = FreshnessPolicy.daily()
        >>> policy.max_age_days
        1.0

        >>> # Create custom policy with 12-hour expiration
        >>> policy = FreshnessPolicy(max_age_days=0.5)
        >>> policy.max_age_days
        0.5

        >>> # Create policy that never expires
        >>> policy = FreshnessPolicy.always_fresh()
        >>> math.isinf(policy.max_age_days)
        True
    """

    max_age_days: float
    check_dependencies: bool = True
    inherit_from_collection: bool = True

    @field_validator("max_age_days")
    @classmethod
    def validate_max_age_days(cls, v: float) -> float:
        """Validate max_age_days is positive or infinity.

        Args:
            v: max_age_days value

        Returns:
            Validated max_age_days

        Raises:
            ValueError: If max_age_days is not positive or infinity
        """
        # Handle special string "Infinity" from JSON deserialization
        if isinstance(v, str) and v == "Infinity":
            return float("inf")

        if not (v > 0 or math.isinf(v)):
            raise ValueError(
                "max_age_days must be positive (> 0) or infinity. "
                f"Got: {v}. Use float('inf') for never-expiring content."
            )
        return v

    @field_serializer("max_age_days")
    def serialize_max_age_days(self, value: float) -> float | str:
        """Serialize infinity as string 'Infinity' for JSON compatibility.

        Args:
            value: max_age_days value

        Returns:
            Original value, or "Infinity" string if value is infinite
        """
        if math.isinf(value):
            return "Infinity"
        return value

    @classmethod
    def always_fresh(cls) -> "FreshnessPolicy":
        """Create policy that never expires (max_age_days = infinity).

        Returns:
            FreshnessPolicy with infinite max_age_days

        Examples:
            >>> policy = FreshnessPolicy.always_fresh()
            >>> math.isinf(policy.max_age_days)
            True
            >>> policy.check_dependencies
            False
        """
        return cls(
            max_age_days=float("inf"),
            check_dependencies=False,
            inherit_from_collection=False,
        )

    @classmethod
    def daily(cls) -> "FreshnessPolicy":
        """Create daily refresh policy (max_age_days = 1).

        Returns:
            FreshnessPolicy with 1-day max_age

        Examples:
            >>> policy = FreshnessPolicy.daily()
            >>> policy.max_age_days
            1.0
        """
        return cls(max_age_days=1.0)

    @classmethod
    def weekly(cls) -> "FreshnessPolicy":
        """Create weekly refresh policy (max_age_days = 7).

        Returns:
            FreshnessPolicy with 7-day max_age

        Examples:
            >>> policy = FreshnessPolicy.weekly()
            >>> policy.max_age_days
            7.0
        """
        return cls(max_age_days=7.0)
