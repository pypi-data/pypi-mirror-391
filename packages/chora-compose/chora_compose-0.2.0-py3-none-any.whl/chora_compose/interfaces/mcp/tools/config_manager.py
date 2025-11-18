"""Configuration manager for templates and collections."""

import fnmatch
from pathlib import Path
from typing import Any

from chora_compose.models.collection import Collection
from chora_compose.models.template import Template


class ConfigManager:
    """In-memory configuration manager for templates and collections.

    Provides CRUD operations for template and collection management.
    Supports pattern-based filtering for discovery.

    Attributes:
        templates: Map of template_id -> Template
        collections: Map of collection_id -> Collection
    """

    def __init__(self):
        """Initialize empty config manager."""
        self.templates: dict[str, Template] = {}
        self.collections: dict[str, Collection] = {}

    # === Template Management ===

    def register_template(self, template: Template) -> None:
        """Register a template.

        Args:
            template: Template to register
        """
        self.templates[template.id] = template

    def get_template(self, template_id: str) -> Template | None:
        """Get a template by ID.

        Args:
            template_id: Template identifier

        Returns:
            Template if found, None otherwise
        """
        return self.templates.get(template_id)

    def update_template(self, template_id: str, updates: dict[str, Any]) -> Template:
        """Update existing template with partial config.

        Args:
            template_id: Template identifier
            updates: Partial config to merge with existing template

        Returns:
            Updated template

        Raises:
            KeyError: If template not found
        """
        if template_id not in self.templates:
            raise KeyError(f"Template '{template_id}' not found")

        template = self.templates[template_id]

        # Merge updates into existing template config (deep merge for nested dicts)
        template_dict = template.model_dump()
        template_dict = self._deep_merge(template_dict, updates)

        # Create updated template and replace
        updated = Template.model_validate(template_dict)
        self.templates[template_id] = updated
        return updated

    def delete_template(self, template_id: str) -> None:
        """Remove template from registry.

        Args:
            template_id: Template identifier

        Raises:
            KeyError: If template not found
        """
        if template_id not in self.templates:
            raise KeyError(f"Template '{template_id}' not found")

        del self.templates[template_id]

    def list_templates(self, pattern: str | None = None) -> list[Template]:
        """List all templates, optionally filtered by glob pattern.

        Args:
            pattern: Optional glob pattern (e.g., "*.md")

        Returns:
            List of templates matching pattern (or all if no pattern)
        """
        templates = list(self.templates.values())

        if pattern:
            templates = [t for t in templates if fnmatch.fnmatch(t.id, pattern)]

        return templates

    # === Collection Management ===

    def register_collection(self, collection: Collection) -> None:
        """Register a collection.

        Args:
            collection: Collection to register
        """
        self.collections[collection.id] = collection

    def get_collection(self, collection_id: str) -> Collection | None:
        """Get a collection by ID.

        Args:
            collection_id: Collection identifier

        Returns:
            Collection if found, None otherwise
        """
        return self.collections.get(collection_id)

    def update_collection(self, collection_id: str, updates: dict[str, Any]) -> Collection:
        """Update existing collection with partial config.

        Args:
            collection_id: Collection identifier
            updates: Partial config to merge with existing collection

        Returns:
            Updated collection

        Raises:
            KeyError: If collection not found
        """
        if collection_id not in self.collections:
            raise KeyError(f"Collection '{collection_id}' not found")

        collection = self.collections[collection_id]

        # Merge updates into existing collection config (deep merge for nested dicts)
        collection_dict = collection.model_dump()
        collection_dict = self._deep_merge(collection_dict, updates)

        # Create updated collection and replace
        updated = Collection.model_validate(collection_dict)
        self.collections[collection_id] = updated
        return updated

    def delete_collection(self, collection_id: str) -> None:
        """Remove collection from registry.

        Args:
            collection_id: Collection identifier

        Raises:
            KeyError: If collection not found
        """
        if collection_id not in self.collections:
            raise KeyError(f"Collection '{collection_id}' not found")

        del self.collections[collection_id]

    def list_collections(self, pattern: str | None = None) -> list[Collection]:
        """List all collections, optionally filtered by glob pattern.

        Args:
            pattern: Optional glob pattern (e.g., "docs-*")

        Returns:
            List of collections matching pattern (or all if no pattern)
        """
        collections = list(self.collections.values())

        if pattern:
            collections = [c for c in collections if fnmatch.fnmatch(c.id, pattern)]

        return collections

    # === Utility Methods ===

    def exists(self, artifact_id: str) -> bool:
        """Check if configuration exists for an artifact ID.

        Args:
            artifact_id: Artifact or collection identifier

        Returns:
            True if template or collection exists for this ID
        """
        return artifact_id in self.templates or artifact_id in self.collections

    def _deep_merge(self, base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
        """Deep merge updates into base dictionary.

        Args:
            base: Base dictionary
            updates: Updates to merge

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Replace value
                result[key] = value

        return result
