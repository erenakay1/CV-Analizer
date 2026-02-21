
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
    placeholder="e.g., Senior Software Engineer",
)
target_location = col2.text_input(
    "📍 Location",
    placeholder="e.g., Remote / New York",
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
    
    # Run analysis
    with st.spinner("🤖 AI Agents analyzing your CV... (30-60 seconds)"):
        try:
            cv_data, final_state = run_career_analysis(
                cv_file_path=tmp_path,
                cv_file_type=uploaded_file.name.split('.')[-1],
                target_role=target_role,
                target_location=target_location,
            )
            
            # Clean up temp file
            os.unlink(tmp_path)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.stop()
    
    st.success("✅ Analysis complete!")
    
    # Parse outputs
    analyzer_data = safe_json_parse(final_state["analyzer_output"])
    critic_data   = safe_json_parse(final_state["critic_output"])
    optimizer_data = safe_json_parse(final_state["optimizer_output"])
    
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
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Analysis",
        "🔧 Improvements",
        "🔗 Agent Trace",
        "📋 Summary"
    ])
    
    with tab1:
        st.subheader("🔍 Issues Detected")
        
        issues = analyzer_data['cv_analysis']['issues']
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
    
    with tab2:
        st.subheader("✨ Optimizations")
        
        improvements = optimizer_data['improvements']
        for i, imp in enumerate(improvements, 1):
            st.markdown(f"#### {i}. {imp['location']} ({imp['issue_category']})")
            
            col_before, col_after = st.columns(2)
            
            with col_before:
                st.markdown("##### ❌ Before")
                st.text_area("", imp['original'], height=100, key=f"before_{i}", disabled=True)
            
            with col_after:
                st.markdown("##### ✅ After")
                st.text_area("", imp['improved'], height=100, key=f"after_{i}", disabled=True)
            
            st.caption(f"💡 {imp['explanation']}")
            st.divider()
    
    with tab3:
        st.subheader("🔗 Agent Debate Trace")
        
        # LangSmith link
        if settings.langsmith_ok:
            project_name = settings.LANGSMITH_PROJECT
            st.markdown(f"""
            ### 🔗 View Full Trace in LangSmith
            
            [Open LangSmith Dashboard →](https://smith.langchain.com/o/YOUR-ORG/projects/p/{project_name})
            
            Look for the most recent run named: **CV Analysis - {target_role or 'General'}**
            """)

        st.markdown(f"""
        **Retry Count:** {final_state['retry_count']}  
        **Critic Approved:** {'✅ Yes' if final_state['approved'] else '❌ No (max retry)'}  
        **Total Steps:** {len(final_state['trace_log'])}
        """)
        
        for entry in final_state['trace_log']:
            agent = entry.get('agent', '?')
            step = entry.get('step', '?')
            st.markdown(f"- **[{agent}]** `{step}`")
    
    with tab4:
        st.subheader("📋 Optimization Summary")
        st.info(optimizer_data.get('optimization_summary', 'No summary available'))
        
        st.markdown("### 💪 Strengths")
        for strength in analyzer_data['cv_analysis'].get('strengths', []):
            st.markdown(f"- ✅ {strength}")
        
        st.markdown("### ⚠️ Skill Gaps")
        for gap in analyzer_data['cv_analysis'].get('skill_gaps', []):
            st.markdown(f"- 🎯 **{gap['skill']}** ({gap['importance']} priority)")
