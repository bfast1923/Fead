"""
Pulls all feeds listed in sources.json, keeps recent entries, de-dupes,
and writes docs/articles.json for the webpage to read.

Run manually:   python fetch_feeds.py
Run on schedule: see .github/workflows/update-feed.yml
"""

import json
import re
import hashlib
from datetime import datetime, timedelta, timezone

import feedparser

MAX_AGE_HOURS = 60        # how far back to keep articles
MAX_PER_SOURCE = 6        # cap per feed so one prolific source can't flood the pool
SOURCES_FILE = "sources.json"
OUTPUT_FILE = "docs/articles.json"

TAG_RE = re.compile(r"<[^>]+>")


def clean_html(raw):
    if not raw:
        return ""
    text = TAG_RE.sub("", raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:280]


def article_id(link):
    return hashlib.sha1(link.encode("utf-8")).hexdigest()[:12]


def parse_published(entry):
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None)
        if val:
            return datetime(*val[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def fetch_source(source):
    articles = []
    try:
        parsed = feedparser.parse(source["url"])
    except Exception as e:
        print(f"  [skip] {source['name']}: {e}")
        return articles

    if getattr(parsed, "bozo", False) and not parsed.entries:
        print(f"  [skip] {source['name']}: feed did not parse cleanly")
        return articles

    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)

    for entry in parsed.entries[: MAX_PER_SOURCE * 2]:
        link = entry.get("link")
        title = entry.get("title")
        if not link or not title:
            continue

        published = parse_published(entry)
        if published < cutoff:
            continue

        summary = clean_html(entry.get("summary", entry.get("description", "")))

        articles.append(
            {
                "id": article_id(link),
                "title": title.strip(),
                "link": link,
                "summary": summary,
                "source": source["name"],
                "topic": source["topic"],
                "published": published.isoformat(),
                "paywalled": source.get("paywalled", False),
            }
        )
        if len(articles) >= MAX_PER_SOURCE:
            break

    print(f"  [ok] {source['name']}: {len(articles)} articles")
    return articles


def main():
    with open(SOURCES_FILE) as f:
        sources = json.load(f)

    all_articles = []
    seen_ids = set()

    print(f"Fetching {len(sources)} sources...")
    for source in sources:
        for article in fetch_source(source):
            if article["id"] not in seen_ids:
                seen_ids.add(article["id"])
                all_articles.append(article)

    all_articles.sort(key=lambda a: a["published"], reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(all_articles),
        "articles": all_articles,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\nWrote {len(all_articles)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
