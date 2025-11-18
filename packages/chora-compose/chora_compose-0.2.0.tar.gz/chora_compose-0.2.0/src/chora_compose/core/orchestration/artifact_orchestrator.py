"""Artifact orchestration with idempotency and dependency management."""

from datetime import datetime, timezone
from typing import Any

from chora_compose.models.artifact import Artifact
from chora_compose.models.collection import Collection
from chora_compose.models.freshness import FreshnessPolicy
from chora_compose.models.template import Template
from ..rendering.factory import RendererFactory
from ..storage.artifact_store import ArtifactStore


class ArtifactOrchestrator:
    """Orchestrates artifact generation with caching and dependency management.

    Implements Scenario C idempotency:
    - Fresh cached artifacts are returned without regeneration
    - Stale cached artifacts are regenerated
    - Force flag bypasses cache completely

    Attributes:
        artifact_store: Storage layer for artifacts

    Examples:
        >>> store = ArtifactStore(base_path=Path(".chora/artifacts"))
        >>> orchestrator = ArtifactOrchestrator(artifact_store=store)
        >>> artifact = orchestrator.create("doc.md", template, context, freshness_policy)
    """

    def __init__(self, artifact_store: ArtifactStore):
        """Initialize orchestrator with artifact store.

        Args:
            artifact_store: Storage layer for artifacts
        """
        self.artifact_store = artifact_store

    def create(
        self,
        artifact_id: str,
        template: Template,
        context: dict[str, Any],
        freshness_policy: FreshnessPolicy,
        force: bool = False,
    ) -> Artifact:
        """Create artifact with idempotency (Scenario C).

        If force=False:
        - Returns cached artifact if fresh (age < max_age_days)
        - Regenerates if stale (age > max_age_days) or not exists

        If force=True:
        - Always regenerates (bypasses cache)

        Args:
            artifact_id: Unique identifier for artifact
            template: Template to use for generation
            context: Runtime context variables
            freshness_policy: Freshness policy for caching
            force: If True, bypass cache and regenerate

        Returns:
            Generated or cached Artifact

        Examples:
            >>> artifact = orchestrator.create(
            ...     "readme.md",
            ...     template,
            ...     {"project": "chora"},
            ...     FreshnessPolicy.daily(),
            ...     force=False
            ... )
        """
        # Check cache if not forcing
        if not force and self.artifact_store.exists(artifact_id):
            age_days = self.artifact_store.get_age_days(artifact_id)
            if age_days is not None and age_days < freshness_policy.max_age_days:
                # Cache is fresh, return it
                return self.artifact_store.load(artifact_id)

        # Generate new artifact
        return self._generate_and_save(
            artifact_id=artifact_id,
            template=template,
            context=context,
            freshness_policy=freshness_policy,
        )

    def refresh(
        self,
        artifact_id: str,
        template: Template,
        context: dict[str, Any],
        freshness_policy: FreshnessPolicy,
    ) -> Artifact:
        """Refresh artifact (always regenerates, bypassing cache).

        This is equivalent to create(..., force=True).

        Args:
            artifact_id: Unique identifier for artifact
            template: Template to use for generation
            context: Runtime context variables
            freshness_policy: Freshness policy for caching

        Returns:
            Newly generated Artifact

        Examples:
            >>> artifact = orchestrator.refresh(
            ...     "readme.md",
            ...     template,
            ...     {"project": "chora"},
            ...     FreshnessPolicy.daily()
            ... )
        """
        return self._generate_and_save(
            artifact_id=artifact_id,
            template=template,
            context=context,
            freshness_policy=freshness_policy,
        )

    def create_collection(
        self,
        collection: Collection,
        templates: dict[str, Template],
        context: dict[str, Any],
        freshness_policy: FreshnessPolicy,
        force: bool = False,
    ) -> list[Artifact]:
        """Create all artifacts in a collection with dependency ordering.

        Uses Kahn's algorithm for topological sort to respect dependencies.
        Merges collection.context with runtime context (runtime overrides).

        Args:
            collection: Collection with members and dependencies
            templates: Map of member_id -> Template
            context: Runtime context variables
            freshness_policy: Freshness policy for all artifacts
            force: If True, bypass cache for all artifacts

        Returns:
            List of generated/cached Artifacts

        Raises:
            ValueError: If template missing for a member
            ValueError: If dependency graph has cycles

        Examples:
            >>> collection = Collection(
            ...     id="docs",
            ...     members=["a.md", "b.md"],
            ...     dependencies={"b.md": ["a.md"]},
            ...     context={"project": "chora"}
            ... )
            >>> artifacts = orchestrator.create_collection(
            ...     collection,
            ...     templates,
            ...     {"version": "v3.0.0"},
            ...     FreshnessPolicy.daily()
            ... )
        """
        # Validate all templates exist
        for member in collection.members:
            if member not in templates:
                raise ValueError(f"Template not found for member: {member}")

        # Merge collection context with runtime context (runtime overrides)
        merged_context = {**collection.context, **context}

        # Compute generation order (topological sort)
        generation_order = self._topological_sort(
            collection.members, collection.dependencies
        )

        # Generate artifacts in dependency order
        artifacts = []
        for member_id in generation_order:
            template = templates[member_id]
            artifact = self.create(
                artifact_id=member_id,
                template=template,
                context=merged_context,
                freshness_policy=freshness_policy,
                force=force,
            )
            artifacts.append(artifact)

        return artifacts

    def _generate_and_save(
        self,
        artifact_id: str,
        template: Template,
        context: dict[str, Any],
        freshness_policy: FreshnessPolicy,
    ) -> Artifact:
        """Generate artifact from template and save to storage.

        Args:
            artifact_id: Unique identifier for artifact
            template: Template to use for generation
            context: Runtime context variables
            freshness_policy: Freshness policy for caching

        Returns:
            Generated Artifact
        """
        # Get renderer for template
        renderer = RendererFactory.get_renderer(template)

        # Render content
        content = renderer.render(template, context)

        # Create artifact
        artifact = Artifact(
            id=artifact_id,
            content=content,
            template_id=template.id,
            context=context,
            generated_at=datetime.now(timezone.utc),
            freshness_policy=freshness_policy,
        )

        # Save to storage
        self.artifact_store.save(artifact)

        return artifact

    def _topological_sort(
        self, members: list[str], dependencies: dict[str, list[str]]
    ) -> list[str]:
        """Topologically sort members based on dependencies using Kahn's algorithm.

        Args:
            members: List of member IDs
            dependencies: Map of member_id -> list of dependencies

        Returns:
            Members sorted in dependency order

        Raises:
            ValueError: If dependency graph has cycles

        Examples:
            >>> # Linear: a -> b -> c
            >>> orchestrator._topological_sort(
            ...     ["a", "b", "c"],
            ...     {"b": ["a"], "c": ["b"]}
            ... )
            ['a', 'b', 'c']

            >>> # Parallel branches
            >>> orchestrator._topological_sort(
            ...     ["a", "b", "c", "d"],
            ...     {"c": ["a"], "d": ["b"]}
            ... )
            ['a', 'b', 'c', 'd']  # or ['b', 'a', 'd', 'c'] etc.
        """
        # Build in-degree map and adjacency list
        in_degree = {member: 0 for member in members}
        adjacency = {member: [] for member in members}

        for member, deps in dependencies.items():
            in_degree[member] = len(deps)
            for dep in deps:
                adjacency[dep].append(member)

        # Kahn's algorithm
        queue = [member for member in members if in_degree[member] == 0]
        sorted_members = []

        while queue:
            # Sort queue for deterministic ordering when multiple nodes have 0 in-degree
            queue.sort()
            current = queue.pop(0)
            sorted_members.append(current)

            # Reduce in-degree of neighbors
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(sorted_members) != len(members):
            raise ValueError("Dependency graph has cycles")

        return sorted_members
