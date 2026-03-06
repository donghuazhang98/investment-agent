# Codex task brief

Build on this MVP into a personal research tool.

## Goals
1. Add SQLite persistence for raw articles and daily reports
2. Add Telegram delivery via bot token and chat ID
3. Add a score per bucket: bullish / neutral / bearish plus 1-5 importance
4. Add retry/error handling for API failures
5. Add tests for classification and de-duplication
6. Keep the project simple, readable, and production-ish

## Constraints
- Python only
- No frontend yet
- Avoid overengineering
- Use environment variables for secrets
- Preserve the existing report format

## Nice to have
- Add a `--tickers` CLI arg
- Add a `--dry-run` mode
- Add an optional RSS fallback if NewsAPI fails
