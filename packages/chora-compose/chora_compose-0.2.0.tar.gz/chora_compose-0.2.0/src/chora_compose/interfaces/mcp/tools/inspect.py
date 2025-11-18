"""Inspect tool implementation."""

import time
from typing import Any

from chora_compose.core.storage.artifact_store import ArtifactStore
from .config_manager import ConfigManager


def inspect_artifact(
    artifact_id: str,
    artifact_store: ArtifactStore,
    config_manager: ConfigManager,
    include_content: bool = False,
) -> dict[str, Any]:
    """Inspect artifact status and metadata without regenerating.

    Args:
        artifact_id: Unique identifier for artifact or collection
        artifact_store: Artifact store for loading artifacts
        config_manager: Configuration manager with templates/collections
        include_content: If True, include full content in response (default: False)

    Returns:
        Response dict with status, result, and metadata

    Examples:
        >>> response = inspect_artifact("doc.md", store, config_mgr)
        >>> assert response["status"] == "success"
        >>> assert response["result"]["exists"] is True
    """
    start_time = time.time()

    # Validate input
    if not artifact_id or not artifact_id.strip():
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": "id cannot be empty",
            },
        }

    # Check if this is a collection
    collection = config_manager.get_collection(artifact_id)

    try:
        if collection:
            # Inspect collection and all members
            members_status = []
            fresh_count = 0
            stale_count = 0
            missing_count = 0

            for member_id in collection.members:
                if artifact_store.exists(member_id):
                    artifact = artifact_store.load(member_id)
                    age_days = artifact_store.get_age_days(member_id)
                    is_fresh = (
                        age_days is not None
                        and age_days < collection.freshness_policy.max_age_days
                    )

                    if is_fresh:
                        fresh_count += 1
                    else:
                        stale_count += 1

                    members_status.append(
                        {
                            "id": member_id,
                            "exists": True,
                            "is_fresh": is_fresh,
                            "age_days": age_days,
                        }
                    )
                else:
                    missing_count += 1
                    members_status.append(
                        {
                            "id": member_id,
                            "exists": False,
                            "is_fresh": None,
                            "age_days": None,
                        }
                    )

            duration_sec = time.time() - start_time

            return {
                "status": "success",
                "result": {
                    "type": "collection",
                    "id": artifact_id,
                    "summary": {
                        "total": len(collection.members),
                        "fresh": fresh_count,
                        "stale": stale_count,
                        "missing": missing_count,
                    },
                    "members": members_status,
                },
                "metadata": {
                    "duration_sec": round(duration_sec, 3),
                },
            }

        else:
            # Inspect single artifact
            if artifact_store.exists(artifact_id):
                artifact = artifact_store.load(artifact_id)
                age_days = artifact_store.get_age_days(artifact_id)

                # Determine if fresh based on artifact's own freshness policy
                is_fresh = (
                    age_days is not None
                    and age_days < artifact.freshness_policy.max_age_days
                )

                result = {
                    "type": "artifact",
                    "id": artifact_id,
                    "exists": True,
                    "freshness": {
                        "is_fresh": is_fresh,
                        "age_days": age_days,
                        "max_age_days": artifact.freshness_policy.max_age_days,
                        "generated_at": artifact.generated_at.isoformat(),
                    },
                    "metadata": {
                        "template_id": artifact.template_id,
                        "content_length": len(artifact.content),
                        "context": artifact.context,
                    },
                }

                # Include content if requested
                if include_content:
                    result["content"] = artifact.content

            else:
                # Artifact doesn't exist
                result = {
                    "type": "artifact",
                    "id": artifact_id,
                    "exists": False,
                    "freshness": None,
                    "metadata": None,
                }

            duration_sec = time.time() - start_time

            return {
                "status": "success",
                "result": result,
                "metadata": {
                    "duration_sec": round(duration_sec, 3),
                },
            }

    except Exception as e:
        duration_sec = time.time() - start_time
        return {
            "status": "error",
            "error": {
                "code": "INSPECTION_ERROR",
                "message": str(e),
                "type": type(e).__name__,
            },
            "metadata": {
                "duration_sec": round(duration_sec, 3),
            },
        }
