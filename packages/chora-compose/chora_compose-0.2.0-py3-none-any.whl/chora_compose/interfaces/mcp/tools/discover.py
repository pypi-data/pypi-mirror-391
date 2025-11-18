"""Discover tool implementation."""

import time
from typing import Any, Literal

from .config_manager import ConfigManager


def discover_items(
    type: Literal["template", "collection", "all"],
    pattern: str | None,
    config_manager: ConfigManager,
) -> dict[str, Any]:
    """Browse available templates and collections.

    Args:
        type: What to discover (template, collection, or all)
        pattern: Optional glob pattern for filtering (e.g., "*.md")
        config_manager: Configuration manager with templates/collections

    Returns:
        Response dict with status, result, and metadata

    Examples:
        >>> response = discover_items("template", "*.md", config_mgr)
        >>> assert response["status"] == "success"
        >>> assert len(response["result"]["templates"]) > 0
    """
    start_time = time.time()

    # Validate input
    if type not in ["template", "collection", "all"]:
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": f"Invalid type '{type}'. Must be 'template', 'collection', or 'all'",
            },
        }

    try:
        templates_list = []
        collections_list = []

        # Discover templates
        if type in ["template", "all"]:
            templates = config_manager.list_templates(pattern=pattern)
            for template in templates:
                templates_list.append(
                    {
                        "id": template.id,
                        "generator": template.generator.value,  # Enum to string
                    }
                )

        # Discover collections
        if type in ["collection", "all"]:
            collections = config_manager.list_collections(pattern=pattern)
            for collection in collections:
                collections_list.append(
                    {
                        "id": collection.id,
                        "member_count": len(collection.members),
                        "freshness_policy": {
                            "max_age_days": collection.freshness_policy.max_age_days,
                        },
                    }
                )

        duration_sec = time.time() - start_time

        return {
            "status": "success",
            "result": {
                "templates": templates_list,
                "collections": collections_list,
                "summary": {
                    "total_templates": len(templates_list),
                    "total_collections": len(collections_list),
                },
            },
            "metadata": {
                "duration_sec": round(duration_sec, 3),
            },
        }

    except Exception as e:
        duration_sec = time.time() - start_time
        return {
            "status": "error",
            "error": {
                "code": "DISCOVERY_ERROR",
                "message": str(e),
                "type": e.__class__.__name__,
            },
            "metadata": {
                "duration_sec": round(duration_sec, 3),
            },
        }
