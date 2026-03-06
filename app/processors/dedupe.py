from __future__ import annotations

from app.models import Article


def dedupe_articles(articles: list[Article]) -> list[Article]:
    seen: set[str] = set()
    deduped: list[Article] = []

    for article in articles:
        key = article.title.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(article)

    return deduped
