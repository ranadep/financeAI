# backend/universe/universe.py
from functools import lru_cache
import pandas as pd
import difflib

SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

@lru_cache(maxsize=1)
def _sp500_df() -> pd.DataFrame:
    # Pull S&P 500 constituents
    tables = pd.read_html(SP500_URL)
    df = tables[0].rename(columns={"Symbol": "Ticker", "Security": "Name"})
    df["Ticker"] = df["Ticker"].str.upper().str.strip()
    df["Name"] = df["Name"].str.strip()
    return df[["Ticker", "Name"]]

def get_sp500_tickers() -> list[str]:
    return _sp500_df()["Ticker"].tolist()

def resolve_companies_to_tickers(inputs: list[str]) -> list[dict]:
    """
    Accepts a mix of tickers or company names.
    Returns dicts: {input, ticker, matched_name, confidence}
    """
    df = _sp500_df()
    tickers = set(df["Ticker"].tolist())
    names = df["Name"].tolist()

    out = []
    for raw in inputs:
        q = (raw or "").strip()
        if not q:
            out.append({"input": raw, "ticker": None, "matched_name": None, "confidence": 0.0})
            continue

        q_upper = q.upper()
        # Direct ticker match
        if q_upper in tickers:
            row = df[df["Ticker"] == q_upper].iloc[0]
            out.append({"input": q, "ticker": row["Ticker"], "matched_name": row["Name"], "confidence": 1.0})
            continue

        # Fuzzy match on company names
        candidate = difflib.get_close_matches(q, names, n=1, cutoff=0.6)
        if candidate:
            name = candidate[0]
            row = df[df["Name"] == name].iloc[0]
            # rudimentary confidence proxy via SequenceMatcher
            score = difflib.SequenceMatcher(None, q.lower(), name.lower()).ratio()
            out.append({"input": q, "ticker": row["Ticker"], "matched_name": name, "confidence": float(score)})
        else:
            out.append({"input": q, "ticker": None, "matched_name": None, "confidence": 0.0})
    return out
