from __future__ import annotations

from datetime import datetime, timedelta, timezone
import requests

from app.models import Article


NEWS_API_URL = "https://newsapi.org/v2/everything"


def fetch_news(api_key: str, queries: list[str], days_back: int = 2, page_size: int = 25) -> list[Article]:
    if not api_key:
        raise ValueError("NEWSAPI_API_KEY is missing")

    since = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    out: list[Article] = []

    for query in queries:
        params = {
            "q": query,
            "from": since,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": api_key,
        }
        resp = requests.get(NEWS_API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("articles", []):
            out.append(
                Article(
                    title=item.get("title") or "",
                    description=item.get("description") or "",
                    url=item.get("url") or "",
                    source=(item.get("source") or {}).get("name", ""),
                    published_at=item.get("publishedAt") or "",
                )
            )

    return out
