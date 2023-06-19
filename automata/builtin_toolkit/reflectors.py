"""Built-in reflectors for automata."""

from typing import Set

from automata.types import Engine, Reflector

BUILTIN_REFLECTORS: Set[str] = set()

def load_builtin_reflector(name: str, engine: Engine) -> Reflector:
    """Load a built-in reflector."""
    raise NotImplementedError
