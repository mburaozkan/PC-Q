from __future__ import annotations
from pcq.graph.state import PCQState


def router(state: PCQState) -> str:
    if state.get("done"):
        return "end"
    if state.get("step", 0) >= state.get("max_steps", 0):
        return "end"
    return "loop"