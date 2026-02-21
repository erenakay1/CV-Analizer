"""
cv_analyzer.py - Agent A: CV Analyzer
--------------------------------------
CV'yi okur, ATS score verir, skill gap ve issues tespit eder.

Retry logic:
  - retry_count == 0 → fresh analiz
  - retry_count > 0  → Critic'in missed_issues feedback'ini dahil et
"""

from src.graph.state import CareerPipelineState
from src.models.llm import get_llm
from src.services.prompt_loader import load_prompt


# ── İlk analiz (retry yok) ──────────────────────────────
_TEMPLATE_FRESH = """Analiz edilecek CV:

{cv_text}

{role_context}

Lütfen yukarıdaki CV'yi detaylı analiz et ve JSON formatında döndür."""


# ── Retry analiz (Critic feedback dahil) ─────────────────
_TEMPLATE_RETRY = """Analiz edilecek CV:

{cv_text}

{role_context}

─────────────────────────

⚠️ ÖNCEKİ ANALİZİN EKSİK KALDI!

Critic'in tespit ettiği EKSIK sorunlar:

{critic_missed_issues}

─────────────────────────

📋 SENİN ÖNCEKİ ANALİZİN (referans için):

{previous_analyzer_output}

─────────────────────────

GÖREV:
1. Önceki analizindeki TÜM sorunları koru (tekrar yaz)
2. Critic'in belirttiği EKSIK sorunları EKLE
3. ATS score'u güncelle (gerekirse)
4. Toplam liste = önceki + yeni eksikler

Lütfen KAPSAMLI ve TAM bir analiz yap.
JSON formatında döndür."""


def cv_analyzer_node(state: CareerPipelineState) -> dict:
    """
    Agent A: CV Analyzer node.
    - retry_count == 0 → fresh analiz
    - retry_count > 0  → Critic feedback ile retry analiz
    """
    llm           = get_llm()
    system_prompt = load_prompt("cv_analyzer")
    
    # Role context (optional)
    role_context = ""
    if state.get("target_role"):
        role_context = f"\n**Hedef Pozisyon:** {state['target_role']}\n"

    if state["retry_count"] == 0:
        # ── Fresh analiz ──────────────────────────────
        user_message = _TEMPLATE_FRESH.format(
            cv_text=state["cv_text"],
            role_context=role_context
        )
    else:
        # ── Retry: Critic feedback dahil ──────────────
        import json
        from src.utils.parser import safe_json_parse
        
        critic_data = safe_json_parse(state["critic_output"])
        missed_issues = critic_data.get("critic_review", {}).get("missed_issues", [])
        
        # Sadece eksik sorunları JSON string yap
        missed_str = json.dumps(missed_issues, ensure_ascii=False, indent=2)
        
        user_message = _TEMPLATE_RETRY.format(
            cv_text=state["cv_text"],
            role_context=role_context,
            critic_missed_issues=missed_str,
            previous_analyzer_output=state["analyzer_output"][:2000],  # İlk 2k char
        )

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message},
    ])

    return {
        "analyzer_output": response.content,
        "trace_log": [{
            "agent":           "CV Analyzer",
            "step":            "analysis_complete",
            "retry_iteration": state["retry_count"],
            "is_retry":        state["retry_count"] > 0,
            "output_preview":  response.content[:400],
        }],
    }