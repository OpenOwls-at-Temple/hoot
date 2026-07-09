import os
import sys
from pathlib import Path

# Add project root to path so llm/ and rag/ are importable when running via
# `streamlit run src/app.py` (Streamlit adds src/ to sys.path, not the root).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dotenv import load_dotenv

from llm.client import LLMClient
from rag.retriever import CHROMA_PATH, build_retriever, load_vectorstore
from rag.service import answer_question

load_dotenv()

# Temple cherry: #9D2235  (used sparingly — title only)
_CSS = """
<style>
/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Title accent */
h1 { color: #9D2235 !important; }

/* Tighten the disclaimer caption */
.stCaption { font-size: 0.82rem; line-height: 1.4; }

/* Citation cards inside the expander */
.citation-card {
    border-left: 3px solid #9D2235;
    padding: 6px 10px;
    margin-bottom: 8px;
}
.citation-card a { font-weight: 600; text-decoration: none; }
.citation-meta { font-size: 0.78rem; color: #888; margin-top: 2px; }
</style>
"""

_EXAMPLES = [
    "What health insurance plans are available to Temple faculty?",
    "How does tuition remission work for dependents?",
    "What are the rules for outside consulting or moonlighting?",
]


@st.cache_resource
def get_retriever():
    vs = load_vectorstore()
    return build_retriever(vs)


@st.cache_resource
def get_llm_client():
    return LLMClient()


def render_citations(citations: list) -> None:
    if not citations:
        return
    label = f"Sources ({len(citations)})"
    with st.expander(label):
        for i, c in enumerate(citations):
            title = c.get("title", "Unknown source")
            url = c.get("url", "")
            category = c.get("category", "")
            last_updated = c.get("last_updated", "")

            title_html = f'<a href="{url}" target="_blank">{title}</a>' if url else title
            meta_parts = []
            if category:
                meta_parts.append(category)
            if last_updated:
                meta_parts.append(f"updated {last_updated}")
            meta_html = " · ".join(meta_parts)

            st.markdown(
                f'<div class="citation-card">'
                f'{title_html}'
                f'{"<div class=citation-meta>" + meta_html + "</div>" if meta_html else ""}'
                f"</div>",
                unsafe_allow_html=True,
            )


def render_empty_state() -> None:
    st.markdown("**Try asking:**")
    for ex in _EXAMPLES:
        st.markdown(f"- *{ex}*")


def main() -> None:
    st.set_page_config(
        page_title="HOOT — Helpful Owl Of Temple",
        page_icon="🦉",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    st.title("🦉 HOOT — Helpful Owl Of Temple")
    st.caption(
        "Answers are drawn from publicly available Temple University documents.  \n"
        "**This is an informational tool — not official HR or legal advice.**  \n"
        "For authoritative guidance contact HR: 215-204-7174."
    )

    if not Path(CHROMA_PATH).exists():
        st.error(
            f"Vector store not found at `{CHROMA_PATH}`. "
            "Run `python src/ingest.py` first."
        )
        st.stop()

    missing = [v for v in ("LLM_BASE_URL", "LLM_API_KEY") if not os.getenv(v)]
    if missing:
        st.error(
            f"Missing environment variables: {', '.join(missing)}. "
            "Copy `.env.example` to `.env` and fill in your values."
        )
        st.stop()

    retriever = get_retriever()
    llm_client = get_llm_client()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Replay history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                render_citations(msg["citations"])

    # Empty state hint — shown only before the first question
    if not st.session_state.messages:
        render_empty_state()

    if question := st.chat_input("Ask about Temple faculty HR policies..."):
        # Clear the empty-state hint on first question (re-render clears it naturally)
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching Temple documents..."):
                result = answer_question(question, retriever, llm_client)

            st.markdown(result["answer"])
            render_citations(result.get("citations", []))

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "citations": result.get("citations", []),
            }
        )


if __name__ == "__main__":
    main()
