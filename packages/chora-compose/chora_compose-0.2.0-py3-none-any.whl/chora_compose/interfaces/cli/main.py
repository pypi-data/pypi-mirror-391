"""CLI commands for chora-compose."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import click

from chora_compose.interfaces.api import Composer


def run_async(coro):
    """Helper to run async functions in Click commands."""
    return asyncio.run(coro)


def format_output(data: dict[str, Any], format_type: str = "json") -> str:
    """Format output data.

    Args:
        data: Data to format
        format_type: Output format - "json" or "text"

    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(data, indent=2)
    else:
        # Simple text format
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)


@click.group()
@click.version_option()
@click.option(
    "--base-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Base path for artifact storage (default: .chora/artifacts)",
)
@click.pass_context
def cli(ctx, base_path):
    """chora-compose - Content generation and orchestration.

    A capability server for workflow-oriented content generation.
    """
    ctx.ensure_object(dict)
    ctx.obj["base_path"] = base_path


@cli.command()
@click.argument("artifact_id")
@click.option(
    "--context",
    "-c",
    type=str,
    help="Context variables as JSON (e.g., '{\"title\": \"Hello\"}')",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force regeneration (bypass cache)",
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Output format",
)
@click.pass_context
def create(ctx, artifact_id, context, force, format):
    """Create artifact with idempotent caching.

    Examples:
        chora-compose create my-artifact
        chora-compose create my-artifact --context '{"title": "Hello"}'
        chora-compose create my-artifact --force
    """
    composer = Composer(base_path=ctx.obj.get("base_path"))

    # Parse context if provided
    context_dict = {}
    if context:
        try:
            context_dict = json.loads(context)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON in --context: {e}", err=True)
            sys.exit(1)

    # Create artifact
    try:
        result = run_async(composer.create(artifact_id, context_dict, force))
        click.echo(format_output(result, format))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("artifact_id")
@click.option(
    "--context",
    "-c",
    type=str,
    help="Context variables as JSON",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force regeneration",
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Output format",
)
@click.pass_context
def refresh(ctx, artifact_id, context, force, format):
    """Refresh stale artifacts.

    Examples:
        chora-compose refresh my-artifact
        chora-compose refresh my-artifact --force
    """
    composer = Composer(base_path=ctx.obj.get("base_path"))

    # Parse context if provided
    context_dict = {}
    if context:
        try:
            context_dict = json.loads(context)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON in --context: {e}", err=True)
            sys.exit(1)

    # Refresh artifact
    try:
        result = run_async(composer.refresh(artifact_id, context_dict, force))
        click.echo(format_output(result, format))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("artifact_id")
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Output format",
)
@click.pass_context
def inspect(ctx, artifact_id, format):
    """Inspect artifact metadata and freshness.

    Examples:
        chora-compose inspect my-artifact
    """
    composer = Composer(base_path=ctx.obj.get("base_path"))

    try:
        result = run_async(composer.inspect(artifact_id))
        click.echo(format_output(result, format))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--type",
    "-t",
    "item_type",
    type=click.Choice(["all", "templates", "collections", "configs"]),
    default="all",
    help="Type of items to discover",
)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Output format",
)
@click.pass_context
def discover(ctx, item_type, format):
    """Discover available templates and configurations.

    Examples:
        chora-compose discover
        chora-compose discover --type templates
    """
    composer = Composer(base_path=ctx.obj.get("base_path"))

    try:
        result = run_async(composer.discover(item_type))
        click.echo(format_output(result, format))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("item_type", type=click.Choice(["template", "collection", "freshness"]))
@click.argument("item_id")
@click.argument("config", type=str)
@click.option(
    "--format",
    type=click.Choice(["json", "text"]),
    default="json",
    help="Output format",
)
@click.pass_context
def configure(ctx, item_type, item_id, config, format):
    """Configure templates, collections, or freshness policies.

    CONFIG should be JSON string with configuration data.

    Examples:
        chora-compose configure template my-template '{"template_path": "templates/my.md"}'
        chora-compose configure collection my-collection '{"template_ids": ["t1", "t2"]}'
        chora-compose configure freshness daily '{"max_age_hours": 24}'
    """
    composer = Composer(base_path=ctx.obj.get("base_path"))

    # Parse config JSON
    try:
        config_dict = json.loads(config)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in config: {e}", err=True)
        sys.exit(1)

    try:
        result = run_async(composer.configure(item_type, item_id, config_dict))
        click.echo(format_output(result, format))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
