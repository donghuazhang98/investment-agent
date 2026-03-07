from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from app.db import DB_PATH


def _fetch_bucket_history(db_path: Path, bucket: str, days: int) -> list[tuple[str, str, str, str]]:
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                r.report_date,
                s.sentiment,
                s.catalysts_json,
                s.key_developments_json
            FROM bucket_summaries s
            JOIN reports r ON r.id = s.report_id
            WHERE LOWER(s.bucket) = LOWER(?)
              AND r.report_date >= ?
            ORDER BY r.report_date DESC
            """,
            (bucket, cutoff),
        ).fetchall()
    return [(str(a), str(b), str(c), str(d)) for a, b, c, d in rows]


def _to_lines(label: str, raw_json: str) -> list[str]:
    try:
        items = json.loads(raw_json)
    except json.JSONDecodeError:
        items = []
    if not isinstance(items, list) or not items:
        return [f"{label}: (none)"]
    out = [f"{label}:"]
    out.extend(f"- {item}" for item in items)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Query historical bucket summaries from SQLite.")
    parser.add_argument("--bucket", required=True, help="Ticker or theme bucket name (e.g., RKLB, ai)")
    parser.add_argument("--days", type=int, default=7, help="How many days of history to include")
    parser.add_argument("--db", default=str(DB_PATH), help="Path to SQLite database")
    args = parser.parse_args()

    if args.days < 1:
        raise SystemExit("--days must be >= 1")

    rows = _fetch_bucket_history(Path(args.db), args.bucket, args.days)
    if not rows:
        print(f"No history found for bucket '{args.bucket}' in the last {args.days} day(s).")
        return

    for report_date, sentiment, catalysts_json, key_developments_json in rows:
        print(f"Report date: {report_date}")
        print(f"Sentiment: {sentiment}")
        for line in _to_lines("Catalysts", catalysts_json):
            print(line)
        for line in _to_lines("Key developments", key_developments_json):
            print(line)
        print("")


if __name__ == "__main__":
    main()
