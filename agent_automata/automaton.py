"""Core automata functionality."""

from functools import lru_cache
from pathlib import Path
from typing import Sequence

from .automaton_loading import load_automaton_data
from .builtin_toolkit.automaton_functions import load_builtin_function
from .knowledge import load_knowledge
from .planners import load_planner
from .reflectors import load_reflector
from .sessions import add_session_handling
from .types import Automaton, AutomatonRunner, AutomatonStep
from .utilities import generate_timestamp_id, quick_import
from .validators import load_validator


def load_automaton(
    automaton_id: str,
    requester_session_id: str,
    requester_id: str,
    automata_location: Path,
) -> Automaton:
    """Load an automaton from a YAML file."""
    return _load_automaton(
        automaton_id,
        requester_session_id,
        requester_id,
        automata_location,
    )


@lru_cache(maxsize=None)
def _load_automaton(  # pylint: disable=too-many-locals
    automaton_id: str,
    requester_session_id: str,
    requester_id: str,
    automata_location: Path,
) -> Automaton:
    self_session_id = generate_timestamp_id()
    automaton_path = automata_location / automaton_id
    automaton_data = load_automaton_data(automaton_path)
    name: str = automaton_data["name"]
    description: str = automaton_data["description"]

    input_info = automaton_data["input"]
    input_validator_data = input_info["validator"]
    input_requirements = input_info["requirements"]
    objectives = input_info["objectives"]
    validate_input = load_validator(
        automaton_path, input_validator_data, input_requirements, objectives
    )

    output_info = automaton_data["output"]
    output_format: str = output_info["format"]

    async def run_core_automaton(request: str) -> str:
        """Run a core automaton."""

        sub_automata = automaton_data["sub_automata"]
        if "think" not in sub_automata:
            raise ValueError(
                f"Core automaton runner: `{automaton_id}` must have a `finalize` sub-automaton defined."
            )
        if validate_input:
            valid, error = await validate_input(request)
            if not valid:
                return error

        reasoning_data = automaton_data["reasoning"]
        knowledge_name = reasoning_data["knowledge"]
        knowledge = load_knowledge(automaton_path, knowledge_name)
        reflector_data = reasoning_data["reflector"]
        reflect = load_reflector(automaton_path, reflector_data)
        planner_data = reasoning_data["planner"]
        plan = load_planner(automaton_path, planner_data)
        sub_automata_data = {
            id: load_automaton_data(automata_location / id)
            for id in sub_automata
        }

        steps_taken: Sequence[AutomatonStep] = []
        while True:
            reflection = (
                await reflect(request, steps_taken, knowledge) if reflect else None
            )
            planned_action, action_text = await plan(
                request, steps_taken, reflection, automaton_data, sub_automata_data
            )

            sub_automaton = load_automaton(
                planned_action.automaton_id,
                self_session_id,
                automaton_id,
                automata_location,
            )
            result = await sub_automaton.run(planned_action.request)
            current_step = AutomatonStep(
                reflection, action_text, planned_action, result
            )
            steps_taken.append(current_step)

            if planned_action.automaton_id == "finalize":
                return result

    async def run_builtin_function(request: str) -> str:
        """Load and run a built-in function."""
        if validate_input:
            valid, error = await validate_input(request)
            if not valid:
                return error

        run: AutomatonRunner = load_builtin_function(
            automaton_id,
            automata_location,
            automaton_data,
            requester_id=requester_id,
        )
        return await run(request)

    runner_name: str = automaton_data["runner"]

    if runner_name.endswith(".py"):
        run: AutomatonRunner = quick_import(automaton_path / runner_name).load(
            automaton_id,
            automata_location,
            automaton_data,
            requester_id=requester_id,
        )
    elif runner_name == "builtin_function_runner":
        run = run_builtin_function
    elif runner_name == "core_automaton_runner":
        run = run_core_automaton
    else:
        raise ValueError(
            f"Invalid runner name: {runner_name}. Must be a .py file or one of: {{builtin_function_runner, core_automaton_runner}}."
        )

    run = add_session_handling(
        run,
        automaton_id=automaton_id,
        automata_location=automata_location,
        session_id=self_session_id,
        automaton_name=name,
        requester_id=requester_id,
        requester_session_id=requester_session_id,
    )

    automaton = Automaton(
        id=automaton_id,
        name=name,
        run=run,
        description=description,
        input_requirements=input_requirements,
        output_format=output_format,
    )
    return automaton
