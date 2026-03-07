# Daily Tech Investment Brief

A minimal Python MVP that pulls news for a small watchlist, groups it into ticker/theme buckets, asks an OpenAI model for concise research notes, and writes a Markdown report.

## What it does
- Pulls recent news from NewsAPI
- De-duplicates by title
- Buckets articles by ticker/theme using simple keyword rules
- Summarizes each bucket with an OpenAI model
- Writes a Markdown report to `reports/YYYY-MM-DD.md`

## Quick start

1. Create and activate a virtual environment
2. Install deps

```bash
pip install -r requirements.txt
```

3. Copy env file and fill keys

```bash
cp .env.example .env
```

4. Run

```bash
python -m app.main
```

## Telegram delivery

Add these to `.env` to send each generated report to Telegram:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Behavior:
- If the report is short (<= 4000 chars), it is sent as a text message
- If it is longer, the markdown file is sent as a document
- If Telegram vars are missing, delivery is skipped without crashing

## Example output

```markdown
# Daily Tech Investment Brief - 2026-03-05

## TSLA
### Key developments
- ...
### Bull case
...
### Bear case
...
### Near-term catalysts
...
### Sentiment
neutral
```

## Suggested next steps
- Add Telegram/email delivery
- Persist raw articles in SQLite/Postgres
- Add SEC filings / earnings / Reddit sentiment
- Add a web UI
