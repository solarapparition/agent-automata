"""Functions relating to the knowledge module for automata."""

from pathlib import Path
from typing import Union

from .builtin_toolkit.knowledge import BUILTIN_KNOWLEDGE, load_builtin_knowledge
from .types import Knowledge
from .utilities import quick_import

def load_knowledge(
    automaton_path: Path,
    name: Union[str, None],
) -> Union[Knowledge, None]:
    """Load the background knowledge for an automaton."""
    if name is None:
        return None
    if name.endswith(".py"):
        return quick_import(automaton_path / name).load()
    try:
        return load_builtin_knowledge(name)
    except ValueError as error:
        raise error
