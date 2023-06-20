"""Planner adapted from the ReAct framework."""

from string import ascii_lowercase
from typing import Any, Mapping, Sequence, Union

from automata.types import AutomatonStep, AutomatonAction, Engine

DIRECTIVES = """You are simulating the output of an "Automaton" called `{name}`. Automata are advanced AI agent capable of fulfilling requests in a predictable way.

Request: `{name}` has been asked to complete the following Request:
{request}

Sub-Automata: Sub-Automata are subsidiary agents that an Automaton can call upon to perform tasks needed to perform the Request. `{name}` has access to the following sub-automata:
{sub_automata_descriptions}

Reasoning Thoughtcycle:
`{name}` goes through a consistent reasoning process to standardize the process for completing requests. To make use of it, it outputs the following thoughtcycle:
```thoughtcycle_format
1. Reflection: `{name}` reflects abstractly upon the events that have occurred so far, as well as relevant information it can recall from its knowledge
2. Progress Record: `{name}` keeps track of an itemized record of actions taken so far and their outcomes, including the names of artifacts (e.g. files) generated
3. Thought: `{name}` analyzes its Result, Reflection and Progress Record to come to a decision about the current status of the Request 
4. Next Action: based on the Thought, `{name}` constructs a concrete, achievable action that can be taken by one of its Sub-Automata to make progress on the Request
5. Sub-Automaton Name: the name of the Sub-Automaton to request the Next Action. MUST be one of the following: [{sub_automata_names}]
6. Input Requirements: the Input Requirements of the Sub-Automaton being used, copied from above
7. Sub-Automaton Input: the request to send to the Sub-Automaton. This MUST follow any Input Requirements of the Sub-Automaton, as described above
8. Result: the reply from the Sub-Automaton, which can include error messages or requests for clarification
... (this `Reflection -> Progress Record -> Thought -> Next Action -> Sub-Automaton Name -> Input Requirements -> Sub-Automaton Input -> Result` thoughtcycle repeats until no further delegation to Sub-Automata is needed, or `{name}` determines that the Request cannot be completed)
```

General instructions regarding the `{name}`'s work process:
- `{name}` always adheres to the Input Requirements of the Sub-Automata it uses
- `{name}`'s output always follows the format of the thoughtcycle defined above
- when `{name}` receives a reply from a Sub-Automaton, it will always parse the reply and use it to update its Progress Record
- if `{name}` completes the request and OR it determines that the Request cannot be completed, it uses the `Finalize Reply` Sub-Automaton to report its result back to the requester

Begin the simulation of `{name}` below, after the divider. Do not include any other text besides what `{name}` would output."""

SUB_AUTOMATON_DESCRIPTION = """`{sub_automaton_name}`:
- Description: {description}
- Input Requirements:
  {input_requirements}"""

PROGRESS_INTRO = """

---`{name}`: Thoughtcycle---

1. Reflection:
{reflection}

2. Progress Record:"""

PREVIOUS_STEPS = """{progress_intro}
{steps_text}"""


async def react_planner(
    request: str,
    steps_taken: Sequence[AutomatonStep],
    reflection: Union[Sequence[str], None],
    automaton_data: Mapping[str, Any],
    sub_automata_data: Mapping[str, Any],
    engine: Engine,
) -> AutomatonAction:
    """Planner adapted from the ReAct framework."""

    sub_automata_names = [f'"{data["name"]}"' for data in sub_automata_data.values()]

    sub_automata_descriptions = [
        SUB_AUTOMATON_DESCRIPTION.format(
            sub_automaton_name=data["name"],
            description=data["description"],
            input_requirements="\n  ".join(
                f"{letter}. {requirement}"
                for letter, requirement in zip(
                    ascii_lowercase, data["input_requirements"]
                )
            ),
        )
        for data in sub_automata_data.values()
    ]

    automaton_name = automaton_data["name"]

    directives = DIRECTIVES.format(
        name=automaton_name,
        request=request,
        sub_automata_names=", ".join(sub_automata_names),
        sub_automata_descriptions="\n".join(sub_automata_descriptions),
    )
    progress_intro = PROGRESS_INTRO.format(
        name=automaton_name,
        reflection="\n".join(f" -{line}" for line in reflection)
        if reflection
        else "N/A",
    )

    previous_steps_text = ""
    prompt = directives + previous_steps_text + progress_intro
    result = await engine(prompt, stop=["Result:", "---"])



    breakpoint()
