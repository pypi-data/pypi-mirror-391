"""Composer class - Native Python API for chora-compose."""

from pathlib import Path
from typing import Any

from chora_compose.core.orchestration.artifact_orchestrator import ArtifactOrchestrator
from chora_compose.core.storage.artifact_store import ArtifactStore
from chora_compose.interfaces.mcp.tools.config_manager import ConfigManager
from chora_compose.interfaces.mcp.tools.configure import configure_item
from chora_compose.interfaces.mcp.tools.create_refresh import (
    create_artifact,
    refresh_artifact,
)
from chora_compose.interfaces.mcp.tools.discover import discover_items
from chora_compose.interfaces.mcp.tools.inspect import inspect_artifact
from chora_compose.models.collection import Collection
from chora_compose.models.template import Template


class Composer:
    """Native Python API for chora-compose.

    Provides a clean, Pythonic interface for content generation and orchestration.

    Example:
        >>> composer = Composer()
        >>> result = await composer.create("my-artifact", context={"title": "Hello"})
        >>> print(result["content"])

    Attributes:
        artifact_store: Artifact storage manager
        orchestrator: Artifact generation orchestrator
        config_manager: Configuration manager
    """

    def __init__(self, base_path: Path | None = None):
        """Initialize Composer.

        Args:
            base_path: Base path for artifact storage. Defaults to .chora/artifacts
                      in current directory.
        """
        if base_path is None:
            base_path = Path.cwd() / ".chora" / "artifacts"

        self.artifact_store = ArtifactStore(base_path=base_path)
        self.orchestrator = ArtifactOrchestrator(artifact_store=self.artifact_store)
        self.config_manager = ConfigManager()

    async def create(
        self,
        artifact_id: str,
        context: dict[str, Any] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """Create artifact with idempotent caching.

        Generates content from templates with smart caching: fresh artifacts are
        returned from cache, stale artifacts are regenerated. Use force=True to
        bypass cache and always regenerate.

        Args:
            artifact_id: Unique identifier for artifact or collection
            context: Runtime context variables (default: {})
            force: If True, bypass cache and regenerate (default: False)

        Returns:
            dict with keys:
                - id: Artifact identifier
                - content: Generated content
                - cached: Whether content was from cache
                - metadata: Artifact metadata (timestamps, template, etc.)

        Raises:
            ValueError: If template not found or invalid configuration
        """
        return await create_artifact(
            id=artifact_id,
            context=context or {},
            force=force,
            artifact_store=self.artifact_store,
            orchestrator=self.orchestrator,
            config_manager=self.config_manager,
        )

    async def refresh(
        self,
        artifact_id: str,
        context: dict[str, Any] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """Refresh stale artifacts or regenerate with force.

        Selectively regenerates stale artifacts based on freshness policies.
        Use force=True to regenerate regardless of freshness.

        Args:
            artifact_id: Unique identifier for artifact or collection
            context: Runtime context variables (default: {})
            force: If True, always regenerate (default: False)

        Returns:
            dict with keys:
                - id: Artifact identifier
                - content: Refreshed content (or None if still fresh)
                - refreshed: Whether artifact was regenerated
                - reason: Why refresh happened (or why skipped)
                - metadata: Artifact metadata

        Raises:
            ValueError: If artifact doesn't exist or invalid configuration
        """
        return await refresh_artifact(
            id=artifact_id,
            context=context or {},
            force=force,
            artifact_store=self.artifact_store,
            orchestrator=self.orchestrator,
            config_manager=self.config_manager,
        )

    async def inspect(self, artifact_id: str) -> dict[str, Any]:
        """Inspect artifact metadata and freshness status.

        Args:
            artifact_id: Artifact identifier to inspect

        Returns:
            dict with keys:
                - id: Artifact identifier
                - exists: Whether artifact exists
                - metadata: Artifact metadata (if exists)
                - freshness: Freshness status and policy info

        Raises:
            ValueError: If artifact_id is invalid
        """
        return await inspect_artifact(
            id=artifact_id,
            artifact_store=self.artifact_store,
            config_manager=self.config_manager,
        )

    async def discover(
        self,
        item_type: str = "all",
    ) -> dict[str, Any]:
        """Discover available templates, collections, and configurations.

        Args:
            item_type: Type to discover - "all", "templates", "collections",
                      "configs" (default: "all")

        Returns:
            dict with keys:
                - templates: List of template definitions (if requested)
                - collections: List of collection definitions (if requested)
                - configs: Configuration status (if requested)
                - count: Total items found

        Raises:
            ValueError: If item_type is invalid
        """
        return await discover_items(
            item_type=item_type,
            config_manager=self.config_manager,
        )

    async def configure(
        self,
        item_type: str,
        item_id: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Configure templates, collections, or freshness policies.

        Args:
            item_type: Type to configure - "template", "collection", "freshness"
            item_id: Identifier for the item
            config: Configuration data (structure depends on item_type)

        Returns:
            dict with keys:
                - success: Whether configuration succeeded
                - item_type: Type that was configured
                - item_id: Identifier that was configured
                - message: Success/error message

        Raises:
            ValueError: If invalid item_type or config structure
        """
        return await configure_item(
            item_type=item_type,
            item_id=item_id,
            config=config,
            config_manager=self.config_manager,
        )

    # Convenience methods for configuration

    async def configure_template(
        self,
        template_id: str,
        template_path: str,
        description: str | None = None,
        default_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Configure a template.

        Args:
            template_id: Unique template identifier
            template_path: Path to template file
            description: Optional template description
            default_context: Default context variables

        Returns:
            Configuration result
        """
        config = {
            "template_path": template_path,
            "description": description or "",
            "default_context": default_context or {},
        }
        return await self.configure("template", template_id, config)

    async def configure_collection(
        self,
        collection_id: str,
        template_ids: list[str],
        description: str | None = None,
    ) -> dict[str, Any]:
        """Configure a collection.

        Args:
            collection_id: Unique collection identifier
            template_ids: List of template IDs in collection
            description: Optional collection description

        Returns:
            Configuration result
        """
        config = {
            "template_ids": template_ids,
            "description": description or "",
        }
        return await self.configure("collection", collection_id, config)

    async def configure_freshness(
        self,
        policy_id: str,
        max_age_hours: int,
        applies_to: list[str] | None = None,
    ) -> dict[str, Any]:
        """Configure a freshness policy.

        Args:
            policy_id: Unique policy identifier
            max_age_hours: Maximum age in hours before artifact is stale
            applies_to: List of artifact/collection IDs this policy applies to

        Returns:
            Configuration result
        """
        config = {
            "max_age_hours": max_age_hours,
            "applies_to": applies_to or [],
        }
        return await self.configure("freshness", policy_id, config)
