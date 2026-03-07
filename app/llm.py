from __future__ import annotations

import json
from openai import OpenAI

from app.models import Article, BucketSummary


SYSTEM_PROMPT = (
    "You are an equity research assistant focused on high-growth technology sectors. "
    "Summarize news for a personal investor. Be concise, factual, and balanced. "
    "Do not provide personalized financial advice. Output valid JSON only."
)

def _clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

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

    text = getattr(response, "output_text", "").strip()
    text = _clean_json_text(text)
    return BucketSummary.model_validate_json(text)