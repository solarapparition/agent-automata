"""Functionality for validating information for automata."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Union

from .builtin_toolkit.reflectors import load_builtin_reflector
from .engines import load_engine
from .types import Reflector
from .utilities import quick_import


def load_reflector(
    automaton_path: Path,
    data: Union[Mapping[str, Any], None],
) -> Union[Reflector, None]:
    """Load the input validator for an automaton."""
    if data is None:
        return None
    name: str = data["name"]
    engine_name: str = data["engine"]
    return _load_reflector(automaton_path, name, engine_name)


@lru_cache(maxsize=None)
def _load_reflector(
    automaton_path: Path,
    name: str,
    engine_name: str
) -> Union[Reflector, None]:
    engine = load_engine(automaton_path, engine_name)
    if name.endswith(".py"):
        return quick_import(automaton_path / name).load(engine)

    try:
        return load_builtin_reflector(name, engine=engine)
    except ValueError as error:
        raise error
