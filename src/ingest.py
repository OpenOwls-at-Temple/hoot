import os
import re
import shutil
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_PATH = os.getenv("CHROMA_PATH", str(PROJECT_ROOT / "chroma"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

_MD_HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def extract_frontmatter(text: str) -> tuple:
    """Return (meta_dict, body_str). meta_dict is empty if no frontmatter found."""
    m = _FRONTMATTER_RE.match(text)
    if m:
        meta = yaml.safe_load(m.group(1)) or {}
        return meta, text[m.end():]
    return {}, text


def extract_title(body: str, filename: str) -> str:
    """Return the first H1 heading from body, or a title derived from the filename."""
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return Path(filename).stem.replace("_", " ").title()


def load_documents() -> list:
    """
    Load every .md file in DATA_DIR, extract frontmatter metadata, split by
    markdown heading (section-aware chunking), and return a list of Documents
    with title, url, category, last_updated, and source metadata fields set.
    """
    md_files = sorted(DATA_DIR.glob("**/*.md"))
    if not md_files:
        print(f"No .md files found in {DATA_DIR}")
        sys.exit(1)

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=_MD_HEADERS,
        strip_headers=False,
    )

    all_docs = []
    for path in md_files:
        raw = path.read_text(encoding="utf-8")
        meta, body = extract_frontmatter(raw)
        title = extract_title(body, path.name)

        chunks = splitter.split_text(body)
        for chunk in chunks:
            chunk.metadata.update(
                {
                    "title": title,
                    "url": str(meta.get("source_url") or ""),
                    "category": str(meta.get("category") or ""),
                    "last_updated": str(meta.get("last_updated") or ""),
                    "source": str(path),
                }
            )
            all_docs.append(chunk)

    print(f"Loaded {len(md_files)} file(s), split into {len(all_docs)} chunk(s)")
    return all_docs


def embed_and_store(docs: list) -> None:
    """Embed docs with EMBEDDING_MODEL and store in ChromaDB at CHROMA_PATH."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    chroma_dir = Path(CHROMA_PATH)

    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
        print(f"Cleared existing vector store at {chroma_dir}")

    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(chroma_dir),
    )
    print(f"Stored {len(docs)} chunk(s) in {chroma_dir}")


def main() -> None:
    print("=== HOOT Document Ingestion ===")
    docs = load_documents()
    embed_and_store(docs)
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
