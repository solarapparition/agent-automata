"""Functions relating to the knowledge module for automata."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Union

from .builtin_toolkit.knowledge import load_builtin_knowledge
from .engines import load_engine
from .types import Knowledge
from .utilities import quick_import


def load_knowledge(
    automaton_path: Path,
    data: Union[Mapping[str, Any], None],
) -> Union[Knowledge, None]:
    """Load the background knowledge for an automaton."""
    if data is None:
        return None
    name: str = data["name"]
    engine_name: str = data["engine"]
    return _load_knowledge(automaton_path, name, engine_name)


@lru_cache(maxsize=None)
def _load_knowledge(
    automaton_path: Path,
    name: str,
    engine_name: str
) -> Union[Knowledge, None]:
    engine = load_engine(automaton_path, engine_name)
    if name.endswith(".py"):
        return quick_import(automaton_path / name).load(engine)
    try:
        return load_builtin_knowledge(name, engine)
    except ValueError as error:
        raise error
