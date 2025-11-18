"""CLI interface for chora-compose.

This module provides a command-line interface using Click.

Usage:
    chora-compose create my-artifact
    chora-compose discover
    chora-compose inspect my-artifact
"""

from .main import cli

__all__ = ["cli"]
