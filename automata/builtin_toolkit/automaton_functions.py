"""Run a specific automaton and its sub-automata."""

from functools import partial
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Union

from langchain import LLMChain
from langchain.agents import load_tools
from langchain.llms.base import BaseLLM
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from automata.engines import load_engine
from automata.types import AutomatonRunner, Engine


def save_text_to_workspace(
    action_input: str, self_name: str, workspace_name: str
) -> str:
    """Save a file."""
    try:
        input_json = json.loads(action_input)
        file_name = input_json["file_name"]
        content = input_json["content"]
        description = input_json.get("description", "")
    except (KeyError, json.JSONDecodeError):
        return "Could not parse input. Please provide the input in the following format: {file_name: <file_name>, description: <description>, content: <content>}"
    path: Path = Path(f"workspace/{workspace_name}/{file_name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content), encoding="utf-8")
    return f"{self_name}: saved file to `{path.relative_to('workspace')}`"


async def run_llm_assistant(request: str, engine: Engine) -> str:
    """Run an LLM assistant."""
    from langchain.schema import SystemMessage, HumanMessage
    system_message = SystemMessage(content="You are a helpful assistant who can help generate a variety of content. However, if anyone asks you to access files, or refers to something from a past interaction, you will immediately inform them that the task is not possible, and provide no further information.")
    request_message = HumanMessage(content=request)
    return await engine([system_message, request_message])
    

def load_builtin_function(
    automaton_id: str,
    automata_location: Path,
    automaton_data: Mapping[str, Any],
    requester_id: str,
) -> AutomatonRunner:
    """Load an automaton function, which are basically wrappers around external functionality (including other agents)."""

    automaton_path = automata_location / automaton_id
    extra_args: Union[None, Mapping[str, Any]] = automaton_data.get("extra_args")

    if automaton_id == "llm_assistant":
        if (
            extra_args is None
            or "engine" not in extra_args
            or extra_args["engine"] is None
        ):
            raise ValueError(
                f'Built-in automaton function `{automaton_id}` requires the "engine" value in the `extra_args` field of the spec.'
            )
        engine_name: str = extra_args["engine"]
        engine: Engine = load_engine(automaton_path, engine_name)  # type: ignore
        
        return partial(run_llm_assistant, engine=engine)

    elif automaton_id == "save_text":

        breakpoint()
        if requester_id is None:
            raise ValueError(
                "Cannot save file without a requester ID. Please provide a requester ID."
            )
        run = partial(
            save_text_to_workspace, self_name=full_name, workspace_name=requester_id
        )

    elif automaton_id == "think":
        run = lambda thought: f"I must think about my next steps. {thought}"

    elif automaton_id == "finalize":
        # not meant to actually be run; the finalize action should be caught by the parser first
        run = lambda _: ""

    elif automaton_id == "search":
        run = load_tools(["google-serper"], llm=engine)[0].run

    else:
        raise NotImplementedError(f"Unsupported function name: {automaton_id}.")

    return run
