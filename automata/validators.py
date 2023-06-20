"""Functionality for validating information for automata."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence, Tuple, Union

from .builtin_toolkit.validators import BUILTIN_VALIDATORS, load_builtin_validator
from .engines import load_engine
from .types import IOValidator
from .utilities import quick_import


def load_validator(
    automaton_path: Path,
    data: Union[Mapping[str, str], None],
    requirements: Union[Sequence[Any], None],
    objectives: Union[Sequence[str], None],
) -> Union[IOValidator, None]:
    """Load the input validator for an automaton."""
    if data is None:
        return None
    name: str = data["name"]
    engine_name: str = data["engine"]
    return _load_validator(
        automaton_path=automaton_path,
        name=name,
        engine_name=engine_name,
        requirements=tuple(requirements) if requirements is not None else tuple(),
        objectives=tuple(objectives) if objectives is not None else tuple(),
    )


@lru_cache(maxsize=None)
def _load_validator(
    automaton_path: Path,
    name: str,
    engine_name: str,
    requirements: Tuple[Any, ...],
    objectives: Tuple[str, ...],
) -> Union[IOValidator, None]:
    engine = load_engine(automaton_path, engine_name)

    if name.endswith(".py"):
        return quick_import(automaton_path / name).load(
            requirements=requirements, objectives=objectives, engine=engine
        )

    if engine is None:
        raise ValueError(
            f"Must specify `engine` for validator `{name}`. Please check specs at `{automaton_path}`."
        )
    if name in BUILTIN_VALIDATORS:
        return load_builtin_validator(name, requirements=requirements, engine=engine)

    raise ValueError(f"Validator `{name}` not found.")
