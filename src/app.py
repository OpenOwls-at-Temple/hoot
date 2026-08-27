import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DEMO_MODE = os.getenv("HOOT_DEMO", "").lower() in ("1", "true", "yes")

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }

/* ── Page background ── */
.stApp { background: #F7F7F8; }

/* ── Hide default title/caption ── */
.hoot-hidden { display: none; }

/* ── Top navbar ── */
.hoot-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 52px;
    background: #fff;
    border-bottom: 1px solid #E5E5E5;
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 10px;
    z-index: 999;
}
.hoot-nav-logo { font-size: 1.35rem; }
.hoot-nav-name {
    font-size: 1rem;
    font-weight: 700;
    color: #1A1A1A;
    letter-spacing: -0.01em;
}
.hoot-nav-badge {
    font-size: 0.65rem;
    font-weight: 600;
    background: #9D2235;
    color: white;
    padding: 2px 8px;
    border-radius: 20px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.hoot-nav-disclaimer {
    margin-left: auto;
    font-size: 0.72rem;
    color: #999;
}

/* ── Push content below navbar ── */
.main .block-container {
    padding-top: 72px !important;
    padding-bottom: 100px !important;
    max-width: 780px !important;
}

/* ── Empty state ── */
.hoot-welcome {
    text-align: center;
    padding: 48px 24px 32px;
}
.hoot-welcome-owl { font-size: 3.5rem; margin-bottom: 12px; }
.hoot-welcome h2 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1A1A1A;
    margin: 0 0 8px;
    letter-spacing: -0.02em;
}
.hoot-welcome p {
    font-size: 0.9rem;
    color: #666;
    margin: 0 0 32px;
}
.hoot-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 580px;
    margin: 0 auto;
}
.hoot-card {
    background: white;
    border: 1px solid #E5E5E5;
    border-radius: 12px;
    padding: 14px 16px;
    cursor: pointer;
    text-align: left;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.hoot-card:hover {
    border-color: #9D2235;
    box-shadow: 0 2px 12px rgba(157,34,53,0.10);
}
.hoot-card-icon { font-size: 1.2rem; margin-bottom: 6px; }
.hoot-card-text { font-size: 0.82rem; color: #333; line-height: 1.4; font-weight: 500; }

/* ── Example card buttons ── */
[data-testid="stMain"] .stButton > button {
    background: white !important;
    border: 1px solid #E5E5E5 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    text-align: left !important;
    height: auto !important;
    min-height: unset !important;
    white-space: normal !important;
    line-height: 1.45 !important;
    font-size: 0.83rem !important;
    color: #333 !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
[data-testid="stMain"] .stButton > button:hover {
    border-color: #9D2235 !important;
    box-shadow: 0 2px 12px rgba(157,34,53,0.10) !important;
    color: #9D2235 !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 4px 0 !important;
}
[data-testid="stChatMessage"][data-testid*="user"] > div {
    background: #9D2235 !important;
    color: white !important;
    border-radius: 18px 18px 4px 18px !important;
}

/* ── Assistant bubble ── */
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) {
    background: white !important;
    border: 1px solid #EBEBEB !important;
    border-radius: 4px 18px 18px 18px !important;
    padding: 16px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}

/* ── Citation cards ── */
.cit-wrap {
    margin-top: 12px;
    border-top: 1px solid #F0F0F0;
    padding-top: 10px;
}
.cit-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #AAA;
    margin-bottom: 8px;
}
.cit-card {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: #FAFAFA;
    border: 1px solid #EBEBEB;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 6px;
    text-decoration: none;
}
.cit-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #9D2235;
    margin-top: 4px;
    flex-shrink: 0;
}
.cit-body { flex: 1; min-width: 0; }
.cit-title {
    font-size: 0.84rem;
    font-weight: 600;
    color: #1A1A1A;
    text-decoration: none;
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.cit-title:hover { color: #9D2235; }
.cit-meta { font-size: 0.72rem; color: #999; margin-top: 2px; }
.cit-badge {
    display: inline-block;
    background: #F3F3F3;
    color: #666;
    padding: 1px 7px;
    border-radius: 8px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-right: 5px;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 1.5px solid #E5E5E5 !important;
    background: white !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #9D2235 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #9D2235 !important; }

/* ── Demo banner ── */
.demo-banner {
    background: #FFF8E1;
    border: 1px solid #FFD54F;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.78rem;
    color: #7A5700;
    margin-bottom: 12px;
    text-align: center;
}
</style>
"""

_NAVBAR = """
<div class="hoot-nav">
    <span class="hoot-nav-logo">🦉</span>
    <span class="hoot-nav-name">HOOT</span>
    <span class="hoot-nav-badge">Temple HR</span>
    <span class="hoot-nav-disclaimer">Informational only · Not official HR advice · 215-204-7174</span>
</div>
"""

_EXAMPLES = [
    ("🏥", "What health insurance plans are available to Temple faculty?"),
    ("🎓", "How does tuition remission work for dependents?"),
    ("📋", "What is the procedure to request two days leave?"),
    ("💼", "What are the rules for outside consulting?"),
]

_DEMO_RESPONSES = {
    "default": {
        "answered": True,
        "answer": (
            "Temple University offers several health insurance options for full-time faculty "
            "through Independence Blue Cross, including Keystone HMO, Personal Choice PPO, "
            "and a High Deductible Health Plan paired with a Health Savings Account (HSA). "
            "Coverage begins on the first day of the month following your hire date. "
            "Open enrollment typically runs each November for changes effective January 1."
        ),
        "citations": [
            {
                "title": "Working at Temple University — Benefits Overview",
                "url": "https://www.temple.edu/about/faculty-staff-resources/working-temple",
                "category": "benefits",
                "last_updated": "2026-07-02",
            },
            {
                "title": "Temple University Wellness & Health Services",
                "url": "https://www.temple.edu/about/faculty-staff-resources/wellness-health-services",
                "category": "benefits",
                "last_updated": "2026-07-02",
            },
        ],
    },
    "tuition": {
        "answered": True,
        "answer": (
            "Full-time Temple faculty are eligible for tuition remission for themselves, "
            "their spouse or domestic partner, and dependent children up to age 25. "
            "The benefit covers up to 18 credits per academic year for dependents at Temple. "
            "A separate application must be submitted each semester through the HR portal "
            "before the tuition deadline."
        ),
        "citations": [
            {
                "title": "Tuition Remission — Faculty & Staff Benefit",
                "url": "https://www.temple.edu/about/faculty-staff-resources/working-temple",
                "category": "benefits",
                "last_updated": "2026-07-02",
            }
        ],
    },
    "deferral": {
        "answered": False,
        "answer": (
            "I wasn't able to find information about that in Temple's published documents. "
            "For an authoritative answer, please contact Temple Human Resources directly at "
            "**215-204-7174** or visit the HR office at 1101 W. Montgomery Ave."
        ),
        "citations": [],
    },
}


def _demo_response(question: str) -> dict:
    q = question.lower()
    if any(w in q for w in ("tuition", "remission", "dependent", "child")):
        return _DEMO_RESPONSES["tuition"]
    if any(w in q for w in ("payroll", "salary", "parking", "gym", "recreation")):
        return _DEMO_RESPONSES["deferral"]
    return _DEMO_RESPONSES["default"]


def render_citations(citations: list) -> None:
    if not citations:
        return
    html = '<div class="cit-wrap"><div class="cit-label">Sources</div>'
    for c in citations:
        title = c.get("title", "Unknown source")
        url = c.get("url", "")
        category = c.get("category", "")
        last_updated = c.get("last_updated", "")
        badge = f'<span class="cit-badge">{category}</span>' if category else ""
        meta = f"{badge}Updated {last_updated}" if last_updated else badge
        link_open = f'<a class="cit-title" href="{url}" target="_blank">' if url else '<span class="cit-title">'
        link_close = "</a>" if url else "</span>"
        html += (
            f'<div class="cit-card">'
            f'<div class="cit-dot"></div>'
            f'<div class="cit-body">'
            f'{link_open}{title}{link_close}'
            f'<div class="cit-meta">{meta}</div>'
            f"</div></div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state() -> None:
    st.markdown(
        '<div class="hoot-welcome">'
        '<div class="hoot-welcome-owl">🦉</div>'
        "<h2>How can I help you today?</h2>"
        "<p>Ask me anything about Temple University faculty HR policies, benefits, and guidelines.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, (icon, text) in enumerate(_EXAMPLES):
        with cols[i % 2]:
            if st.button(f"{icon}  {text}", key=f"ex_{i}"):
                st.session_state["prefill"] = text
                st.rerun()


def get_answer(question: str, retriever, llm_client) -> dict:
    if DEMO_MODE:
        return _demo_response(question)
    from rag.service import answer_question
    return answer_question(question, retriever, llm_client)


def main() -> None:
    st.set_page_config(
        page_title="HOOT — Helpful Owl Of Temple",
        page_icon="🦉",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(_NAVBAR, unsafe_allow_html=True)

    if DEMO_MODE:
        st.markdown('<div class="demo-banner">Demo mode — responses are illustrative, not live retrieval.</div>', unsafe_allow_html=True)
        retriever, llm_client = None, None
    else:
        from rag.retriever import CHROMA_PATH, build_retriever, load_vectorstore
        from llm.client import LLMClient

        if not Path(CHROMA_PATH).exists():
            st.error(f"Vector store not found at `{CHROMA_PATH}`. Run `python src/ingest.py` first.")
            st.stop()

        missing = [v for v in ("LLM_BASE_URL", "LLM_API_KEY") if not os.getenv(v)]
        if missing:
            st.error(f"Missing environment variables: {', '.join(missing)}.")
            st.stop()

        @st.cache_resource
        def get_retriever():
            vs = load_vectorstore()
            return build_retriever(vs)

        @st.cache_resource
        def get_llm_client():
            return LLMClient()

        retriever = get_retriever()
        llm_client = get_llm_client()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                render_citations(msg["citations"])

    if not st.session_state.messages:
        render_empty_state()

    # Handle prefill from example card clicks
    prefill = st.session_state.pop("prefill", "")

    question = st.chat_input("Ask about Temple faculty HR policies...") or prefill
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching Temple documents..."):
                result = get_answer(question, retriever, llm_client)
            st.markdown(result["answer"])
            render_citations(result.get("citations", []))

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "citations": result.get("citations", []),
        })
        st.rerun()


if __name__ == "__main__":
    main()
