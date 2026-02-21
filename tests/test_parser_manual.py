
import sys
sys.path.insert(0, '.')

from src.api.job_scraper import search_jobs

print("🔍 Testing LinkedIn Jobs Search API\n")
print("=" * 60)

try:
    jobs = search_jobs(
        query="Python Developer",
        location="United States",
        num_results=5
    )
    
    print(f"✅ SUCCESS! Found {len(jobs)} jobs\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']}")
        print(f"   🏢 Company: {job['company']}")
        print(f"   📍 Location: {job['location']}")
        print(f"   💰 Salary: {job['salary_range']}")
        print(f"   📅 Posted: {job['posted_at']}")
        print(f"   🔗 URL: {job['url'][:60]}...")
        print()
    
    # Verify real data
    first_url = jobs[0]['url']
    if 'linkedin.com/jobs' in first_url and '3847562' not in first_url:
        print("=" * 60)
        print("✅ REAL LINKEDIN DATA CONFIRMED!")
        print("=" * 60)
    else:
        print("⚠️ Data might be mock")

except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nPossible fixes:")
    print("1. Subscribe to API: https://rapidapi.com/jaypat87/api/linkedin-jobs-search")
    print("2. Check RAPIDAPI_KEY in .env")
    print("3. Verify subscription is active")
