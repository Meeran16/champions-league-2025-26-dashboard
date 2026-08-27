from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from src.ai.presentation import render_evidence
from src.ai.service import SUPPORTED_EXAMPLES, analyze_question
from src.components import hero, scope_note, section_header
from src.data_loader import data_ready, load_all, missing_files
from src.ui import configure_page, data_missing_message

configure_page("AI Football Analyst")

if not data_ready():
    data_missing_message(missing_files())

data = load_all()

hero(
    "Grounded intelligence",
    "AI Football Analyst — Evidence Engine",
    "Ask football questions against approved analytical functions. This development stage proves grounding before a language model is connected.",
    ["No arbitrary SQL", "No API key", "Evidence-first", "Validated local data"],
)

scope_note(
    "This branch currently tests the grounding layer only. Answers below are generated "
    "from controlled Python analytics functions. The future LLM will receive these same "
    "bounded evidence objects and will be allowed to explain them, not invent statistics."
)

section_header("Ask a question", "Try a supported analytical question in natural language.")

if "ai_question" not in st.session_state:
    st.session_state.ai_question = "Compare Arsenal and Bayern Munich."

question = st.text_input(
    "Question",
    key="ai_question",
    placeholder="e.g. Which teams had high possession but weak results?",
)

analyze = st.button("Analyze", type="primary")

with st.expander("Example questions"):
    cols = st.columns(2)
    for i, example in enumerate(SUPPORTED_EXAMPLES):
        with cols[i % 2]:
            st.caption(f"• {example}")

if analyze and question.strip():
    try:
        result = analyze_question(question.strip(), data)
        st.session_state["ai_last_result"] = result
    except Exception as exc:
        st.error(f"The evidence engine could not complete this query: {exc}")

result = st.session_state.get("ai_last_result")
if result is not None:
    st.divider()
    render_evidence(result)

    with st.expander("Developer view: structured evidence payload"):
        st.json(result.llm_payload())

    if result.intent == "unsupported":
        st.warning(
            "The safe router did not recognize this question. This is intentional: "
            "unsupported questions return no invented statistics."
        )
