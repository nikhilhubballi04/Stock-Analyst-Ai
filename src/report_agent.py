import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"  # change to llama3.2:3b if you pulled the smaller one


def generate_report(ticker: str, latest_close: float, predicted_price: float,
                     predicted_return_pct: float, naive_mape: float,
                     xgb_mape: float, rsi: float, macd_signal: str,
                     currency: str = "$") -> str:

    if xgb_mape < naive_mape:
        comparison_text = f"The XGBoost model outperformed the naive baseline ({xgb_mape}% vs {naive_mape}% MAPE)."
    elif xgb_mape > naive_mape:
        comparison_text = f"The XGBoost model did NOT outperform the naive baseline ({xgb_mape}% vs {naive_mape}% MAPE) — the naive baseline was slightly more accurate."
    else:
        comparison_text = f"The XGBoost model performed about the same as the naive baseline ({xgb_mape}% MAPE for both)."

    prompt = f"""You are a financial analyst assistant writing a short daily note.

STRICT RULE: Only use the numbers provided below. Do not invent, estimate,
or reference any number not explicitly given to you. Use the comparison
verdict below exactly as given — do not recalculate or reinterpret it.
Use the currency symbol "{currency}" for all prices, not "$".

DATA:
- Ticker: {ticker}
- Latest close price: {currency}{latest_close}
- Model-predicted next price: {currency}{predicted_price}
- Predicted return: {predicted_return_pct}%
- Backtest comparison verdict: {comparison_text}
- Current RSI: {rsi} ({"overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"})
- MACD signal: {macd_signal}

Write a 4-5 sentence analyst note that:
1. States the current price and the model's predicted move using {currency}
2. Mentions the RSI/MACD signal in plain English
3. States the backtest comparison verdict exactly as given above
4. Ends with a brief, appropriately cautious note that this is not financial
   advice and price prediction from technical indicators alone has known
   limitations

Keep it professional and concise, like a real analyst memo."""

    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"]


if __name__ == "__main__":
    test_report = generate_report(
        ticker="AAPL",
        latest_close=315.32,
        predicted_price=314.93,
        predicted_return_pct=-0.123,
        naive_mape=1.6,
        xgb_mape=1.6,
        rsi=58.2,
        macd_signal="bullish crossover"
    )
    print(test_report)