from llm.client import LLMClient
from llm.prompts import DEFERRAL


def answer_question(question: str, retriever, llm_client: LLMClient) -> dict:
    """
    Orchestrate the RAG pipeline for a single question.

    1. Retrieve relevant chunks.
    2. If none found, return the deferral immediately — do NOT call the LLM.
    3. Otherwise call the LLM with the question + chunk texts.
    4. Return the {answered, answer, citations} response.
    """
    docs = retriever.invoke(question)

    if not docs:
        return dict(DEFERRAL)

    chunks = [doc.page_content for doc in docs]
    return llm_client.chat(question, chunks)
