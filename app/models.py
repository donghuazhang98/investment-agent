from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal


class Article(BaseModel):
    title: str
    description: str = ""
    url: str
    source: str = ""
    published_at: str = ""
    matched_buckets: list[str] = Field(default_factory=list)


class BucketSummary(BaseModel):
    bucket: str
    key_developments: list[str]
    bull_case: str
    bear_case: str
    catalysts: list[str]
    sentiment: Literal["bullish", "neutral", "bearish"]
    importance: int
    disclaimer: str
