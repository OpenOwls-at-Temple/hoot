"""
Tests for src/ingest.py — frontmatter extraction and title parsing.
"""
import sys
from pathlib import Path

# ingest.py lives in src/, which is not a package — add project root to path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingest import extract_frontmatter, extract_title


# ---------------------------------------------------------------------------
# Frontmatter extraction
# ---------------------------------------------------------------------------

def test_extract_frontmatter_parses_all_fields():
    raw = (
        "---\n"
        "category: benefits\n"
        "source_url: https://careers.temple.edu/tuition\n"
        "last_updated: 2026-06-28\n"
        "---\n\n"
        "# Tuition Policy\n\nBody text here."
    )
    meta, body = extract_frontmatter(raw)

    assert meta["category"] == "benefits"
    assert meta["source_url"] == "https://careers.temple.edu/tuition"
    assert str(meta["last_updated"]) == "2026-06-28"
    assert "# Tuition Policy" in body


def test_extract_frontmatter_no_source_url_returns_none():
    raw = "---\ncategory: policy\nlast_updated: 2026-06-28\n---\n\n# Doc\nBody"
    meta, body = extract_frontmatter(raw)

    assert meta.get("source_url") is None
    assert meta["category"] == "policy"


def test_extract_frontmatter_no_frontmatter_returns_empty_meta():
    raw = "# Just a doc\n\nNo frontmatter at all."
    meta, body = extract_frontmatter(raw)

    assert meta == {}
    assert "Just a doc" in body


# ---------------------------------------------------------------------------
# Title extraction
# ---------------------------------------------------------------------------

def test_extract_title_from_h1_heading():
    body = "\n# Faculty Handbook\n\nSome content."
    assert extract_title(body, "faculty_handbook.md") == "Faculty Handbook"


def test_extract_title_falls_back_to_filename_stem():
    body = "No heading here at all."
    assert extract_title(body, "hr_faqs.md") == "Hr Faqs"


def test_extract_title_picks_first_h1_only():
    body = "# First Heading\n\nContent.\n\n# Second Heading\n\nMore."
    assert extract_title(body, "doc.md") == "First Heading"
