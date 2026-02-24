from __future__ import annotations

from pcq.graph.state import PCQState
from pcq.llm import get_llm, llm_decide


def think_node(state: PCQState) -> PCQState:
    model = state.get("model_name", "gpt-4.1-mini")
    llm = get_llm(model=model, temperature=0.0)

    out = llm_decide(
        llm=llm,
        goal=state["goal"],
        screenshot_b64=state["screenshot_b64"],
        last_result=state.get("last_result", ""),
        step=state["step"],
        max_steps=state["max_steps"],
    )
    state["last_action"] = out.action.model_dump()
    return state