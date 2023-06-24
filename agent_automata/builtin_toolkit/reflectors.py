"""Built-in reflectors for automata."""

from typing import Set, Union

from agent_automata.types import Engine, Reflector

BUILTIN_REFLECTORS: Set[str] = set()

def load_builtin_reflector(name: str, engine: Union[Engine, None]) -> Reflector:
    """Load a built-in reflector."""
    raise NotImplementedError
