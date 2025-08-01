# backend/recommender/advisor.py
from __future__ import annotations
import yfinance as yf
import pandas as pd
from universe.universe import get_sp500_tickers

def _percent_change_last_day(df: pd.DataFrame) -> float:
    df = df.dropna()
    if len(df) < 2:
        return 0.0
    last_close = float(df["Close"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2])
    return ((last_close / prev_close) - 1.0) * 100.0

def top_n_momentum(n: int = 5) -> list[dict]:
    tickers = get_sp500_tickers()
    # Batch download (faster than one-by-one)
    data = yf.download(
        tickers=tickers, period="2d", interval="1d",
        group_by="ticker", auto_adjust=False, threads=True, progress=False
    )

    rows = []
    for t in tickers:
        # yfinance returns different shapes depending on #tickers; normalize access:
        try:
            sub = data[t] if isinstance(data.columns, pd.MultiIndex) else data
        except KeyError:
            continue
        if "Close" not in sub.columns:
            continue
        pct = _percent_change_last_day(sub)
        rows.append({"ticker": t, "score_pct_change_1d": pct})

    df = pd.DataFrame(rows).dropna()
    df = df.sort_values("score_pct_change_1d", ascending=False)
    picks = df.head(n).to_dict(orient="records")
    # Add action + reason fields
    for p in picks:
        p["action"] = "buy" if p["score_pct_change_1d"] > 0 else "hold"
        p["reason"] = f"1-day momentum {p['score_pct_change_1d']:.2f}%"
    return picks

def recommend_stocks(n: int = 5) -> list[dict]:
    return top_n_momentum(n=n)
