import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_documents():
    loader = DirectoryLoader(
        str(DATA_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    if not docs:
        print(f"No .md files found in {DATA_DIR}")
        sys.exit(1)
    print(f"Loaded {len(docs)} document(s) from {DATA_DIR}")
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunk(s)")
    return chunks


def embed_and_store(chunks):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
        print(f"Cleared existing vector store at {CHROMA_DIR}")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    print(f"Stored {len(chunks)} chunk(s) in {CHROMA_DIR}")
    return vectorstore


def main():
    print("=== HOOT Document Ingestion ===")
    docs = load_documents()
    chunks = split_documents(docs)
    embed_and_store(chunks)
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
