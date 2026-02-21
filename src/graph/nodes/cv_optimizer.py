
"""
cv_optimizer.py - Agent C: CV Optimizer
----------------------------------------
Onaylanan tüm sorunlar için iyileştirilmiş CV sections yazar.
"""

import json

from src.graph.state import CareerPipelineState
from src.models.llm import get_llm
from src.services.prompt_loader import load_prompt
from src.utils.parser import merge_issues


_USER_TEMPLATE = """Orijinal CV:

{cv_text}

--------------------------

Tespit edilen tüm sorunlar (Analyzer + Critic):

{all_issues}

--------------------------

Lütfen her sorun için iyileştirilmiş versiyonlar yaz ve JSON formatında döndür."""


def cv_optimizer_node(state: CareerPipelineState) -> dict:
    """
    Agent C: CV Optimizer node.
    Analyzer + Critic sorunlarını birleştir -> LLM ile optimize -> optimizer_output'a yaz.
    """
    llm           = get_llm()
    system_prompt = load_prompt("cv_optimizer")

    # Analyzer + Critic'in tüm sorunlarını merge et
    all_issues   = merge_issues(state["analyzer_output"], state["critic_output"])
    approved_str = json.dumps(all_issues, ensure_ascii=False, indent=2)

    user_message = _USER_TEMPLATE.format(
        cv_text=state["cv_text"],
        all_issues=approved_str,
    )

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message},
    ])

    return {
        "optimizer_output": response.content,
        "trace_log": [{
            "agent":          "CV Optimizer",
            "step":           "optimization_complete",
            "output_preview": response.content[:400],
        }],
    }
