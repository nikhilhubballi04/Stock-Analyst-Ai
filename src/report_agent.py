import os
import requests

USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def generate_report(ticker, latest_close, predicted_price, predicted_return_pct,
                     naive_mape, xgb_mape, rsi, macd_signal, currency="$"):

    if xgb_mape < naive_mape:
        comparison_text = f"The XGBoost model outperformed the naive baseline ({xgb_mape}% vs {naive_mape}% MAPE)."
    elif xgb_mape > naive_mape:
        comparison_text = f"The XGBoost model did NOT outperform the naive baseline ({xgb_mape}% vs {naive_mape}% MAPE) — the naive baseline was slightly more accurate."
    else:
        comparison_text = f"The XGBoost model performed about the same as the naive baseline ({xgb_mape}% MAPE for both)."

    prompt = f"""You are a financial analyst assistant writing a short daily note.

STRICT RULE: Only use the numbers provided below. Do not invent, estimate,
or reference any number not explicitly given to you. Use the comparison
verdict below exactly as given. Use the currency symbol "{currency}" for all prices.

DATA:
- Ticker: {ticker}
- Latest close price: {currency}{latest_close}
- Model-predicted next price: {currency}{predicted_price}
- Predicted return: {predicted_return_pct}%
- Backtest comparison verdict: {comparison_text}
- Current RSI: {rsi} ({"overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral"})
- MACD signal: {macd_signal}

Write a 4-5 sentence analyst note covering the price move, the RSI/MACD signal,
the backtest verdict exactly as given, and a brief note that this isn't financial advice."""

    if USE_GROQ:
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    else:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"]