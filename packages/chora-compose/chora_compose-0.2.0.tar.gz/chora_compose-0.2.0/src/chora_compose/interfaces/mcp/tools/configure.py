"""Configure tool implementation."""

import time
from typing import Any, Literal

from chora_compose.models.collection import Collection
from chora_compose.models.template import Template
from .config_manager import ConfigManager


def configure_item(
    operation: Literal["register", "update", "delete", "get"],
    type: Literal["template", "collection"],
    id: str,
    config: dict[str, Any] | None,
    config_manager: ConfigManager,
) -> dict[str, Any]:
    """Manage templates and collections.

    Args:
        operation: Action to perform (register, update, delete, get)
        type: Configuration type (template or collection)
        id: Unique identifier
        config: Configuration data (required for register/update)
        config_manager: Configuration manager instance

    Returns:
        Response dict with status, result, and metadata

    Examples:
        >>> response = configure_item("register", "template", "test.md", {...}, config_mgr)
        >>> assert response["status"] == "success"
    """
    start_time = time.time()

    # Validate inputs
    if operation not in ["register", "update", "delete", "get"]:
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": f"Invalid operation '{operation}'. Must be one of: register, update, delete, get",
            },
        }

    if type not in ["template", "collection"]:
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": f"Invalid type '{type}'. Must be one of: template, collection",
            },
        }

    if not id or not id.strip():
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": "id cannot be empty",
            },
        }

    if operation in ["register", "update"] and config is None:
        return {
            "status": "error",
            "error": {
                "code": "INVALID_INPUT",
                "message": f"config is required for {operation} operation",
            },
        }

    try:
        # Handle template operations
        if type == "template":
            if operation == "register":
                # Create and register new template
                template = Template.model_validate({"id": id, **config})
                config_manager.register_template(template)
                result_config = template.model_dump(mode="json")

            elif operation == "update":
                # Update existing template
                updated_template = config_manager.update_template(id, config)
                result_config = updated_template.model_dump(mode="json")

            elif operation == "delete":
                # Delete template
                config_manager.delete_template(id)
                result_config = None

            elif operation == "get":
                # Get template configuration
                template = config_manager.get_template(id)
                if template is None:
                    duration_sec = time.time() - start_time
                    return {
                        "status": "error",
                        "error": {
                            "code": "NOT_FOUND",
                            "message": f"Template '{id}' not found",
                        },
                        "metadata": {
                            "duration_sec": round(duration_sec, 3),
                        },
                    }
                result_config = template.model_dump(mode="json")

        # Handle collection operations
        elif type == "collection":
            if operation == "register":
                # Create and register new collection
                collection = Collection.model_validate({"id": id, **config})
                config_manager.register_collection(collection)
                result_config = collection.model_dump(mode="json")

            elif operation == "update":
                # Update existing collection
                updated_collection = config_manager.update_collection(id, config)
                result_config = updated_collection.model_dump(mode="json")

            elif operation == "delete":
                # Delete collection
                config_manager.delete_collection(id)
                result_config = None

            elif operation == "get":
                # Get collection configuration
                collection = config_manager.get_collection(id)
                if collection is None:
                    duration_sec = time.time() - start_time
                    return {
                        "status": "error",
                        "error": {
                            "code": "NOT_FOUND",
                            "message": f"Collection '{id}' not found",
                        },
                        "metadata": {
                            "duration_sec": round(duration_sec, 3),
                        },
                    }
                result_config = collection.model_dump(mode="json")

        duration_sec = time.time() - start_time

        return {
            "status": "success",
            "result": {
                "operation": operation,
                "type": type,
                "id": id,
                "config": result_config,
            },
            "metadata": {
                "duration_sec": round(duration_sec, 3),
            },
        }

    except KeyError as e:
        # Handle not found errors from ConfigManager
        duration_sec = time.time() - start_time
        return {
            "status": "error",
            "error": {
                "code": "NOT_FOUND",
                "message": str(e).strip("'"),
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
                "code": "CONFIGURATION_ERROR",
                "message": str(e),
                "type": e.__class__.__name__,
            },
            "metadata": {
                "duration_sec": round(duration_sec, 3),
            },
        }
