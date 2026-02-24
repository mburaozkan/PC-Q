from __future__ import annotations

from pcq.graph.state import PCQState
from pcq.llm import get_llm, llm_verify
from pcq.tools import screenshot_b64


def verify_node(state: PCQState) -> PCQState:
    # In dry-run, skip verify (nothing changed)
    if state.get("dry_run", False):
        return state

    if state.get("done"):
        return state

    state["screenshot_b64"] = screenshot_b64()

    model = state.get("model_name", "gpt-4.1-mini")
    llm = get_llm(model=model, temperature=0.0)

    state["done"] = llm_verify(llm=llm, goal=state["goal"], screenshot_b64=state["screenshot_b64"])
    return state