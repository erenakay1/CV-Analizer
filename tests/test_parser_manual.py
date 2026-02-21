# test_agent_a_only.py

import sys
sys.path.insert(0, '.')

from src.api.cv_parser import parse_cv
from src.graph.nodes.cv_analyzer import cv_analyzer_node
from src.graph.state import CareerPipelineState
from src.utils.parser import safe_json_parse

print("🧪 Testing Agent A (CV Analyzer) Only...\n")

# Step 1: Parse CV
print("Step 1: Parsing CV...")
cv_data = parse_cv("samples/test_cv.txt", "txt")
print(f"✅ CV parsed: {cv_data['char_count']} chars\n")

# Step 2: Create initial state
print("Step 2: Creating pipeline state...")
initial_state: CareerPipelineState = {
    "cv_text": cv_data['raw_text'],
    "target_role": "Senior Software Engineer",
    "target_location": "Remote",
    "analyzer_output": "",
    "critic_output": "",
    "optimizer_output": "",
    "job_hunter_output": "",
    "retry_count": 0,
    "approved": False,
    "trace_log": [],
}
print("✅ State created\n")

# Step 3: Run Agent A
print("Step 3: Running Agent A (CV Analyzer)...")
print("⏳ Calling OpenAI API (this may take 10-20 seconds)...\n")

result = cv_analyzer_node(initial_state)

print("✅ Agent A completed!\n")

# Step 4: Parse result
print("Step 4: Parsing Agent A output...")
try:
    analysis = safe_json_parse(result['analyzer_output'])
    
    print("=" * 50)
    print("AGENT A RESULTS")
    print("=" * 50)
    print(f"ATS Score: {analysis['cv_analysis']['ats_score']}/100")
    print(f"Quality: {analysis['cv_analysis']['overall_quality']}")
    print(f"\nIssues Found: {len(analysis['cv_analysis']['issues'])}")
    
    for i, issue in enumerate(analysis['cv_analysis']['issues'][:3], 1):
        print(f"\n{i}. [{issue['severity']}] {issue['category']}")
        print(f"   {issue['description'][:80]}...")
    
    print(f"\nStrengths: {len(analysis['cv_analysis']['strengths'])}")
    for strength in analysis['cv_analysis']['strengths']:
        print(f"   ✅ {strength}")
    
    print(f"\nSkill Gaps: {len(analysis['cv_analysis']['skill_gaps'])}")
    for gap in analysis['cv_analysis']['skill_gaps'][:3]:
        print(f"   ⚠️ {gap['skill']} - {gap['importance']} importance")
    
    print("\n" + "=" * 50)
    print("✅ Agent A test successful!")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Error parsing output: {e}")
    print(f"\nRaw output:\n{result['analyzer_output'][:500]}")