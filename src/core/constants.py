"""
constants.py
────────────
Tüm sabit değerler burada. Magic number yok.
"""

# ─── CV Processing ───────────────────────────────────────
MAX_CV_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
SUPPORTED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt"}

# Quick test mode için
QUICK_TEST_MODE: bool = True

if QUICK_TEST_MODE:
    MAX_CV_CHARS: int = 20_000      # 20k char max (hızlı test)
else:
    MAX_CV_CHARS: int = 50_000      # Normal: 50k char

# ─── Agent Pipeline ─────────────────────────────────────
MAX_CRITIC_RETRIES: int = 2 if QUICK_TEST_MODE else 3

# ─── LLM ─────────────────────────────────────────────────
DEFAULT_MODEL: str = "gpt-4o-mini"
DEFAULT_TEMPERATURE: float = 0.2  # Düşük = tutarlı analiz

# ─── ATS Scoring ─────────────────────────────────────────
MIN_ATS_SCORE: int = 60        # Minimum kabul edilebilir
GOOD_ATS_SCORE: int = 75       # İyi sayılan skor
EXCELLENT_ATS_SCORE: int = 85  # Mükemmel skor

# ─── Job Matching ────────────────────────────────────────
MIN_MATCH_SCORE: int = 60      # Minimum match %
MAX_JOB_RESULTS: int = 20      # Max job count

# ─── Prompt File Paths ───────────────────────────────────
import os

_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")

PROMPT_CV_ANALYZER_PATH = os.path.normpath(os.path.join(_PROMPTS_DIR, "cv_analyzer.txt"))
PROMPT_CV_CRITIC_PATH   = os.path.normpath(os.path.join(_PROMPTS_DIR, "cv_critic.txt"))
PROMPT_CV_OPTIMIZER_PATH = os.path.normpath(os.path.join(_PROMPTS_DIR, "cv_optimizer.txt"))
PROMPT_JOB_HUNTER_PATH  = os.path.normpath(os.path.join(_PROMPTS_DIR, "job_hunter.txt"))

# ─── Common Job Titles (for matching) ────────────────────
COMMON_TECH_ROLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "DevOps Engineer",
    "Data Engineer",
    "Machine Learning Engineer",
    "AI Engineer",
    "Product Manager",
]

# ─── Common Skills (for extraction) ──────────────────────
TECH_SKILLS = {
    "languages": ["Python", "JavaScript", "Java", "C#", "Go", "Rust", "TypeScript"],
    "frameworks": ["React", "Angular", "Vue", "Django", "Flask", "FastAPI", ".NET", "Spring"],
    "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch"],
    "cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes"],
    "tools": ["Git", "Jenkins", "CircleCI", "Terraform", "Ansible"],
}