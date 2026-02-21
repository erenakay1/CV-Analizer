"""
retry.py - Retry Node
----------------------
retry_count'u artiran tek node.
trace_log'a yazar, sonra Analyzer'e gecer.
"""

from src.graph.state import CareerPipelineState
from src.core.constants import MAX_CRITIC_RETRIES


def retry_node(state: CareerPipelineState) -> dict:
    """
    retry_count += 1 yap ve trace log'a yaz.
    """
    new_count = state["retry_count"] + 1

    return {
        "retry_count": new_count,
        "trace_log": [{
            "agent":   "Retry",
            "step":    "retry_loop",
            "message": (
                f"Critic onaylamadı. "
                f"Retry {new_count}/{MAX_CRITIC_RETRIES} — Analyzer'a tekrar gönderildi."
            ),
        }],
    }