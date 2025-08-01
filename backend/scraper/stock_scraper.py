# backend/scraper/stock_scraper.py
from __future__ import annotations
import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    return {
        "info": stock.info if hasattr(stock, "info") else {},
        "history": hist.tail(5).reset_index().to_dict(orient="records")
    }

def get_daily_change(ticker: str) -> dict:
    """
    Returns last close, previous close, abs and pct change for the most recent session.
    """
    df = yf.download(ticker, period="2d", interval="1d", progress=False, auto_adjust=False)
    df = df.dropna()
    if len(df) < 2:
        # fallback: single day
        last_close = float(df["Close"].iloc[-1].item()) if len(df["Close"]) > 0 else 0.0
        prev_close = float(df["Close"].iloc[-2].item()) if len(df["Close"]) > 1 else 0.0
    else:
        last_close = float(df["Close"].iloc[-1].item()) if len(df["Close"]) > 0 else 0.0
        prev_close = float(df["Close"].iloc[-2].item()) if len(df["Close"]) > 1 else 0.0


    change_abs = last_close - prev_close
    change_pct = (change_abs / prev_close) * 100 if prev_close else 0.0
    return {
        "ticker": ticker,
        "last_close": last_close,
        "prev_close": prev_close,
        "change_abs": change_abs,
        "change_pct": change_pct,
        "direction": "up" if change_abs > 0 else ("down" if change_abs < 0 else "flat")
    }

def get_intraday_sparkline(ticker):
    import yfinance as yf
    from datetime import datetime, timedelta
    import pandas as pd

    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    try:
        df = yf.download(
            tickers=ticker,
            start=start_time.strftime("%Y-%m-%d"),
            end=end_time.strftime("%Y-%m-%d"),
            interval="15m",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            print(f"⚠️ No data found for {ticker}")
            return []

        # If multi-indexed columns (can happen with yf), flatten it
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Prioritize 'Close', fallback to other columns if needed
        for col in ["Close", "Adj Close", "Open"]:
            if col in df.columns:
                data_series = df[col]
                break
        else:
            # If none found, try average of High and Low
            if "High" in df.columns and "Low" in df.columns:
                data_series = (df["High"] + df["Low"]) / 2
            else:
                print(f"❌ No usable price data for {ticker}")
                return []

        closes = data_series.dropna().astype(float).tolist()

        # Normalize for chart scaling
        if len(closes) > 1:
            min_val = min(closes)
            max_val = max(closes)
            if max_val != min_val:
                closes = [((val - min_val) / (max_val - min_val)) * 100 for val in closes]
            else:
                closes = [50 for _ in closes]  # flat line fallback

        return closes

    except Exception as e:
        print(f"❌ Error fetching sparkline for {ticker}: {e}")
        return []
