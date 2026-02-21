"""
config.py
─────────
App-wide configuration. Env var'lar burada yüklenir.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable settings. App startup'ta bir kez oluşur."""

    # ── API Keys ──────────────────────────────────────
    OPENAI_API_KEY:    str = os.getenv("OPENAI_API_KEY", "")
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    
    # ── Job Search APIs (optional) ────────────────────
    LINKEDIN_API_KEY:  str = os.getenv("LINKEDIN_API_KEY", "")
    INDEED_PUBLISHER_ID: str = os.getenv("INDEED_PUBLISHER_ID", "")
    RAPIDAPI_KEY:      str = os.getenv("RAPIDAPI_KEY", "")

    # ── LangSmith ─────────────────────────────────────
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT", "ai-career-advisor")

    # ── Application Settings ──────────────────────────
    MAX_CV_SIZE_MB:    int = int(os.getenv("MAX_CV_SIZE_MB", "5"))
    SUPPORTED_FORMATS: str = os.getenv("SUPPORTED_FORMATS", "pdf,docx,txt")

    # ── Validation ────────────────────────────────────
    @property
    def openai_ok(self) -> bool:
        return bool(self.OPENAI_API_KEY)

    @property
    def langsmith_ok(self) -> bool:
        return bool(self.LANGSMITH_API_KEY)
    
    @property
    def rapidapi_ok(self) -> bool:
        return bool(self.RAPIDAPI_KEY)

    @property
    def supported_formats_list(self) -> list[str]:
        return [fmt.strip() for fmt in self.SUPPORTED_FORMATS.split(",")]


# ─── Singleton ───────────────────────────────────────────
settings = Settings()