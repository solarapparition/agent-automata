"""Utilities for the package."""

from datetime import datetime
from importlib import import_module
import os
from pathlib import Path
from types import ModuleType


def generate_timestamp_id() -> str:
    """Generate an id based on the current timestamp."""
    return datetime.utcnow().strftime("%Y-%m-%d_%H%M-%S-%f")


def quick_import(location: Path) -> ModuleType:
    """Import a module directly from a Path."""
    return import_module(str(location.with_suffix("")).replace(os.path.sep, "."))
