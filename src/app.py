"""HOOT — Helpful Owl Of Temple: Streamlit frontend."""

import os
import sys
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm.client import LLMClient
from rag.retriever import build_retriever, load_vectorstore
from rag.service import answer_question

DEMO_MODE = os.getenv("HOOT_DEMO", "").lower() in ("1", "true", "yes")
MODEL_NAME = os.getenv("LLM_MODEL", "claude-sonnet-5")

_EXAMPLES = [
    ("🏥", "Health Insurance", "What health insurance plans are available to Temple faculty?"),
    ("🎓", "Tuition Remission", "How does tuition remission work for dependents?"),
    ("💼", "Outside Employment", "What are the rules for outside consulting or moonlighting?"),
    ("📋", "Leave Policy", "How many vacation days do full-time faculty members get?"),
]

_DEMO_RESPONSES = {
    "tuition": {
        "answered": True,
        "answer": (
            "Temple University offers **tuition remission** benefits to eligible faculty and "
            "their dependents. Full-time faculty may receive remission for up to **18 credit "
            "hours** per academic year for themselves, and dependent children may receive "
            "remission for **undergraduate coursework** at Temple. The benefit covers tuition "
            "only — fees, books, and room & board are not included. Apply through HR each semester."
        ),
        "citations": [
            {
                "title": "Temple University Tuition Remission Policy",
                "url": "https://hr.temple.edu/benefits/tuition-remission",
                "category": "Benefits",
                "last_updated": "2024-08-01",
            }
        ],
    },
    "health": {
        "answered": True,
        "answer": (
            "Temple University faculty have access to several health insurance options through "
            "Independence Blue Cross, including **Keystone HMO**, **Personal Choice PPO**, and "
            "**Blue Cross Direct**. Coverage begins on your first day of employment for eligible "
            "full-time faculty. Open enrollment typically occurs each November. Premiums are "
            "deducted pre-tax via payroll."
        ),
        "citations": [
            {
                "title": "Temple University Health Benefits",
                "url": "https://hr.temple.edu/benefits/health-insurance",
                "category": "Benefits",
                "last_updated": "2024-01-15",
            }
        ],
    },
    "default": {
        "answered": False,
        "answer": (
            "I couldn't find that in Temple's published documents. "
            "Please contact HR at **215-204-7174** or visit **hr.temple.edu**."
        ),
        "citations": [],
    },
}

_CSS = """
<style>
/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }

/* ── Hero banner ── */
.hoot-hero {
    background: linear-gradient(135deg, #9D2235 0%, #6B1523 100%);
    color: white;
    padding: 1.75rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.75rem;
    display: flex;
    align-items: center;
    gap: 1.4rem;
}
.hoot-hero .owl { font-size: 3.5rem; line-height: 1; }
.hoot-hero h1 {
    margin: 0 0 0.2rem;
    font-size: 1.9rem;
    font-weight: 800;
    color: white !important;
    letter-spacing: -0.01em;
}
.hoot-hero p {
    margin: 0;
    font-size: 0.92rem;
    color: rgba(255,255,255,0.88) !important;
}

/* ── Section label ── */
.sect-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 0.85rem;
    margin-top: 0.5rem;
}

/* ── Example card buttons (main area only) ── */
[data-testid="stMain"] .stButton > button {
    background: white !important;
    border: 1.5px solid #E4E4E4 !important;
    border-radius: 12px !important;
    padding: 0.9rem 1.1rem !important;
    text-align: left !important;
    height: auto !important;
    min-height: 3.5rem !important;
    white-space: normal !important;
    line-height: 1.5 !important;
    font-size: 0.87rem !important;
    color: #2C2C2C !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    transition: border-color 0.15s, box-shadow 0.15s, color 0.15s !important;
}
[data-testid="stMain"] .stButton > button:hover {
    border-color: #9D2235 !important;
    box-shadow: 0 2px 12px rgba(157,34,53,0.14) !important;
    color: #9D2235 !important;
}
[data-testid="stMain"] .stButton > button:active {
    background: #F9EAEC !important;
}

/* ── Citation cards ── */
.cit-card {
    background: #FAFAFA;
    border: 1px solid #EBEBEB;
    border-left: 4px solid #9D2235;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.55rem;
}
.cit-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: #1A1A1A;
    text-decoration: none;
}
.cit-title:hover { text-decoration: underline; color: #9D2235; }
.cit-meta { font-size: 0.76rem; color: #888; margin-top: 0.3rem; }
.badge {
    display: inline-block;
    background: #9D2235;
    color: white;
    padding: 1px 8px;
    border-radius: 10px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-right: 0.5rem;
    vertical-align: middle;
}

/* ── Disclaimer ── */
.disclaimer {
    background: #FFFBEB;
    border: 1px solid #EDD55A;
    border-radius: 8px;
    padding: 0.72rem 1rem;
    font-size: 0.77rem;
    color: #5C4A00;
    margin-top: 2rem;
    margin-bottom: 0.75rem;
    line-height: 1.55;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}
.sb-owl { font-size: 2.8rem; text-align: center; margin-bottom: 0.15rem; }
.sb-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #9D2235;
    text-align: center;
    letter-spacing: -0.01em;
}
.sb-sub { font-size: 0.73rem; color: #AAA; text-align: center; margin-bottom: 1.3rem; }
.sb-divider { border-top: 1px solid #E6E6E6; margin: 1rem 0; }
.sb-about { font-size: 0.82rem; color: #555; line-height: 1.58; }
.sb-kv { font-size: 0.82rem; color: #444; margin-bottom: 0.2rem; }
.model-pill {
    display: inline-block;
    background: linear-gradient(135deg, #9D2235, #6B1523);
    color: white;
    padding: 0.28rem 0.85rem;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    margin-top: 0.25rem;
}
.mode-live { color: #16a34a; font-weight: 700; font-size: 0.84rem; }
.mode-demo { color: #d97706; font-weight: 700; font-size: 0.84rem; }
.sb-contact {
    background: #F9EAEC;
    border-radius: 8px;
    padding: 0.7rem 0.9rem;
    font-size: 0.8rem;
    color: #7A1A28;
    line-height: 1.65;
}

/* ── Sidebar buttons keep standard Streamlit look ── */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important;
    min-height: unset !important;
    box-shadow: none !important;
}
</style>
"""


def _demo_response(question: str) -> dict:
    q = question.lower()
    if any(w in q for w in ("tuition", "remission", "dependent", "child")):
        return dict(_DEMO_RESPONSES["tuition"])
    if any(w in q for w in ("health", "insurance", "medical", "dental", "vision")):
        return dict(_DEMO_RESPONSES["health"])
    return dict(_DEMO_RESPONSES["default"])


@st.cache_resource(show_spinner=False)
def _load_retriever():
    vs = load_vectorstore()
    return build_retriever(vs)


@st.cache_resource(show_spinner=False)
def _load_llm():
    return LLMClient()


def _get_answer(question: str) -> dict:
    if DEMO_MODE:
        import time
        time.sleep(0.8)
        return _demo_response(question)
    return answer_question(question, _load_retriever(), _load_llm())


def _render_citations(citations: list) -> None:
    if not citations:
        return
    with st.expander("📚 Sources", expanded=False):
        for c in citations:
            title = c.get("title") or "Untitled"
            url = c.get("url") or ""
            category = c.get("category") or ""
            last_updated = c.get("last_updated") or ""
            badge = f'<span class="badge">{category}</span>' if category else ""
            meta = f"Updated {last_updated}" if last_updated else ""
            link = (
                f'<a href="{url}" target="_blank" class="cit-title">{title}</a>'
                if url
                else f'<span class="cit-title">{title}</span>'
            )
            st.markdown(
                f'<div class="cit-card">{badge}{link}'
                f'<div class="cit-meta">{meta}</div></div>',
                unsafe_allow_html=True,
            )


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown('<div class="sb-owl">🦉</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-title">HOOT</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sb-sub">Helpful Owl Of Temple</div>', unsafe_allow_html=True
        )
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sb-about">'
            "HOOT answers HR &amp; policy questions for Temple University faculty — "
            "benefits, leave, outside employment, research rules, and more — using "
            "official Temple published documents."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        st.markdown('<span class="sb-kv"><strong>Model</strong></span>', unsafe_allow_html=True)
        st.markdown(
            f'<div><span class="model-pill">✦ {MODEL_NAME}</span></div>',
            unsafe_allow_html=True,
        )
        st.write("")

        st.markdown('<span class="sb-kv"><strong>Status</strong></span>', unsafe_allow_html=True)
        if DEMO_MODE:
            st.markdown('<span class="mode-demo">◉ Demo Mode</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="mode-live">◉ Live</span>', unsafe_allow_html=True)

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sb-contact">'
            "📞 <strong>Temple Human Resources</strong><br>"
            "215-204-7174<br>"
            '<a href="https://hr.temple.edu" style="color:#7A1A28;">hr.temple.edu</a>'
            "</div>",
            unsafe_allow_html=True,
        )


def _render_hero() -> None:
    st.markdown(
        '<div class="hoot-hero">'
        '<div class="owl">🦉</div>'
        "<div>"
        "<h1>HOOT</h1>"
        "<p>Helpful Owl Of Temple &mdash; HR &amp; Policy Assistant for Faculty</p>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_examples() -> Optional[str]:
    st.markdown('<div class="sect-label">Try asking about</div>', unsafe_allow_html=True)
    cols = st.columns(2, gap="small")
    for i, (icon, title, question) in enumerate(_EXAMPLES):
        with cols[i % 2]:
            if st.button(
                f"{icon} **{title}**\n\n{question}",
                key=f"ex_{i}",
                use_container_width=True,
            ):
                return question
    return None


def main() -> None:
    st.set_page_config(
        page_title="HOOT — Helpful Owl Of Temple",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending" not in st.session_state:
        st.session_state.pending = None

    _render_sidebar()

    # Centre the main content with flanking padding columns
    _, col, _ = st.columns([0.5, 8, 0.5])
    with col:
        _render_hero()

        # Replay conversation history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("citations"):
                    _render_citations(msg["citations"])

        # Drain pending question set by an example card click on the prior run
        question: Optional[str] = st.session_state.pending
        st.session_state.pending = None

        # Empty state — show example cards before the first question
        if not st.session_state.messages and question is None:
            selected = _render_examples()
            if selected:
                st.session_state.pending = selected
                st.rerun()

        # Always-visible chat input
        typed = st.chat_input("Ask about Temple HR policies, benefits, or faculty rules…")
        if typed:
            question = typed

        # Process whichever question arrived this run
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Searching Temple policy documents…"):
                    result = _get_answer(question)
                answer = result.get("answer", "")
                citations = result.get("citations", [])
                st.markdown(answer)
                _render_citations(citations)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "citations": citations}
                )

        st.markdown(
            '<div class="disclaimer">'
            "<strong>Informational only.</strong> HOOT provides general information based on "
            "publicly available Temple University documents. This is not official HR advice or "
            "legal guidance. Always verify with Temple Human Resources (215-204-7174) before "
            "making employment decisions."
            "</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
