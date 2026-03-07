from __future__ import annotations

from pathlib import Path

import requests


TELEGRAM_TEXT_LIMIT = 4000


def send_report_to_telegram(report_path: Path, bot_token: str, chat_id: str) -> None:
    if not bot_token or not chat_id:
        print("Telegram not configured; skipping delivery")
        return

    text = report_path.read_text(encoding="utf-8")
    base_url = f"https://api.telegram.org/bot{bot_token}"

    if len(text) <= TELEGRAM_TEXT_LIMIT:
        response = requests.post(
            f"{base_url}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=20,
        )
    else:
        with report_path.open("rb") as file_obj:
            response = requests.post(
                f"{base_url}/sendDocument",
                data={"chat_id": chat_id},
                files={"document": (report_path.name, file_obj, "text/markdown")},
                timeout=30,
            )

    response.raise_for_status()
