"""
Download publicly available Temple University HR/policy documents and
save them as markdown files with YAML frontmatter in data/.

Run:  python3 scripts/download_docs.py
"""

import re
import time
import urllib.robotparser
from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "HOOT-RAG-Ingestor/1.0 (Temple University class project)"}

# Public Temple pages to ingest — no login required
SOURCES = [
    {
        "url": "https://www.temple.edu/about/faculty-staff-resources",
        "category": "policy",
        "slug": "faculty_staff_resources",
        "title": "Temple University Faculty & Staff Resources",
    },
    {
        "url": "https://www.temple.edu/about/faculty-staff-resources/working-temple",
        "category": "benefits",
        "slug": "working_at_temple",
        "title": "Working at Temple University",
    },
    {
        "url": "https://www.temple.edu/about/faculty-staff-resources/faculty-resources",
        "category": "policy",
        "slug": "faculty_resources",
        "title": "Temple University Faculty Resources",
    },
    {
        "url": "https://www.temple.edu/about/faculty-staff-resources/wellness-health-services",
        "category": "benefits",
        "slug": "wellness_health",
        "title": "Temple University Wellness & Health Services for Faculty and Staff",
    },
    {
        "url": "https://www.temple.edu/temple-research/grants-funding",
        "category": "research",
        "slug": "research_grants_funding",
        "title": "Temple University Research Grants & Funding",
    },
    {
        "url": "https://www.temple.edu/temple-research/centers-institutes",
        "category": "research",
        "slug": "research_centers",
        "title": "Temple University Research Centers & Institutes",
    },
    {
        "url": "https://www.temple.edu/temple-research/faculty-research-news",
        "category": "research",
        "slug": "faculty_research_news",
        "title": "Temple University Faculty Research News",
    },
]


def robots_allowed(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        return True  # allow if we can't read robots.txt


def fetch_page(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  SKIP — fetch failed: {e}")
        return None


def extract_main_content(html: str, url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Find the main content area FIRST (before any decomposition)
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"^(main|content|body)$", re.I))
        or soup.body
    )

    if main is None:
        return ""

    # Remove noise from within the content area only
    for tag in main.find_all(["script", "style", "noscript", "form"]):
        tag.decompose()
    for tag in main.find_all(class_=re.compile(
            r"breadcrumb|cookie|banner|social|share|print|skip", re.I)):
        tag.decompose()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    text = h.handle(str(main))

    # Clean up excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def save_document(slug: str, title: str, url: str, category: str, body: str) -> None:
    frontmatter = (
        f"---\n"
        f"title: {title}\n"
        f"source_url: {url}\n"
        f"category: {category}\n"
        f"last_updated: {TODAY}\n"
        f"---\n\n"
    )
    out_path = DATA_DIR / f"{slug}.md"
    out_path.write_text(frontmatter + body, encoding="utf-8")
    print(f"  Saved → {out_path.name} ({len(body):,} chars)")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {len(SOURCES)} Temple documents → {DATA_DIR}\n")

    ok, skipped = 0, 0
    for src in SOURCES:
        url = src["url"]
        print(f"Fetching: {url}")

        if not robots_allowed(url):
            print("  SKIP — disallowed by robots.txt")
            skipped += 1
            continue

        html = fetch_page(url)
        if not html:
            skipped += 1
            continue

        body = extract_main_content(html, url)
        if len(body) < 100:
            print(f"  SKIP — content too short ({len(body)} chars), likely blocked or empty page")
            skipped += 1
            continue

        save_document(src["slug"], src["title"], url, src["category"], body)
        ok += 1
        time.sleep(1)  # be polite

    print(f"\nDone: {ok} saved, {skipped} skipped.")
    if ok == 0:
        print("No documents saved — check network connectivity or try different URLs.")


if __name__ == "__main__":
    main()
