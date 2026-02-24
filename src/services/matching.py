"""
matching.py
────────────
Job–CV eşleşme skoru hesaplama yardımcıları.

Amaç:
- Hem Türkiye hem global job scrapers için tek bir ortak
  `calculate_match_score` fonksiyonu sağlamak.
"""

from typing import List


def calculate_match_score(cv_skills: List[str], job_description: str) -> int:
    """
    Skill overlap tabanlı match skoru hesapla.

    - Boş girişlerde makul bir default skor döner.
    - Skoru 40–95 aralığında sınırlar.
    """
    if not cv_skills or not job_description:
        return 60  # Default moderate score

    job_lower = job_description.lower()

    matched_skills = [skill for skill in cv_skills if skill.lower() in job_lower]

    if not matched_skills:
        # Hiç eşleşme yoksa düşük ama sıfır olmayan bir skor ver
        return 45

    match_percentage = int((len(matched_skills) / len(cv_skills)) * 100)

    # UX için hafif boost
    boosted_score = match_percentage + 15

    # 40–95 aralığında sınırla
    final_score = max(40, min(95, boosted_score))

    return final_score

