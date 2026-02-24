from __future__ import annotations

from langgraph.graph import StateGraph, END

from pcq.graph.state import PCQState
from pcq.graph.nodes import sense_node, think_node, act_node, verify_node, router


def build_graph():
    g = StateGraph(PCQState)

    g.add_node("sense", sense_node)
    g.add_node("think", think_node)
    g.add_node("act", act_node)
    g.add_node("verify", verify_node)

    g.set_entry_point("sense")
    g.add_edge("sense", "think")
    g.add_edge("think", "act")
    g.add_edge("act", "verify")

    g.add_conditional_edges("verify", router, {"loop": "sense", "end": END})
    return g.compile()