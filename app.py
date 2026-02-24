"""
app.py — Streamlit Entry Point
───────────────────────────────
AI Career Advisor ana arayüzü.
"""

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from src.core.config import settings
from src.services.career_services import run_career_analysis
from src.utils.parser import safe_json_parse


# ═══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🎯 AI Career Advisor",
    page_icon="🎯",
    layout="wide",
)


# ═══════════════════════════════════════════════════════════
#  CUSTOM CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e2e8f0; }
    
    .metric-card {
        background: #1a1d26;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #48bb78;
        margin-bottom: 12px;
    }
    
    .issue-critical { color: #fc8181; font-weight: 600; }
    .issue-warning  { color: #f6ad55; font-weight: 600; }
    .issue-info     { color: #63b3ed; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.header("⚙️ Configuration")
    st.checkbox(
        "✅ OpenAI API" if settings.openai_ok else "❌ OpenAI API Missing",
        value=settings.openai_ok,
        disabled=True,
    )
    st.checkbox(
        "✅ LangSmith" if settings.langsmith_ok else "❌ LangSmith Missing",
        value=settings.langsmith_ok,
        disabled=True,
    )
    st.checkbox(
        "✅ RapidAPI (Jobs)" if settings.rapidapi_ok else "⚠️ RapidAPI Missing (Mock Data)",
        value=settings.rapidapi_ok,
        disabled=True,
    )


# ═══════════════════════════════════════════════════════════
#  MAIN UI
# ═══════════════════════════════════════════════════════════
st.title("🎯 AI Career Advisor")
st.markdown("**Multi-Agent CV Optimization & Job Matching**")

st.info("""
💡 **How it works:**
1. Upload your CV (PDF, DOCX, or TXT)
2. AI agents analyze and optimize your CV
3. Get improved CV + job recommendations
""")

# ── CV Upload ──────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📄 Upload your CV",
    type=["pdf", "docx", "txt"],
    help="Supported formats: PDF, DOCX, TXT"
)

col1, col2 = st.columns(2)
target_role = col1.text_input(
    "🎯 Target Role",
    placeholder="e.g., Software Engineer, Yazılım Mühendisi",
)

# Location with helpful options
location_options = [
    "Remote",  # Default
    "Istanbul",
    "Ankara",
    "United States",
    "New York, NY",
    "San Francisco, CA",
    "London, UK",
    "Custom...",
]

target_location = col2.selectbox(
    "📍 Location Preference",
    options=location_options,
    index=0,  # Default: Remote
    help="Select 'Remote' for work-from-anywhere positions"
)

# Custom location input
if target_location == "Custom...":
    target_location = st.text_input(
        "Enter custom location:",
        placeholder="e.g., Berlin, Germany"
    )

analyze_btn = st.button("🚀 Analyze CV", type="primary", use_container_width=True)


# ═══════════════════════════════════════════════════════════
#  ANALYSIS
# ═══════════════════════════════════════════════════════════
if analyze_btn:
    if not uploaded_file:
        st.error("⚠️ Please upload a CV first!")
        st.stop()
    
    if not settings.openai_ok:
        st.error("❌ OpenAI API key not configured. Check .env file.")
        st.stop()
    
    # Save uploaded file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    
    # Run analysis with progress
    progress_bar = st.progress(0, text="Starting analysis...")
    
    try:
        progress_bar.progress(10, text="📄 Parsing CV...")
        
        cv_data, final_state = run_career_analysis(
            cv_file_path=tmp_path,
            cv_file_type=uploaded_file.name.split('.')[-1],
            target_role=target_role,
            target_location=target_location,
        )
        
        progress_bar.progress(100, text="✅ Analysis complete!")
        
        # Clean up
        import time
        time.sleep(0.5)
        progress_bar.empty()
        os.unlink(tmp_path)
        
    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ Analysis failed: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()
    
    st.success("✅ Analysis complete!")
    
    # Parse outputs
    analyzer_data = safe_json_parse(final_state["analyzer_output"])
    critic_data   = safe_json_parse(final_state["critic_output"])
    optimizer_data = safe_json_parse(final_state["optimizer_output"])
    
    # Job data - SAFE PARSE
    try:
        if final_state.get("job_hunter_output"):
            job_data = safe_json_parse(final_state["job_hunter_output"])
        else:
            job_data = {
                "job_recommendations": [],
                "search_summary": "Job search not completed",
                "total_jobs_found": 0
            }
    except Exception as e:
        st.warning(f"⚠️ Job search failed: {e}")
        job_data = {
            "job_recommendations": [],
            "search_summary": "Job search failed",
            "total_jobs_found": 0
        }
    
    # ═══════════════════════════════════════════════════════════
    #  RESULTS
    # ═══════════════════════════════════════════════════════════
    st.divider()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    initial_ats = analyzer_data['cv_analysis']['ats_score']
    final_ats = optimizer_data.get('new_ats_score', initial_ats)
    
    col1.metric("Initial ATS Score", f"{initial_ats}/100")
    col2.metric("Final ATS Score", f"{final_ats}/100", delta=f"+{final_ats - initial_ats}")
    col3.metric("Issues Found", len(analyzer_data['cv_analysis']['issues']))
    col4.metric("Improvements", len(optimizer_data['improvements']))
    
    # Tabs (5 tabs!)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Analysis",
        "🔧 Improvements",
        "💼 Job Matches",
        "🔗 Agent Trace",
        "📋 Summary"
    ])
    
    # ─── TAB 1: ANALYSIS ────────────────────────────────
    with tab1:
        st.subheader("🔍 Issues Detected")
        
        issues = analyzer_data['cv_analysis']['issues']
        
        if not issues:
            st.success("🎉 No major issues found!")
        else:
            for issue in issues:
                severity = issue['severity']
                severity_class = {
                    'Critical': 'issue-critical',
                    'Warning': 'issue-warning',
                    'Info': 'issue-info'
                }.get(severity, 'issue-info')
                
                with st.expander(f"[{severity}] {issue['category']} - {issue['location']}"):
                    st.markdown(f"**Issue:** {issue['description']}")
                    st.markdown(f"**Suggestion:** {issue['suggestion']}")
    
    # ─── TAB 2: IMPROVEMENTS ────────────────────────────
    with tab2:
        st.subheader("✨ Before vs After Comparison")
        
        # Download button
        improvements = optimizer_data['improvements']
        optimized_cv_text = "\n\n".join([
            f"[{imp['location']}]\n{imp['improved']}"
            for imp in improvements
        ])
        
        st.download_button(
            label="📥 Download Optimized CV",
            data=optimized_cv_text,
            file_name="optimized_cv.txt",
            mime="text/plain",
            use_container_width=True,
        )
        
        st.divider()
        
        for i, imp in enumerate(improvements, 1):
            st.markdown(f"### {i}. {imp['location']}")
            st.caption(f"**Issue:** {imp['issue_category']}")
            
            col_before, col_after = st.columns(2)
            
            with col_before:
                st.markdown("#### ❌ Original")
                st.info(imp['original'])
            
            with col_after:
                st.markdown("#### ✅ Improved")
                st.success(imp['improved'])
            
            st.caption(f"💡 **Why:** {imp['explanation']}")
            
            if i < len(improvements):
                st.divider()
    
    # ─── TAB 3: JOB MATCHES ─────────────────────────────
    with tab3:
        st.subheader("💼 Job Recommendations")
        
        jobs = job_data.get("job_recommendations", [])
        
        if not jobs:
            st.warning("⚠️ No jobs found or job search not completed.")
            st.info("""
            **Possible reasons:**
            - RapidAPI key not configured (using mock data)
            - No matching jobs for the target role
            - API rate limit reached
            - Job search service unavailable
            """)
        else:
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Jobs", job_data.get("total_jobs_found", 0))
            col2.metric("Showing Top", len(jobs))
            col3.metric("Best Match", f"{jobs[0]['match_score']}%" if jobs else "N/A")
            
            st.info(job_data.get("search_summary", ""))
            
            st.divider()
            
            # Job cards
            for i, job in enumerate(jobs, 1):
                match_score = job['match_score']
                match_color = "🟢" if match_score >= 80 else "🟡" if match_score >= 60 else "🔴"
                
                with st.expander(f"{match_color} {i}. {job['title']} @ {job['company']} - {match_score}% Match"):
                    col_info, col_details = st.columns([2, 1])
                    
                    with col_info:
                        st.markdown(f"**🏢 Company:** {job['company']}")
                        st.markdown(f"**📍 Location:** {job['location']}")
                        st.markdown(f"**💰 Salary:** {job['salary_range']}")
                        st.markdown(f"**📅 Posted:** {job.get('posted_at', 'N/A')}")
                        st.markdown(f"**⏰ Type:** {job.get('employment_type', 'Full-time')}")
                    
                    with col_details:
                        st.metric("Match Score", f"{match_score}%")
                    
                    st.markdown("**🎯 Why it matches:**")
                    for reason in job.get('match_reasons', []):
                        st.markdown(f"- ✅ {reason}")
                    
                    if job.get('url'):
                        st.link_button("🔗 Apply Now", job['url'], use_container_width=True)
    
    # ─── TAB 4: AGENT TRACE ─────────────────────────────
    with tab4:
        st.subheader("🔗 Agent Debate Trace")
        
        # LangSmith link
        if settings.langsmith_ok:
            st.markdown("""
            ### 🔗 View in LangSmith Dashboard
            
            Click below to see the full agent debate trace:
            """)
            
            st.link_button(
                "🔍 Open LangSmith Trace →",
                f"https://smith.langchain.com/projects/p/{settings.LANGSMITH_PROJECT}",
                use_container_width=True,
            )
            
            st.info(f"""
            **Look for:** Recent run named `CV Analysis - {target_role or 'General'}`
            
            **What you'll see:**
            - Full conversation between agents
            - Token usage per agent
            - Latency breakdown
            - Retry loops
            """)
        
        st.divider()
        
        # Agent trace log
        st.markdown("### 📋 Quick Summary")
        st.markdown(f"""
        - **Retry Count:** {final_state['retry_count']}
        - **Critic Approved:** {'✅ Yes' if final_state['approved'] else '❌ No (max retry)'}
        - **Total Steps:** {len(final_state['trace_log'])}
        """)
        
        for entry in final_state['trace_log']:
            agent = entry.get('agent', '?')
            step = entry.get('step', '?')
            st.markdown(f"- **[{agent}]** `{step}`")
    
    # ─── TAB 5: SUMMARY ─────────────────────────────────
    with tab5:
        st.subheader("📋 Optimization Summary")
        st.info(optimizer_data.get('optimization_summary', 'No summary available'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💪 Strengths")
            for strength in analyzer_data['cv_analysis'].get('strengths', []):
                st.markdown(f"- ✅ {strength}")
        
        with col2:
            st.markdown("### ⚠️ Skill Gaps")
            for gap in analyzer_data['cv_analysis'].get('skill_gaps', []):
                st.markdown(f"- 🎯 **{gap['skill']}** ({gap['importance']} priority)")