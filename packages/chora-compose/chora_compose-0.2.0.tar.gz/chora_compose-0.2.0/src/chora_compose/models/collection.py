"""Collection model for grouped artifacts with dependencies.

This module implements the Collection model following
chora-compose v3.0.0 design specification.
"""

from collections import deque
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .freshness import FreshnessPolicy


class Collection(BaseModel):
    """Collection of artifacts with shared configuration and dependency management.

    Attributes:
        id: Unique identifier for the collection
        members: List of artifact IDs in this collection (must be non-empty)
        dependencies: Dependency graph mapping artifact ID to list of dependencies
        context: Shared context variables for all members
        freshness_policy: Freshness policy for all members
        template_id: Optional default template for members

    Examples:
        >>> # Simple collection
        >>> collection = Collection(
        ...     id="docs",
        ...     members=["a.md", "b.md"],
        ...     freshness_policy=FreshnessPolicy.weekly()
        ... )
        >>> collection.resolve_generation_order()
        ['a.md', 'b.md']

        >>> # Collection with linear dependencies
        >>> collection = Collection(
        ...     id="docs",
        ...     members=["a.md", "b.md", "c.md"],
        ...     dependencies={"b.md": ["a.md"], "c.md": ["b.md"]},
        ...     freshness_policy=FreshnessPolicy.weekly()
        ... )
        >>> collection.resolve_generation_order()
        ['a.md', 'b.md', 'c.md']
    """

    id: str = Field(..., min_length=1, description="Unique collection identifier")
    members: list[str] = Field(..., min_length=1, description="Member artifact IDs")
    dependencies: dict[str, list[str]] = Field(
        default_factory=dict, description="Dependency graph (artifact_id -> [dependency_ids])"
    )
    context: dict[str, Any] = Field(default_factory=dict, description="Shared context variables")
    freshness_policy: FreshnessPolicy = Field(..., description="Freshness policy for members")
    template_id: str | None = Field(default=None, description="Default template for members")

    @field_validator("members")
    @classmethod
    def validate_members_not_empty(cls, v: list[str]) -> list[str]:
        """Validate members list is not empty.

        Args:
            v: members list

        Returns:
            Validated members list

        Raises:
            ValueError: If members list is empty
        """
        if len(v) == 0:
            raise ValueError("Collection must have at least one member")
        return v

    @field_validator("dependencies")
    @classmethod
    def validate_dependencies(cls, v: dict[str, list[str]], info) -> dict[str, list[str]]:
        """Validate dependency graph references only valid members.

        Args:
            v: dependencies dict
            info: Validation context with other field values

        Returns:
            Validated dependencies dict

        Raises:
            ValueError: If dependency key or value references non-member or self
        """
        members = info.data.get("members", [])
        members_set = set(members)

        for dependent, dependency_list in v.items():
            # Check dependency key is in members
            if dependent not in members_set:
                raise ValueError(
                    f"Dependency key '{dependent}' must be in members. "
                    f"Members: {members}"
                )

            # Check each dependency value is in members
            for dependency in dependency_list:
                if dependency not in members_set:
                    raise ValueError(
                        f"Dependency '{dependency}' (required by '{dependent}') "
                        f"must be in members. Members: {members}"
                    )

                # Check for self-dependency
                if dependency == dependent:
                    raise ValueError(
                        f"Self-dependency not allowed: '{dependent}' depends on itself"
                    )

        return v

    def resolve_generation_order(self) -> list[str]:
        """Resolve generation order using topological sort (Kahn's algorithm).

        Returns:
            List of member IDs in dependency-satisfying order

        Raises:
            ValueError: If circular dependency detected

        Examples:
            >>> # No dependencies
            >>> c = Collection(id="c", members=["a", "b"], freshness_policy=FreshnessPolicy.daily())
            >>> set(c.resolve_generation_order()) == {"a", "b"}
            True

            >>> # Linear dependencies
            >>> c = Collection(
            ...     id="c",
            ...     members=["a", "b", "c"],
            ...     dependencies={"b": ["a"], "c": ["b"]},
            ...     freshness_policy=FreshnessPolicy.daily()
            ... )
            >>> c.resolve_generation_order()
            ['a', 'b', 'c']
        """
        # Build in-degree count for each node
        in_degree = {member: 0 for member in self.members}
        for dependent, dependency_list in self.dependencies.items():
            in_degree[dependent] = len(dependency_list)

        # Build adjacency list (reverse of dependencies for processing)
        # For each node, track what depends on it
        dependents_map: dict[str, list[str]] = {member: [] for member in self.members}
        for dependent, dependency_list in self.dependencies.items():
            for dependency in dependency_list:
                dependents_map[dependency].append(dependent)

        # Initialize queue with nodes that have no dependencies (in_degree == 0)
        queue = deque([member for member in self.members if in_degree[member] == 0])

        # Process nodes in topological order
        result = []
        while queue:
            # Remove node with no dependencies
            current = queue.popleft()
            result.append(current)

            # For each node that depends on current, reduce in-degree
            for dependent in dependents_map[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # If we processed all nodes, we have a valid topological order
        if len(result) == len(self.members):
            return result

        # If not all nodes processed, there's a circular dependency
        # Find nodes involved in cycle for better error message
        remaining = [member for member in self.members if member not in result]
        raise ValueError(
            f"Circular dependency detected. Could not resolve order for: {remaining}"
        )
