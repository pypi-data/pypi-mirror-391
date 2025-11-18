"""Artifact storage with file-based persistence.

This module implements the ArtifactStore for persisting artifacts
with freshness metadata following chora-compose v3.0.0 design.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from chora_compose.models.artifact import Artifact


class ArtifactStore:
    """File-based storage for artifacts with freshness tracking.

    Attributes:
        base_path: Base directory for artifact storage

    Storage Structure:
        .chora/artifacts/
        ├── hello.md                    # Artifact content
        ├── sap-029/
        │   ├── overview.md             # Artifact content (subdirectory)
        │   └── details.md
        └── .metadata/
            ├── hello.md.json           # Metadata (generated_at, template_id, etc.)
            └── sap-029/
                ├── overview.md.json
                └── details.md.json

    Examples:
        >>> store = ArtifactStore()
        >>> artifact = Artifact(...)
        >>> store.save(artifact)
        >>> loaded = store.load("hello.md")
        >>> age = store.get_age_days("hello.md")
    """

    def __init__(self, base_path: Path | str | None = None):
        """Initialize artifact store.

        Args:
            base_path: Base directory for artifacts (default: .chora/artifacts)
        """
        if base_path is None:
            base_path = Path(".chora/artifacts")
        self.base_path = Path(base_path)

    def save(self, artifact: Artifact) -> None:
        """Save artifact to disk with metadata.

        Args:
            artifact: Artifact to save

        Side Effects:
            - Creates base_path if it doesn't exist
            - Writes content to {base_path}/{artifact.id}
            - Writes metadata to {base_path}/.metadata/{artifact.id}.json
        """
        # Create directories
        content_path = self.base_path / artifact.id
        content_path.parent.mkdir(parents=True, exist_ok=True)

        metadata_path = self._get_metadata_path(artifact.id)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        content_path.write_text(artifact.content)

        # Write metadata
        metadata = artifact.model_dump(mode="json")
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def load(self, artifact_id: str) -> Artifact | None:
        """Load artifact from disk.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Artifact instance, or None if not found

        Raises:
            ValueError: If metadata is corrupted or missing
        """
        content_path = self.base_path / artifact_id
        metadata_path = self._get_metadata_path(artifact_id)

        # Check if artifact exists
        if not content_path.exists():
            return None

        # Check if metadata exists
        if not metadata_path.exists():
            raise ValueError(
                f"Artifact '{artifact_id}' has content but metadata not found at {metadata_path}"
            )

        # Load content
        content = content_path.read_text()

        # Load metadata
        try:
            metadata = json.loads(metadata_path.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Corrupted metadata for artifact '{artifact_id}' at {metadata_path}: {e}"
            ) from e

        # Reconstruct artifact
        metadata["content"] = content
        return Artifact.model_validate(metadata)

    def exists(self, artifact_id: str) -> bool:
        """Check if artifact exists on disk.

        Args:
            artifact_id: Artifact identifier

        Returns:
            True if artifact exists, False otherwise
        """
        content_path = self.base_path / artifact_id
        return content_path.exists()

    def get_age_days(self, artifact_id: str) -> float | None:
        """Calculate artifact age in days.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Age in days (fractional), or None if artifact not found
        """
        if not self.exists(artifact_id):
            return None

        # Load artifact to get generated_at
        artifact = self.load(artifact_id)
        if artifact is None:
            return None

        # Calculate age
        return artifact.age_days

    def _get_metadata_path(self, artifact_id: str) -> Path:
        """Get metadata file path for artifact.

        Args:
            artifact_id: Artifact identifier

        Returns:
            Path to metadata JSON file
        """
        return self.base_path / ".metadata" / f"{artifact_id}.json"
