"""
job_scraper.py
--------------
Hybrid job search system:
- Turkey: Kariyer.net + Indeed Turkey scraper
- Global: JSearch API (RapidAPI)
"""

import requests
import logging
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup

from src.core.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  MAIN SEARCH FUNCTION (Auto-detect Turkey vs Global)
# ═══════════════════════════════════════════════════════════

def search_jobs(
    query: str,
    location: str = "",
    num_results: int = 10
) -> List[Dict]:
    """
    Search for jobs - automatically detects Turkey vs Global.
    
    Turkey cities → Kariyer.net + Indeed Turkey scraper
    Other locations → JSearch API
    """
    
    # Turkey cities detection
    turkey_keywords = [
        "istanbul", "ankara", "izmir", "bursa", "antalya",
        "adana", "gaziantep", "konya", "eskişehir", "kayseri",
        "turkey", "türkiye", "turkiye"
    ]
    
    is_turkey = any(keyword in location.lower() for keyword in turkey_keywords)
    
    if is_turkey:
        logger.info(f"🇹🇷 Turkey detected: Using Turkish job scrapers")
        return _search_jobs_turkey(query, location, num_results)
    else:
        logger.info(f"🌍 Global search: Using JSearch API")
        return _search_jobs_jsearch(query, location, num_results)


# ═══════════════════════════════════════════════════════════
#  TURKEY JOB SEARCH (Kariyer.net + Indeed Turkey)
# ═══════════════════════════════════════════════════════════

def _search_jobs_turkey(query: str, city: str, num_results: int) -> List[Dict]:
    """Search Turkish job sites."""
    
    # Import the advanced scraper
    from src.api.job_scraper_turkey import search_jobs_turkey
    
    return search_jobs_turkey(query, city, num_results)


def _scrape_kariyer_net(query: str, city: str, num_results: int) -> List[Dict]:
    """Scrape Kariyer.net job listings."""
    
    # City mapping for Kariyer.net URLs
    city_map = {
        "istanbul": "istanbul",
        "ankara": "ankara",
        "izmir": "izmir",
        "bursa": "bursa",
        "antalya": "antalya",
        "adana": "adana",
        "gaziantep": "gaziantep",
        "konya": "konya",
    }
    
    city_slug = city_map.get(city.lower(), "istanbul")
    
    # Build search URL
    query_slug = query.replace(" ", "-").lower()
    url = f"https://www.kariyer.net/is-ilanlari/{query_slug}-{city_slug}"
    
    logger.info(f"🔍 Kariyer.net: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find job listings
        job_cards = soup.find_all('div', {'data-test': 'job-card'}, limit=num_results * 2)
        
        if not job_cards:
            # Try alternative selectors
            job_cards = soup.find_all('div', class_='list-items', limit=num_results * 2)
        
        jobs = []
        for card in job_cards[:num_results]:
            try:
                job = _parse_kariyer_job(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.debug(f"Failed to parse Kariyer.net job: {e}")
                continue
        
        return jobs
    
    except Exception as e:
        logger.error(f"Kariyer.net scraping error: {e}")
        return []


def _parse_kariyer_job(card) -> Dict:
    """Parse a single Kariyer.net job card."""
    
    try:
        # Title & URL
        title_elem = card.find('a', class_='job-title') or card.find('h3')
        if not title_elem:
            return None
        
        title = title_elem.get_text(strip=True)
        job_url = title_elem.get('href', '')
        if job_url and not job_url.startswith('http'):
            job_url = f"https://www.kariyer.net{job_url}"
        
        # Company
        company_elem = card.find('span', class_='company-name') or card.find('a', class_='company')
        company = company_elem.get_text(strip=True) if company_elem else "Belirtilmemiş"
        
        # Location
        location_elem = card.find('span', class_='location') or card.find('li', class_='location')
        location = location_elem.get_text(strip=True) if location_elem else "Istanbul"
        
        # Posted date
        date_elem = card.find('span', class_='publish-date')
        posted = date_elem.get_text(strip=True) if date_elem else "Yeni"
        
        return {
            "title": title,
            "company": company,
            "location": location,
            "salary_range": "Görüşülecek",  # Kariyer.net rarely shows salary
            "description": f"{company} şirketinde {title} pozisyonu",
            "url": job_url or "#",
            "posted_at": posted,
            "employment_type": "Tam zamanlı",
        }
    
    except Exception as e:
        logger.debug(f"Error parsing Kariyer.net job card: {e}")
        return None


def _scrape_indeed_turkey(query: str, city: str, num_results: int) -> List[Dict]:
    """Scrape Indeed Turkey job listings."""
    
    url = "https://tr.indeed.com/jobs"
    
    params = {
        "q": query,
        "l": city,
        "sort": "date",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    logger.info(f"🔍 Indeed Turkey: {query} in {city}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find job cards
        job_cards = soup.find_all('div', class_='job_seen_beacon', limit=num_results * 2)
        
        if not job_cards:
            # Try alternative selector
            job_cards = soup.find_all('td', class_='resultContent', limit=num_results * 2)
        
        jobs = []
        for card in job_cards[:num_results]:
            try:
                job = _parse_indeed_job(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.debug(f"Failed to parse Indeed job: {e}")
                continue
        
        return jobs
    
    except Exception as e:
        logger.error(f"Indeed Turkey scraping error: {e}")
        return []


def _parse_indeed_job(card) -> Dict:
    """Parse a single Indeed job card."""
    
    try:
        # Title & Job Key
        title_elem = card.find('h2', class_='jobTitle')
        if not title_elem:
            return None
        
        link = title_elem.find('a')
        title = link.get_text(strip=True) if link else title_elem.get_text(strip=True)
        job_key = link.get('data-jk', '') if link else ""
        url = f"https://tr.indeed.com/viewjob?jk={job_key}" if job_key else "#"
        
        # Company
        company_elem = card.find('span', class_='companyName')
        company = company_elem.get_text(strip=True) if company_elem else "Belirtilmemiş"
        
        # Location
        location_elem = card.find('div', class_='companyLocation')
        location = location_elem.get_text(strip=True) if location_elem else "Istanbul"
        
        # Salary
        salary_elem = card.find('div', class_='salary-snippet')
        salary = salary_elem.get_text(strip=True) if salary_elem else "Belirtilmemiş"
        
        # Description snippet
        desc_elem = card.find('div', class_='job-snippet')
        description = desc_elem.get_text(strip=True)[:300] if desc_elem else ""
        
        return {
            "title": title,
            "company": company,
            "location": location,
            "salary_range": salary,
            "description": description or f"{company} - {title}",
            "url": url,
            "posted_at": "Yeni",
            "employment_type": "Tam zamanlı",
        }
    
    except Exception as e:
        logger.debug(f"Error parsing Indeed job card: {e}")
        return None


# ═══════════════════════════════════════════════════════════
#  GLOBAL JOB SEARCH (JSearch API)
# ═══════════════════════════════════════════════════════════

# src/api/job_scraper.py - _search_jobs_jsearch fonksiyonunu güncelle

def _search_jobs_jsearch(query: str, location: str, num_results: int) -> List[Dict]:
    """Search using JSearch API (global)."""
    
    if not settings.RAPIDAPI_KEY:
        raise ValueError("RAPIDAPI_KEY required for global job search")
    
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    # Build search query
    search_query = query
    
    # REMOTE FILTER - Özel handling
    if location and location.lower() in ["remote", "remote work", "uzaktan"]:
        search_query = f"{query} remote"
    elif location and location.lower() not in ["worldwide", ""]:
        search_query = f"{query} in {location}"
    
    params = {
        "query": search_query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "all",
    }
    
    # Remote için ek filter
    if location and location.lower() in ["remote", "remote work", "uzaktan"]:
        params["remote_jobs_only"] = "true"  # JSearch remote filter
    
    logger.info(f"🔍 JSearch: '{search_query}' | Remote filter: {params.get('remote_jobs_only', 'false')}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        if response.status_code == 429:
            raise Exception("JSearch API rate limit exceeded")
        
        if response.status_code != 200:
            raise Exception(f"JSearch API error: HTTP {response.status_code}")
        
        data = response.json()
        jobs = data.get("data", [])
        
        if not jobs:
            raise Exception(f"No remote jobs found for '{query}'")
        
        logger.info(f"✅ JSearch: {len(jobs)} jobs found")
        
        # Parse jobs
        parsed_jobs = []
        for job in jobs[:num_results]:
            parsed = _parse_jsearch_job(job)
            if parsed:
                # Extra filter for remote (double-check)
                if location and location.lower() in ["remote", "remote work", "uzaktan"]:
                    if _is_truly_remote(parsed):
                        parsed_jobs.append(parsed)
                else:
                    parsed_jobs.append(parsed)
        
        logger.info(f"✅ Filtered to {len(parsed_jobs)} jobs")
        
        return parsed_jobs
    
    except requests.exceptions.Timeout:
        raise Exception("JSearch API timeout")
    except requests.exceptions.RequestException as e:
        raise Exception(f"JSearch API network error: {str(e)}")


def _is_truly_remote(job: Dict) -> bool:
    """
    Check if job is truly remote (not hybrid/office).
    Safe version - handles None values.
    """
    
    # Safe get with empty string fallback
    location = (job.get("location") or "").lower()
    emp_type = (job.get("employment_type") or "").lower()
    
    remote_keywords = [
        "remote", "anywhere", "work from home", "wfh",
        "worldwide", "global", "distributed"
    ]
    
    non_remote_keywords = [
        "hybrid", "office", "onsite", "on-site", "in-person",
        "headquarters", "hq"
    ]
    
    # Check for remote keywords
    has_remote = any(kw in location for kw in remote_keywords)
    has_non_remote = any(kw in location for kw in non_remote_keywords)
    is_remote_type = "remote" in emp_type
    
    # True remote: has remote keyword AND no non-remote keywords
    return (has_remote or is_remote_type) and not has_non_remote


def _parse_jsearch_job(job: Dict) -> Dict:
    """Parse JSearch API job result."""
    
    try:
        # Location
        city = job.get("job_city", "")
        state = job.get("job_state", "")
        country = job.get("job_country", "")
        
        location_parts = [p for p in [city, state, country] if p]
        location = ", ".join(location_parts) if location_parts else "Remote"
        
        # Salary
        min_sal = job.get("job_min_salary")
        max_sal = job.get("job_max_salary")
        currency = job.get("job_salary_currency", "USD")
        
        if min_sal and max_sal:
            salary = f"${min_sal:,} - ${max_sal:,} {currency}"
        elif min_sal:
            salary = f"From ${min_sal:,} {currency}"
        else:
            salary = "Not specified"
        
        # Posted date
        posted_timestamp = job.get("job_posted_at_timestamp")
        if posted_timestamp:
            try:
                dt = datetime.fromtimestamp(posted_timestamp)
                days_ago = (datetime.now() - dt).days
                
                if days_ago == 0:
                    posted = "Today"
                elif days_ago == 1:
                    posted = "Yesterday"
                elif days_ago < 7:
                    posted = f"{days_ago} days ago"
                else:
                    posted = dt.strftime("%b %d, %Y")
            except:
                posted = "Recently"
        else:
            posted = job.get("job_posted_at_datetime_utc", "Recently")
        
        return {
            "title": job.get("job_title", "N/A"),
            "company": job.get("employer_name", "Unknown"),
            "location": location,
            "salary_range": salary,
            "description": (job.get("job_description") or "")[:500],
            "url": job.get("job_apply_link") or job.get("job_google_link", "#"),
            "posted_at": posted,
            "employment_type": job.get("job_employment_type", "Full-time"),
        }
    
    except Exception as e:
        logger.error(f"Error parsing JSearch job: {e}")
        return None


# ═══════════════════════════════════════════════════════════
#  MATCH SCORE CALCULATION
# ═══════════════════════════════════════════════════════════

def calculate_match_score(cv_skills: List[str], job_description: str) -> int:
    """
    Calculate match score based on skill overlap.
    
    Args:
        cv_skills: List of skills from CV
        job_description: Job description text
    
    Returns:
        Match score between 40-95
    """
    
    if not cv_skills or not job_description:
        return 60  # Default moderate score
    
    job_lower = job_description.lower()
    
    # Count matched skills
    matched_skills = [skill for skill in cv_skills if skill.lower() in job_lower]
    
    # Calculate percentage
    match_percentage = int((len(matched_skills) / len(cv_skills)) * 100)
    
    # Boost slightly for better UX
    boosted_score = match_percentage + 15
    
    # Ensure score is between 40-95
    final_score = max(40, min(95, boosted_score))
    
    return final_score