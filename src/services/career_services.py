"""
career_service.py (UPDATED)
"""

import os
from src.api.cv_parser import parse_cv
from src.graph.graph import build_graph
from src.graph.state import CareerPipelineState


def run_career_analysis(
    cv_file_path: str,
    cv_file_type: str,
    target_role: str = "",
    target_location: str = ""
) -> tuple[dict, CareerPipelineState]:
    """Career analysis pipeline with LangSmith tracing."""

    # ── FORCE LangSmith Environment ──────────────────
    from src.core.config import settings
    
    if settings.langsmith_ok:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"  # ← EKLE!
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        print(f"✅ LangSmith tracing enabled: {settings.LANGSMITH_PROJECT}")
    else:
        print("⚠️ LangSmith API key missing, tracing disabled")

    # ── Step 1: CV Parse ──────────────────────────────
    cv_data = parse_cv(cv_file_path, cv_file_type)

    # ── Step 2: Pipeline çalıştır ────────────────────
    pipeline = build_graph()

    initial_state: CareerPipelineState = {
        "cv_text":          cv_data["raw_text"],
        "target_role":      target_role,
        "target_location":  target_location,
        "analyzer_output":  "",
        "critic_output":    "",
        "optimizer_output": "",
        "job_hunter_output": "",
        "retry_count":      0,
        "approved":         False,
        "trace_log":        [],
    }

    # LangSmith config (ENHANCED!)
    config = {
        "tags": [
            "ai-career-advisor",
            "multi-agent",
            "cv-analysis",
            f"target-role:{target_role}" if target_role else "no-target-role"
        ],
        "metadata": {
            "run_type": "career_analysis",
            "cv_chars": cv_data["char_count"],
            "target_role": target_role,
            "target_location": target_location,
        },
        "run_name": f"CV Analysis - {target_role or 'General'}",  # ← Trace'de görünür isim
    }

    final_state: CareerPipelineState = pipeline.invoke(initial_state, config=config)

    return cv_data, final_state