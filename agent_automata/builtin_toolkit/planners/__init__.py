"""Builtin planners that can be used by automata."""

from functools import partial
from typing import Set, Union

from agent_automata.types import Engine, Planner
from .react import react_planner

BUILTIN_PLANNERS: Set[str] = {"react"}


def load_builtin_planner(
    name: str, engine: Union[Engine, None]
) -> Planner:
    """Load a builtin engine."""

    if name == "react":
        if engine is None:
            raise ValueError(
                "Engine must be specified for builtin planner `react`. Currently `None`."
            )
        return partial(react_planner, engine=engine)

    raise ValueError(
        f"Planner `{name}` not part of builtin planners: `{BUILTIN_PLANNERS}`."
    )


# from .types import AutomatonAction


# def default_zero_shot_planner(
#     agent: Agent,
#     intermediate_steps: List[Tuple[AutomatonAction, str]],
#     reflection: Union[str, None],
#     **kwargs,
# ) -> str:
#     """Default planner for automata."""

#     full_inputs = agent.get_full_inputs(intermediate_steps, **kwargs)
#     full_inputs[
#         "agent_scratchpad"
#     ] = f'{full_inputs["agent_scratchpad"]}\n{reflection}\n\n{agent.llm_prefix}'
#     full_output = agent.llm_chain.predict(**full_inputs)
#     return full_output
