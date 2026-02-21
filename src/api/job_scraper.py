# src/api/job_scraper.py - WORKING VERSION

"""
job_scraper.py
--------------
LinkedIn Jobs Search API (RapidAPI)
"""

import requests
import logging
from typing import List, Dict
from datetime import datetime, timedelta

from src.core.config import settings

logger = logging.getLogger(__name__)


def search_jobs(
    query: str,
    location: str = "",
    num_results: int = 10
) -> List[Dict]:
    """
    Search LinkedIn jobs via RapidAPI.
    API: https://rapidapi.com/jaypat87/api/linkedin-jobs-search
    """
    
    if not settings.RAPIDAPI_KEY:
        logger.error("❌ RAPIDAPI_KEY not set")
        raise ValueError("RAPIDAPI_KEY required")
    
    url = "https://linkedin-jobs-search.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "linkedin-jobs-search.p.rapidapi.com"
    }
    
    # Build query params
    params = {
        "query": query,
        "location": location if location else "Worldwide",
        "datePosted": "anyTime",  # anyTime, pastMonth, pastWeek, past24Hours
        "sort": "mostRelevant"
    }
    
    try:
        logger.info(f"🔍 API Request: {query} in {params['location']}")
        
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        logger.info(f"📊 Response Status: {response.status_code}")
        
        # Check response
        if response.status_code != 200:
            logger.error(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            raise Exception(f"API returned {response.status_code}")
        
        # Parse JSON
        data = response.json()
        logger.info(f"📦 Response keys: {list(data.keys())}")
        
        # Extract jobs
        jobs = data.get("jobs", []) or data.get("data", []) or []
        
        if not jobs:
            logger.warning(f"⚠️ No jobs found. Response: {str(data)[:200]}")
            raise Exception("No jobs in response")
        
        logger.info(f"✅ Found {len(jobs)} jobs")
        
        # Parse jobs
        parsed_jobs = []
        for job in jobs[:num_results]:
            parsed_jobs.append(_parse_linkedin_job(job))
        
        return parsed_jobs
    
    except Exception as e:
        logger.error(f"❌ Job search failed: {e}")
        raise


def _parse_linkedin_job(job: Dict) -> Dict:
    """Parse a single LinkedIn job."""
    
    return {
        "title": job.get("title") or job.get("jobTitle", "N/A"),
        "company": job.get("company") or job.get("companyName", "Unknown Company"),
        "location": job.get("location") or job.get("jobLocation", "Remote"),
        "salary_range": _extract_salary(job),
        "description": (job.get("description") or job.get("jobDescription", ""))[:500],
        "url": job.get("jobUrl") or job.get("url") or job.get("link", "#"),
        "posted_at": _format_posted_date(job),
        "employment_type": job.get("employmentType") or job.get("type", "Full-time"),
    }


def _extract_salary(job: Dict) -> str:
    """Extract salary from job data."""
    
    # Try different salary fields
    salary = (
        job.get("salary") or 
        job.get("salaryRange") or 
        job.get("compensation")
    )
    
    if salary:
        return str(salary)
    
    return "Not specified"


def _format_posted_date(job: Dict) -> str:
    """Format posted date."""
    
    posted = job.get("postedAt") or job.get("postedDate") or job.get("publishedAt")
    
    if not posted:
        return "Recently"
    
    # If it's already a string like "2 days ago"
    if isinstance(posted, str):
        return posted
    
    # If it's a timestamp
    try:
        if isinstance(posted, int):
            dt = datetime.fromtimestamp(posted)
            days_ago = (datetime.now() - dt).days
            
            if days_ago == 0:
                return "Today"
            elif days_ago == 1:
                return "Yesterday"
            elif days_ago < 7:
                return f"{days_ago} days ago"
            else:
                return posted
    except:
        pass
    
    return str(posted)


def calculate_match_score(cv_skills: List[str], job_description: str) -> int:
    """Calculate match score based on skill overlap."""
    
    if not cv_skills or not job_description:
        return 60  # Default moderate score
    
    job_lower = job_description.lower()
    
    # Count matched skills
    matched_skills = []
    for skill in cv_skills:
        if skill.lower() in job_lower:
            matched_skills.append(skill)
    
    # Calculate percentage
    match_percentage = int((len(matched_skills) / len(cv_skills)) * 100)
    
    # Ensure score is between 40-95
    score = max(40, min(95, match_percentage))
    
    return score