"""
FoundryDB package initializer.

This makes the 'foundrydb' directory a proper Python package and exposes
the main Database class at the package level.

Usage:
    from foundrydb import Database
"""

from .database import Database

__all__ = ["Database"]
