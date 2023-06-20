"""Planners for automata."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Union

from .builtin_toolkit.planners import load_builtin_planner
from .engines import load_engine
from .types import Planner
from .utilities import quick_import


def load_planner(
    automaton_path: Path,
    data: Mapping[str, Any],
) -> Planner:
    """Load planner for an automaton."""
    name: str = data["name"]
    engine_name: str = data["engine"]
    return _load_planner(automaton_path, name, engine_name)


@lru_cache(maxsize=None)
def _load_planner(
    automaton_path: Path,
    name: str,
    engine_name: str,
) -> Planner:
    engine = load_engine(automaton_path, engine_name)
    if name.endswith(".py"):
        return quick_import(automaton_path / name).load(engine)

    try:
        return load_builtin_planner(name, engine)
    except ValueError as error:
        raise error
