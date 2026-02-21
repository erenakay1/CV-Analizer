"""
parser.py
─────────
LLM çıktılarından JSON parse eden yardımcı functions.
"""

import json


def safe_json_parse(raw: str) -> dict:
    """
    LLM çıktısından JSON bul ve parse et.

    Handles:
        - ```json ... ``` markdown blocks
        - Leading/trailing whitespace
        - Plain JSON string

    Raises:
        ValueError: parse başarısız olursa
    """
    text = raw.strip()

    # markdown code block varsa çıkar
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.startswith("json"):
                inner = inner[4:]
            text = inner.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse hatası: {e}\n\nRaw input:\n{raw[:500]}") from e


def merge_issues(analyzer_output: str, critic_output: str) -> list[dict]:
    """
    Analyzer findings + Critic missed_issues'ı tek listede birleştir.
    Optimizer'a verilecek "all issues" listesi.
    """
    analyzer_data = safe_json_parse(analyzer_output)
    critic_data  = safe_json_parse(critic_output)

    all_issues = list(analyzer_data.get("cv_analysis", {}).get("issues", []))
    
    # Critic'in missed issues'ını ekle
    missed = critic_data.get("critic_review", {}).get("missed_issues", [])
    all_issues.extend(missed)

    return all_issues