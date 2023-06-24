"""Create various engines for automata to use."""

from functools import lru_cache
from pathlib import Path
from typing import Union

from .types import Engine
from .utilities import quick_import
from .builtin_toolkit.engines import BUILTIN_ENGINES, load_builtin_engine


@lru_cache(maxsize=None)
def _load_engine(automaton_path: Path, name: Union[str, None]) -> Union[Engine, None]:
    if name is None:
        return None

    if name.endswith(".py"):
        return quick_import(automaton_path / name).load()

    try:
        return load_builtin_engine(name)
    except ValueError as error:
        raise error


def load_engine(automaton_path: Path, name: Union[str, None]) -> Union[Engine, None]:
    """Load the engine for an automaton."""
    return _load_engine(automaton_path, name)
