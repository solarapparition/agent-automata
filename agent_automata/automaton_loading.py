"""Load automaton info from source files."""

from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import yaml


def load_automaton_data(automaton_path: Path) -> Mapping[str, Any]:
    """Load an automaton from a YAML file."""
    return _load_automaton_data(automaton_path)


@lru_cache
def _load_automaton_data(automaton_path: Path) -> Mapping[str, Any]:
    data = yaml.load(
        (automaton_path / "spec.yml").read_text(encoding="utf-8"),
        Loader=yaml.FullLoader,
    )
    return data


# def get_full_name(automaton_id: str, automata_location: Path) -> str:
#     """Get the full name of an automaton."""
#     automaton_path = automata_location / automaton_id
#     data = load_automaton_data(automaton_path)
#     return f"{data['name']} ({data['role']} {data['rank']})"


# def get_role_info(role: str) -> Dict:
#     """Get the role info for a given role."""
#     return yaml.load(
#         Path(f"automata/prompts/roles/{role}.yml").read_text(encoding="utf-8"),
#         Loader=yaml.FullLoader,
#     )
