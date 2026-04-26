"""
LangGraph state machine for the Financial AI pipeline (Task 1).

Architecture:
    planner → [fan-out] → rag_agent ─┐
                         financial_data → [merge via Annotated reducers] → END
                         regulation  ─┘
                         graph_rag   ─┘

LangGraph v1.x does NOT automatically fan-out when you call add_edge() to
multiple nodes from one source.  The correct pattern is to use a router node
that returns a list of `Send` objects, one per worker.
"""
from langgraph.graph import StateGraph, END
from langgraph.types import Send

from graph.state import GraphState
from agents.planner import planner_node
from agents.workers.rag_agent import rag_agent_node
from agents.workers.financial_data_agent import financial_data_node
from agents.workers.regulation_agent import regulation_node
from agents.workers.graph_rag_agent import graph_rag_node


# ---------------------------------------------------------------------------
# Fan-out router
# ---------------------------------------------------------------------------

def _fan_out_to_workers(state: GraphState) -> list[Send]:
    """
    Called after the planner finishes.
    Returns one Send per worker so LangGraph executes them in parallel.
    Each worker receives the *full* current state as its input.
    """
    return [
        Send("rag_agent", state),
        Send("financial_data", state),
        Send("regulation", state),
        Send("graph_rag", state),
    ]


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph():
    g = StateGraph(GraphState)

    # Register nodes
    g.add_node("planner", planner_node)
    g.add_node("rag_agent", rag_agent_node)
    g.add_node("financial_data", financial_data_node)
    g.add_node("regulation", regulation_node)
    g.add_node("graph_rag", graph_rag_node)

    # Entry point
    g.set_entry_point("planner")

    # Parallel fan-out: planner → all 4 workers simultaneously
    g.add_conditional_edges("planner", _fan_out_to_workers)

    # All workers finish at END for Task 1.
    # Developer B will replace these with edges to debate nodes.
    g.add_edge("rag_agent", END)
    g.add_edge("financial_data", END)
    g.add_edge("regulation", END)
    g.add_edge("graph_rag", END)

    return g.compile()
