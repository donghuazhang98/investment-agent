from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _csv(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    newsapi_api_key: str = os.getenv("NEWSAPI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    watchlist: list[str] = field(default_factory=lambda: _csv("WATCHLIST", "TSLA,RKLB,GOOGL,NVDA"))
    themes: list[str] = field(default_factory=lambda: _csv("THEMES", "robotics,ai,space"))
    days_back: int = int(os.getenv("DAYS_BACK", "2"))
    max_articles_per_bucket: int = int(os.getenv("MAX_ARTICLES_PER_BUCKET", "8"))
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")


settings = Settings()
