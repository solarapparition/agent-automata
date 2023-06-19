"""Functionality for validating information for automata."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Union

from .builtin_toolkit.reflectors import BUILTIN_REFLECTORS, load_builtin_reflector
from .engines import load_engine
from .types import Reflector
from .utilities import quick_import


def load_reflector(
    automaton_path: Path,
    data: Union[Mapping[str, Any], None],
) -> Union[Reflector, None]:
    """Load the input validator for an automaton."""
    return _load_reflector(automaton_path, data)


@lru_cache(maxsize=None)
def _load_reflector(
    automaton_path: Path,
    data: Union[Mapping[str, Any], None],
) -> Union[Reflector, None]:
    if data is None:
        return None

    name: str = data["name"]
    engine = load_engine(automaton_path, data["engine"])
    if name.endswith(".py"):
        return quick_import(automaton_path / name).load()

    if engine is None:
        raise ValueError(
            f"Must specify `engine` for reflector `{name}`. Please check specs at `{automaton_path}`."
        )

    if name in BUILTIN_REFLECTORS:
        return load_builtin_reflector(name, engine=engine)

    raise ValueError(f"Reflector `{name}` not found.")
