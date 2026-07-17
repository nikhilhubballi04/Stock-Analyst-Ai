import yfinance as yf
import pandas as pd
import ta
from database import init_db, save_data


def fetch_raw_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Pull raw OHLCV data from Yahoo Finance."""
    print(f"Fetching data for {ticker}...")
    df = yf.download(ticker, period=period, interval="1d", progress=False)

    if df.empty:
        raise ValueError(f"No data found for ticker '{ticker}'. Check the symbol.")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]

    return df


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add RSI, MACD, and moving averages as features."""
    df = df.copy()

    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()

    macd = ta.trend.MACD(close=df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    df["ma_20"] = df["close"].rolling(window=20).mean()
    df["ma_50"] = df["close"].rolling(window=50).mean()

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values created by rolling calculations."""
    before = len(df)
    df = df.dropna().reset_index(drop=True)
    after = len(df)
    print(f"Dropped {before - after} rows with missing indicator values (expected, due to rolling windows).")
    return df


def process_ticker(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Full pipeline: fetch -> add indicators -> clean -> save."""
    raw = fetch_raw_data(ticker, period)
    enriched = add_technical_indicators(raw)
    clean = clean_data(enriched)

    columns_needed = ["date", "open", "high", "low", "close", "volume",
                       "rsi", "macd", "macd_signal", "ma_20", "ma_50"]
    clean = clean[columns_needed]
    clean["date"] = clean["date"].astype(str)

    save_data(clean, ticker)
    print(f"Saved {len(clean)} rows for {ticker} to database.\n")
    return clean


def get_latest_signals(df):
    """Extract the most recent RSI and MACD signal for reporting."""
    latest = df.sort_values("date").iloc[-1]
    rsi = round(float(latest["rsi"]), 2)

    macd_signal = "bullish crossover" if latest["macd"] > latest["macd_signal"] else "bearish crossover"

    return rsi, macd_signal


if __name__ == "__main__":
    init_db()

    tickers = ["AAPL", "TSLA", "BTC-USD"]

    for t in tickers:
        try:
            df = process_ticker(t, period="5y")
            print(df.tail(3))
            print("-" * 60)
        except ValueError as e:
            print(e)