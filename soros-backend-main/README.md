# Soros Insights Backend (Trimmed)

This backend now exposes only the features used by the frontend:

- `POST /api/ragbot/` (Soros RAG chatbot)
- `POST /api/pairs/` (pairs trading backtest)

## What Was Removed

- Financial statements endpoint (`/api/financials/...`)
- Direct Gemini chatbot endpoint (`/api/chatbot/`)
- External transformer proxy endpoint (`/api/transformerbot/`)
- Legacy unused retrieval/generation files for old pipelines

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set Gemini key for RAG (and optional pairs insight):

```bash
export GEMINI_API_KEY="YOUR_KEY"
# or
export GOOGLE_API_KEY="YOUR_KEY"
```

## Run

```bash
python manage.py migrate
python manage.py runserver
```

Server runs at `http://127.0.0.1:8000`.

## API

### `POST /api/ragbot/`
Request:

```json
{ "message": "How would Soros think about NVDA?" }
```

Response:

```json
{ "reply": "..." }
```

### `POST /api/pairs/`
Request:

```json
{
  "symbolA": "XLF",
  "symbolB": "JPM",
  "startDate": "2024-01-01",
  "endDate": "2025-01-01",
  "entryZ": 1.0,
  "exitZ": 0.25,
  "rollingWindow": 60
}
```

Response includes hedge ratio, cointegration stats, z-score history, spread bands, PnL series, and optional Soros-style strategy insight.
