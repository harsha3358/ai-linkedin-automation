from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any
from urllib.parse import quote_plus

import requests

from models import TrendItem
from scoring import score_trend_item
from storage import dedupe_keep_order


UA = {
    "User-Agent": "Mozilla/5.0 (compatible; ai-linkedin-automation/2.0; +https://github.com/harsha3358/ai-linkedin-automation)"
}


def _parse_dt(value: str) -> str:
    return value or ""


def fetch_hackernews_ai(limit: int = 10) -> List[TrendItem]:
    url = "https://hn.algolia.com/api/v1/search?query=AI%20OR%20machine%20learning%20OR%20llm&tags=story&hitsPerPage=20"
    data = requests.get(url, headers=UA, timeout=20).json()
    items: List[TrendItem] = []
    for hit in data.get("hits", [])[:limit]:
        title = hit.get("title") or ""
        link = hit.get("url") or ""
        if not title or not link:
            continue
        items.append(
            TrendItem(
                title=title,
                source="hackernews",
                url=link,
                summary=hit.get("commentary", "")[:400],
                published_at=hit.get("created_at", ""),
                metadata={"points": hit.get("points", 0), "author": hit.get("author", "")},
            )
        )
    return items


def fetch_arxiv_ai(limit: int = 10) -> List[TrendItem]:
    query = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL"
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={quote_plus(query)}&start=0&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
    )
    xml = requests.get(url, headers=UA, timeout=20).text
    root = ET.fromstring(xml)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items: List[TrendItem] = []
    for entry in root.findall("atom:entry", ns)[:limit]:
        title = " ".join((entry.findtext("atom:title", default="", namespaces=ns) or "").split())
        summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ns) or "").split())
        link = ""
        for l in entry.findall("atom:link", ns):
            if l.attrib.get("rel") == "alternate":
                link = l.attrib.get("href", "")
                break
        if title and link:
            items.append(
                TrendItem(
                    title=title,
                    source="arxiv",
                    url=link,
                    summary=summary[:500],
                    published_at=entry.findtext("atom:published", default="", namespaces=ns) or "",
                    metadata={"authors": [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]},
                )
            )
    return items


def fetch_reddit_ai(limit: int = 10) -> List[TrendItem]:
    subs = ["MachineLearning", "artificial", "LocalLLaMA", "singularity"]
    items: List[TrendItem] = []
    for sub in subs:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit={max(3, limit // len(subs))}"
        try:
            data = requests.get(url, headers=UA, timeout=20).json()
        except Exception:
            continue
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            title = d.get("title", "")
            permalink = d.get("permalink", "")
            if not title or not permalink:
                continue
            items.append(
                TrendItem(
                    title=title,
                    source=f"reddit:{sub}",
                    url=f"https://www.reddit.com{permalink}",
                    summary=d.get("selftext", "")[:400],
                    published_at=datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc).isoformat() if d.get("created_utc") else "",
                    metadata={"score": d.get("score", 0), "num_comments": d.get("num_comments", 0)},
                )
            )
    return items[:limit]


def fetch_github_ai(limit: int = 10) -> List[TrendItem]:
    url = "https://api.github.com/search/repositories?q=topic:machine-learning+OR+topic:artificial-intelligence&sort=stars&order=desc&per_page=10"
    try:
        data = requests.get(url, headers=UA, timeout=20).json()
    except Exception:
        return []
    items: List[TrendItem] = []
    for repo in data.get("items", [])[:limit]:
        items.append(
            TrendItem(
                title=repo.get("full_name", ""),
                source="github",
                url=repo.get("html_url", ""),
                summary=repo.get("description", "") or "",
                published_at=repo.get("created_at", "") or "",
                metadata={"stars": repo.get("stargazers_count", 0), "forks": repo.get("forks_count", 0)},
            )
        )
    return items


def fetch_trends(limit: int = 20) -> List[TrendItem]:
    items: List[TrendItem] = []
    items.extend(fetch_hackernews_ai(limit=limit))
    items.extend(fetch_arxiv_ai(limit=limit))
    items.extend(fetch_reddit_ai(limit=limit))
    items.extend(fetch_github_ai(limit=limit))

    # Score and dedupe
    scored: List[TrendItem] = []
    for item in items:
        item.score = score_trend_item(item)
        scored.append(item)

    scored = sorted(scored, key=lambda x: x.score, reverse=True)
    scored = dedupe_keep_order(scored, key_fn=lambda x: x.url)
    return scored[:limit]