from __future__ import annotations

from datetime import date

from openai import OpenAI

from app.config import settings
from app.db import init_db, save_articles, save_report
from app.fetchers.news import fetch_news
from app.llm import summarize_bucket
from app.outputs.markdown import write_report
from app.outputs.telegram import send_report_to_telegram
from app.processors.classify import classify_articles
from app.processors.dedupe import dedupe_articles


def main() -> None:
    if not settings.openai_api_key:
        raise SystemExit("OPENAI_API_KEY is missing")
    if not settings.newsapi_api_key:
        raise SystemExit("NEWSAPI_API_KEY is missing")

    init_db()

    client = OpenAI(api_key=settings.openai_api_key)
    queries = settings.watchlist + settings.themes

    articles = fetch_news(
        api_key=settings.newsapi_api_key,
        queries=queries,
        days_back=settings.days_back,
    )
    inserted_articles = save_articles(articles)
    print(f"Persisted articles: {inserted_articles} new rows")

    articles = dedupe_articles(articles)
    buckets = classify_articles(articles)

    summaries = []
    for bucket, bucket_articles in buckets.items():
        if bucket == "general":
            continue
        trimmed = bucket_articles[: settings.max_articles_per_bucket]
        if not trimmed:
            continue
        summaries.append(
            summarize_bucket(
                client=client,
                model=settings.openai_model,
                bucket=bucket,
                articles=trimmed,
            )
        )

    report_path = write_report(summaries)
    print(f"Generated report: {report_path}")

    report_id = save_report(
        report_date=date.today().isoformat(),
        report_path=report_path,
        summaries=summaries,
    )
    print(f"Persisted report metadata: id={report_id}")

    send_report_to_telegram(
        report_path=report_path,
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )


if __name__ == "__main__":
    main()
