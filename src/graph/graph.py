"""
graph.py
--------
LangGraph StateGraph'i build ve compile eder.

Topology:
    START -> analyzer -> critic --(retry)--> retry_node -> analyzer  (loop)
                            |
                            +-----------(optimizer)---> optimizer -> END
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from langgraph.graph import StateGraph, END

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

from src.graph.state import CareerPipelineState
from src.graph.nodes.cv_analyzer import cv_analyzer_node
from src.graph.nodes.cv_critic import cv_critic_node
from src.graph.nodes.cv_optimizer import cv_optimizer_node
from src.graph.nodes.retry import retry_node
from src.graph.router import critic_router


def build_graph() -> "CompiledStateGraph":
    """
    Graph'i oluştur ve compile et.

    Returns:
        Compiled LangGraph — .invoke() ile çalıştırılır.
    """
    graph = StateGraph(CareerPipelineState)

    # ── Nodes ──────────────────────────────────────────
    graph.add_node("cv_analyzer",  cv_analyzer_node)
    graph.add_node("cv_critic",    cv_critic_node)
    graph.add_node("retry",        retry_node)
    graph.add_node("cv_optimizer", cv_optimizer_node)

    # ── Edges ──────────────────────────────────────────
    graph.set_entry_point("cv_analyzer")                # START -> analyzer

    graph.add_edge("cv_analyzer", "cv_critic")          # analyzer -> critic (her zaman)

    graph.add_conditional_edges(                        # critic -> router karar
        "cv_critic",
        critic_router,
        {
            "retry":     "retry",                       # not approved + retry left
            "optimizer": "cv_optimizer",                # approved OR max retry
        },
    )

    graph.add_edge("retry", "cv_analyzer")              # retry -> analyzer (loop back)
    graph.add_edge("cv_optimizer", END)                 # optimizer -> END

    return graph.compile()
