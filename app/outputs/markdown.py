from __future__ import annotations

from datetime import date
from pathlib import Path

from app.models import BucketSummary


def write_report(summaries: list[BucketSummary], output_dir: str = "reports") -> Path:
    today = date.today().isoformat()
    path = Path(output_dir) / f"{today}.md"
    lines = [f"# Daily Tech Investment Brief - {today}", ""]

    for item in summaries:
        lines.extend(
            [
                f"## {item.bucket}",
                "### Key developments",
                *[f"- {x}" for x in item.key_developments],
                "### Bull case",
                item.bull_case,
                "### Bear case",
                item.bear_case,
                "### Near-term catalysts",
                *[f"- {x}" for x in item.catalysts],
                "### Sentiment",
                item.sentiment,
                "### Importance",
                str(item.importance),
                "### Disclaimer",
                item.disclaimer,
                "",
            ]
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
