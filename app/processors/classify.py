from __future__ import annotations

from collections import defaultdict

from app.models import Article


KEYWORDS: dict[str, list[str]] = {
    "TSLA": ["tesla", "tsla", "optimus", "elon musk", "model y", "model 3", "cybertruck"],
    "RKLB": ["rocket lab", "rklb", "electron", "neutron launch", "neutron rocket", "space systems"],
    "GOOGL": ["google", "alphabet", "googl", "gemini", "waymo"],
    "NVDA": ["nvidia", "nvda", "cuda", "h100", "blackwell"],
    "robotics": ["robot", "robotics", "humanoid", "automation", "warehouse robot", "industrial robot"],
    "ai": ["ai", "artificial intelligence", "llm", "model", "inference", "gpu"],
    "space": ["space", "launch", "satellite", "rocket", "orbital", "payload"],
}


def classify_articles(articles: list[Article]) -> dict[str, list[Article]]:
    buckets: dict[str, list[Article]] = defaultdict(list)

    for article in articles:
        haystack = f"{article.title} {article.description}".lower()
        matched = []
        for bucket, terms in KEYWORDS.items():
            if any(term in haystack for term in terms):
                buckets[bucket].append(article)
                matched.append(bucket)
        article.matched_buckets = matched or ["general"]

    return dict(buckets)
