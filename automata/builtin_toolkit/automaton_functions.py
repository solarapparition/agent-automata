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


def run_llm_assistant(action_input: str, engine: BaseLLM) -> str:
    """Run an LLM assistant."""
    template = "You are a helpful assistant who can help generate a variety of content. However, if anyone asks you to access files, or refers to something from a past interaction, you will immediately inform them that the task is not possible, and provide no further information."
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    assistant_chain = LLMChain(llm=engine, prompt=chat_prompt)
    return assistant_chain.run(action_input)


def load_builtin_function(
    id: str,
    automata_location: Path,
    automaton_data: Mapping[str, Any],
    requester_id: str,
) -> Callable[[str], str]:
    """Load an automaton function, which are basically wrappers around external functionality (including other agents)."""

    breakpoint()

    run: Callable[[str], str]
    if id == "llm_assistant":
        if engine is None:
            raise ValueError(
                "Cannot load LLM assistant without an LLM engine. Please provide an LLM engine."
            )
        run = partial(run_llm_assistant, engine=engine)

    elif id == "save_text":
        if requester_id is None:
            raise ValueError(
                "Cannot save file without a requester ID. Please provide a requester ID."
            )
        run = partial(
            save_text_to_workspace, self_name=full_name, workspace_name=requester_id
        )

    elif id == "think":
        run = lambda thought: f"I must think about my next steps. {thought}"

    elif id == "finalize":
        # not meant to actually be run; the finalize action should be caught by the parser first
        run = lambda _: ""

    elif id == "search":
        run = load_tools(["google-serper"], llm=engine)[0].run

    else:
        raise NotImplementedError(f"Unsupported function name: {id}.")

    return run
