import sys

sys.path.insert(0, ".")

from src.services.matching import calculate_match_score


def test_match_score_basic_overlap():
    cv_skills = ["Python", "Django", "PostgreSQL"]
    desc = "We are looking for a Python developer with Django experience."

    score = calculate_match_score(cv_skills, desc)

    # İki skill eşleşmeli, skor orta-üst bandta olmalı
    assert 70 <= score <= 95


def test_match_score_no_overlap():
    cv_skills = ["Kubernetes", "Docker"]
    desc = "We sell books in a local store."

    score = calculate_match_score(cv_skills, desc)

    # Hiç eşleşme yoksa da tamamen sıfır olmasın ama düşük olsun
    assert 40 <= score <= 60


def test_match_score_empty_inputs():
    assert calculate_match_score([], "some job") == 60
    assert calculate_match_score(["Python"], "") == 60

