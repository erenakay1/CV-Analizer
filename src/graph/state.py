"""
state.py
--------
LangGraph pipeline'in state'i.
"""

from typing import Annotated
from typing_extensions import TypedDict
import operator


class CareerPipelineState(TypedDict):
    """Multi-agent career advisor pipeline state."""

    # ── Input ───────────────────────────────────────────
    cv_text: str                    # CV raw text
    target_role: str                # Hedef pozisyon (optional)
    target_location: str            # İş arama lokasyonu (optional)

    # ── Agent Outputs (raw JSON strings) ────────────────
    analyzer_output: str            # Agent A: CV Analyzer
    critic_output:   str            # Agent B: CV Critic
    optimizer_output: str           # Agent C: CV Optimizer
    job_hunter_output: str          # Agent D: Job Hunter (Phase 2)

    # ── Flow Control ────────────────────────────────────
    retry_count: int                # Critic -> Analyzer loop sayisi
    approved:    bool               # Critic onay flag'i

    # ── Logging ─────────────────────────────────────────
    trace_log: Annotated[list[dict], operator.add]