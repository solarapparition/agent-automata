"""Functionality for validating information for automata."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence, Union

from .builtin_toolkit.validators import BUILTIN_VALIDATORS, load_builtin_validator
from .engines import load_engine
from .types import IOValidator
from .utilities import quick_import


@lru_cache(maxsize=None)
def load_validator(
    automaton_path: Path,
    data: Union[Mapping[str, str], None],
    requirements: Sequence[Any],
    objectives: Sequence[str],
) -> Union[IOValidator, None]:
    """Load the input validator for an automaton."""

    if data is None:
        return None

    name = data["name"]
    engine = load_engine(automaton_path, data["engine"])
    
    if name.endswith(".py"):
        return quick_import(automaton_path / name).load(
            requirements=requirements, objectives=objectives, engine=engine
        )

    if engine is None:
        raise ValueError(
            f"Must specify `engine` for validator `{name}`. Please check specs at `{automaton_path}`."
        )
    if name in BUILTIN_VALIDATORS:
        return load_builtin_validator(
            name, requirements=requirements, engine=engine
        )

    raise ValueError(f"Validator `{name}` not found.")
