"""Native Python API for chora-compose.

This module provides a clean, Pythonic interface for programmatic access
to chora-compose functionality.

Example:
    >>> from chora_compose.interfaces.api import Composer
    >>> composer = Composer()
    >>> await composer.create("my-artifact", context={"title": "Hello"})
"""

from .composer import Composer

__all__ = ["Composer"]
