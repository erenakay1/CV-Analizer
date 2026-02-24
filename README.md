## 🎯 AI Career Advisor – Multi‑Agent CV & Job Matcher

AI Career Advisor is a **multi‑agent, LLM‑powered career assistant** that:

- **Analyzes your CV** (ATS focus, strengths, gaps)
- **Critiques and optimizes** it for a target role
- **Searches and ranks real job postings** (Turkey + global)
- Presents results in a **modern Streamlit UI**

You upload a CV, select target role & location, and the app returns:

- A detailed CV analysis (issues, strengths, ATS score)
- A “before vs after” optimized CV view
- Ranked job recommendations with match scores
- An agent trace view for debugging & observability

---

## 🚀 Quick Start

### 1. Clone & environment

```bash
git clone https://github.com/<your-username>/CV-Analizer.git
cd CV-Analizer

python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env  # if available, otherwise create manually
```

Minimum required keys:

```bash
OPENAI_API_KEY=sk-...

# Optional but recommended
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=cv-analizer

# For global job search via RapidAPI
RAPIDAPI_KEY=...
```

> If `RAPIDAPI_KEY` is missing, the app can still work in “mock / Turkey‑only” mode using curated or scraped jobs.

### 3. Run the app

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

---

## 🧩 High‑Level Architecture

**Entry point**

- `app.py` – Streamlit UI and main flow:
  - CV upload
  - Target role & location inputs
  - Calls `run_career_analysis` to execute the agent pipeline
  - Renders analysis, improvements, job matches, and agent trace

**Core modules**

- `src/core/config.py` – Settings, `.env` loading, feature flags (OpenAI, LangSmith, RapidAPI).
- `src/core/constants.py` – Global constants (default model, temperatures, etc.).
- `src/models/llm.py` – `get_llm()` factory returning a configured `ChatOpenAI` client.

**Services**

- `src/services/career_services.py` – Orchestrates the **career analysis pipeline**:
  - Parses the CV file
  - Runs LangGraph agents (analyzer, critic, optimizer, job hunter)
  - Returns final state for the UI.
- `src/services/prompt_loader.py` – Loads prompt templates from `prompts/*.txt`.

**Agent graph (LangGraph)**

- `src/graph/graph.py` – Builds the LangGraph.
- `src/graph/state.py` – Shared state between nodes.
- `src/graph/router.py` – Routing / control‑flow between nodes.
- `src/graph/nodes/cv_analyzer.py` – Initial CV analysis (ATS score, issues, strengths, gaps).
- `src/graph/nodes/cv_critic.py` – Critical review, consistency checks, retry logic.
- `src/graph/nodes/cv_optimizer.py` – Generates improved CV content and final suggestions.
- `src/graph/nodes/job_hunter.py` – Uses job scrapers + LLM to rank and explain job matches.
- `src/graph/nodes/retry.py` – Handles retry policies when critic is not satisfied.

**Job search**

- `src/api/job_scraper.py`
  - `search_jobs(query, location, num_results)`:
    - Auto‑detects **Turkey vs global** based on location.
    - For Turkey → delegates to `search_jobs_turkey`.
    - For global → calls JSearch API via RapidAPI.
  - Contains parsers for Kariyer.net, Indeed Turkey and JSearch results.
- `src/api/job_scraper_turkey.py`
  - Advanced, Turkey‑specific scraping with:
    - User‑agent rotation
    - Basic anti‑bot precautions
    - Fallback to **curated Turkish tech jobs** when sites block scraping.

**CV parsing**

- `src/api/cv_parser.py` & `src/utils/parser.py`
  - Read CV files (PDF, DOCX, TXT) using:
    - `PyPDF2`, `pdfplumber`
    - `python-docx`, `mammoth`
  - Normalize into a structured representation consumed by agents.

---

## 🧠 Multi‑Agent Flow (Conceptual)

1. **CV Analyzer Agent**
   - Reads the parsed CV + target role.
   - Produces:
     - ATS score
     - Issue list (with severity)
     - Strengths & skill gaps.

2. **CV Critic Agent**
   - Challenges the analyzer’s output.
   - Requests retries if the analysis is weak or inconsistent.

3. **CV Optimizer Agent**
   - Generates improved sections (summary, experience bullets, skills).
   - Outputs “before vs after” content + optimization summary.

4. **Job Hunter Agent**
   - Calls `search_jobs` to get a job list (Turkey scrapers or global via RapidAPI).
   - Computes **match scores** (skill overlap + heuristics).
   - Returns ranked job recommendations with explanations.

5. **Agent Trace & Observability**
   - `final_state["trace_log"]` keeps a chronological trace of agent steps.
   - If LangSmith is enabled, the full graph run is visible in the dashboard.

---

## 🧪 Testing

The project includes basic tests under `tests/` (e.g. manual parser tests and job search checks).

Planned improvements:

- Isolated unit tests for:
  - CV parsing (PDF/DOCX fixtures)
  - Match score calculation
  - Job parsing helpers (Kariyer, Indeed, JSearch)
- Higher‑level tests for the agent graph using mocked LLM responses.

Run tests with:

```bash
pytest -q
```

---

## 🌍 Turkey vs Global Job Search

- **Turkey**
  - Scrapers for:
    - Kariyer.net
    - Indeed Turkey
  - Anti‑bot precautions and graceful fallbacks to curated tech jobs.

- **Global**
  - JSearch API via RapidAPI.
  - Supports:
    - Remote‑only filters
    - Location‑aware queries (e.g. “Software Engineer in New York”).

If external services fail or rate‑limit, the UI shows clear warnings and continues gracefully where possible.

---

## 🧭 Roadmap / Ideas

- Replace ad‑hoc `Dict` payloads with **Pydantic models** for CV, jobs and agent state.
- Add a small **FastAPI** layer to expose CV analysis and job matching as HTTP endpoints.
- Improve job matching with:
  - Embedding‑based similarity (e.g. sentence‑transformers)
  - Per‑skill importance weights.
- Add evaluation tooling with LangSmith to compare different prompts / agent configurations.

---

## 🇹🇷 Kısa Türkçe Özet

Bu proje, **LLM destekli çok ajanlı bir kariyer asistanı**:

- CV’ni analiz ediyor (ATS skoru, güçlü yanlar, eksikler),
- Hedef pozisyona göre içeriği optimize ediyor,
- Türkiye ve global iş ilanlarını tarayıp **eşleşme skorları** üretiyor,
- Sonuçları modern bir Streamlit arayüzünde gösteriyor.

Teknik olarak:

- `LangChain` + `LangGraph` ile ajan tabanlı mimari,
- `OpenAI` tabanlı LLM client (`ChatOpenAI`),
- `Streamlit` ile interaktif web arayüzü,
- Kariyer.net, Indeed Turkey ve RapidAPI (JSearch) ile job search entegrasyonları kullanıyor.

Capstone / portföy projesi olarak:

- Hem **LLM uygulama geliştirme** hem de
- **uçtan uca ürün tasarımı** yeteneğini göstermek için güçlü bir örnek.

