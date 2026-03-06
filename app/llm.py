from __future__ import annotations

import json
from openai import OpenAI

from app.models import Article, BucketSummary


SYSTEM_PROMPT = (
    "You are an equity research assistant focused on high-growth technology sectors. "
    "Summarize news for a personal investor. Be concise, factual, and balanced. "
    "Do not provide personalized financial advice. Output valid JSON only."
)


def _strip_markdown_code_fences(text: str) -> str:
    text = text.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) >= 2 and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def summarize_bucket(client: OpenAI, model: str, bucket: str, articles: list[Article]) -> BucketSummary:
    payload = [
        {
            "title": a.title,
            "description": a.description,
            "source": a.source,
            "published_at": a.published_at,
            "url": a.url,
        }
        for a in articles
    ]

    user_prompt = f'''
Bucket: {bucket}

Given these articles, produce a JSON object with this exact schema:
{{
  "bucket": "{bucket}",
  "key_developments": ["3 short bullets max"],
  "bull_case": "1 short paragraph",
  "bear_case": "1 short paragraph",
  "catalysts": ["up to 3 short bullets"],
  "sentiment": "bullish|neutral|bearish",
  "importance": 1,
  "disclaimer": "1 sentence saying this is research, not advice"
}}

Articles:
{json.dumps(payload, ensure_ascii=False)}
'''.strip()

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_text = getattr(response, "output_text", "").strip()
    text = _strip_markdown_code_fences(raw_text)
    try:
        return BucketSummary.model_validate_json(text)
    except Exception:
        print(raw_text)
        raise
