"""
cv_critic.py - Agent B: CV Critic
----------------------------------
Analyzer çıktısını denetler.
Eksik/yanlış varsa -> approved=False -> retry loop.
Her şey iyiyse -> approved=True -> Optimizer'a geç.
"""

from src.graph.state import CareerPipelineState
from src.models.llm import get_llm
from src.services.prompt_loader import load_prompt
from src.utils.parser import safe_json_parse


_USER_TEMPLATE = """Orijinal CV:

{cv_text}

--------------------------

Agent A (CV Analyzer) çıktığı analiz:

{analyzer_output}

Lütfen bu analizi denet ve JSON formatında döndür."""


def cv_critic_node(state: CareerPipelineState) -> dict:
    """
    Agent B: CV Critic node.
    Analyzer çıktısını denet -> approved flag'ini set.
    """
    llm           = get_llm()
    system_prompt = load_prompt("cv_critic")
    user_message  = _USER_TEMPLATE.format(
        cv_text=state["cv_text"],
        analyzer_output=state["analyzer_output"],
    )

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message},
    ])

    raw_output = response.content

    # JSON parse -> approved flag çıkar
    parsed   = safe_json_parse(raw_output)
    approved = parsed.get("critic_review", {}).get("approved", False)

    return {
        "critic_output": raw_output,
        "approved":      approved,
        "trace_log": [{
            "agent":          "CV Critic",
            "step":           "review_complete",
            "approved":       approved,
            "retry_count":    state["retry_count"],
            "output_preview": raw_output[:400],
        }],
    }