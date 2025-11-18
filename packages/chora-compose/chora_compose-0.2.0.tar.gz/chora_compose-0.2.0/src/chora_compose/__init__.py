"""chora-compose - Content generation and orchestration capability server.

This package provides multi-interface access to content generation capabilities:
- Native Python API (Composer class)
- CLI (chora-compose command)
- HTTP REST API (FastAPI server)
- MCP Server (Model Context Protocol)

Example:
    >>> from chora_compose import Composer
    >>> composer = Composer()
    >>> await composer.create("my-artifact")
"""

from chora_compose.interfaces.api import Composer

__version__ = "0.2.0"
__all__ = ["Composer"]
