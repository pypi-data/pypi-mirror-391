"""HTTP REST API for chora-compose.

This module provides a FastAPI-based REST API with OpenAPI/Swagger documentation.

Usage:
    uvicorn chora_compose.interfaces.http.server:app --reload
"""

from .server import app

__all__ = ["app"]
