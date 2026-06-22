# ticker_utils.py

import re

VALID_TICKERS = {
    "AAPL", "MSFT", "NVDA", "GOOG", "GOOGL", "AMZN", "META", "TSLA", "NFLX", "AMD",
    "INTC", "IBM", "ORCL", "CRM", "PYPL", "UBER", "COIN", "JPM", "BAC", "WFC", "GS",
    "BRK.A", "BRK.B", "CVX", "XOM", "OXY", "T", "VZ", "SPY", "QQQ", "IWM", "V",
    "MA", "DIS", "PEP", "KO", "COST", "HD", "MCD", "NKE", "SBUX"
}

COMMON_NON_TICKERS = {
    "WHAT", "HOW", "WHY", "WHEN", "THIS", "THAT",
    "FED", "GDP", "USA", "AND", "FOR", "THE", "IS", "ARE"
}


def extract_ticker(text: str) -> str | None:
    """
    Extracts a stock ticker ONLY if it is in VALID_TICKERS.
    """
    if not text:
        return None

    candidates = re.findall(r"\b[A-Z]{1,5}\b", text.upper())

    for cand in candidates:
        if cand in VALID_TICKERS and cand not in COMMON_NON_TICKERS:
            return cand

    return None


if __name__ == "__main__":
    tests = [
        "What does Soros think about NVDA right now?",
        "Is TSLA too risky for Soros?",
        "How would Soros view the FED raising rates?",
    ]
    for t in tests:
        print(t, "->", extract_ticker(t))
