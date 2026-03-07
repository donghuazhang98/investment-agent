from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from app.models import Article, BucketSummary


DB_PATH = Path("data") / "investment_agent.db"


def _normalize_title(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", (title or "").strip().lower())
    return cleaned


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                url TEXT,
                normalized_title TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT,
                published_at TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_url_unique
            ON articles(url)
            WHERE url IS NOT NULL AND url != '';

            CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_normalized_title_unique
            ON articles(normalized_title)
            WHERE normalized_title != '';

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY,
                report_date TEXT NOT NULL,
                report_path TEXT NOT NULL UNIQUE,
                summary_count INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS bucket_summaries (
                id INTEGER PRIMARY KEY,
                report_id INTEGER NOT NULL,
                bucket TEXT NOT NULL,
                key_developments_json TEXT NOT NULL,
                bull_case TEXT NOT NULL,
                bear_case TEXT NOT NULL,
                catalysts_json TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                importance INTEGER NOT NULL,
                disclaimer TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
            );
            """
        )


def save_articles(articles: list[Article], db_path: Path = DB_PATH) -> int:
    inserted = 0
    with _connect(db_path) as conn:
        for article in articles:
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO articles (
                    url,
                    normalized_title,
                    title,
                    description,
                    source,
                    published_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    article.url.strip() or None,
                    _normalize_title(article.title),
                    article.title,
                    article.description,
                    article.source,
                    article.published_at,
                ),
            )
            inserted += cursor.rowcount
    return inserted


def save_report(
    report_date: str,
    report_path: Path,
    summaries: list[BucketSummary],
    db_path: Path = DB_PATH,
) -> int:
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO reports (report_date, report_path, summary_count)
            VALUES (?, ?, ?)
            ON CONFLICT(report_path) DO UPDATE SET
                report_date=excluded.report_date,
                summary_count=excluded.summary_count
            """,
            (report_date, str(report_path), len(summaries)),
        )

        row = conn.execute("SELECT id FROM reports WHERE report_path = ?", (str(report_path),)).fetchone()
        if not row:
            raise RuntimeError("Failed to upsert report metadata")
        report_id = int(row[0])

        conn.execute("DELETE FROM bucket_summaries WHERE report_id = ?", (report_id,))
        for item in summaries:
            conn.execute(
                """
                INSERT INTO bucket_summaries (
                    report_id,
                    bucket,
                    key_developments_json,
                    bull_case,
                    bear_case,
                    catalysts_json,
                    sentiment,
                    importance,
                    disclaimer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    item.bucket,
                    json.dumps(item.key_developments, ensure_ascii=False),
                    item.bull_case,
                    item.bear_case,
                    json.dumps(item.catalysts, ensure_ascii=False),
                    item.sentiment,
                    item.importance,
                    item.disclaimer,
                ),
            )

    return report_id
