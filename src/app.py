import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Make sure imports work depending on how it's run
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.models import TIER_DESCRIPTIONS
from src.core.engine import EvaluationEngine
from src.llm.mock_client import MockLLMClient
from src.llm.groq_client import GroqClient
from src.utils.parser import extract_text_from_pdf

load_dotenv()

st.set_page_config(page_title="AI Resume Evaluator", layout="wide")

st.title("📄 AI Resume Shortlisting & Interview Assistant")
st.markdown("Evaluate candidate resumes against Job Descriptions using AI-powered semantic matching and multi-dimensional scoring.")

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    llm_mode = st.radio("Select LLM Mode", ["Mock LLM (Fast, Free)", "Groq (Llama 3.3 70B)"])
    
    api_key = ""
    if llm_mode == "Groq (Llama 3.3 70B)":
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            api_key = st.text_input("Groq API Key", type="password")
            if not api_key:
                st.warning("Please provide a Groq API key or set GROQ_API_KEY env var.")
                st.stop()
    
# Main Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste the Job Description here", height=400, 
                           placeholder="e.g. We are looking for a Senior Python Developer with Kafka experience...")

with col2:
    st.subheader("Candidate Resume")
    input_method = st.radio("Resume Input Method", ["Text", "PDF Upload"], horizontal=True)
    
    resume_text = ""
    if input_method == "Text":
        resume_text = st.text_area("Paste Candidate Resume here", height=330,
                                   placeholder="e.g. Experienced Software Engineer with 5 years in AWS...")
    else:
        uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")
        if uploaded_file is not None:
            try:
                resume_text = extract_text_from_pdf(uploaded_file.read())
                st.success("PDF parsed successfully!")
                with st.expander("View extracted text"):
                    st.text(resume_text)
            except Exception as e:
                st.error(f"Error parsing PDF: {e}")

if st.button("Evaluate Candidate", type="primary", use_container_width=True):
    if not jd_text.strip() or not resume_text.strip():
        st.error("Please provide both a Job Description and a Resume.")
    else:
        with st.spinner("Evaluating candidate... This may take a moment."):
            # Setup client
            if llm_mode == "Mock LLM (Fast, Free)":
                client = MockLLMClient()
            else:
                client = GroqClient(api_key=api_key)
            
            engine = EvaluationEngine(client)
            
            try:
                result = engine.evaluate(resume_text, jd_text)
                
                st.markdown("---")
                st.header("Evaluation Results")
                
                # Top metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Overall Score", f"{result.scores.overall_score}/100")
                
                tier_color = "green" if result.tier == "A" else ("orange" if result.tier == "B" else "red")
                m2.markdown(f"**Tier:** <span style='color:{tier_color};font-size:1.5em'>{result.tier.value}</span>", unsafe_allow_html=True)
                tier_desc = TIER_DESCRIPTIONS.get(result.tier.value, "")
                m2.markdown(f"<span style='color:gray;font-size:0.9em'>{tier_desc}</span>", unsafe_allow_html=True)
                
                # Summary
                st.subheader("Summary")
                st.info(result.summary)
                
                # Section-wise Scores
                st.subheader("Section-wise Scores")
                for sec in result.section_scores:
                    st.markdown(f"**{sec.section}**")
                    sec_col1, sec_col2 = st.columns([8, 2])
                    with sec_col1:
                        st.progress(sec.score / 100)
                    with sec_col2:
                        st.markdown(f"**{sec.score}**")
                    st.caption(sec.explanation)
                st.markdown("<br>", unsafe_allow_html=True)

                # JD vs Resume Gap Analysis
                st.subheader("JD vs Resume Gap Analysis")
                if result.requirement_matches:
                    data = []
                    for req in result.requirement_matches:
                        status = "✅ Matched" if req.match_percent >= 80 else ("⚠️ Partial" if req.match_percent >= 40 else "❌ Missing")
                        data.append({
                            "Requirement": req.requirement,
                            "Match %": req.match_percent,
                            "Status": status,
                            "Evidence": req.evidence
                        })
                    df = pd.DataFrame(data)
                    st.dataframe(
                        df,
                        column_config={
                            "Match %": st.column_config.ProgressColumn(
                                "Match %",
                                help="Percentage match for this requirement",
                                format="%f%%",
                                min_value=0,
                                max_value=100,
                            ),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                st.markdown("<br>", unsafe_allow_html=True)

                # Detailed scores
                st.subheader("Detailed Scoring")
                
                def render_score(title, dimension):
                    st.markdown(f"**{title}:** {dimension.score}/100")
                    st.caption(f"Reasoning: {dimension.explanation}")
                    st.progress(dimension.score / 100)

                    with st.expander("▶ View Details"):
                        if dimension.matched_keywords:
                            st.markdown(f"**Matched Skills:** <span style='color:green'>{', '.join(dimension.matched_keywords)}</span>", unsafe_allow_html=True)
                        if dimension.missing_keywords:
                            st.markdown(f"**Missing Skills:** <span style='color:red'>{', '.join(dimension.missing_keywords)}</span>", unsafe_allow_html=True)
                        if dimension.suggestions:
                            st.markdown("**Suggestions:**")
                            for sug in dimension.suggestions:
                                st.markdown(f"- {sug}")

                    st.markdown("<br>", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    render_score("Exact Match", result.scores.exact_match)
                    render_score("Impact & Achievement", result.scores.impact_achievement)
                with c2:
                    render_score("Similarity Match", result.scores.similarity_match)
                    render_score("Ownership", result.scores.ownership)

            except Exception as e:
                st.error(f"An error occurred during evaluation: {e}")
