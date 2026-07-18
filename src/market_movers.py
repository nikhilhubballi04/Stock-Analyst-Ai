import yfinance as yf

US_WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "AMD", "INTC"]
NSE_WATCHLIST = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
                  "SBIN.NS", "ITC.NS", "BHARTIARTL.NS", "TATAMOTORS.NS", "WIPRO.NS"]


def get_movers(market: str = "US", limit: int = 5):
    """Compute top gainers/losers from a tracked watchlist."""
    tickers = US_WATCHLIST if market == "US" else NSE_WATCHLIST
    movers = []

    for symbol in tickers:
        try:
            data = yf.Ticker(symbol).history(period="2d")
            if len(data) < 2:
                continue
            prev_close = data["Close"].iloc[-2]
            latest_close = data["Close"].iloc[-1]
            change_pct = ((latest_close - prev_close) / prev_close) * 100

            display_name = symbol.replace(".NS", "")
            movers.append({
                "symbol": display_name,
                "price": round(float(latest_close), 2),
                "change_pct": round(float(change_pct), 2),
            })
        except Exception:
            continue

    gainers = sorted([m for m in movers if m["change_pct"] > 0], key=lambda x: -x["change_pct"])[:limit]
    losers = sorted([m for m in movers if m["change_pct"] < 0], key=lambda x: x["change_pct"])[:limit]

    return gainers, losers