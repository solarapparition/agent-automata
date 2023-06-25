"""Planner adapted from the ReAct framework."""

from string import ascii_lowercase
import re
from typing import Any, Mapping, Sequence, Tuple, Union

from agent_automata.types import AutomatonStep, AutomatonAction, Engine

SUB_AUTOMATON_DESCRIPTION = """`{sub_automaton_name}`:
- Description: {description}
- Input Requirements:
  {input_requirements}"""

DIRECTIVES = """You are simulating the output of an "Automaton" called `{name}`. Automata are advanced AI agents capable of fulfilling requests in a predictable way.

Request: `{name}` has been asked to complete the following Request:
```
{request}
```

Sub-Automata: Sub-Automata are subsidiary agents that an Automaton can call upon to perform tasks needed to perform the Request. `{name}` has access to the following sub-automata:
{sub_automata_descriptions}

Reasoning Thoughtcycle:
`{name}` goes through a consistent reasoning process to standardize the process for completing requests. To make use of it, it outputs the following thoughtcycle:
```thoughtcycle_format
Reflection: `{name}` reflects abstractly upon the events that have occurred so far, as well as relevant information it can recall from its knowledge
Thought: `{name}` analyzes its Result, Reflection and Progress Record to come to a decision about the current status of the Request 
Progress Record: `{name}` keeps track of an itemized record of actions taken so far and their outcomes, including the names of artifacts (e.g. files) generated
Next Action: a concrete, achievable action that can be taken by a Sub-Automaton to make progress on the Request
Sub-Automaton Name: the name of the Sub-Automaton to request the Next Action. MUST be one of the following: [{sub_automata_names}]
Sub-Automaton Input Requirements: the Input Requirements of the Sub-Automaton being used, copied from above
Sub-Automaton Input: the request to send to the Sub-Automaton. This MUST follow any Input Requirements of the Sub-Automaton, as described above
Result: the reply from the Sub-Automaton, which can include error messages or requests for clarification
... (this `Reflection -> Progress Record -> Thought -> Next Action -> Sub-Automaton Name -> Sub-Automaton Input Requirements -> Sub-Automaton Input -> Result` thoughtcycle repeats until no further delegation to Sub-Automata is needed, or `{name}` determines that the Request cannot be completed)
```

General instructions regarding the `{name}`'s work process:
- `{name}` always adheres to the Input Requirements of the Sub-Automata it uses
- `{name}`'s output always follows the format of the thoughtcycle defined above
- when `{name}` receives a reply from a Sub-Automaton, it will always parse the reply and use it to update its Progress Record
- if `{name}` completes the request and OR it determines that the Request cannot be completed, it uses the `Finalize Reply` Sub-Automaton to report its result back to the requester

Begin the simulation of `{name}` below, after the divider. Do not include any other text besides what `{name}` would output."""

STEP_INTRO = """---`{name}`: Thoughtcycle---

Reflection:
{reflection}

Thought:"""

PREVIOUS_STEP = """{STEP_INTRO}
{plan}

Result:
{result}"""

PROMPT = """{DIRECTIVES}

{previous_steps}{STEP_INTRO}"""


def parse_result(result: str) -> Tuple[str, str]:
    """Parse the result of the ReAct planner."""

    action_regex = r"Sub-Automaton Name\s*\d*\s*:(.*?)\nSub-Automaton\s*\d*\s*Input\s*\d*\s*Requirements\s*\d*\s*:(.*?)\nSub-Automaton\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
    match = re.search(action_regex, result, re.DOTALL)

    if not match or len(match.groups()) < 3:
        return (
            "Think",
            "I must output the following:\n- the `Sub-Automaton Name` to send a request to\n- the `Input Requirements`\n- what `Sub-Automaton Input` to send\nThe output must follow the format specified in the `thoughtcycle_format` block above",
        )

    sub_automaton_name = match.group(1).strip().strip(" ").strip('"').strip(".")
    sub_automaton_request = match.group(3).strip().strip(" ").strip('"').strip(".")
    return sub_automaton_name, sub_automaton_request


async def react_planner(
    request: str,
    steps_taken: Sequence[AutomatonStep],
    reflection: Union[Sequence[str], None],
    automaton_data: Mapping[str, Any],
    sub_automata_data: Mapping[str, Any],
    engine: Engine,
) -> Tuple[AutomatonAction, str]:
    """Planner adapted from the ReAct framework."""

    if "think" not in sub_automata_data:
        raise ValueError(
            "The ReAct planner requires a sub-automaton named `think` to be defined."
        )

    sub_automata_names = [f'"{data["name"]}"' for data in sub_automata_data.values()]
    sub_automata_descriptions = [
        SUB_AUTOMATON_DESCRIPTION.format(
            sub_automaton_name=sub_automaton["name"],
            description=sub_automaton["description"],
            input_requirements="\n  ".join(
                f"{letter}. {requirement}"
                for letter, requirement in zip(
                    ascii_lowercase, sub_automaton["input"]["requirements"]
                )
            ),
        )
        for sub_automaton in sub_automata_data.values()
    ]

    automaton_name = automaton_data["name"]

    directives = DIRECTIVES.format(
        name=automaton_name,
        request=request,
        sub_automata_names=", ".join(sub_automata_names),
        sub_automata_descriptions="\n".join(sub_automata_descriptions),
    )
    step_intro = STEP_INTRO.format(
        name=automaton_name,
        reflection="\n".join(f" -{line}" for line in reflection)
        if reflection
        else "None",
    )
    formatted_previous_steps = (
        [
            PREVIOUS_STEP.format(
                STEP_INTRO=step_intro,
                plan=step.plan_text,
                result=step.result,
            )
            for step in steps_taken
        ]
        if steps_taken
        else []
    )

    prompt = PROMPT.format(
        DIRECTIVES=directives,
        previous_steps="\n\n".join(formatted_previous_steps) + "\n\n"
        if steps_taken
        else "",
        STEP_INTRO=step_intro,
    )
    if not steps_taken:
        print(directives)
    print("\n" + step_intro)
    result = (await engine(prompt, stop=["Result:", "---"])).strip()
    print(result)
    delegate_name, delegate_request = parse_result(result)

    try:
        delegate_id = next(
            id
            for id, data in sub_automata_data.items()
            if data["name"] == delegate_name
        )
    except StopIteration:
        return (
            AutomatonAction(
                "think",
                f"The Sub-Automaton Name must be one of the following: {sub_automata_names}",
            ),
            result,
        )
    return AutomatonAction(delegate_id, delegate_request), result
