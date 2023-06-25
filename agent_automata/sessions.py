"""Functionality relating to session management."""

import functools
import json
from pathlib import Path
from typing import Callable, Dict, Tuple, Union

from .types import AutomatonRunner
from .utilities import generate_timestamp_id

def save_event(event: Dict[str, str], automaton_id: str, automata_location: Path, session_id: str):
    """Save an event to the event log of an automaton."""
    log_path = automata_location / f"{automaton_id}/event_log/{session_id}.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")


def add_session_handling(
    run: AutomatonRunner,
    *,
    automaton_id: str,
    automata_location: Path,
    session_id: str,
    automaton_name: str,
    requester_id: str,
    requester_session_id: str,
) -> AutomatonRunner:
    """Handle errors and printouts during execution of a query."""
    preprint = f"\n\n---{automaton_name}: Start---\n\n"
    postprint = f"\n\n---{automaton_name}: End---\n\n"

    @functools.wraps(run)
    async def wrapper(request: str):
        print(preprint)
        try:
            result = await run(request)
        except KeyboardInterrupt:
            # manual interruption should escape back to the requester
            result = f"Sub-automaton `{automaton_name}` took too long to process and was manually stopped."
        print(postprint)

        event = {
            "requester": requester_id,
            "sub_automaton_name": automaton_id,
            "input": request,
            "result": result,
            "timestamp": generate_timestamp_id(),
        }
        save_event(event, automaton_id, automata_location, session_id)
        save_event(event, requester_id, automata_location, requester_session_id)
        return result

    return wrapper
