"""
career_services.py
──────────────────
LLM tabanlı kariyer analiz pipeline'ı için servis katmanı.
"""

import os
from typing import Tuple

from src.api.cv_parser import parse_cv
from src.graph.graph import build_graph
from src.graph.state import CareerPipelineState
from src.models.schemas import (
    CareerAnalysisResult,
    CVParseResult,
    CVAnalysis,
    CVOptimizerOutput,
    JobSearchResult,
    JobRecommendation,
    AgentTraceEntry,
)
from src.utils.parser import safe_json_parse


def run_career_analysis(
    cv_file_path: str,
    cv_file_type: str,
    target_role: str = "",
    target_location: str = "",
) -> Tuple[dict, CareerPipelineState]:
    """Career analysis pipeline with LangSmith tracing (ham dict + state döner)."""

    # ── FORCE LangSmith Environment ──────────────────
    from src.core.config import settings

    if settings.langsmith_ok:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
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
        "cv_text": cv_data["raw_text"],
        "target_role": target_role,
        "target_location": target_location,
        "analyzer_output": "",
        "critic_output": "",
        "optimizer_output": "",
        "job_hunter_output": "",
        "retry_count": 0,
        "approved": False,
        "trace_log": [],
    }

    # LangSmith config
    config = {
        "tags": [
            "ai-career-advisor",
            "multi-agent",
            "cv-analysis",
            f"target-role:{target_role}" if target_role else "no-target-role",
        ],
        "metadata": {
            "run_type": "career_analysis",
            "cv_chars": cv_data["char_count"],
            "target_role": target_role,
            "target_location": target_location,
        },
        "run_name": f"CV Analysis - {target_role or 'General'}",
    }

    final_state: CareerPipelineState = pipeline.invoke(initial_state, config=config)

    return cv_data, final_state


def run_career_analysis_structured(
    cv_file_path: str,
    cv_file_type: str,
    target_role: str = "",
    target_location: str = "",
) -> CareerAnalysisResult:
    """
    Yüksek seviyeli servis fonksiyonu.

    - CV dosyasını okur,
    - LangGraph pipeline'ını çalıştırır,
    - Analyzer / Optimizer / Job Hunter çıktısını Pydantic modellerine map eder.
    """

    cv_data_raw, final_state = run_career_analysis(
        cv_file_path=cv_file_path,
        cv_file_type=cv_file_type,
        target_role=target_role,
        target_location=target_location,
    )

    # ── Analyzer output ───────────────────────────────
    analyzer_data = safe_json_parse(final_state["analyzer_output"])
    cv_analysis_raw = analyzer_data.get("cv_analysis", {})
    cv_analysis = CVAnalysis.model_validate(cv_analysis_raw)

    # ── Optimizer output ──────────────────────────────
    optimizer_data_raw = safe_json_parse(final_state["optimizer_output"])
    optimizer_output = CVOptimizerOutput.model_validate(optimizer_data_raw)

    # ── Job hunter output (opsiyonel) ────────────────
    if final_state.get("job_hunter_output"):
        job_data_raw = safe_json_parse(final_state["job_hunter_output"])
    else:
        job_data_raw = {
            "job_recommendations": [],
            "search_summary": "Job search not completed",
            "total_jobs_found": 0,
        }

    # Job recommendations listesi Pydantic'e map edilirken
    # olası veri hatalarına karşı esnek davranmak için model_validate kullanıyoruz.
    job_recommendations = [
        JobRecommendation.model_validate(job) for job in job_data_raw.get("job_recommendations", [])
    ]
    jobs = JobSearchResult(
        job_recommendations=job_recommendations,
        search_summary=job_data_raw.get("search_summary", ""),
        total_jobs_found=job_data_raw.get("total_jobs_found", len(job_recommendations)),
    )

    # ── CV parse result ───────────────────────────────
    cv_parsed = CVParseResult(
        raw_text=cv_data_raw["raw_text"],
        char_count=cv_data_raw["char_count"],
    )

    # ── Trace log ─────────────────────────────────────
    trace_entries = [
        AgentTraceEntry(
            agent=entry.get("agent"),
            step=entry.get("step"),
            details={k: v for k, v in entry.items() if k not in {"agent", "step"}},
        )
        for entry in final_state.get("trace_log", [])
    ]

    return CareerAnalysisResult(
        cv=cv_parsed,
        analysis=cv_analysis,
        optimization=optimizer_output,
        jobs=jobs,
        retry_count=final_state.get("retry_count", 0),
        approved=final_state.get("approved", False),
        trace_log=trace_entries,
    )
