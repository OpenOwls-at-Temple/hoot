import json
import os
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from llm.prompts import DEFERRAL, GROUNDED_ANSWER_SYSTEM


class LLMClient:
    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model=os.getenv("LLM_MODEL", "claude-sonnet-5"),
            temperature=0,
        )

    def chat(self, question: str, chunks: list[str]) -> dict:
        """
        Send the question + retrieved chunks to the LLM.
        Expects a JSON response matching {answered, answer, citations}.
        Retries once on bad JSON; falls back to DEFERRAL if still invalid.
        """
        context = "\n\n---\n\n".join(chunks)
        messages = [
            SystemMessage(content=GROUNDED_ANSWER_SYSTEM),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
        ]

        for _ in range(2):
            raw = self._llm.invoke(messages).content
            result = self._parse(raw)
            if result is not None:
                return result

        return dict(DEFERRAL)

    @staticmethod
    def _parse(raw: str) -> Optional[dict]:
        try:
            data = json.loads(raw)
            if (
                isinstance(data, dict)
                and "answered" in data
                and "answer" in data
                and "citations" in data
            ):
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        return None
