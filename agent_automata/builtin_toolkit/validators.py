"""Built-in validators for automata."""

from typing import Sequence, Set

from agent_automata.types import Engine, IOValidator

BUILTIN_VALIDATORS: Set[str] = set()

def load_builtin_validator(
    name: str, requirements: Sequence[str], engine: Engine
) -> IOValidator:
    """Load a builtin validator."""

    raise ValueError(
        f"Validator {name} not part of builtin validators: `{BUILTIN_VALIDATORS}`"
    )
