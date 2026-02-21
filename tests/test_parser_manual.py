import sys
sys.path.insert(0, '.')

from src.services.career_services import run_career_analysis
from src.utils.parser import safe_json_parse

print("🧪 Testing FULL Pipeline (Analyzer + Critic + Optimizer)...\n")

# Run full pipeline
print("⏳ Running full analysis (may take 30-60 seconds)...\n")

cv_data, final_state = run_career_analysis(
    cv_file_path="samples/test_cv.txt",
    cv_file_type="txt",
    target_role="Senior Software Engineer",
    target_location="Remote"
)

print("✅ Pipeline completed!\n")

# Parse outputs
analyzer_output = safe_json_parse(final_state["analyzer_output"])
critic_output   = safe_json_parse(final_state["critic_output"])
optimizer_output = safe_json_parse(final_state["optimizer_output"])

# Display results
print("=" * 60)
print("PIPELINE RESULTS")
print("=" * 60)

print(f"\n📊 ANALYZER:")
print(f"   ATS Score: {analyzer_output['cv_analysis']['ats_score']}/100")
print(f"   Issues: {len(analyzer_output['cv_analysis']['issues'])}")

print(f"\n🔎 CRITIC:")
print(f"   Approved: {final_state['approved']}")
print(f"   Retry Count: {final_state['retry_count']}")
print(f"   Missed Issues: {len(critic_output['critic_review']['missed_issues'])}")

print(f"\n🔧 OPTIMIZER:")
print(f"   Improvements: {len(optimizer_output['improvements'])}")
print(f"   New ATS Score: {optimizer_output.get('new_ats_score', 'N/A')}")

print(f"\n📋 TRACE LOG:")
for entry in final_state['trace_log']:
    agent = entry.get('agent', '?')
    step = entry.get('step', '?')
    print(f"   → [{agent}] {step}")

print("\n" + "=" * 60)
print("✅ Full pipeline test successful!")
print("=" * 60)


