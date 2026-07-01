import os
from pathlib import Path

from langchain.retrievers import ContextualCompressionRetriever, EnsembleRetriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma")


def load_vectorstore() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )


def build_retriever(vectorstore: Chroma) -> ContextualCompressionRetriever:
    """
    Hybrid retriever: Chroma (dense) + BM25 (sparse) ensemble, then FlashRank rerank.
    Dense handles semantic queries; BM25 catches exact policy terms (FMLA, T-26, etc.).
    """
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
