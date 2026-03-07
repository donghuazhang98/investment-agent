from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from app.db import init_db, save_report
from app.history import _fetch_bucket_history, main
from app.models import BucketSummary


class HistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "history.db"
        init_db(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _summary(self, bucket: str, sentiment: str = "neutral") -> BucketSummary:
        return BucketSummary(
            bucket=bucket,
            key_developments=["k1", "k2"],
            bull_case="bull",
            bear_case="bear",
            catalysts=["c1", "c2"],
            sentiment=sentiment,
            importance=1,
            disclaimer="research only",
        )

    def test_fetch_bucket_history_filters_by_bucket_and_days(self) -> None:
        today = date.today().isoformat()
        old = (date.today() - timedelta(days=10)).isoformat()
        save_report(today, Path("reports/today.md"), [self._summary("RKLB", "bullish")], self.db_path)
        save_report(today, Path("reports/ai.md"), [self._summary("ai", "neutral")], self.db_path)
        save_report(old, Path("reports/old.md"), [self._summary("RKLB", "bearish")], self.db_path)

        rows = _fetch_bucket_history(self.db_path, "rklb", 7)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], today)
        self.assertEqual(rows[0][1], "bullish")

    def test_cli_prints_required_fields(self) -> None:
        today = date.today().isoformat()
        save_report(today, Path("reports/rklb.md"), [self._summary("RKLB", "bullish")], self.db_path)

        out = io.StringIO()
        with patch("sys.argv", ["app.history", "--bucket", "RKLB", "--days", "7", "--db", str(self.db_path)]):
            with redirect_stdout(out):
                main()

        printed = out.getvalue()
        self.assertIn("Report date:", printed)
        self.assertIn("Sentiment:", printed)
        self.assertIn("Catalysts:", printed)
        self.assertIn("Key developments:", printed)


if __name__ == "__main__":
    unittest.main()
