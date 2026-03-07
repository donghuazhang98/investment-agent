from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.db import init_db, save_articles
from app.models import Article


class DbDuplicateProtectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        init_db(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _article_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM articles").fetchone()
        return int(row[0]) if row else 0

    def test_save_articles_ignores_duplicate_url(self) -> None:
        articles = [
            Article(title="First title", url="https://example.com/a"),
            Article(title="Different title", url="https://example.com/a"),
        ]

        inserted = save_articles(articles, self.db_path)

        self.assertEqual(inserted, 1)
        self.assertEqual(self._article_count(), 1)

    def test_save_articles_ignores_duplicate_normalized_title(self) -> None:
        articles = [
            Article(title="Rocket   Launch", url="https://example.com/a"),
            Article(title="  rocket launch  ", url="https://example.com/b"),
        ]

        inserted = save_articles(articles, self.db_path)

        self.assertEqual(inserted, 1)
        self.assertEqual(self._article_count(), 1)


if __name__ == "__main__":
    unittest.main()
