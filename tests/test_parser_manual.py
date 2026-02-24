
import sys
sys.path.insert(0, '.')

from src.api.job_scraper import search_jobs

print("🇹🇷 Testing Complete Turkey Job Search\n")
print("=" * 70)

# Test 1: Turkey
try:
    jobs = search_jobs(
        query="Yazılım Mühendisi",
        location="Istanbul",
        num_results=5
    )
    
    print(f"✅ Found {len(jobs)} jobs in Turkey!\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']}")
        print(f"   🏢 {job['company']}")
        print(f"   📍 {job['location']}")
        print(f"   🔗 {job['url'][:60]}...")
        print()

except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 2: Global (for comparison)
print("\n" + "=" * 70)
print("🌍 Testing Global Search (US)")
print("=" * 70)

try:
    jobs = search_jobs(
        query="Software Engineer",
        location="United States",
        num_results=3
    )
    
    print(f"✅ Found {len(jobs)} jobs globally!\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} @ {job['company']}")

except Exception as e:
    print(f"❌ Error: {e}")
