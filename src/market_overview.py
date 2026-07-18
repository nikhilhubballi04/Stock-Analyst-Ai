import yfinance as yf

INDICES = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "Nifty 50": "^NSEI",
    "Sensex": "^BSESN",
    "Bitcoin": "BTC-USD",
}


def get_market_snapshot():
    """Fetch latest price + % change for major indices, for a live ticker strip."""
    snapshot = []
    for name, symbol in INDICES.items():
        try:
            data = yf.Ticker(symbol).history(period="2d")
            if len(data) < 2:
                continue
            prev_close = data["Close"].iloc[-2]
            latest_close = data["Close"].iloc[-1]
            change_pct = ((latest_close - prev_close) / prev_close) * 100

            snapshot.append({
                "name": name,
                "price": round(float(latest_close), 2),
                "change_pct": round(float(change_pct), 2),
            })
        except Exception:
            continue
    return snapshot