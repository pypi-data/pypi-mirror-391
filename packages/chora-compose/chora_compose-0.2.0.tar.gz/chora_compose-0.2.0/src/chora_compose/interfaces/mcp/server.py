"""chora-mcp-compose MCP Server.

This server implements the Model Context Protocol (MCP) following
Chora MCP Conventions v1.0 for tool/resource naming.

Tools are namespaced as: choracompose:tool_name
Resources use URI scheme: choracompose://type/id

Reference: https://github.com/liminalcommons/chora-base/blob/main/docs/standards/CHORA_MCP_CONVENTIONS_v1.0.md
"""

import logging
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from . import (
    NAMESPACE,
    make_resource_uri,
    make_tool_name,
    validate_resource_uri,
    validate_tool_name,
)
from chora_compose.core.orchestration.artifact_orchestrator import ArtifactOrchestrator
from chora_compose.core.storage.artifact_store import ArtifactStore
from .tools.config_manager import ConfigManager
from .tools.configure import configure_item
from .tools.create_refresh import create_artifact, refresh_artifact
from .tools.discover import discover_items
from .tools.inspect import inspect_artifact

# Configure logging
logger = logging.getLogger(__name__)

# === Version Resolution ===


def _get_version() -> str:
    """Get package version from installed metadata.

    Returns version from pyproject.toml (via package metadata) to ensure
    single source of truth. Falls back to development version if package
    is not installed (e.g., during development without editable install).

    Returns:
        Package version string (e.g., "1.5.0") or "0.0.0-dev" if not found.
    """
    try:
        return version("chora_compose")
    except PackageNotFoundError:
        # Development fallback when package not installed
        return "0.0.0-dev"


# === MCP Server Instance ===

mcp = FastMCP(
    name="chora-mcp-compose",
    version=_get_version(),
)

# === Server State Initialization ===

# Initialize artifact storage (default: .chora/artifacts in current directory)
_artifact_store = ArtifactStore(base_path=Path.cwd() / ".chora" / "artifacts")

# Initialize orchestrator for artifact generation
_orchestrator = ArtifactOrchestrator(artifact_store=_artifact_store)

# Initialize configuration manager for templates and collections
_config_manager = ConfigManager()

# === Workflow Tools ===

# Tool names are automatically namespaced via Chora MCP Conventions
# Full names: choracompose:create, choracompose:refresh


@mcp.tool()
async def create(
    id: str,
    context: dict[str, Any] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Create artifact with idempotent caching.

    Tool name: choracompose:create

    Generates content from templates with smart caching: fresh artifacts are
    returned from cache, stale artifacts are regenerated. Use force=True to
    bypass cache and always regenerate.

    Args:
        id: Unique identifier for artifact or collection
        context: Runtime context variables (default: {})
        force: If True, bypass cache and regenerate (default: False)

    Returns:
        Response dict with status, result, and metadata:
        - status: "success" or "error"
        - result: Artifact/collection details with freshness info
        - metadata: Generation metadata (duration, template_id, etc.)

    Raises:
        ValueError: If id is empty or configuration not found

    Example:
        # Create single artifact
        response = await create(id="hello.md", context={"name": "World"})

        # Create collection (generates all members)
        response = await create(id="docs-v1")

        # Force regeneration
        response = await create(id="stale.md", force=True)
    """
    logger.info(f"create() called: id={id}, force={force}")

    # Call synchronous tool function
    result = create_artifact(
        artifact_id=id,
        config_manager=_config_manager,
        orchestrator=_orchestrator,
        context=context,
        force=force,
    )

    logger.info(f"create() completed: status={result['status']}")
    return result


@mcp.tool()
async def refresh(
    id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Refresh artifact (always regenerates, bypassing cache).

    Tool name: choracompose:refresh

    Always regenerates content regardless of freshness. Use this when you need
    to update content with latest data or ensure it's regenerated.

    Args:
        id: Unique identifier for artifact or collection
        context: Runtime context variables (default: {})

    Returns:
        Response dict with status, result, and metadata:
        - status: "success" or "error"
        - result: Artifact/collection details (cached=False)
        - metadata: Generation metadata

    Raises:
        ValueError: If id is empty or configuration not found

    Example:
        # Refresh single artifact
        response = await refresh(id="doc.md")

        # Refresh collection (regenerates all members)
        response = await refresh(id="docs-v1")
    """
    logger.info(f"refresh() called: id={id}")

    # Call synchronous tool function
    result = refresh_artifact(
        artifact_id=id,
        config_manager=_config_manager,
        orchestrator=_orchestrator,
        context=context,
    )

    logger.info(f"refresh() completed: status={result['status']}")
    return result


@mcp.tool()
async def inspect(
    id: str,
    include_content: bool = False,
) -> dict[str, Any]:
    """Inspect artifact status and metadata without regenerating.

    Tool name: choracompose:inspect

    Check generation status, freshness metadata, and artifact details without
    triggering regeneration. Use this to check if content is stale before
    deciding to refresh, or to gather freshness statistics.

    Args:
        id: Unique identifier for artifact or collection
        include_content: If True, include full content in response (default: False)

    Returns:
        Response dict with status, result, and metadata:
        - status: "success" or "error"
        - result: Artifact/collection status with freshness info
        - metadata: Inspection metadata (duration)

    Example:
        # Check if artifact is fresh
        response = await inspect(id="doc.md")
        is_fresh = response["result"]["freshness"]["is_fresh"]

        # Inspect with content
        response = await inspect(id="doc.md", include_content=True)
        content = response["result"]["content"]

        # Inspect collection status
        response = await inspect(id="docs-v1")
        summary = response["result"]["summary"]
    """
    logger.info(f"inspect() called: id={id}, include_content={include_content}")

    # Call synchronous tool function
    result = inspect_artifact(
        artifact_id=id,
        artifact_store=_artifact_store,
        config_manager=_config_manager,
        include_content=include_content,
    )

    logger.info(f"inspect() completed: status={result['status']}")
    return result


@mcp.tool()
async def configure(
    operation: str,
    type: str,
    id: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Manage templates and collections at runtime.

    Tool name: choracompose:configure

    Register, update, delete, or get templates and collections. Use this to
    dynamically configure the system without restarting the server.

    Args:
        operation: Action to perform (register, update, delete, get)
        type: Configuration type (template or collection)
        id: Unique identifier
        config: Configuration data (required for register/update)

    Returns:
        Response dict with status, result, and metadata:
        - status: "success" or "error"
        - result: Operation details with current config
        - metadata: Operation metadata (duration)

    Example:
        # Register new template
        response = await configure(
            operation="register",
            type="template",
            id="greeting.md",
            config={
                "validation_schema": {"type": "object"},
                "generator": "llm",
                "generator_config": {
                    "prompt": "Generate greeting for {name}",
                    "model": "claude-3-5-sonnet-20241022"
                }
            }
        )

        # Update template
        response = await configure(
            operation="update",
            type="template",
            id="greeting.md",
            config={"generator_config": {"prompt": "New prompt"}}
        )

        # Get template configuration
        response = await configure(operation="get", type="template", id="greeting.md")

        # Delete template
        response = await configure(operation="delete", type="template", id="greeting.md")
    """
    logger.info(f"configure() called: operation={operation}, type={type}, id={id}")

    # Call synchronous tool function
    result = configure_item(
        operation=operation,
        type=type,
        id=id,
        config=config,
        config_manager=_config_manager,
    )

    logger.info(f"configure() completed: status={result['status']}")
    return result


@mcp.tool()
async def discover(
    type: str = "all",
    pattern: str | None = None,
) -> dict[str, Any]:
    """Browse available templates and collections.

    Tool name: choracompose:discover

    List all available templates and collections with optional pattern filtering.
    Use this to explore what's available in the system.

    Args:
        type: What to discover (template, collection, or all) (default: all)
        pattern: Optional glob pattern for filtering (e.g., "*.md")

    Returns:
        Response dict with status, result, and metadata:
        - status: "success" or "error"
        - result: Lists of templates and collections with summary
        - metadata: Discovery metadata (duration)

    Example:
        # Discover all templates and collections
        response = await discover()

        # Discover only templates
        response = await discover(type="template")

        # Discover with pattern filter
        response = await discover(type="template", pattern="*.md")

        # Check what's available
        templates = response["result"]["templates"]
        collections = response["result"]["collections"]
    """
    logger.info(f"discover() called: type={type}, pattern={pattern}")

    # Call synchronous tool function
    result = discover_items(
        type=type,
        pattern=pattern,
        config_manager=_config_manager,
    )

    logger.info(f"discover() completed: status={result['status']}")
    return result


# === Example Resources ===

# Resources use URI scheme: choracompose://type/id


@mcp.resource(uri=make_resource_uri("capabilities", "server"))
async def get_capabilities() -> dict[str, Any]:
    """Server capabilities resource.

    Resource URI: choracompose://capabilities/server

    Returns:
        Server metadata and capabilities

    Example:
        # Access via MCP client:
        capabilities = await client.get_resource("choracompose://capabilities/server")
    """
    uri = make_resource_uri("capabilities", "server")
    validate_resource_uri(uri, expected_namespace=NAMESPACE)

    return {
        "name": "chora-mcp-compose",
        "namespace": NAMESPACE,
        "version": _get_version(),
        "architecture": "4-Layer Architecture (v3.0.0)",
        "tools": {
            "implemented": [
                make_tool_name("create"),
                make_tool_name("refresh"),
                make_tool_name("inspect"),
                make_tool_name("configure"),
                make_tool_name("discover"),
            ],
            "planned": [],
        },
        "resources": [
            make_resource_uri("capabilities", "server"),
            make_resource_uri("config", "template"),
            "choracompose://templates/{id}",
            "choracompose://collections/{id}",
            "choracompose://artifacts/{id}/metadata",
        ],
        "conventions": "Chora MCP Conventions v1.0",
        "sprint_status": "Sprint 4-5 Complete (5-tool workflow interface)",
    }


@mcp.resource(uri=make_resource_uri("config", "template"))
async def get_template_config() -> dict[str, Any]:
    """Template configuration resource.

    Resource URI: choracompose://config/template

    Returns:
        Template configuration and customization guidance

    Example:
        config = await client.get_resource("choracompose://config/template")
    """
    return {
        "name": "chora-mcp-compose",
        "purpose": "Content generation and orchestration via MCP",
        "namespace": NAMESPACE,
        "description": {
            "short": "Workflow-oriented content generation with smart caching",
            "value_proposition": "88% tool call reduction, 74% token savings, 60-85% time savings",
        },
        "architecture": {
            "layers": [
                "Tool Interface (MCP tools: create, refresh, inspect, configure, discover)",
                "Orchestration (dependency resolution, collection management, freshness tracking)",
                "Core Operations (template rendering: LLM + Jinja2, artifact generation)",
                "Storage (artifact persistence, metadata management)",
            ],
            "coverage": "85%+ test coverage (Sprint 4-5)",
        },
        "usage": {
            "create": "Generate content with smart caching (fresh=cached, stale=regenerate)",
            "refresh": "Always regenerate content, bypass cache",
            "inspect": "Check artifact status and freshness without regenerating",
            "configure": "Manage templates and collections at runtime (register, update, delete, get)",
            "discover": "Browse available templates and collections with pattern filtering",
            "conventions": "https://github.com/liminalcommons/chora-base/blob/main/docs/standards/CHORA_MCP_CONVENTIONS_v1.0.md",
        },
    }


# === Sprint 4-5 Bonus Resources ===


@mcp.resource(uri="choracompose://templates/{id}")
async def get_template(id: str) -> dict[str, Any]:
    """Get full template configuration by ID.

    Resource URI: choracompose://templates/{id}

    Args:
        id: Template identifier

    Returns:
        Full template configuration

    Example:
        template = await client.get_resource("choracompose://templates/greeting.md")
    """
    template = _config_manager.get_template(id)
    if template is None:
        return {
            "error": "NOT_FOUND",
            "message": f"Template '{id}' not found",
            "suggestion": "Use discover(type='template') to list available templates",
        }

    return {
        "id": template.id,
        "validation_schema": template.validation_schema,
        "generator": template.generator.value,
        "generator_config": template.generator_config,
        "default_context": template.default_context,
    }


@mcp.resource(uri="choracompose://collections/{id}")
async def get_collection(id: str) -> dict[str, Any]:
    """Get full collection configuration by ID.

    Resource URI: choracompose://collections/{id}

    Args:
        id: Collection identifier

    Returns:
        Full collection configuration

    Example:
        collection = await client.get_resource("choracompose://collections/docs-v1")
    """
    collection = _config_manager.get_collection(id)
    if collection is None:
        return {
            "error": "NOT_FOUND",
            "message": f"Collection '{id}' not found",
            "suggestion": "Use discover(type='collection') to list available collections",
        }

    return {
        "id": collection.id,
        "members": collection.members,
        "dependencies": collection.dependencies,
        "context": collection.context,
        "template_id": collection.template_id,
        "freshness_policy": {
            "max_age_days": collection.freshness_policy.max_age_days,
        },
    }


@mcp.resource(uri="choracompose://artifacts/{id}/metadata")
async def get_artifact_metadata(id: str) -> dict[str, Any]:
    """Get artifact metadata without content.

    Resource URI: choracompose://artifacts/{id}/metadata

    Args:
        id: Artifact identifier

    Returns:
        Artifact metadata (no content)

    Example:
        metadata = await client.get_resource("choracompose://artifacts/doc.md/metadata")
    """
    # Use inspect tool to get metadata without content
    result = inspect_artifact(
        artifact_id=id,
        artifact_store=_artifact_store,
        config_manager=_config_manager,
        include_content=False,
    )

    if result["status"] == "error":
        return {
            "error": result["error"]["code"],
            "message": result["error"]["message"],
        }

    # Return just the result portion (metadata without wrapping)
    return result["result"]


# === Main Entry Point ===


def main() -> None:
    """Run the MCP server.

    This is the entry point registered in pyproject.toml:
        [project.scripts]
        chora-mcp-compose = "chora_compose.server:main"
    """
    logger.info("Starting chora-mcp-compose MCP server...")
    logger.info(f"Namespace: {NAMESPACE}")
    logger.info(f"Namespacing enabled: {True}")
    mcp.run()


if __name__ == "__main__":
    main()
