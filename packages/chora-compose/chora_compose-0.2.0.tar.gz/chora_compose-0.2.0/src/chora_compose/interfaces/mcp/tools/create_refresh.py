"""Create and refresh tool implementations."""

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chora_compose.models.freshness import FreshnessPolicy
from chora_compose.core.orchestration.artifact_orchestrator import ArtifactOrchestrator
from chora_compose.core.storage.artifact_store import ArtifactStore
from .config_manager import ConfigManager


def create_artifact(
    artifact_id: str,
    config_manager: ConfigManager,
    orchestrator: ArtifactOrchestrator,
    context: dict[str, Any] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Create artifact with idempotency.

    Args:
        artifact_id: Unique identifier for artifact or collection
        config_manager: Configuration manager with templates/collections
        orchestrator: Artifact orchestrator for generation
        context: Runtime context variables (default: {})
        force: If True, bypass cache and regenerate (default: False)

    Returns:
        Response dict with status, result, and metadata

    Examples:
        >>> response = create_artifact("hello.md", config_mgr, orch, {"name": "World"})
        >>> assert response["status"] == "success"
        >>> assert response["result"]["id"] == "hello.md"
    """
    start_time = time.time()
    context = context or {}

    # Validate input
    if not artifact_id or not artifact_id.strip():
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": "id cannot be empty",
            },
        }

    # Check if configuration exists
    template = config_manager.get_template(artifact_id)
    collection = config_manager.get_collection(artifact_id)

    if not template and not collection:
        return {
            "status": "error",
            "error": {
                "code": "CONFIG_NOT_FOUND",
                "message": f"No template or collection found for '{artifact_id}'",
                "suggestion": "Use configure() tool to register templates and collections",
            },
        }

    # Determine freshness policy (default to daily)
    if collection:
        freshness_policy = collection.freshness_policy
    else:
        freshness_policy = FreshnessPolicy.daily()

    try:
        # Handle simple template
        if template:
            # Check if artifact exists and is fresh BEFORE calling create()
            existed_before = orchestrator.artifact_store.exists(artifact_id)
            age_before = orchestrator.artifact_store.get_age_days(artifact_id) if existed_before else None
            will_use_cache = (
                not force
                and existed_before
                and age_before is not None
                and age_before < freshness_policy.max_age_days
            )

            artifact = orchestrator.create(
                artifact_id=artifact_id,
                template=template,
                context=context,
                freshness_policy=freshness_policy,
                force=force,
            )

            # Get final age after creation
            age_days = orchestrator.artifact_store.get_age_days(artifact_id)

            duration_sec = time.time() - start_time

            return {
                "status": "success",
                "result": {
                    "type": "artifact",
                    "id": artifact.id,
                    "content_length": len(artifact.content),
                    "cached": will_use_cache,
                    "freshness": {
                        "is_fresh": age_days is None or age_days < freshness_policy.max_age_days,
                        "age_days": age_days,
                        "max_age_days": freshness_policy.max_age_days,
                        "generated_at": artifact.generated_at.isoformat(),
                    },
                },
                "metadata": {
                    "duration_sec": round(duration_sec, 3),
                    "template_id": artifact.template_id,
                },
            }

        # Handle collection
        elif collection:
            # Get templates for all members
            member_templates = {}
            missing_templates = []

            for member_id in collection.members:
                member_template = config_manager.get_template(member_id)
                if member_template:
                    member_templates[member_id] = member_template
                else:
                    missing_templates.append(member_id)

            # Check if all templates exist
            if missing_templates:
                return {
                    "status": "error",
                    "error": {
                        "code": "TEMPLATE_NOT_FOUND",
                        "message": f"Templates not found for members: {', '.join(missing_templates)}",
                        "missing_members": missing_templates,
                    },
                }

            # Generate collection
            artifacts = orchestrator.create_collection(
                collection=collection,
                templates=member_templates,
                context=context,
                freshness_policy=freshness_policy,
                force=force,
            )

            duration_sec = time.time() - start_time

            return {
                "status": "success",
                "result": {
                    "type": "collection",
                    "id": collection.id,
                    "summary": {
                        "total": len(artifacts),
                        "succeeded": len(artifacts),
                        "failed": 0,
                    },
                    "results": [
                        {
                            "id": art.id,
                            "status": "success",
                            "content_length": len(art.content),
                        }
                        for art in artifacts
                    ],
                },
                "metadata": {
                    "duration_sec": round(duration_sec, 3),
                    "collection_id": collection.id,
                },
            }

    except Exception as e:
        duration_sec = time.time() - start_time
        return {
            "status": "error",
            "error": {
                "code": "GENERATION_ERROR",
                "message": str(e),
                "type": type(e).__name__,
            },
            "metadata": {
                "duration_sec": round(duration_sec, 3),
            },
        }


def refresh_artifact(
    artifact_id: str,
    config_manager: ConfigManager,
    orchestrator: ArtifactOrchestrator,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Refresh artifact (always regenerates, bypassing cache).

    Args:
        artifact_id: Unique identifier for artifact or collection
        config_manager: Configuration manager with templates/collections
        orchestrator: Artifact orchestrator for generation
        context: Runtime context variables (default: {})

    Returns:
        Response dict with status, result, and metadata

    Examples:
        >>> response = refresh_artifact("doc.md", config_mgr, orch)
        >>> assert response["status"] == "success"
        >>> assert response["result"]["cached"] == False
    """
    start_time = time.time()
    context = context or {}

    # Validate input
    if not artifact_id or not artifact_id.strip():
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": "id cannot be empty",
            },
        }

    # Check if configuration exists
    template = config_manager.get_template(artifact_id)
    collection = config_manager.get_collection(artifact_id)

    if not template and not collection:
        return {
            "status": "error",
            "error": {
                "code": "CONFIG_NOT_FOUND",
                "message": f"No template or collection found for '{artifact_id}'",
                "suggestion": "Use configure() tool to register templates and collections",
            },
        }

    # Determine freshness policy
    if collection:
        freshness_policy = collection.freshness_policy
    else:
        freshness_policy = FreshnessPolicy.daily()

    try:
        # Handle simple template
        if template:
            artifact = orchestrator.refresh(
                artifact_id=artifact_id,
                template=template,
                context=context,
                freshness_policy=freshness_policy,
            )

            duration_sec = time.time() - start_time

            return {
                "status": "success",
                "result": {
                    "type": "artifact",
                    "id": artifact.id,
                    "content_length": len(artifact.content),
                    "cached": False,  # refresh always regenerates
                    "freshness": {
                        "is_fresh": True,  # Just generated
                        "generated_at": artifact.generated_at.isoformat(),
                    },
                },
                "metadata": {
                    "duration_sec": round(duration_sec, 3),
                    "template_id": artifact.template_id,
                },
            }

        # Handle collection
        elif collection:
            # Get templates for all members
            member_templates = {}
            for member_id in collection.members:
                member_template = config_manager.get_template(member_id)
                if member_template:
                    member_templates[member_id] = member_template

            # Refresh collection (force=True to bypass cache)
            artifacts = orchestrator.create_collection(
                collection=collection,
                templates=member_templates,
                context=context,
                freshness_policy=freshness_policy,
                force=True,  # refresh always forces regeneration
            )

            duration_sec = time.time() - start_time

            return {
                "status": "success",
                "result": {
                    "type": "collection",
                    "id": collection.id,
                    "summary": {
                        "total": len(artifacts),
                        "succeeded": len(artifacts),
                        "failed": 0,
                    },
                    "results": [
                        {
                            "id": art.id,
                            "status": "success",
                            "content_length": len(art.content),
                        }
                        for art in artifacts
                    ],
                },
                "metadata": {
                    "duration_sec": round(duration_sec, 3),
                    "collection_id": collection.id,
                },
            }

    except Exception as e:
        duration_sec = time.time() - start_time
        return {
            "status": "error",
            "error": {
                "code": "GENERATION_ERROR",
                "message": str(e),
                "type": type(e).__name__,
            },
            "metadata": {
                "duration_sec": round(duration_sec, 3),
            },
        }
