
"""
job_hunter.py - Agent D: Job Hunter
------------------------------------
Gerçek job search API kullanarak iş ilanları bulur.
"""

import json
from src.graph.state import CareerPipelineState
from src.api.job_scraper import search_jobs, calculate_match_score
from src.utils.parser import safe_json_parse


def job_hunter_node(state: CareerPipelineState) -> dict:
    """
    Agent D: Job Hunter node.
    RapidAPI JSearch kullanarak gerçek iş ilanları bulur.
    """
    
    target_role = state.get("target_role") or "Software Engineer"
    target_location = state.get("target_location", "")
    
    # CV'den skills çıkar
    try:
        analyzer_data = safe_json_parse(state["analyzer_output"])
        cv_skills = analyzer_data.get("cv_analysis", {}).get("optimized_sections", {}).get("key_skills", [])
        if not cv_skills:
            # Fallback: skill_gaps'den al
            skill_gaps = analyzer_data.get("cv_analysis", {}).get("skill_gaps", [])
            cv_skills = [gap["skill"] for gap in skill_gaps]
    except:
        cv_skills = ["Python", "JavaScript", "AWS"]  # Fallback
    
    # Job search
    jobs = search_jobs(
        query=target_role,
        location=target_location,
        num_results=10
    )
    
    # Calculate match scores
    job_recommendations = []
    for job in jobs:
        match_score = calculate_match_score(cv_skills, job["description"])
        
        # Match reasons
        matched_skills = [
            skill for skill in cv_skills 
            if skill.lower() in job["description"].lower()
        ]
        
        match_reasons = []
        if matched_skills:
            match_reasons.append(f"{len(matched_skills)} skills match: {', '.join(matched_skills[:3])}")
        if job["location"] and target_location.lower() in job["location"].lower():
            match_reasons.append("Location matches preference")
        if "remote" in job["location"].lower() and "remote" in target_location.lower():
            match_reasons.append("Remote work available")
        
        if not match_reasons:
            match_reasons = ["Good fit for your experience level"]
        
        job_recommendations.append({
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "match_score": match_score,
            "match_reasons": match_reasons,
            "salary_range": job["salary_range"],
            "url": job["url"],
            "posted_at": job["posted_at"],
            "employment_type": job["employment_type"],
        })
    
    # Sort by match score
    job_recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    output = {
        "job_recommendations": job_recommendations[:5],  # Top 5
        "search_summary": f"Found {len(jobs)} {target_role} positions, showing top 5 matches",
        "total_jobs_found": len(jobs),
    }
    
    return {
        "job_hunter_output": json.dumps(output, ensure_ascii=False, indent=2),
        "trace_log": [{
            "agent": "Job Hunter",
            "step": "job_search_complete",
            "jobs_found": len(jobs),
            "top_match_score": job_recommendations[0]["match_score"] if job_recommendations else 0,
        }],
    }
