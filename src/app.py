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
    with st.expander("Sources"):
        for c in citations:
            title = c.get("title", "Unknown source")
            url = c.get("url", "")
            category = c.get("category", "")
            last_updated = c.get("last_updated", "")

            link = f"[{title}]({url})" if url else title
            badges = " · ".join(
                filter(None, [category, f"Updated: {last_updated}" if last_updated else ""])
            )
            st.markdown(f"- {link}{' — ' + badges if badges else ''}")


def main() -> None:
    st.set_page_config(page_title="HOOT", page_icon="🦉")
    st.title("🦉 HOOT — Helpful Owl Of Temple")
    st.caption(
        "Ask questions about Temple University faculty HR policies, benefits, and more.  \n"
        "**This is an informational tool — not official HR or legal advice.**"
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

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                render_citations(msg["citations"])

    if question := st.chat_input("Ask about Temple faculty HR policies..."):
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
