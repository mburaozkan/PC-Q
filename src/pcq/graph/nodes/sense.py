from __future__ import annotations
from pcq.graph.state import PCQState
from pcq.tools import screenshot_b64


def sense_node(state: PCQState) -> PCQState:
    state["screenshot_b64"] = screenshot_b64()
    state["step"] = state.get("step", 0) + 1
    return state