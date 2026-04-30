# graph.py
from langgraph.graph import StateGraph, END, START
from langgraph.types import Send

from state import AgentState
from nodes import (
    parse_query,
    macro_node,
    political_node,
    sector_node,
    exit_node,
    fx_node,
    timing_node,
    aggregate_node,
    regulatory_node,
    brief_node,
    reflect_node,
)


# ---------------------------------------------------------------------------
# Conditional edge: check route before fanning out
# ---------------------------------------------------------------------------

def route_after_parse(state: AgentState):
    """If out of scope, go straight to END. Otherwise fan out to research nodes."""
    if state.get("route") == "direct":
        return END
    return "dispatch"

def dispatch_parallel_research(state: AgentState):
    return [
        Send("macro_node",     state),
        Send("political_node", state),
        Send("sector_node",    state),
        Send("exit_node",      state),
        Send("fx_node",        state),
        Send("timing_node",    state),
    ]


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("parse_query",     parse_query)
    graph.add_node("macro_node",      macro_node)
    graph.add_node("political_node",  political_node)
    graph.add_node("sector_node",     sector_node)
    graph.add_node("exit_node",       exit_node)
    graph.add_node("fx_node",         fx_node)
    graph.add_node("timing_node",     timing_node)
    graph.add_node("aggregate_node",  aggregate_node)
    graph.add_node("regulatory_node", regulatory_node)
    graph.add_node("brief_node",      brief_node)
    graph.add_node("reflect_node",    reflect_node)

    # Step 1: START → parse_query
    graph.add_edge(START, "parse_query")

    # Step 2: check scope — if out of scope go to END, otherwise dispatch research
    graph.add_conditional_edges(
        "parse_query",
        route_after_parse,
        {END: END, "dispatch": "dispatch"}
    )

    # Dispatch node fans out to 6 parallel research nodes
    graph.add_node("dispatch", lambda state: state)
    graph.add_conditional_edges(
        "dispatch",
        dispatch_parallel_research,
        ["macro_node", "political_node", "sector_node", "exit_node", "fx_node", "timing_node"]
    )

    # Step 3: All 6 parallel nodes → aggregate_node
    graph.add_edge("macro_node",     "aggregate_node")
    graph.add_edge("political_node", "aggregate_node")
    graph.add_edge("sector_node",    "aggregate_node")
    graph.add_edge("exit_node",      "aggregate_node")
    graph.add_edge("fx_node",        "aggregate_node")
    graph.add_edge("timing_node",    "aggregate_node")

    # Step 4: aggregate → regulatory
    graph.add_edge("aggregate_node", "regulatory_node")

    # Step 5: regulatory → brief (draft)
    graph.add_edge("regulatory_node", "brief_node")

    # Step 6: brief → reflect (critique + rewrite)
    graph.add_edge("brief_node", "reflect_node")

    # Step 7: reflect → END
    graph.add_edge("reflect_node", END)

    return graph.compile()
