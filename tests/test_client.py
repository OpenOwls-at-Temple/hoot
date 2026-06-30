"""
Tests for llm/client.py — JSON contract, retry logic, and deferral fallback.
These tests mock the underlying ChatOpenAI call.
"""
import json
from unittest.mock import MagicMock, patch

from llm.client import LLMClient


def _client_with_mock_llm(responses):
    """
    Build an LLMClient whose internal _llm returns the given list of content
    strings in order (one per .invoke() call).
    """
    client = LLMClient.__new__(LLMClient)
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = [MagicMock(content=r) for r in responses]
    client._llm = mock_llm
    return client, mock_llm


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_json_answer_is_returned_on_first_attempt():
    payload = {
        "answered": True,
        "answer": "Tuition remission is available after the first semester.",
        "citations": [
            {"title": "Tuition Policy", "url": "https://t.edu/tuition", "category": "benefits", "last_updated": "2025-01-01"}
        ],
    }
    client, mock_llm = _client_with_mock_llm([json.dumps(payload)])

    result = client.chat("Do I get tuition remission?", ["...policy text..."])

    assert result["answered"] is True
    assert result["answer"] == payload["answer"]
    assert mock_llm.invoke.call_count == 1


def test_answered_false_json_is_returned_directly():
    payload = {"answered": False, "answer": "Could not find it.", "citations": []}
    client, mock_llm = _client_with_mock_llm([json.dumps(payload)])

    result = client.chat("Some obscure question", ["...context..."])

    assert result["answered"] is False
    assert mock_llm.invoke.call_count == 1


# ---------------------------------------------------------------------------
# Retry + deferral
# ---------------------------------------------------------------------------

def test_malformed_json_on_first_attempt_triggers_retry():
    valid = {"answered": True, "answer": "The answer.", "citations": []}
    client, mock_llm = _client_with_mock_llm(["not json at all", json.dumps(valid)])

    result = client.chat("A question", ["context"])

    assert mock_llm.invoke.call_count == 2
    assert result["answered"] is True


def test_malformed_json_on_both_attempts_returns_deferral():
    client, mock_llm = _client_with_mock_llm(["bad json", "also bad json"])

    result = client.chat("A question", ["context"])

    assert mock_llm.invoke.call_count == 2
    assert result["answered"] is False
    assert "215-204-7174" in result["answer"]
    assert result["citations"] == []


def test_missing_required_keys_triggers_retry_then_deferral():
    # Valid JSON but missing the contract keys — should be treated as malformed
    client, mock_llm = _client_with_mock_llm(['{"foo": "bar"}', '{"baz": 1}'])

    result = client.chat("A question", ["context"])

    assert result["answered"] is False
    assert mock_llm.invoke.call_count == 2
