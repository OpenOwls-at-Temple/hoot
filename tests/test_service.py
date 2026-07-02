"""
Tests for rag/service.py — the grounding-critical orchestration layer.
These tests run without a real vector store or LLM.
"""
from unittest.mock import MagicMock

from langchain_core.documents import Document

from rag.service import answer_question


def _make_retriever(docs):
    """Return a mock retriever that yields the given docs."""
    r = MagicMock()
    r.invoke.return_value = docs
    return r


def _make_llm_client(response):
    """Return a mock LLMClient whose .chat() returns the given dict."""
    c = MagicMock()
    c.chat.return_value = response
    return c


# ---------------------------------------------------------------------------
# Feature 3: Deferral guard
# ---------------------------------------------------------------------------

def test_empty_retrieval_returns_deferral_without_calling_llm():
    retriever = _make_retriever([])
    llm_client = _make_llm_client({})

    result = answer_question("What is the FMLA policy?", retriever, llm_client)

    assert result["answered"] is False
    assert "215-204-7174" in result["answer"]
    assert result["citations"] == []
    llm_client.chat.assert_not_called()


def test_non_empty_retrieval_calls_llm_with_chunk_text():
    doc = Document(page_content="FMLA allows 12 weeks of leave.", metadata={})
    retriever = _make_retriever([doc])
    llm_client = _make_llm_client(
        {"answered": True, "answer": "12 weeks.", "citations": []}
    )

    result = answer_question("What is the FMLA policy?", retriever, llm_client)

    llm_client.chat.assert_called_once()
    call_args = llm_client.chat.call_args
    assert call_args[0][0] == "What is the FMLA policy?"
    assert "FMLA allows 12 weeks of leave." in call_args[0][1]


# ---------------------------------------------------------------------------
# Feature 2: Source passthrough
# ---------------------------------------------------------------------------

def test_llm_response_is_returned_unchanged():
    doc = Document(page_content="Some policy text.", metadata={})
    retriever = _make_retriever([doc])
    expected = {
        "answered": True,
        "answer": "The policy says X.",
        "citations": [{"title": "Policy Doc", "url": "https://t.edu", "category": "policy", "last_updated": "2025-01-01"}],
    }
    llm_client = _make_llm_client(expected)

    result = answer_question("What is the policy?", retriever, llm_client)

    assert result == expected


def test_answered_false_from_llm_is_returned_as_is():
    doc = Document(page_content="Unrelated text.", metadata={})
    retriever = _make_retriever([doc])
    llm_deferral = {
        "answered": False,
        "answer": "I couldn't find that in Temple's published documents. Please contact HR at 215-204-7174.",
        "citations": [],
    }
    llm_client = _make_llm_client(llm_deferral)

    result = answer_question("Random off-topic question", retriever, llm_client)

    assert result["answered"] is False
    assert result["citations"] == []
