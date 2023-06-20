"""Type definitions for automaton components."""

# pylint: disable=unnecessary-ellipsis, too-few-public-methods

from dataclasses import dataclass
from typing import (
    Any,
    Mapping,
    Protocol,
    Tuple,
    Sequence,
    Union,
)


class AutomatonRunner(Protocol):
    """Represents the run function of an automaton."""

    async def __call__(self, request: str) -> str:
        """Run the automaton on the given request."""
        ...


@dataclass(frozen=True)
class Automaton:
    """Represents an automaton."""

    id: str
    """Unique identifier for the automaton."""

    name: str
    """Name of the automaton. Viewable to requesters."""

    run: AutomatonRunner
    """Async function that takes in a query and returns a response."""

    capabilities: str
    """Description of what the automaton can do."""

    input_requirements: Sequence[Any]
    """Requirements for the input to the automaton."""

    output_format: Any
    """Format of the output of the automaton."""


@dataclass(frozen=True)
class AutomatonStep:
    """Represents a step in an automaton's execution."""

    ...


class Engine(Protocol):
    """Interface for a language model."""

    async def __call__(self, prompt: str) -> str:
        """Run the language model on the given prompt."""
        ...


class IOValidator(Protocol):
    """Represents an LLM-based validation function for validating whether inputs or outputs adhere to requirements."""

    requirements: Sequence[Any]

    async def __call__(self, value_to_validate: str) -> Tuple[bool, str]:
        """Validate the given input or output."""
        ...


class Knowledge(Protocol):
    """Represents an automaton's knowledge base."""

    async def __call__(self, topic: str) -> str:
        """Retrieve information relating to a topic from the knowledge base."""
        ...


class Reflector(Protocol):
    """Represents an automaton's ability to reflect on previous events and retrieve useful information related to its current task."""

    async def __call__(
        self,
        request: str,
        steps_taken: Sequence[AutomatonStep],
        knowledge: Union[Knowledge, None],
    ) -> Sequence[str]:
        """Reflect on the given prompt."""
        ...


@dataclass(frozen=True)
class AutomatonAction:
    """Represents an action for an automaton."""

    sub_automaton_id: str
    """ID of the sub-automaton to run."""

    sub_automaton_request: str
    """Request to send to the sub-automaton."""


class Planner(Protocol):
    """Represents an automaton's ability to plan its next steps."""

    async def __call__(
        self,
        request: str,
        steps_taken: Sequence[AutomatonStep],
        reflection: Union[Sequence[str], None],
        automaton_data: Mapping[str, Any],
        sub_automata_data: Mapping[str, Any],
    ) -> AutomatonAction:
        """Plan the next step."""
        ...
