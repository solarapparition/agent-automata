"""Builtin knowledge bases that can be used by automata."""

from typing import Set

from agent_automata.types import Engine, Knowledge, Union

BUILTIN_KNOWLEDGE: Set[str] = set()


def load_builtin_knowledge(name: str, engine: Union[Engine, None]) -> Knowledge:
    """Load a builtin engine."""

    raise ValueError(
        f"Knowledge base {name} not part of builtin knowledge bases: `{BUILTIN_KNOWLEDGE}`"
    )
