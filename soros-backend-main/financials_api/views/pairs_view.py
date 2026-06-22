import pandas as pd
import numpy as np
import yfinance as yf
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

try:
    import google.generativeai as genai
    # env first, fallback to project secrets
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        try:
            from soros_backend import secrets
            GEMINI_API_KEY = getattr(secrets, "GEMINI_API_KEY", None)
        except Exception:
            GEMINI_API_KEY = None
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    genai = None
    GEMINI_API_KEY = None

try:
    from statsmodels.tsa.stattools import coint
except Exception:
    coint = None

try:
    from yfinance.shared import _exceptions as yf_exceptions  # type: ignore
except Exception:
    yf_exceptions = None


class PairTradingView(APIView):
    """
    Runs a quick cointegration check and simple mean-reversion backtest
    for two symbols over a given date range.
    """

    def post(self, request):
        symbol_a = request.data.get("symbolA", "").upper().strip()
        symbol_b = request.data.get("symbolB", "").upper().strip()
        start = request.data.get("startDate")
        end = request.data.get("endDate")
        entry_z = float(request.data.get("entryZ", 1.0))
        exit_z = float(request.data.get("exitZ", 0.25))
        rolling_window = int(request.data.get("rollingWindow", 60))

        if not symbol_a or not symbol_b:
            return Response({"error": "Both symbolA and symbolB are required."}, status=status.HTTP_400_BAD_REQUEST)

        today = pd.Timestamp.today().normalize()

        # Default to last 1Y if no dates provided
        if not start or not end:
            end = today
            start = end - pd.Timedelta(days=365)
        else:
            try:
                start = pd.to_datetime(start).normalize()
                end = pd.to_datetime(end).normalize()
            except Exception:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

            # Clamp future dates to today
            if end > today:
                end = today
            if start > end:
                start = end - pd.Timedelta(days=365)

        try:
            raw = yf.download(
                [symbol_a, symbol_b],
                start=start,
                end=end,
                auto_adjust=False,  # keep Adj Close
                progress=False,
            )
            if raw is None or raw.empty:
                return Response(
                    {
                        "error": "Price data unavailable (likely rate limit from data source).",
                        "suggestion": "Wait a few minutes and retry. Reduce rapid repeated requests.",
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            # yfinance can return different shapes; normalize to a 2-column DataFrame
            if isinstance(raw.columns, pd.MultiIndex):
                prices = raw.get("Adj Close")
            elif "Adj Close" in raw:
                prices = raw["Adj Close"]
            else:
                prices = raw
            if isinstance(prices, pd.Series):
                prices = prices.to_frame()
        except Exception as e:
            msg = str(e)
            if "Too Many Requests" in msg or (yf_exceptions and isinstance(e, getattr(yf_exceptions, "YFRateLimitError", ()))):
                return Response(
                    {
                        "error": "Rate limited by data provider (yfinance).",
                        "suggestion": "Wait a few minutes or reduce repeated requests. Consider caching or widening the interval.",
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            return Response({"error": f"Failed to download prices: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If nothing came back, try a wider window as a fallback
        fallback_used = False
        if prices is None or prices.empty or prices.isna().all().any():
            try:
                fallback_start = start - pd.Timedelta(days=60)
                raw_fb = yf.download(
                    [symbol_a, symbol_b],
                    start=fallback_start,
                    end=end,
                    auto_adjust=False,
                    progress=False,
                )
                if isinstance(raw_fb.columns, pd.MultiIndex):
                    prices = raw_fb.get("Adj Close")
                elif "Adj Close" in raw_fb:
                    prices = raw_fb["Adj Close"]
                else:
                    prices = raw_fb
                if isinstance(prices, pd.Series):
                    prices = prices.to_frame()
                fallback_used = True
                start = fallback_start
            except Exception:
                prices = None

        if prices is None or prices.empty or prices.isna().all().any():
            return Response(
                {
                    "error": "Price data unavailable for one or both symbols in the chosen window.",
                    "suggestion": "Try a broader lookback (e.g., past 3–6 months), avoid illiquid symbols, and allow a few minutes if rate limited."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Ensure both tickers are present after download
        missing_symbols = [s for s in [symbol_a, symbol_b] if s not in prices.columns]
        if missing_symbols:
            return Response(
                {"error": f"Missing price data for: {', '.join(missing_symbols)}. Please check the symbols or try a different date range."},
                status=status.HTTP_404_NOT_FOUND
            )

        series_a = prices[symbol_a].dropna()
        series_b = prices[symbol_b].dropna()

        common_index = series_a.index.intersection(series_b.index)
        if common_index.empty:
            return Response({"error": "No overlapping trading days for the selected symbols."}, status=status.HTTP_404_NOT_FOUND)

        series_a = series_a.loc[common_index]
        series_b = series_b.loc[common_index]

        # Suggest a fuller window if overlap is thin
        suggest_start = None
        suggest_end = None
        suggestion_reason = None
        if not common_index.empty:
            span_days = (common_index.max() - common_index.min()).days
            if span_days < 180:
                suggest_end = min(today, end)
                suggest_start = suggest_end - pd.Timedelta(days=365)
                suggestion_reason = "Tight overlap detected; try a 1Y lookback for a more stable hedge ratio."

        # Hedge ratio via simple linear fit (A ~ beta * B)
        beta, _ = np.polyfit(series_b.values, series_a.values, 1)

        # Cointegration p-value if statsmodels is available
        p_value = None
        cointegration_stat = None
        if coint and len(series_a) >= 30:
            try:
                # Cointegration works better on log prices to reduce scale effects.
                log_a = np.log(series_a.replace(0, np.nan)).dropna()
                log_b = np.log(series_b.replace(0, np.nan)).dropna()
                align_idx = log_a.index.intersection(log_b.index)
                log_a = log_a.loc[align_idx]
                log_b = log_b.loc[align_idx]
                test_stat, p_val, _ = coint(log_a, log_b, trend='c')
                p_value = float(p_val)
                cointegration_stat = float(test_stat)
            except Exception:
                p_value = None
        else:
            p_value = None

        spread = series_a - beta * series_b
        # Rolling z-score to adapt to regime shifts
        rolling_mean = spread.rolling(window=rolling_window, min_periods=max(2, rolling_window // 2)).mean()
        rolling_std = spread.rolling(window=rolling_window, min_periods=max(2, rolling_window // 2)).std().replace(0, np.nan)
        zscore = (spread - rolling_mean) / (rolling_std.fillna(rolling_std.mean() or 1e-9))

        returns_a = series_a.pct_change().fillna(0.0)
        returns_b = series_b.pct_change().fillna(0.0)

        position = 0  # 1 = long spread (long A/short B), -1 = short spread
        daily_pnl = []
        trades = 0

        z_history = []
        pnl_series = []
        cumulative_ret = 1.0

        spread_series = []
        entry_upper = rolling_mean + entry_z * rolling_std
        entry_lower = rolling_mean - entry_z * rolling_std
        exit_upper = rolling_mean + exit_z * rolling_std
        exit_lower = rolling_mean - exit_z * rolling_std

        for idx in spread.index:
            spread_series.append({
                "date": str(idx.date()),
                "spread": float(spread.loc[idx]) if pd.notna(spread.loc[idx]) else None,
                "mean": float(rolling_mean.loc[idx]) if pd.notna(rolling_mean.loc[idx]) else None,
                "entryUpper": float(entry_upper.loc[idx]) if pd.notna(entry_upper.loc[idx]) else None,
                "entryLower": float(entry_lower.loc[idx]) if pd.notna(entry_lower.loc[idx]) else None,
                "exitUpper": float(exit_upper.loc[idx]) if pd.notna(exit_upper.loc[idx]) else None,
                "exitLower": float(exit_lower.loc[idx]) if pd.notna(exit_lower.loc[idx]) else None,
            })

        for idx, (z, ret_a, ret_b) in enumerate(zip(zscore.iloc[1:], returns_a.iloc[1:], returns_b.iloc[1:])):
            z_history.append({"date": str(zscore.index[idx + 1].date()), "z": float(z) if pd.notna(z) else None})
            if position == 0:
                if pd.notna(z) and z > entry_z:
                    position = -1  # short spread: short A, long B
                    trades += 1
                elif pd.notna(z) and z < -entry_z:
                    position = 1   # long spread: long A, short B
                    trades += 1
            elif pd.notna(z) and abs(z) < exit_z:
                position = 0

            pnl = position * (ret_a - beta * ret_b)
            daily_pnl.append(pnl)
            cumulative_ret *= (1 + pnl)
            pnl_series.append({"date": str(zscore.index[idx + 1].date()), "cumulativeReturn": float(cumulative_ret - 1)})

        cumulative_return = float(cumulative_ret - 1) if daily_pnl else 0.0

        gemini_insight = None
        if genai and GEMINI_API_KEY:
            try:
                prompt = (
                    "You are George Soros. Given a pairs trade backtest summary, suggest if adjacent date windows "
                    "around the user selection might be better. Keep it to 3 bullets and one action. "
                    "If there is little info, say so briefly. Also propose a potentially better strategy tweak versus the one used "
                    "(entry/exit z thresholds, rolling window length, or posture: cut/press/hedge/wait) based on the data provided. "
                    "Note: the only user-adjustable variables are entry Z, exit Z, rolling window, the two symbols, and the date range (hedge ratio is computed, not user-managed).\n\n"
                    "Make sure your tone and content reflect George Soros's own investment philosophy, especially for pairs trading and reflexivity.\n\n"
                    f"Symbols: {symbol_a} vs {symbol_b}\n"
                    f"Date range: {start.date()} to {end.date()}\n"
                    f"Hedge ratio (A~beta*B): {beta:.4f}\n"
                    f"Latest z-score: {zscore.iloc[-1] if not zscore.empty else 'N/A'}\n"
                    f"Trades: {trades}\n"
                    f"Cumulative return: {cumulative_return:.4f}\n"
                    f"Entry Z: {entry_z}, Exit Z: {exit_z}, Rolling window: {rolling_window}\n"
                    f"Overlap days: {(common_index.max() - common_index.min()).days if not common_index.empty else 'N/A'}\n"
                    f"Suggested alt range (internal calc): {suggest_start.date() if suggest_start is not None else 'N/A'} to {suggest_end.date() if suggest_end is not None else 'N/A'}\n\n"
                    "Output format:\n"
                    "- Insight 1\n"
                    "- Insight 2\n"
                    "- Insight 3\n"
                    "- Strategy tweak: <what to change and why>\n"
                    "Action: cut risk / press / hedge / wait\n"
                )
                model = genai.GenerativeModel('gemini-2.0-flash')
                resp = model.generate_content(prompt)
                gemini_insight = resp.text.strip() if resp and hasattr(resp, "text") else None
            except Exception:
                gemini_insight = None

        def safe_num(val):
            try:
                f = float(val)
                if np.isnan(f) or np.isinf(f):
                    return None
                return f
            except Exception:
                return None

        result = {
            "symbols": {"A": symbol_a, "B": symbol_b},
            "dateRange": {"start": str(start), "end": str(end)},
            "hedgeRatio": safe_num(beta),
            "cointegrationPValue": safe_num(p_value),
            "cointegrationTestStatistic": safe_num(cointegration_stat),
            "cointegrationInterpretation": (
                "✅ p < 0.05: cointegrated (reject H₀ of no cointegration)" if p_value is not None and p_value < 0.05 else
                "❌ p ≥ 0.05: not cointegrated (fail to reject H₀)" if p_value is not None else
                "Cointegration test unavailable (need statsmodels + sufficient data)"
            ),
            "latestZScore": safe_num(zscore.iloc[-1]) if not zscore.empty else None,
            "trades": trades,
            "cumulativeReturn": safe_num(cumulative_return),
            "entryZ": entry_z,
            "exitZ": exit_z,
            "rollingWindow": rolling_window,
            "zHistory": [
                {"date": item["date"], "z": safe_num(item["z"])}
                for item in z_history[-200:]
            ],
            "spreadSeries": spread_series[-300:],  # for plotting spread + bands
            "pnlSeries": pnl_series[-300:],        # for plotting cumulative PnL
            "priceSeries": [
                {
                    "date": str(ts.date()),
                    "priceA": safe_num(series_a.loc[ts]),
                    "priceB": safe_num(series_b.loc[ts]),
                }
                for ts in series_a.index[-300:]
            ],
        }

        if suggestion_reason:
            result["suggestedRange"] = {"start": str(suggest_start.date()), "end": str(suggest_end.date())}
            result["suggestionReason"] = suggestion_reason
        if gemini_insight:
            # Present as Soros insight
            result["georgeSorosInsight"] = gemini_insight
            # Optionally split out a strategy tweak line if present
            for line in gemini_insight.splitlines():
                if line.lower().startswith("strategy tweak:"):
                    result["strategyTweak"] = line.split(":", 1)[1].strip()
                    break

        return Response(result, status=status.HTTP_200_OK)
