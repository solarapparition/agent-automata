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
    output_validator_data = output_info["validator"]
    validate_output = load_validator(
        automaton_path, output_validator_data, output_format, objectives
    )

    async def run_core_automaton(request: str) -> str:
        """Run a core automaton."""

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
            for id in automaton_data["sub_automata"]
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

    breakpoint()

    def run_core_automaton(request: str) -> str:
        breakpoint()
        sub_automata = [
            load_automaton(
                sub_automata_id,
                requester_session_id=self_session_id,
                requester_id=automaton_id,
                automata_location=automata_location,
            )
            for sub_automata_id in automaton_data["sub_automata"]
        ]
        create_background_knowledge = load_knowledge(
            automaton_path,
            automaton_data["knowledge"],
        )
        background_knowledge = (
            create_background_knowledge(args[0])
            if create_background_knowledge
            else None
        )
        prompt = create_automaton_prompt(
            objective=automaton_data["objective"],
            self_instructions=automaton_data["instructions"],
            self_imperatives=automaton_data["imperatives"],
            role_info=get_role_info(automaton_data["role"]),
            background_knowledge=background_knowledge,
            sub_automata=sub_automata,
            requester_full_name=get_full_name(requester_id, automata_location),
        )
        # print(prompt.format(input="blah", agent_scratchpad={}))
        # breakpoint()
        agent_executor = AutomatonExecutor.from_agent_and_tools(
            agent=AutomatonAgent(
                llm_chain=LLMChain(llm=engine, prompt=prompt),
                allowed_tools=[sub_automaton.name for sub_automaton in sub_automata],
                output_parser=AutomatonOutputParser(validate_output=validate_output),
                reflect=reflect,
                planner=planner,
            ),
            tools=sub_automata,
            verbose=True,
            max_iterations=None,
            max_execution_time=None,
        )
        return agent_executor.run(*args, **kwargs)

    breakpoint()

    return automaton


# from functools import lru_cache, partial
# from pathlib import Path
# from typing import Callable, Dict, List, Union

# from langchain import LLMChain, PromptTemplate
# from langchain.agents import Tool
# import yaml

# from automata.engines import create_engine
# from automata.builtin_functions import load_builtin_function
# from automata.validation import (
#     load_input_validator,
#     load_output_validator,
#     IOValidator,
# )
# from automata.reasoning import (
#     AutomatonAgent,
#     AutomatonExecutor,
#     AutomatonOutputParser,
# )
# from automata.knowledge import load_knowledge
# from automata.loaders import (
#     get_full_name,
#     get_role_info,
#     load_automaton_data,
# )
# from automata.planners import load_planner
# from automata.reflection import load_reflect
# from automata.sessions import add_session_handling
# from automata.types import Automaton, AutomatonRunner
# from automata.utilities import generate_timestamp_id
# from .utilities.importing import quick_import


# def create_automaton_prompt(
#     objective: str,
#     self_instructions: List[str],
#     self_imperatives: List[str],
#     role_info: Dict[str, str],
#     sub_automata: List[Tool],
#     requester_full_name: str,
#     background_knowledge: Union[str, None],
# ) -> PromptTemplate:
#     """Put together a prompt for an automaton."""

#     imperatives = role_info["imperatives"] + (self_imperatives or [])
#     imperatives = "\n".join([f"- {imperative}" for imperative in imperatives]) or "N/A"

#     instructions = (self_instructions or []) + role_info["instructions"]
#     instructions = (
#         "\n".join([f"- {instruction}" for instruction in instructions]) or "N/A"
#     )
#     affixes: Dict[str, str] = {
#         key: val.strip()
#         for key, val in yaml.load(
#             Path("automata/prompts/automaton.yml").read_text(encoding="utf-8"),
#             Loader=yaml.FullLoader,
#         ).items()
#     }

#     prefix = affixes["prefix"].format(
#         role_description=role_info["description"],
#         imperatives=imperatives,
#         background_knowledge=background_knowledge,
#     )

#     suffix = (
#         affixes["suffix"]
#         .replace("{instructions}", instructions)
#         .replace("{objective}", objective)
#         .replace("{requester}", requester_full_name)
#     )
#     prompt = AutomatonAgent.create_prompt(
#         sub_automata,
#         prefix=prefix,
#         suffix=suffix,
#         input_variables=["input", "agent_scratchpad"],
#         format_instructions=role_info["output_format"],
#     )
#     return prompt


# @lru_cache(maxsize=None)
# def load_automaton(
#     automaton_id: str,
#     automata_location: Path,
#     requester_session_id: str,
#     requester_id: str,
# ) -> Automaton:
#     """Load an automaton from a YAML file."""

#     data = load_automaton_data(automata_location / automaton_id)
#     automaton_path = automata_location / automaton_id
#     full_name = f"{data['name']} ({data['role']} {data['rank']})"
#     engine = create_engine(data["engine"])

#     input_requirements = data["input_requirements"]
#     input_requirements_prompt = (
#         "\n".join([f"- {req}" for req in input_requirements])
#         if input_requirements
#         else "None"
#     )
#     description_and_input = (
#         data["description"] + f" Input requirements:\n{input_requirements_prompt}"
#     )

#     input_validator = load_input_validator(
#         data["input_validator"], input_requirements, automaton_id, automata_location
#     )

#     def run_builtin_function(*args, **kwargs) -> str:
#         run = load_builtin_function(
#             automaton_id,
#             automata_location,
#             data,
#             engine,
#             requester_id=requester_id,
#         )
#         return run(*args, **kwargs)

#     self_session_id = generate_timestamp_id()

#     # lazy load sub-automata until needed
#     def run_core_automaton(*args, **kwargs) -> str:
#         request = args[0]
#         output_validator: Union[IOValidator, None] = load_output_validator(
#             data["output_validator"], request=request, file_name=automaton_id
#         )
#         reflect: Union[Callable, None] = load_reflect(
#             automata_location / automaton_id, data["reflect"]
#         )
#         planner = load_planner(automaton_path, data["planner"])
#         sub_automata = [
#             load_automaton(
#                 sub_automata_id,
#                 requester_session_id=self_session_id,
#                 requester_id=automaton_id,
#                 automata_location=automata_location,
#             )
#             for sub_automata_id in data["sub_automata"]
#         ]
#         create_background_knowledge = load_knowledge(
#             automaton_path,
#             data["knowledge"],
#         )
#         background_knowledge = (
#             create_background_knowledge(args[0])
#             if create_background_knowledge
#             else None
#         )
#         prompt = create_automaton_prompt(
#             objective=data["objective"],
#             self_instructions=data["instructions"],
#             self_imperatives=data["imperatives"],
#             role_info=get_role_info(data["role"]),
#             background_knowledge=background_knowledge,
#             sub_automata=sub_automata,
#             requester_full_name=get_full_name(requester_id, automata_location),
#         )
#         # print(prompt.format(input="blah", agent_scratchpad={}))
#         # breakpoint()
#         agent_executor = AutomatonExecutor.from_agent_and_tools(
#             agent=AutomatonAgent(
#                 llm_chain=LLMChain(llm=engine, prompt=prompt),
#                 allowed_tools=[sub_automaton.name for sub_automaton in sub_automata],
#                 output_parser=AutomatonOutputParser(validate_output=output_validator),
#                 reflect=reflect,
#                 planner=planner,
#             ),
#             tools=sub_automata,
#             verbose=True,
#             max_iterations=None,
#             max_execution_time=None,
#         )
#         return agent_executor.run(*args, **kwargs)

#     runner_name: str = data["runner"]

#     if runner_name.endswith(".py"):
#         custom_runner: AutomatonRunner = quick_import(
#             automata_location / runner_name
#         ).run
#         runner = partial(
#             custom_runner,
#             automaton_id=automaton_id,
#             automata_data=data,
#             requester_id=requester_id,
#         )
#     elif runner_name == "default_function_runner":
#         runner = run_builtin_function
#     elif runner_name == "default_automaton_runner":
#         runner = run_core_automaton
#     else:
#         raise NotImplementedError(f"Unknown runner {runner_name}")

#     automaton = Tool(
#         full_name,
#         add_session_handling(
#             runner,
#             automaton_id=automaton_id,
#             automata_location=automata_location,
#             session_id=self_session_id,
#             full_name=full_name,
#             requester_id=requester_id,
#             input_validator=input_validator,
#             requester_session_id=requester_session_id,
#         ),
#         description_and_input,
#     )
#     return automaton
