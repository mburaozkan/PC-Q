from __future__ import annotations

from rich.console import Console
from pcq.graph.state import PCQState
from pcq.llm.schemas import parse_action_dict, Done
from pcq.tools import execute_action

console = Console()

def act_node(state: PCQState) -> PCQState:
    action = parse_action_dict(state["last_action"])

    # Print what the AI wants to do
    console.print(f"[bold cyan]Step {state.get('step')} action:[/bold cyan] {action.model_dump()}")

    # If dry-run, do NOT execute
    if state.get("dry_run", False):
        state["last_result"] = "DRY_RUN: not executed"
        state["done"] = isinstance(action, Done)
        return state

    # Otherwise execute for real
    state["last_result"] = execute_action(action)
    state["done"] = isinstance(action, Done)
    return state