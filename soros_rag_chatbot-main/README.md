# Soros RAG Core (Trimmed)

This folder now contains only the reusable RAG core modules.

## Kept Modules

- `rag_interface.py`
- `rag_retriever.py`
- `rag_generator.py`
- `rag_data.py`
- `ticker_utils.py`
- `market_data.py`

These modules are kept as reference/core logic and can be reused by backend services.

## Data / Storage

- `data/Soros_Questions.xlsx` (knowledge base)
- `chroma_db/` (persisted embeddings)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GOOGLE_API_KEY="YOUR_KEY"
```
