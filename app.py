import streamlit as st
from core.graph import run_workflow
from core.config import logger

st.set_page_config(page_title="Multi-Agent System", page_icon="robot", layout="wide")
st.title("Multi-Agent Collaboration System")
st.markdown("Enter a question and 4 AI Agents will collaborate to research and write an article.")

with st.sidebar:
    st.header("How to Use")
    st.markdown("1. Enter your question below\n2. Click Start Collaboration\n3. Wait for agents\n4. View results")
    st.markdown("---")
    st.markdown("Made by xiaomao14")

question = st.text_area("Enter your question:", placeholder="e.g., What are the impacts of AI on the job market?", height=100)

if st.button("Start Collaboration", type="primary", disabled=not question):
    with st.spinner("Agents are collaborating..."):
        try:
            result = run_workflow(question)
            with st.expander("Execution Logs", expanded=False):
                for log in result.get("logs", []):
                    st.text(log)
            with st.expander("Review Feedback", expanded=True):
                for fb in result.get("review_feedback", []):
                    st.markdown(f"- {fb}")
            st.markdown("---")
            st.subheader("Final Article")
            st.markdown(result.get("draft", "No article"))
        except Exception as e:
            st.error(f"Error: {e}")
            logger.error(f"Streamlit error: {e}")
