"""
server.py
─────────
FastAPI tabanlı hafif bir HTTP API katmanı.

Ana endpoint:
- POST /analyze-cv
  - Multipart form:
    - file: CV dosyası (pdf / docx / txt)
    - target_role: str (optional)
    - target_location: str (optional)
  - Dönen JSON: CareerAnalysisResult (Pydantic model)
"""

import os
import tempfile
from typing import Annotated

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.services.career_services import run_career_analysis_structured
from src.models.schemas import CareerAnalysisResult


app = FastAPI(
    title="AI Career Advisor API",
    description="Multi-agent CV analysis and job matching as an HTTP API.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze-cv", response_model=CareerAnalysisResult)
async def analyze_cv(
    file: Annotated[UploadFile, File(..., description="CV file (pdf/docx/txt)")],
    target_role: Annotated[str | None, Form()] = "",
    target_location: Annotated[str | None, Form()] = "",
) -> CareerAnalysisResult:
    """
    CV dosyasını analiz eden endpoint.

    Streamlit arayüzüyle aynı pipeline'ı kullanır, ancak
    sonucu JSON olarak döner.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="CV file is required")

    ext = (file.filename.rsplit(".", 1)[-1] or "").lower()
    if ext not in {"pdf", "docx", "txt"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = run_career_analysis_structured(
            cv_file_path=tmp_path,
            cv_file_type=ext,
            target_role=target_role or "",
            target_location=target_location or "",
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

