"""
router.py
---------
Critic sonrasi routing logic — PURE FUNCTION.
"""

from src.graph.state import CareerPipelineState
from src.core.constants import MAX_CRITIC_RETRIES


def critic_router(state: CareerPipelineState) -> str:
    """
    Conditional edge: critic -> ?

    Returns:
        "retry"     -> retry_node'a git (counter artir, sonra analyzer)
        "optimizer" -> onaylandı veya max retry asildi
    """

    # Case 1: Critic onayladı
    if state["approved"]:
        return "optimizer"

    # Case 2: Onaylanmadi ama retry kalan var
    if state["retry_count"] < MAX_CRITIC_RETRIES:
        return "retry"

    # Case 3: Max retry asildi
    return "optimizer"