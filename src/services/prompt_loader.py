"""
prompt_loader.py
────────────────
prompts/ klasöründen .txt dosyaları okur ve cache'ler.
"""

import os
from functools import lru_cache

from src.core.constants import (
    PROMPT_CV_ANALYZER_PATH,
    PROMPT_CV_CRITIC_PATH,
    PROMPT_CV_OPTIMIZER_PATH,
    PROMPT_JOB_HUNTER_PATH,
)

# ─── Path mapping ────────────────────────────────────────
_PROMPT_PATHS: dict[str, str] = {
    "cv_analyzer": PROMPT_CV_ANALYZER_PATH,
    "cv_critic":   PROMPT_CV_CRITIC_PATH,
    "cv_optimizer": PROMPT_CV_OPTIMIZER_PATH,
    "job_hunter":  PROMPT_JOB_HUNTER_PATH,
}


@lru_cache(maxsize=8)
def load_prompt(name: str) -> str:
    """
    Prompt dosyasını oku ve döndür. İlk okumada cache'lenir.

    Args:
        name: "cv_analyzer" | "cv_critic" | "cv_optimizer" | "job_hunter"

    Returns:
        Prompt text string

    Raises:
        KeyError:      Bilinmeyen prompt adı
        FileNotFoundError: Dosya yok
    """
    if name not in _PROMPT_PATHS:
        raise KeyError(
            f"Bilinmeyen prompt: '{name}'. "
            f"Geçerli: {list(_PROMPT_PATHS.keys())}"
        )

    path = _PROMPT_PATHS[name]

    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Prompt dosyası bulunamadı: {path}"
        )

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()