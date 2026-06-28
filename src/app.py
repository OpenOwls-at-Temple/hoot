import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.retrievers import ContextualCompressionRetriever, EnsembleRetriever

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

SYSTEM_PROMPT = (
    "You are HOOT (Helpful Owl Of Temple), an informational assistant for "
    "Temple University faculty. You answer questions about HR policy, benefits, "
    "research/funding opportunities, and conduct rules.\n\n"
    "Strict rules:\n"
    "- Answer ONLY using the provided context passages. Do not use outside knowledge.\n"
    "- If the answer is not fully supported by the context, say you could not find it "
    "in Temple's published documents and suggest contacting HR at 215-204-7174.\n"
    "- Never guess, infer beyond the text, or fill gaps.\n"
    "- Every claim must be traceable to the provided context.\n"
    "- You are informational only — not official HR or legal advice.\n"
    "- Cite the source document for each claim."
)


@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )


@st.cache_resource
def build_retriever():
    vectorstore = load_vectorstore()

    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    collection_data = vectorstore.get()
    bm25_docs = [
        Document(page_content=doc, metadata=meta or {})
        for doc, meta in zip(
            collection_data["documents"], collection_data["metadatas"]
        )
    ]
    bm25_retriever = BM25Retriever.from_documents(bm25_docs, k=6)

    ensemble = EnsembleRetriever(
        retrievers=[chroma_retriever, bm25_retriever],
        weights=[0.5, 0.5],
    )

    compressor = FlashrankRerank(top_n=5)
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble,
    )


def get_llm():
    return ChatOpenAI(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        temperature=0.1,
    )


def build_messages(chat_history, question, context):
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for turn in chat_history:
        messages.append(HumanMessage(content=turn["human"]))
        messages.append(AIMessage(content=turn["ai"]))
    messages.append(
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")
    )
    return messages


def format_sources(docs):
    seen, sources = set(), []
    for doc in docs:
        src = doc.metadata.get("source", "Unknown")
        if src not in seen:
            seen.add(src)
            sources.append(src)
    return sources


def main():
    st.set_page_config(page_title="HOOT", page_icon="\U0001f989")
    st.title("\U0001f989 HOOT — Helpful Owl Of Temple")
    st.caption(
        "Ask questions about Temple University HR policies, benefits, and more. "
        "This is an informational tool — not official HR or legal advice."
    )

    if not CHROMA_DIR.exists():
        st.error("Vector store not found. Run `python src/ingest.py` first.")
        st.stop()

    missing = [
        v for v in ("LLM_BASE_URL", "LLM_API_KEY") if not os.getenv(v)
    ]
    if missing:
        st.error(
            f"Missing environment variables: {', '.join(missing)}. "
            "Copy `.env.example` to `.env` and fill in your values."
        )
        st.stop()

    retriever = build_retriever()
    llm = get_llm()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources"):
                    for src in msg["sources"]:
                        st.markdown(f"- `{src}`")

    if question := st.chat_input("Ask about Temple HR policies..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching Temple documents..."):
                docs = retriever.invoke(question)
                context = "\n\n---\n\n".join(doc.page_content for doc in docs)
                messages = build_messages(
                    st.session_state.chat_history, question, context
                )
                response = llm.invoke(messages)
                answer = response.content
                sources = format_sources(docs)

            st.markdown(answer)
            if sources:
                with st.expander("Sources"):
                    for src in sources:
                        st.markdown(f"- `{src}`")

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
        st.session_state.chat_history.append({"human": question, "ai": answer})


if __name__ == "__main__":
    main()
